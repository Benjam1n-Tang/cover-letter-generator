import json
from pathlib import Path
from typing import Dict, Optional

class ProfileManager:
    """Manages user profile data"""
    
    def __init__(self, profiles_dir: Path):
        self.profiles_dir = Path(profiles_dir)
        self.profiles_dir.mkdir(exist_ok=True)
        self.profile_file = self.profiles_dir / "user_profile.json"
    
    def get_profile(self) -> Optional[Dict]:
        """Get the user profile"""
        if not self.profile_file.exists():
            return None
            
        try:
            with open(self.profile_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading profile: {e}")
            return None
    
    def save_profile(self, profile_data: Dict) -> bool:
        """Save user profile data"""
        try:
            # Validate required fields
            required_fields = ['first_name', 'last_name', 'email', 'phone', 'address']
            for field in required_fields:
                if not profile_data.get(field):
                    raise ValueError(f"Missing required field: {field}")
            
            with open(self.profile_file, 'w') as f:
                json.dump(profile_data, f, indent=2)
            return True
            
        except Exception as e:
            print(f"Error saving profile: {e}")
            return False
    
    def profile_exists(self) -> bool:
        """Check if a profile exists"""
        return self.profile_file.exists()
    
    def delete_profile(self) -> bool:
        """Delete the user profile"""
        try:
            if self.profile_file.exists():
                self.profile_file.unlink()
            return True
        except Exception as e:
            print(f"Error deleting profile: {e}")
            return False