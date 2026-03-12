import json
from pathlib import Path
from typing import Dict, Any, Optional

MSG = {
    "en": {
        "profile_load_error": "Failed to load profile file: {error}",
        "profile_save_error": "Failed to save profile file: {error}",
        "profile_not_found": "Profile file not found, using default configuration"
    },
    "zh": {
        "profile_load_error": "[FAIL] Failed to load profile file: {error}",
        "profile_save_error": "[FAIL] Failed to save profile file: {error}",
        "profile_not_found": "[INFO] Profile file not found, using default configuration"
    }
}


class AppProfileManager:
    
    def __init__(self, profile_path: str = None, lang: str = "en"):
        if profile_path is None:
            profile_path = Path(__file__).parent / "app_profiles.json"
        
        self.profile_path = Path(profile_path)
        self.lang = lang
        self.profiles = self._load_profiles()
    
    def _msg(self, key: str, **kwargs) -> str:
        template = MSG.get(self.lang, MSG["en"]).get(key, key)
        return template.format(**kwargs)
    
    def _load_profiles(self) -> Dict[str, Any]:
        if self.profile_path.exists():
            try:
                with open(self.profile_path, 'r', encoding='utf-8', errors='replace') as f:
                    return json.load(f)
            except FileNotFoundError:
                print(self._msg("profile_not_found"), flush=True)
            except json.JSONDecodeError as e:
                print(self._msg("profile_load_error", error=str(e)), flush=True)
            except PermissionError as e:
                print(self._msg("profile_load_error", error=str(e)), flush=True)
            except OSError as e:
                print(self._msg("profile_load_error", error=str(e)), flush=True)
        return {"apps": {}, "default": {}}
    
    def find_app_profile(self, identifier: str) -> Optional[Dict[str, Any]]:
        identifier_lower = identifier.lower()
        
        for app_id, profile in self.profiles.get("apps", {}).items():
            aliases = profile.get("aliases", [])
            if identifier_lower in [a.lower() for a in aliases]:
                return profile
            
            window_patterns = profile.get("window_patterns", [])
            for pattern in window_patterns:
                if pattern.lower() in identifier_lower:
                    return profile
        
        return None
    
    def get_app_config(self, app_id: str, key: str = None, default: Any = None) -> Any:
        app_profile = self.profiles.get("apps", {}).get(app_id)
        
        if app_profile is None:
            return self.profiles.get("default", {}).get(key, default)
        
        if key is None:
            return app_profile
        
        value = app_profile.get(key)
        if value is None:
            return self.profiles.get("default", {}).get(key, default)
        
        return value
    
    def list_apps(self) -> Dict[str, str]:
        apps = {}
        for app_id, profile in self.profiles.get("apps", {}).items():
            apps[app_id] = profile.get("name", app_id)
        return apps
    
    def add_app_profile(self, app_id: str, profile: Dict[str, Any]) -> bool:
        if "apps" not in self.profiles:
            self.profiles["apps"] = {}
        
        self.profiles["apps"][app_id] = profile
        return self._save_profiles()
    
    def _save_profiles(self) -> bool:
        try:
            with open(self.profile_path, 'w', encoding='utf-8', errors='replace') as f:
                json.dump(self.profiles, f, indent=2, ensure_ascii=False)
            return True
        except FileNotFoundError as e:
            print(self._msg("profile_save_error", error=str(e)), flush=True)
        except PermissionError as e:
            print(self._msg("profile_save_error", error=str(e)), flush=True)
        except (TypeError, ValueError) as e:
            print(self._msg("profile_save_error", error=str(e)), flush=True)
        except OSError as e:
            print(self._msg("profile_save_error", error=str(e)), flush=True)
        return False
