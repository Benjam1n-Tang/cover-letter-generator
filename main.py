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

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key')
app.config['DEBUG'] = os.environ.get('DEBUG', 'True').lower() == 'true'

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

# Ensure directories exist
for directory in [DATA_DIR, RESUME_DIR, COVER_LETTERS_DIR, PROFILES_DIR]:
    directory.mkdir(exist_ok=True)

# Initialize managers
pdf_generator = PDFGenerator()
resume_parser = ResumeParser()
profile_manager = ProfileManager(PROFILES_DIR)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/profile', methods=['GET', 'POST'])
def handle_profile():
    """Handle user profile operations"""
    if request.method == 'GET':
        profile = profile_manager.get_profile()
        return jsonify(profile)
    
    elif request.method == 'POST':
        profile_data = request.json
        profile_manager.save_profile(profile_data)
        return jsonify({"message": "Profile saved successfully"})

@app.route('/api/resume', methods=['POST'])
def upload_resume():
    """Upload and parse resume"""
    if 'resume' not in request.files:
        return jsonify({"error": "No resume file provided"}), 400
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = RESUME_DIR / filename
        file.save(str(filepath))
        
        # Parse resume content
        resume_content = resume_parser.parse_resume(str(filepath))
        
        return jsonify({
            "message": "Resume uploaded successfully",
            "filename": filename,
            "content": resume_content
        })

@app.route('/api/generate-resume-pdf', methods=['POST'])
def generate_resume_pdf():
    """Generate PDF version of uploaded resume"""
    try:
        # Get user profile
        profile = profile_manager.get_profile()
        if not profile:
            return jsonify({"error": "No user profile found. Please create a profile first."}), 400
        
        # Get resume content
        resume_content = resume_parser.get_latest_resume_content()
        if not resume_content:
            return jsonify({"error": "No resume found. Please upload a resume first."}), 400
        
        # Generate PDF filename
        filename = f"{profile['first_name']}_{profile['last_name']}_Resume"
        pdf_path = pdf_generator.generate_resume_pdf(
            resume_content, 
            profile, 
            filename
        )
        
        # Save resume PDF metadata
        resume_id = str(uuid.uuid4())
        metadata = {
            "id": resume_id,
            "type": "resume",
            "filename": f"{filename}.pdf",
            "created_at": datetime.now().isoformat()
        }
        
        metadata_path = COVER_LETTERS_DIR / f"resume_{resume_id}.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return jsonify({
            "message": "Resume PDF generated successfully",
            "resume_id": resume_id,
            "filename": f"{filename}.pdf",
            "download_url": f"/api/download-resume/{resume_id}"
        })
        
    except Exception as e:
        logger.error(f"Error generating resume PDF: {str(e)}")
        return jsonify({"error": "Failed to generate resume PDF"}), 500

@app.route('/api/download-resume/<resume_id>')
def download_resume_pdf(resume_id):
    """Download a generated resume PDF"""
    metadata_path = COVER_LETTERS_DIR / f"resume_{resume_id}.json"
    
    if not metadata_path.exists():
        return jsonify({"error": "Resume PDF not found"}), 404
    
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    pdf_path = COVER_LETTERS_DIR / metadata['filename']
    
    if not pdf_path.exists():
        return jsonify({"error": "PDF file not found"}), 404
    
    return send_file(str(pdf_path), as_attachment=True, download_name=metadata['filename'])

