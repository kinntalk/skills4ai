"""
Configuration management module for url-to-obsidian skill.

Handles:
- Configuration file reading/writing
- Credential encryption/decryption
- Default configuration management
"""

import json
import os
import base64
from pathlib import Path
from typing import Any, Optional
from datetime import datetime

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

try:
    from .vault_detector import detect_vault_path, get_vault_attachment_folder
except ImportError:
    from vault_detector import detect_vault_path, get_vault_attachment_folder


DEFAULT_CONFIG = {
    "vault_path": None,
    "auto_detect_vault": True,
    "output": {
        "subfolder": "web-clippings",
        "filename_template": "{title}-{date}",
        "add_frontmatter": True,
        "default_tags": ["web-clipping"]
    },
    "assets": {
        "folder": None,
        "download": True,
        "wikilink": False,
        "naming": "{title}-{timestamp}-{index}"
    },
    "credentials": {},
    "browser": {
        "profile": None,
        "timeout": 30000
    }
}


class ConfigManager:
    """Manages configuration for url-to-obsidian skill."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize configuration manager.
        
        Args:
            config_dir: Directory to store configuration files.
                       Defaults to ~/.web2obs/
        """
        if config_dir is None:
            config_dir = Path.home() / ".web2obs"
        
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "config.json"
        self.key_file = self.config_dir / "key.bin"
        self._fernet: Optional[Fernet] = None
        self._config: Optional[dict] = None
        
    def _ensure_config_dir(self) -> None:
        """Ensure configuration directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key.
        
        Returns:
            Encryption key bytes
        """
        self._ensure_config_dir()
        
        if self.key_file.exists():
            return self.key_file.read_bytes()
        
        key = Fernet.generate_key()
        self.key_file.write_bytes(key)
        self.key_file.chmod(0o600)
        return key
    
    def _get_fernet(self) -> Fernet:
        """Get Fernet instance for encryption/decryption.
        
        Returns:
            Fernet instance
        """
        if self._fernet is None:
            key = self._get_or_create_key()
            self._fernet = Fernet(key)
        return self._fernet
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string.
        
        Args:
            plaintext: String to encrypt
            
        Returns:
            Encrypted string with 'encrypted:' prefix
        """
        fernet = self._get_fernet()
        encrypted = fernet.encrypt(plaintext.encode('utf-8'))
        return f"encrypted:{base64.b64encode(encrypted).decode('utf-8')}"
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a string.
        
        Args:
            ciphertext: Encrypted string with 'encrypted:' prefix
            
        Returns:
            Decrypted string
        """
        if not ciphertext.startswith("encrypted:"):
            return ciphertext
        
        fernet = self._get_fernet()
        encrypted = base64.b64decode(ciphertext[10:])
        return fernet.decrypt(encrypted).decode('utf-8')
    
    def load(self) -> dict:
        """Load configuration from file.
        
        Returns:
            Configuration dictionary
        """
        if self._config is not None:
            return self._config
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._config = DEFAULT_CONFIG.copy()
        else:
            self._config = DEFAULT_CONFIG.copy()
        
        return self._config
    
    def save(self, config: Optional[dict] = None) -> None:
        """Save configuration to file.
        
        Args:
            config: Configuration dictionary to save.
                   Defaults to current configuration.
        """
        self._ensure_config_dir()
        
        if config is not None:
            self._config = config
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        config = self.load()
        
        keys = key.split('.')
        value = config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        config = self.load()
        
        keys = key.split('.')
        current = config
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
        self.save(config)
    
    def get_vault_path(self) -> Optional[Path]:
        """Get Obsidian vault path.
        
        Returns:
            Path to Obsidian vault or None if not set
        """
        vault_path = self.get('vault_path')
        if vault_path:
            return Path(vault_path)
        return None
    
    def set_vault_path(self, path: str | Path) -> None:
        """Set Obsidian vault path.
        
        Args:
            path: Path to Obsidian vault
        """
        self.set('vault_path', str(path))
    
    def get_credentials(self, domain: str) -> Optional[dict]:
        """Get credentials for a domain.
        
        Args:
            domain: Domain name
            
        Returns:
            Dictionary with username and password, or None
        """
        credentials = self.get(f'credentials.{domain}')
        if not credentials:
            return None
        
        return {
            'username': self.decrypt(credentials.get('username', '')),
            'password': self.decrypt(credentials.get('password', ''))
        }
    
    def set_credentials(self, domain: str, username: str, password: str) -> None:
        """Set credentials for a domain.
        
        Args:
            domain: Domain name
            username: Username
            password: Password
        """
        config = self.load()
        
        if 'credentials' not in config:
            config['credentials'] = {}
        
        config['credentials'][domain] = {
            'username': self.encrypt(username),
            'password': self.encrypt(password)
        }
        
        self.save(config)
    
    def remove_credentials(self, domain: str) -> bool:
        """Remove credentials for a domain.
        
        Args:
            domain: Domain name
            
        Returns:
            True if credentials were removed, False if not found
        """
        config = self.load()
        
        if 'credentials' in config and domain in config['credentials']:
            del config['credentials'][domain]
            self.save(config)
            return True
        
        return False
    
    def list_credentials(self) -> list:
        """List all domains with stored credentials.
        
        Returns:
            List of domain names
        """
        credentials = self.get('credentials', {})
        return list(credentials.keys())
    
    def get_output_config(self) -> dict:
        """Get output configuration.
        
        Returns:
            Output configuration dictionary
        """
        return self.get('output', DEFAULT_CONFIG['output'])
    
    def get_browser_config(self) -> dict:
        """Get browser configuration.
        
        Returns:
            Browser configuration dictionary
        """
        return self.get('browser', DEFAULT_CONFIG['browser'])
    
    def get_vault_path_with_auto_detect(self) -> Optional[Path]:
        """Get Obsidian vault path with auto-detection support.
        
        If vault_path is manually configured, returns it directly.
        If auto_detect_vault is True, attempts to auto-detect the vault.
        
        Returns:
            Path to Obsidian vault or None if not found
        """
        vault_path = self.get('vault_path')
        if vault_path:
            return Path(vault_path)
        
        if self.get('auto_detect_vault', True):
            detected_path = detect_vault_path()
            if detected_path:
                return Path(detected_path)
        
        return None
    
    def get_assets_config(self) -> dict:
        """Get assets configuration.
        
        Returns:
            Assets configuration dictionary with keys:
            - folder: Path to assets folder (None means use vault config)
            - download: Whether to download assets
            - wikilink: Whether to use wikilink format
            - naming: Naming template for assets
        """
        return self.get('assets', DEFAULT_CONFIG['assets'])


