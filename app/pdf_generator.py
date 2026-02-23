from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import black
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
        
        # Set up styles
        self.styles = getSampleStyleSheet()
        
        # Custom header style
        self.header_style = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Heading1'],
            fontSize=14,
            spaceAfter=12,
            textColor=black,
            alignment=0,  # Left align
        )
        
        # Custom body style
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            textColor=black,
            alignment=4,  # Justified
            leftIndent=0,
            rightIndent=0,
        )
        
        # Date style
        self.date_style = ParagraphStyle(
            'DateStyle',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=24,
            textColor=black,
            alignment=2,  # Right align
        )
    
    def generate_pdf(self, cover_letter_text: str, profile: dict, company_name: str, filename: str) -> str:
        """Generate PDF cover letter"""
        try:
            # Create filename with .pdf extension
            pdf_filename = f"{filename}.pdf"
            pdf_path = self.cover_letters_dir / pdf_filename
            
            # Create PDF document
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=letter,
                topMargin=1*inch,
                bottomMargin=1*inch,
                leftMargin=1*inch,
                rightMargin=1*inch
            )
            
            # Build document content
            story = []
            
            # Header with user information
            header_text = f"""<b>{profile.get('first_name', '')} {profile.get('last_name', '')}</b><br/>
{profile.get('address', '')}<br/>
{profile.get('phone', '')} | {profile.get('email', '')}"""
            
            story.append(Paragraph(header_text, self.header_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Date
            current_date = datetime.now().strftime("%B %d, %Y")
            story.append(Paragraph(current_date, self.date_style))
            
            # Add some space after date
            story.append(Spacer(1, 0.2*inch))
            
            # Process cover letter text into paragraphs
            paragraphs = self._process_cover_letter_text(cover_letter_text)
            
            for paragraph_text in paragraphs:
                if paragraph_text.strip():
                    # Escape HTML special characters and preserve line breaks
                    processed_text = self._escape_html(paragraph_text)
                    story.append(Paragraph(processed_text, self.body_style))
            
            # Add signature space
            story.append(Spacer(1, 0.5*inch))
            story.append(Paragraph(f"Sincerely,<br/><br/><br/>{profile.get('first_name', '')} {profile.get('last_name', '')}", self.body_style))
            
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
        paragraphs = text.split('\n\n')
        
        processed_paragraphs = []
        for paragraph in paragraphs:
            # Clean up the paragraph
            cleaned = paragraph.strip().replace('\n', ' ')
            if cleaned:
                processed_paragraphs.append(cleaned)
        
        return processed_paragraphs
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters for ReportLab"""
        # Basic HTML escaping
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        return text
    
    def generate_resume_pdf(self, resume_content: str, profile: dict, filename: str) -> str:
        """Generate PDF resume"""
        try:
            # Create filename with .pdf extension
            pdf_filename = f"{filename}.pdf"
            pdf_path = self.cover_letters_dir / pdf_filename
            
            # Create PDF document
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=letter,
                topMargin=1*inch,
                bottomMargin=1*inch,
                leftMargin=1*inch,
                rightMargin=1*inch
            )
            
            # Build document content
            story = []
            
            # Header with user information
            header_text = f"""<b>{profile.get('first_name', '')} {profile.get('last_name', '')}</b><br/>
{profile.get('address', '')}<br/>
{profile.get('phone', '')} | {profile.get('email', '')}"""
            
            story.append(Paragraph(header_text, self.header_style))
            story.append(Spacer(1, 0.5*inch))
            
            # Process resume content into sections
            resume_sections = self._process_resume_text(resume_content)
            
            for section in resume_sections:
                if section.strip():
                    # Check if it looks like a section header (all caps or starts with common resume sections)
                    if self._is_section_header(section):
                        # Use header style for section headers
                        story.append(Paragraph(self._escape_html(section), self.header_style))
                        story.append(Spacer(1, 0.1*inch))
                    else:
                        # Use body style for content
                        story.append(Paragraph(self._escape_html(section), self.body_style))
            
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
        sections = text.split('\n\n')
        
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
            'PROFESSIONAL SUMMARY', 'SUMMARY', 'OBJECTIVE',
            'EXPERIENCE', 'PROFESSIONAL EXPERIENCE', 'WORK EXPERIENCE',
            'EDUCATION', 'SKILLS', 'TECHNICAL SKILLS', 'CERTIFICATIONS',
            'PROJECTS', 'ACHIEVEMENTS', 'AWARDS', 'LANGUAGES',
            'VOLUNTEER', 'PUBLICATIONS', 'REFERENCES'
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