import os
from datetime import datetime
import json
from pathlib import Path
import uuid
from flask import Flask, request, jsonify, render_template, send_file
from werkzeug.utils import secure_filename
import logging
from openai import OpenAI
from dotenv import load_dotenv
from app.pdf_generator import PDFGenerator
from app.resume_parser import ResumeParser
from app.profile_manager import ProfileManager
from app.template_manager import TemplateManager

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")
app.config["DEBUG"] = os.environ.get("DEBUG", "True").lower() == "true"

# Initialize OpenAI client for GitHub Models
client = OpenAI(
    base_url="https://models.github.ai/inference",
    api_key=os.environ.get("GITHUB_TOKEN"),
)

# Create data directories
DATA_DIR = Path("data")
RESUME_DIR = DATA_DIR / "resume"
COVER_LETTERS_DIR = DATA_DIR / "cover_letters"
PROFILES_DIR = DATA_DIR / "profiles"
TEMPLATES_DIR = DATA_DIR / "templates"

# Ensure directories exist
for directory in [DATA_DIR, RESUME_DIR, COVER_LETTERS_DIR, PROFILES_DIR, TEMPLATES_DIR]:
    directory.mkdir(exist_ok=True)

# Initialize managers
pdf_generator = PDFGenerator()
resume_parser = ResumeParser()
profile_manager = ProfileManager(PROFILES_DIR)
template_manager = TemplateManager(TEMPLATES_DIR)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route("/")
def index():
    """Render the main page"""
    return render_template("index.html")


@app.route("/api/profile", methods=["GET", "POST"])
def handle_profile():
    """Handle user profile operations"""
    if request.method == "GET":
        profile = profile_manager.get_profile()
        return jsonify(profile)

    elif request.method == "POST":
        profile_data = request.json
        profile_manager.save_profile(profile_data)
        return jsonify({"message": "Profile saved successfully"})


@app.route("/api/resume", methods=["GET", "POST"])
def handle_resume():
    """Handle resume operations"""
    if request.method == "GET":
        # Check if resume exists
        resume_content = resume_parser.get_latest_resume_content()
        if resume_content:
            return jsonify({"has_resume": True, "message": "Resume found"})
        else:
            return jsonify({"has_resume": False, "message": "No resume uploaded"})

    elif request.method == "POST":
        """Upload and parse resume"""
        if "resume" not in request.files:
            return jsonify({"error": "No resume file provided"}), 400

        file = request.files["resume"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        if file:
            filename = secure_filename(file.filename)
            filepath = RESUME_DIR / filename
            file.save(str(filepath))

            # Parse resume content
            resume_content = resume_parser.parse_resume(str(filepath))

            return jsonify(
                {
                    "message": "Resume uploaded successfully",
                    "filename": filename,
                    "content": resume_content,
                }
            )


@app.route("/api/generate-resume-pdf", methods=["POST"])
def generate_resume_pdf():
    """Generate PDF version of uploaded resume"""
    try:
        # Get user profile
        profile = profile_manager.get_profile()
        if not profile:
            return (
                jsonify(
                    {"error": "No user profile found. Please create a profile first."}
                ),
                400,
            )

        # Get resume content
        resume_content = resume_parser.get_latest_resume_content()
        if not resume_content:
            return (
                jsonify({"error": "No resume found. Please upload a resume first."}),
                400,
            )

        # Generate PDF filename
        filename = f"{profile['first_name']}_{profile['last_name']}_Resume"
        pdf_path = pdf_generator.generate_resume_pdf(resume_content, profile, filename)

        # Save resume PDF metadata
        resume_id = str(uuid.uuid4())
        metadata = {
            "id": resume_id,
            "type": "resume",
            "filename": f"{filename}.pdf",
            "created_at": datetime.now().isoformat(),
        }

        metadata_path = COVER_LETTERS_DIR / f"resume_{resume_id}.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        return jsonify(
            {
                "message": "Resume PDF generated successfully",
                "resume_id": resume_id,
                "filename": f"{filename}.pdf",
                "download_url": f"/api/download-resume/{resume_id}",
            }
        )

    except Exception as e:
        logger.error(f"Error generating resume PDF: {str(e)}")
        return jsonify({"error": "Failed to generate resume PDF"}), 500