def get_config_manager() -> ConfigManager:
    """Get a ConfigManager instance.
    
    Returns:
        ConfigManager instance
    """
    return ConfigManager()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Configuration management")
    parser.add_argument('command', choices=['list', 'get', 'set', 'add-credentials', 'remove-credentials', 'set-vault'])
    parser.add_argument('args', nargs='*', help="Command arguments")
    
    args = parser.parse_args()
    manager = ConfigManager()
    
    if args.command == 'list':
        config = manager.load()
        print(json.dumps(config, indent=2, ensure_ascii=False))
    
    elif args.command == 'get':
        if len(args.args) < 1:
            print("Usage: config_manager.py get <key>")
            exit(1)
        value = manager.get(args.args[0])
        print(json.dumps(value, indent=2, ensure_ascii=False) if isinstance(value, (dict, list)) else value)
    
    elif args.command == 'set':
        if len(args.args) < 2:
            print("Usage: config_manager.py set <key> <value>")
            exit(1)
        manager.set(args.args[0], args.args[1])
        print(f"Set {args.args[0]} = {args.args[1]}")
    
    elif args.command == 'add-credentials':
        if len(args.args) < 1:
            print("Usage: config_manager.py add-credentials <domain>")
            exit(1)
        domain = args.args[0]
        username = input("Username: ")
        password = input("Password: ")
        manager.set_credentials(domain, username, password)
        print(f"Credentials stored for {domain}")
    
    elif args.command == 'remove-credentials':
        if len(args.args) < 1:
            print("Usage: config_manager.py remove-credentials <domain>")
            exit(1)
        if manager.remove_credentials(args.args[0]):
            print(f"Credentials removed for {args.args[0]}")
        else:
            print(f"No credentials found for {args.args[0]}")
    
    elif args.command == 'set-vault':
        if len(args.args) < 1:
            print("Usage: config_manager.py set-vault <path>")
            exit(1)
        manager.set_vault_path(args.args[0])
        print(f"Vault path set to: {args.args[0]}")
