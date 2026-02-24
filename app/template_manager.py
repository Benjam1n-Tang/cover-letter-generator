import json
import logging
from pathlib import Path
from typing import Optional, List, Dict
import re

logger = logging.getLogger(__name__)


class TemplateManager:
    """Manages cover letter templates with placeholder replacement"""

    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self.templates_dir.mkdir(exist_ok=True)
        self.template_file = self.templates_dir / "templates.json"

    def save_template(self, name: str, content: str) -> bool:
        """Save a new template or update existing one"""
        try:
            templates = self._load_templates()
            templates[name] = {
                "content": content,
                "created_at": "2026-02-23",  # You could use datetime here
                "placeholders": self._extract_placeholders(content),
            }

            with open(self.template_file, "w") as f:
                json.dump(templates, f, indent=2)

            logger.info(f"Template '{name}' saved successfully")
            return True

        except Exception as e:
            logger.error(f"Error saving template: {str(e)}")
            return False

    def get_template(self, name: str) -> Optional[Dict]:
        """Get a specific template by name"""
        try:
            templates = self._load_templates()
            return templates.get(name)
        except Exception as e:
            logger.error(f"Error getting template: {str(e)}")
            return None

    def list_templates(self) -> List[Dict]:
        """List all available templates"""
        try:
            templates = self._load_templates()
            return [
                {
                    "name": name,
                    "placeholders": template["placeholders"],
                    "preview": (
                        template["content"][:200] + "..."
                        if len(template["content"]) > 200
                        else template["content"]
                    ),
                }
                for name, template in templates.items()
            ]
        except Exception as e:
            logger.error(f"Error listing templates: {str(e)}")
            return []

    def delete_template(self, name: str) -> bool:
        """Delete a template"""
        try:
            templates = self._load_templates()
            if name in templates:
                del templates[name]
                with open(self.template_file, "w") as f:
                    json.dump(templates, f, indent=2)
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting template: {str(e)}")
            return False

    def generate_from_template(
        self, template_name: str, replacements: Dict[str, str]
    ) -> Optional[str]:
        """Generate cover letter content from template with replacements"""
        try:
            template = self.get_template(template_name)
            if not template:
                return None

            content = template["content"]

            # Replace placeholders with actual values
            for placeholder, value in replacements.items():
                # Handle different placeholder formats: [PLACEHOLDER] and {PLACEHOLDER}
                content = re.sub(
                    rf"\[{re.escape(placeholder)}\]",
                    value,
                    content,
                    flags=re.IGNORECASE,
                )
                content = re.sub(
                    rf"\{{{re.escape(placeholder)}\}}",
                    value,
                    content,
                    flags=re.IGNORECASE,
                )

            return content

        except Exception as e:
            logger.error(f"Error generating from template: {str(e)}")
            return None

    def _load_templates(self) -> Dict:
        """Load templates from file"""
        try:
            if self.template_file.exists():
                with open(self.template_file, "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading templates: {str(e)}")
            return {}

    def _extract_placeholders(self, content: str) -> List[str]:
        """Extract all placeholders from template content"""
        # Find placeholders in [PLACEHOLDER] and {PLACEHOLDER} format
        bracket_placeholders = re.findall(r"\[([^\]]+)\]", content)
        brace_placeholders = re.findall(r"\{([^}]+)\}", content)

        # Combine and deduplicate
        all_placeholders = list(set(bracket_placeholders + brace_placeholders))
        return sorted(all_placeholders)

    def get_smart_replacements(
        self, job_data: Dict, profile: Dict, resume_content: str = ""
    ) -> Dict[str, str]:
        """Generate smart replacements based on job data, profile, and resume"""
        replacements = {}

        # Basic job information
        replacements["Role Name"] = job_data.get("job_role", "")
        replacements["ROLE NAME"] = job_data.get("job_role", "")
        replacements["Company Name"] = job_data.get("company_name", "")
        replacements["COMPANY NAME"] = job_data.get("company_name", "")

        # Hiring manager handling
        hiring_manager = job_data.get("hiring_manager", "")
        if hiring_manager:
            last_name = (
                hiring_manager.split()[-1] if hiring_manager.split() else hiring_manager
            )
            replacements["MR/MS HR LAST NAME"] = f"Mr. {last_name}"
            replacements["HR LAST NAME"] = last_name
        else:
            replacements["MR/MS HR LAST NAME"] = "Hiring Manager"
            replacements["HR LAST NAME"] = "Hiring Manager"

        # Profile information
        replacements["Your Name"] = (
            f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip()
        )
        replacements["YOUR NAME"] = (
            f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip()
        )

        # Try to extract information from resume
        if resume_content:
            # Extract university (simple pattern matching)
            university_match = re.search(
                r"(University|College|Institute)[^,\n]*", resume_content, re.IGNORECASE
            )
            if university_match:
                replacements["University"] = university_match.group(0)
                replacements["UNIVERSITY"] = university_match.group(0)

            # Extract graduation year (4-digit year pattern)
            grad_year_match = re.search(r"\b(202[0-9])\b", resume_content)
            if grad_year_match:
                replacements["Graduation Year"] = grad_year_match.group(0)
                replacements["GRADUATION YEAR"] = grad_year_match.group(0)

        return replacements