@app.route("/api/download-resume/<resume_id>")
def download_resume_pdf(resume_id):
    """Download a generated resume PDF"""
    metadata_path = COVER_LETTERS_DIR / f"resume_{resume_id}.json"

    if not metadata_path.exists():
        return jsonify({"error": "Resume PDF not found"}), 404

    with open(metadata_path, "r") as f:
        metadata = json.load(f)

    pdf_path = COVER_LETTERS_DIR / metadata["filename"]

    if not pdf_path.exists():
        return jsonify({"error": "PDF file not found"}), 404

    return send_file(
        str(pdf_path), as_attachment=True, download_name=metadata["filename"]
    )


@app.route("/api/generate-cover-letter", methods=["POST"])
def generate_cover_letter():
    """Generate a cover letter based on job details"""
    try:
        data = request.json
        hiring_manager = data.get("hiring_manager", "")
        hiring_manager_role = data.get("hiring_manager_role", "")
        job_role = data.get("job_role")
        company_name = data.get("company_name")
        company_address = data.get("company_address", "")
        company_city = data.get("company_city")
        company_state = data.get("company_state")
        company_zip = data.get("company_zip", "")
        job_description = data.get("job_description")

        if not all(
            [job_role, company_name, company_city, company_state, job_description]
        ):
            return (
                jsonify(
                    {
                        "error": "Job role, company name, company city, company state, and job description are required"
                    }
                ),
                400,
            )

        # Get user profile
        profile = profile_manager.get_profile()
        if not profile:
            return (
                jsonify(
                    {"error": "No user profile found. Please create a profile first."}
                ),
                400,
            )

        # Get resume content
        resume_content = resume_parser.get_latest_resume_content()
        if not resume_content:
            return (
                jsonify({"error": "No resume found. Please upload a resume first."}),
                400,
            )

        # Build company location string
        company_location = f"{company_city}, {company_state}"
        if company_zip:
            company_location += f" {company_zip}"

        # Generate cover letter using AI with new parameters
        cover_letter_text = generate_cover_letter_ai(
            profile,
            resume_content,
            job_role,
            company_name,
            company_location,
            job_description,
            hiring_manager,
            hiring_manager_role,
        )

        # Return text for editing instead of immediately generating PDF
        return jsonify(
            {
                "message": "Cover letter generated successfully",
                "cover_letter_text": cover_letter_text,
                "company_name": company_name,
                "company_location": company_location,
                "company_address": company_address,
                "hiring_manager": hiring_manager,
                "hiring_manager_role": hiring_manager_role,
                "job_role": job_role,
            }
        )

    except Exception as e:
        logger.error(f"Error generating cover letter: {str(e)}")
        return jsonify({"error": "Failed to generate cover letter"}), 500


@app.route("/api/generate-cover-letter-pdf", methods=["POST"])
def generate_cover_letter_pdf():
    """Generate PDF from edited cover letter text"""
    try:
        data = request.json
        cover_letter_text = data.get("cover_letter_text")
        company_name = data.get("company_name")
        company_location = data.get("company_location", "")
        company_address = data.get("company_address", "")
        hiring_manager = data.get("hiring_manager", "")
        hiring_manager_role = data.get("hiring_manager_role", "")

        if not all([cover_letter_text, company_name]):
            return (
                jsonify({"error": "Cover letter text and company name are required"}),
                400,
            )

        # Get user profile
        profile = profile_manager.get_profile()
        if not profile:
            return jsonify({"error": "No user profile found"}), 400

        # Generate PDF with new parameters
        filename = f"{profile['first_name']}_{profile['last_name']}_CoverLetter_{company_name.replace(' ', '_')}"
        pdf_path = pdf_generator.generate_pdf(
            cover_letter_text,
            profile,
            company_name,
            company_location,
            company_address,
            hiring_manager,
            hiring_manager_role,
            filename,
        )

        # Generate unique filename for direct download - no JSON metadata needed
        cover_letter_id = str(uuid.uuid4())
        pdf_filename = f"{filename}_{cover_letter_id[:8]}.pdf"

        # Rename the PDF to include unique ID
        final_pdf_path = COVER_LETTERS_DIR / pdf_filename
        Path(pdf_path).rename(final_pdf_path)

        return jsonify(
            {
                "message": "Cover letter PDF generated successfully",
                "cover_letter_id": cover_letter_id[:8],
                "filename": pdf_filename,
                "download_url": f"/api/download/{pdf_filename}",
            }
        )

    except Exception as e:
        logger.error(f"Error generating cover letter PDF: {str(e)}")
        return jsonify({"error": "Failed to generate cover letter PDF"}), 500