@app.route('/api/generate-cover-letter', methods=['POST'])
def generate_cover_letter():
    """Generate a cover letter based on job details"""
    try:
        data = request.json
        company_name = data.get('company_name')
        location = data.get('location')
        job_description = data.get('job_description')
        
        if not all([company_name, location, job_description]):
            return jsonify({"error": "Company name, location, and job description are required"}), 400
        
        # Get user profile
        profile = profile_manager.get_profile()
        if not profile:
            return jsonify({"error": "No user profile found. Please create a profile first."}), 400
        
        # Get resume content
        resume_content = resume_parser.get_latest_resume_content()
        if not resume_content:
            return jsonify({"error": "No resume found. Please upload a resume first."}), 400
        
        # Generate cover letter using AI
        cover_letter_text = generate_cover_letter_ai(
            profile, resume_content, company_name, location, job_description
        )
        
        # Generate PDF
        filename = f"{profile['first_name']}_{profile['last_name']}_CoverLetter_{company_name.replace(' ', '_')}"
        pdf_path = pdf_generator.generate_pdf(
            cover_letter_text, 
            profile, 
            company_name, 
            filename
        )
        
        # Save cover letter metadata
        cover_letter_id = str(uuid.uuid4())
        metadata = {
            "id": cover_letter_id,
            "company_name": company_name,
            "location": location,
            "job_description": job_description,
            "filename": f"{filename}.pdf",
            "created_at": datetime.now().isoformat(),
            "text_content": cover_letter_text
        }
        
        metadata_path = COVER_LETTERS_DIR / f"{cover_letter_id}.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return jsonify({
            "message": "Cover letter generated successfully",
            "cover_letter_id": cover_letter_id,
            "filename": f"{filename}.pdf",
            "download_url": f"/api/download/{cover_letter_id}"
        })
        
    except Exception as e:
        logger.error(f"Error generating cover letter: {str(e)}")
        return jsonify({"error": "Failed to generate cover letter"}), 500

@app.route('/api/download/<cover_letter_id>')
def download_cover_letter(cover_letter_id):
    """Download a generated cover letter"""
    metadata_path = COVER_LETTERS_DIR / f"{cover_letter_id}.json"
    
    if not metadata_path.exists():
        return jsonify({"error": "Cover letter not found"}), 404
    
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    pdf_path = COVER_LETTERS_DIR / metadata['filename']
    
    if not pdf_path.exists():
        return jsonify({"error": "PDF file not found"}), 404
    
    return send_file(str(pdf_path), as_attachment=True, download_name=metadata['filename'])

@app.route('/api/cover-letters', methods=['GET'])
def list_cover_letters():
    """List all generated cover letters"""
    cover_letters = []
    
    for metadata_file in COVER_LETTERS_DIR.glob("*.json"):
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Remove text content from list view for performance
            metadata_summary = {k: v for k, v in metadata.items() if k != 'text_content'}
            cover_letters.append(metadata_summary)
        except Exception as e:
            logger.error(f"Error reading metadata file {metadata_file}: {str(e)}")
    
    # Sort by creation date, newest first
    cover_letters.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify(cover_letters)

def generate_cover_letter_ai(profile, resume_content, company_name, location, job_description):
    """Generate cover letter using AI"""
    
    system_prompt = f"""You are an expert cover letter writer. Generate a professional, engaging one-page cover letter based on the provided information.

Guidelines:
- Keep it to approximately 3-4 paragraphs
- Make it specific to the company and role
- Highlight relevant experience from the resume
- Use a professional yet engaging tone
- Include specific examples when possible
- End with a strong call to action

The cover letter should NOT include the header information (name, address, contact info) as that will be added separately."""

    user_prompt = f"""Please write a cover letter for the following:

APPLICANT PROFILE:
Name: {profile.get('first_name', '')} {profile.get('last_name', '')}
Email: {profile.get('email', '')}
Phone: {profile.get('phone', '')}
Address: {profile.get('address', '')}

RESUME CONTENT:
{resume_content}

JOB DETAILS:
Company: {company_name}
Location: {location}
Job Description: {job_description}

Please generate a compelling cover letter that demonstrates why this candidate is perfect for this role."""

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="openai/gpt-4o-mini",
            temperature=0.7,
            max_tokens=2000,
            top_p=1
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.error(f"Error generating cover letter with AI: {str(e)}")
        raise Exception("Failed to generate cover letter content")

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5000)