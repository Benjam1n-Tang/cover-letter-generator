import os
from pathlib import Path
from typing import Optional
import PyPDF2
import docx
import logging

logger = logging.getLogger(__name__)

class ResumeParser:
    """Handles resume file parsing and content extraction"""
    
    def __init__(self):
        self.resume_dir = Path("data/resume")
        self.resume_dir.mkdir(exist_ok=True)
        self.supported_formats = ['.pdf', '.txt', '.docx']
    
    def parse_resume(self, file_path: str) -> str:
        """Parse resume content from file"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"Resume file not found: {file_path}")
            
            file_extension = file_path.suffix.lower()
            
            if file_extension == '.pdf':
                return self._parse_pdf(file_path)
            elif file_extension == '.txt':
                return self._parse_txt(file_path)
            elif file_extension == '.docx':
                return self._parse_docx(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
                
        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            return f"Error parsing resume: {str(e)}"
    
    def _parse_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error parsing PDF: {str(e)}")
    
    def _parse_txt(self, file_path: Path) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            raise Exception(f"Error parsing TXT: {str(e)}")
    
    def _parse_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error parsing DOCX: {str(e)}")
    
    def get_latest_resume_content(self) -> Optional[str]:
        """Get content from the most recently uploaded resume"""
        try:
            resume_files = []
            for ext in self.supported_formats:
                resume_files.extend(list(self.resume_dir.glob(f"*{ext}")))
            
            if not resume_files:
                return None
            
            # Get the most recent file by modification time
            latest_file = max(resume_files, key=lambda f: f.stat().st_mtime)
            return self.parse_resume(str(latest_file))
            
        except Exception as e:
            logger.error(f"Error getting latest resume: {str(e)}")
            return None
    
    def list_resumes(self) -> list:
        """List all available resume files"""
        resumes = []
        for ext in self.supported_formats:
            for file_path in self.resume_dir.glob(f"*{ext}"):
                resumes.append({
                    'filename': file_path.name,
                    'path': str(file_path),
                    'size': file_path.stat().st_size,
                    'modified': file_path.stat().st_mtime
                })
        
        # Sort by modification time, newest first
        resumes.sort(key=lambda x: x['modified'], reverse=True)
        return resumes
    
    def delete_resume(self, filename: str) -> bool:
        """Delete a resume file"""
        try:
            file_path = self.resume_dir / filename
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting resume: {str(e)}")
            return False