@app.route("/api/download/<filename>")
def download_cover_letter(filename):
    """Download a generated cover letter PDF directly"""
    # Security check - ensure filename ends with .pdf and contains no path traversal
    if not filename.endswith(".pdf") or "/" in filename or ".." in filename:
        return jsonify({"error": "Invalid filename"}), 400

    pdf_path = COVER_LETTERS_DIR / filename

    if not pdf_path.exists():
        return jsonify({"error": "PDF file not found"}), 404

    return send_file(str(pdf_path), as_attachment=True, download_name=filename)


@app.route("/api/cover-letters", methods=["GET"])
def list_cover_letters():
    """List all generated cover letters"""
    cover_letters = []

    for metadata_file in COVER_LETTERS_DIR.glob("*.json"):
        try:
            with open(metadata_file, "r") as f:
                metadata = json.load(f)

            # Remove text content from list view for performance
            metadata_summary = {
                k: v for k, v in metadata.items() if k != "text_content"
            }
            cover_letters.append(metadata_summary)
        except Exception as e:
            logger.error(f"Error reading metadata file {metadata_file}: {str(e)}")

    # Sort by creation date, newest first
    cover_letters.sort(key=lambda x: x["created_at"], reverse=True)

    return jsonify(cover_letters)


# Template Management Endpoints
@app.route("/api/templates", methods=["GET", "POST"])
def handle_templates():
    """Handle template operations"""
    if request.method == "GET":
        templates = template_manager.list_templates()
        return jsonify(templates)

    elif request.method == "POST":
        data = request.json
        name = data.get("name")
        content = data.get("content")

        if not name or not content:
            return jsonify({"error": "Template name and content are required"}), 400

        success = template_manager.save_template(name, content)
        if success:
            return jsonify({"message": "Template saved successfully"})
        else:
            return jsonify({"error": "Failed to save template"}), 500


@app.route("/api/templates/<template_name>", methods=["GET", "DELETE"])
def handle_single_template(template_name):
    """Handle single template operations"""
    if request.method == "GET":
        template = template_manager.get_template(template_name)
        if template:
            return jsonify(template)
        else:
            return jsonify({"error": "Template not found"}), 404

    elif request.method == "DELETE":
        success = template_manager.delete_template(template_name)
        if success:
            return jsonify({"message": "Template deleted successfully"})
        else:
            return jsonify({"error": "Template not found"}), 404


@app.route("/api/generate-from-template", methods=["POST"])
def generate_from_template():
    """Generate cover letter from template"""
    try:
        data = request.json
        template_name = data.get("template_name")
        job_data = data.get("job_data", {})

        if not template_name:
            return jsonify({"error": "Template name is required"}), 400

        # Get user profile and resume content
        profile = profile_manager.get_profile()
        if not profile:
            return jsonify({"error": "No user profile found"}), 400

        resume_content = resume_parser.get_latest_resume_content() or ""

        # Get smart replacements
        replacements = template_manager.get_smart_replacements(
            job_data, profile, resume_content
        )

        # Generate content from template
        cover_letter_text = template_manager.generate_from_template(
            template_name, replacements
        )

        if not cover_letter_text:
            return (
                jsonify(
                    {"error": "Failed to generate from template or template not found"}
                ),
                400,
            )

        return jsonify(
            {
                "cover_letter_text": cover_letter_text,
                "company_name": job_data.get("company_name", ""),
                "company_location": f"{job_data.get('company_city', '')}, {job_data.get('company_state', '')}".strip(
                    ", "
                ),
                "company_address": job_data.get("company_address", ""),
                "hiring_manager": job_data.get("hiring_manager", ""),
                "hiring_manager_role": job_data.get("hiring_manager_role", ""),
                "job_role": job_data.get("job_role", ""),
                "replacements_used": replacements,
            }
        )

    except Exception as e:
        logger.error(f"Error generating from template: {str(e)}")
        return jsonify({"error": "Failed to generate cover letter from template"}), 500


