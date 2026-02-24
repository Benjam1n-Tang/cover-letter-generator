from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
from datetime import datetime
import textwrap
import logging

logger = logging.getLogger(__name__)


class PDFGenerator:
    """Generates PDF cover letters"""

    def __init__(self):
        self.cover_letters_dir = Path("data/cover_letters")
        self.cover_letters_dir.mkdir(exist_ok=True)

        # Set up styles with Times New Roman
        self.styles = getSampleStyleSheet()

        # Header info style (name, address, contact) - single line spacing
        self.header_info_style = ParagraphStyle(
            "HeaderInfo",
            parent=self.styles["Normal"],
            fontName="Times-Roman",
            fontSize=12,
            spaceAfter=0,
            textColor=black,
            alignment=0,  # Left align
            leading=14,  # Single line spacing (1.17x font size)
        )

        # Date style - single line spacing
        self.date_style = ParagraphStyle(
            "DateStyle",
            parent=self.styles["Normal"],
            fontName="Times-Roman",
            fontSize=12,
            spaceAfter=6,  # Reduced spacing
            textColor=black,
            alignment=0,  # Left align
            leading=14,
        )

        # Company address style - single line spacing
        self.company_style = ParagraphStyle(
            "CompanyStyle",
            parent=self.styles["Normal"],
            fontName="Times-Roman",
            fontSize=12,
            spaceAfter=0,  # No extra spacing between lines
            textColor=black,
            alignment=0,  # Left align
            leading=14,
        )

        # Body text style - single line spacing, tighter margins
        self.body_style = ParagraphStyle(
            "BodyStyle",
            parent=self.styles["Normal"],
            fontName="Times-Roman",
            fontSize=12,
            spaceAfter=10,  # Reduced paragraph spacing
            textColor=black,
            alignment=4,  # Justified
            leading=14,  # Single line spacing
            leftIndent=0,
            rightIndent=0,
        )

    def generate_pdf(
        self,
        cover_letter_text: str,
        profile: dict,
        company_name: str,
        company_location: str,
        company_address: str = "",
        hiring_manager: str = "",
        hiring_manager_role: str = "",
        filename: str = "",
    ) -> str:
        """Generate PDF cover letter using professional template format"""
        try:
            # Create filename with .pdf extension
            pdf_filename = f"{filename}.pdf"
            pdf_path = self.cover_letters_dir / pdf_filename

            # Create PDF document with tighter margins for single-page layout
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=letter,
                topMargin=0.75 * inch,  # Reduced margins
                bottomMargin=0.75 * inch,
                leftMargin=0.75 * inch,
                rightMargin=0.75 * inch,
            )

            # Build document content
            story = []

            # Header with user information - formatted as requested
            # Name
            story.append(
                Paragraph(
                    f"{profile.get('first_name', '')} {profile.get('last_name', '')}",
                    self.header_info_style,
                )
            )
            # Address
            story.append(Paragraph(profile.get("address", ""), self.header_info_style))
            # City, State, ZIP
            city_state_zip = f"{profile.get('city', '')}, {profile.get('state', '')} {profile.get('zip_code', '')}"
            story.append(Paragraph(city_state_zip, self.header_info_style))
            # Email
            story.append(Paragraph(profile.get("email", ""), self.header_info_style))
            # Phone
            story.append(Paragraph(profile.get("phone", ""), self.header_info_style))

            # Add 2 lines after header
            story.append(Spacer(1, 0.3 * inch))

            # Date
            current_date = datetime.now().strftime("%B %d, %Y")
            story.append(Paragraph(current_date, self.date_style))

            # Reduced space after date
            story.append(Spacer(1, 0.15 * inch))

            # Company information with hiring manager logic
            if hiring_manager and hiring_manager_role:
                # Extract last name and determine Mr./Mrs. (defaulting to Mr.)
                last_name = (
                    hiring_manager.split()[-1]
                    if hiring_manager.split()
                    else hiring_manager
                )
                story.append(Paragraph(f"Mr. {last_name}", self.company_style))
                story.append(Paragraph(hiring_manager_role, self.company_style))

            story.append(Paragraph(company_name, self.company_style))
            if company_address:
                story.append(Paragraph(company_address, self.company_style))
            story.append(Paragraph(company_location, self.company_style))

            # Add more space after company info before greeting
            story.append(Spacer(1, 0.25 * inch))

            # Greeting
            if hiring_manager and hiring_manager_role:
                last_name = (
                    hiring_manager.split()[-1]
                    if hiring_manager.split()
                    else hiring_manager
                )
                greeting = f"Dear Mr. {last_name},"
            else:
                greeting = "Dear Hiring Manager,"
            story.append(Paragraph(greeting, self.body_style))

            # Process cover letter text into paragraphs
            paragraphs = self._process_cover_letter_text(cover_letter_text)

            for paragraph_text in paragraphs:
                if paragraph_text.strip():
                    # Escape HTML special characters and preserve line breaks
                    processed_text = self._escape_html(paragraph_text)
                    story.append(Paragraph(processed_text, self.body_style))

            # Signature
            story.append(Spacer(1, 0.2 * inch))
            story.append(Paragraph(f"Sincerely,", self.body_style))
            story.append(Spacer(1, 0.3 * inch))
            story.append(
                Paragraph(
                    f"{profile.get('first_name', '')} {profile.get('last_name', '')}",
                    self.body_style,
                )
            )

            # Build PDF
            doc.build(story)

            logger.info(f"PDF generated successfully: {pdf_path}")
            return str(pdf_path)

        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise Exception(f"Failed to generate PDF: {str(e)}")

    def _process_cover_letter_text(self, text: str) -> list:
        """Process cover letter text into paragraph list"""
        # Split by double newlines to identify paragraphs
        paragraphs = text.split("\n\n")

        processed_paragraphs = []
        for paragraph in paragraphs:
            # Clean up the paragraph
            cleaned = paragraph.strip().replace("\n", " ")
            if cleaned:
                processed_paragraphs.append(cleaned)

        return processed_paragraphs

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters for ReportLab"""
        # Basic HTML escaping
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        return text

    def generate_resume_pdf(
        self, resume_content: str, profile: dict, filename: str
    ) -> str:
        """Generate PDF resume"""
        try:
            # Create filename with .pdf extension
            pdf_filename = f"{filename}.pdf"
            pdf_path = self.cover_letters_dir / pdf_filename

            # Create PDF document
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=letter,
                topMargin=0.75 * inch,
                bottomMargin=0.75 * inch,
                leftMargin=0.75 * inch,
                rightMargin=0.75 * inch,
            )

            # Build document content
            story = []

            # Header with user information
            header_text = f"""<b>{profile.get('first_name', '')} {profile.get('last_name', '')}</b><br/>
{profile.get('address', '')}<br/>
{profile.get('phone', '')} | {profile.get('email', '')}"""

            story.append(Paragraph(header_text, self.header_style))
            story.append(Spacer(1, 0.5 * inch))

            # Process resume content into sections
            resume_sections = self._process_resume_text(resume_content)

            for section in resume_sections:
                if section.strip():
                    # Check if it looks like a section header (all caps or starts with common resume sections)
                    if self._is_section_header(section):
                        # Use header style for section headers
                        story.append(
                            Paragraph(self._escape_html(section), self.header_style)
                        )
                        story.append(Spacer(1, 0.1 * inch))
                    else:
                        # Use body style for content
                        story.append(
                            Paragraph(self._escape_html(section), self.body_style)
                        )

            # Build PDF
            doc.build(story)

            logger.info(f"Resume PDF generated successfully: {pdf_path}")
            return str(pdf_path)

        except Exception as e:
            logger.error(f"Error generating resume PDF: {str(e)}")
            raise Exception(f"Failed to generate resume PDF: {str(e)}")

    def _process_resume_text(self, text: str) -> list:
        """Process resume text into sections"""
        # Split by double newlines to identify sections
        sections = text.split("\n\n")

        processed_sections = []
        for section in sections:
            # Clean up the section but preserve line breaks within sections
            cleaned = section.strip()
            if cleaned:
                processed_sections.append(cleaned)

        return processed_sections

    def _is_section_header(self, text: str) -> bool:
        """Check if text is likely a section header"""
        text = text.strip()

        # Common resume section headers
        section_keywords = [
            "PROFESSIONAL SUMMARY",
            "SUMMARY",
            "OBJECTIVE",
            "EXPERIENCE",
            "PROFESSIONAL EXPERIENCE",
            "WORK EXPERIENCE",
            "EDUCATION",
            "SKILLS",
            "TECHNICAL SKILLS",
            "CERTIFICATIONS",
            "PROJECTS",
            "ACHIEVEMENTS",
            "AWARDS",
            "LANGUAGES",
            "VOLUNTEER",
            "PUBLICATIONS",
            "REFERENCES",
        ]

        # Check if it's all uppercase and short (likely a header)
        if text.isupper() and len(text) < 50:
            return True

        # Check if it matches common section keywords
        for keyword in section_keywords:
            if keyword in text.upper():
                return True

        return False

    def delete_pdf(self, filename: str) -> bool:
        """Delete a PDF file"""
        try:
            pdf_path = self.cover_letters_dir / filename
            if pdf_path.exists():
                pdf_path.unlink()
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting PDF: {str(e)}")
            return False
