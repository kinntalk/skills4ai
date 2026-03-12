import os
import json
from typing import Optional, Dict, Any, List
from pathlib import Path


MSG = {
    "en": {
        "warn_load_failed": "[WARN] Failed to load config: {error}",
        "error_save_failed": "[ERROR] Failed to save config: {error}",
    },
    "zh": {
        "warn_load_failed": "[警告] 加载配置失败: {error}",
        "error_save_failed": "[错误] 保存配置失败: {error}",
    }
}


def _t(key: str, **kwargs) -> str:
    lang = os.environ.get("SKILL_LANG", "zh")
    template = MSG.get(lang, MSG["en"]).get(key, MSG["en"][key])
    return template.format(**kwargs)


class ConfigManager:
    def __init__(self):
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / "app_config.json"
        self._ensure_config_exists()

    def _get_config_dir(self) -> Path:
        skill_dir = Path(__file__).parent.parent
        config_dir = skill_dir / "templates"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    def _ensure_config_exists(self):
        if not self.config_file.exists():
            default_config = {
                "apps": {},
                "settings": {
                    "auto_verify": True,
                    "max_startup_wait": 5,
                    "search_drives": []
                }
            }
            self._save_config(default_config)

    def _load_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_file, "r", encoding="utf-8", errors="replace") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, PermissionError) as e:
            print(_t("warn_load_failed", error=str(e)))
            return {"apps": {}, "settings": {}}

    def _save_config(self, config: Dict[str, Any]) -> bool:
        try:
            with open(self.config_file, "w", encoding="utf-8", errors="replace") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except (PermissionError, OSError) as e:
            print(_t("error_save_failed", error=str(e)))
            return False

    def get_app_info(self, app_key: str) -> Optional[Dict[str, Any]]:
        config = self._load_config()
        app_key_lower = app_key.lower()
        return config.get("apps", {}).get(app_key_lower)

    def save_app_info(self, app_name: str, exe_path: str, process_name: Optional[str] = None, description: str = "") -> bool:
        config = self._load_config()

        if process_name is None:
            process_name = Path(exe_path).stem

        app_key = app_name.lower().replace(" ", "_")

        if "apps" not in config:
            config["apps"] = {}

        config["apps"][app_key] = {
            "name": app_name,
            "path": exe_path,
            "process_name": process_name,
            "description": description
        }

        return self._save_config(config)

    def delete_app_info(self, app_name: str) -> bool:
        config = self._load_config()
        app_key = app_name.lower().replace(" ", "_")

        if app_key in config.get("apps", {}):
            del config["apps"][app_key]
            return self._save_config(config)
        return False

    def list_apps(self) -> List[Dict[str, Any]]:
        config = self._load_config()
        apps = config.get("apps", {})
        return list(apps.values())

    def update_settings(self, settings: Dict[str, Any]) -> bool:
        config = self._load_config()
        config["settings"] = settings
        return self._save_config(config)

    def get_settings(self) -> Dict[str, Any]:
        config = self._load_config()
        return config.get("settings", {})

    def find_app_by_keyword(self, keyword: str) -> Optional[Dict[str, Any]]:
        config = self._load_config()
        keyword_lower = keyword.lower()

        apps = config.get("apps", {})
        for key, app in apps.items():
            if keyword_lower in key or keyword_lower in app.get("name", "").lower():
                return app

        return None


def get_config_manager() -> ConfigManager:
    return ConfigManager()