def generate_cover_letter_ai(
    profile,
    resume_content,
    job_role,
    company_name,
    location,
    job_description,
    hiring_manager="",
    hiring_manager_role="",
    template_guidance=None,
):
    """Generate cover letter using AI with optional template guidance"""

    # Handle template guidance
    template_guidance_text = ""
    if template_guidance:
        template_guidance_text = f"\n\nTEMPLATE GUIDANCE (use as inspiration for style and structure):\n{template_guidance}\n"
    system_prompt = """You are an expert cover letter writer who creates highly professional, authentic cover letters that sound genuinely human-written and passionate, never robotic or AI-generated.

CRITICAL TONE REQUIREMENTS:
- Write in a natural, conversational yet professional tone
- Sound genuinely excited and passionate about the specific opportunity
- NEVER use double dashes (--) or em dashes that sound AI-generated
- Use simple, clear language that feels authentic
- Avoid overly formal or robotic phrasing
- Focus on quality over quantity - every sentence should add value
- DO NOT copy specific numbers, percentages, or detailed project descriptions from the resume
- Use the resume as context for understanding skills and experience level, not as content to copy

COVER LETTER PURPOSE:
- Show connection and genuine interest in THIS specific company
- Demonstrate what value you would bring to THEIR team
- Explain how your background makes you excited about THEIR mission/work
- Focus on learnings, growth, and team contribution rather than project details

REQUIRED STRUCTURE (exactly 4 paragraphs):

1. OPENING PARAGRAPH (3-4 sentences):
   - Express strong interest in the specific role at the specific company
   - Briefly introduce who you are (student status, graduation year, etc.)
   - Mention something specific about the company's work, products, or mission
   - State what draws you to their team/values and how it aligns with your passion

2. EXPERIENCE PARAGRAPH (4-5 sentences):
   - Highlight the TYPE of professional experience you have (internships, projects, etc.)
   - Focus on LEARNINGS and SKILLS GAINED, not specific project details or numbers
   - Explain what this experience taught you about teamwork, problem-solving, or engineering
   - Connect how these learnings would help you contribute to their team's success

3. TECHNICAL/PROJECT PARAGRAPH (3-4 sentences):
   - Discuss your technical growth and problem-solving approach
   - Focus on learning new technologies quickly and adaptability
   - Show your passion for building solutions that solve real problems
   - Connect your technical mindset to what the company/role needs

4. CLOSING PARAGRAPH (2-3 sentences):
   - Confidently state how your skills and approach would make you valuable to their team
   - Thank them professionally
   - Express forward-looking enthusiasm about contributing to their specific mission

DO NOT include header, greeting, or signature - only the 4 body paragraphs.
Prioritize authenticity and genuine company connection over resume rehashing."""

    hiring_manager_info = ""
    if hiring_manager and hiring_manager_role:
        hiring_manager_info = (
            f"\nHIRING MANAGER: {hiring_manager}, {hiring_manager_role}"
        )

    user_prompt = f"""Write a professional, human-sounding cover letter body for:

APPLICANT: {profile.get('first_name', '')} {profile.get('last_name', '')}
POSITION: {job_role}
COMPANY: {company_name}
LOCATION: {location}{hiring_manager_info}

APPLICANT'S BACKGROUND:
{resume_content}

JOB DETAILS:
{job_description}
{template_guidance_text}

IMPORTANT: Use the background information to understand the applicant's experience level and skills, but DO NOT copy specific project details, numbers, percentages, or technical implementations. Focus on learnings, growth, and how the experience translates to value for {company_name}.

Write exactly 4 paragraphs following this structure:

PARAGRAPH 1: Express genuine interest in the {job_role} position at {company_name}. Introduce yourself as a Computer Science student graduating in 2026. Research and mention something specific about {company_name}'s work, products, or mission that genuinely interests you. Explain what draws you to their team's focus and how it aligns with your passion for building meaningful software solutions.

PARAGRAPH 2: Discuss your internship/professional experience in general terms - focus on what you LEARNED about effective engineering, teamwork, or business impact rather than specific project details. Explain how these learnings shaped your approach to software development and how they would help you contribute meaningfully to {company_name}'s team.

PARAGRAPH 3: Talk about your technical growth and passion for learning new technologies. Focus on your problem-solving mindset and adaptability rather than specific project implementations. Show how you approach challenges and how this mindset would benefit {company_name}'s {job_role} work.

PARAGRAPH 4: Confidently state how your technical foundation, learning ability, and collaborative approach would make you a valuable addition to their team. Thank them for their time and consideration. Express genuine enthusiasm about contributing to {company_name}'s mission and success.

Remember: This is about YOUR CONNECTION to {company_name} and the VALUE you would bring to THEIR team, not a summary of your resume. Sound like you've researched {company_name} specifically and are genuinely excited about this opportunity."""

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model="openai/gpt-4o-mini",
            temperature=0.6,
            max_tokens=1500,
            top_p=1,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.error(f"Error generating cover letter with AI: {str(e)}")
        raise Exception("Failed to generate cover letter content")


if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"], host="0.0.0.0", port=5001)
