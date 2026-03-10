"""
XHS Search Configuration Manager
Manages configuration for Xiaohongshu search to Obsidian skill.
"""

import json
import os
from pathlib import Path
from typing import Any, Optional


class ConfigManager:
    """Configuration manager for xhs-search skill."""
    
    DEFAULT_CONFIG = {
        "vault_path": None,
        "auto_detect_vault": True,
        "output": {
            "subfolder": "xiaohongshu",
            "filename_template": "{type}-{keyword}-{date}",
            "add_frontmatter": True,
            "default_tags": ["xhs-search"]
        },
        "assets": {
            "folder": None,
            "download": True,
            "wikilink": True
        },
        "browser": {
            "session_name": "xhs-search",
            "timeout": 30000,
            "headed": False
        },
        "search": {
            "default_limit": 20,
            "request_delay": 2.0
        }
    }
    
    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            config_dir = Path.home() / ".xhs-search"
        self.config_dir = config_dir
        self.config_file = config_dir / "config.json"
        self._config = None
    
    @property
    def config(self) -> dict:
        if self._config is None:
            self._config = self._load_config()
        return self._config
    
    def _load_config(self) -> dict:
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                merged = self._merge_config(self.DEFAULT_CONFIG.copy(), user_config)
                return merged
            except Exception:
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()
    
    def _merge_config(self, base: dict, override: dict) -> dict:
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any) -> None:
        keys = key.split(".")
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_config()
    
    def get_vault_path(self) -> Optional[Path]:
        vault_path = self.get("vault_path")
        if vault_path:
            return Path(vault_path)
        
        if self.get("auto_detect_vault"):
            return self._detect_vault()
        return None
    
    def set_vault_path(self, path: str) -> None:
        self.set("vault_path", str(path))
    
    def _detect_vault(self) -> Optional[Path]:
        obsidian_config_paths = [
            Path(os.environ.get("APPDATA", "")) / "obsidian" / "obsidian.json",
            Path.home() / "Library" / "Application Support" / "obsidian" / "obsidian.json",
            Path.home() / ".config" / "obsidian" / "obsidian.json",
        ]
        
        for config_path in obsidian_config_paths:
            if config_path.exists():
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        config = json.load(f)
                    vaults = config.get("vaults", {})
                    if vaults:
                        latest_vault = max(vaults.items(), key=lambda x: x[1].get("open", 0))
                        return Path(latest_vault[1].get("path", ""))
                except Exception:
                    continue
        return None
    
    def get_asset_folder(self) -> Path:
        vault = self.get_vault_path()
        if not vault:
            raise ValueError("Obsidian vault not found. Run 'config set-vault <path>' first.")
        
        asset_folder = self.get("assets.folder")
        if asset_folder:
            return vault / asset_folder
        
        app_json = vault / ".obsidian" / "app.json"
        if app_json.exists():
            try:
                with open(app_json, "r", encoding="utf-8") as f:
                    app_config = json.load(f)
                attachment_folder = app_config.get("attachmentFolderPath", "assets")
                return vault / attachment_folder
            except Exception:
                pass
        
        return vault / "assets"
    
    def list_config(self) -> str:
        return json.dumps(self.config, indent=2, ensure_ascii=False)
