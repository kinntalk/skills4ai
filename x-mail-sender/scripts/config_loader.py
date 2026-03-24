#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
x-mail-sender: Configuration loader
Handles loading configuration from multiple sources with proper error handling
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


PRESET_SMTP_SERVERS = {
    '126': {'host': 'smtp.126.com', 'port': 465, 'ssl': True},
    '163': {'host': 'smtp.163.com', 'port': 465, 'ssl': True},
    'qq': {'host': 'smtp.qq.com', 'port': 465, 'ssl': True},
    'gmail': {'host': 'smtp.gmail.com', 'port': 465, 'ssl': True},
    'outlook': {'host': 'smtp.office365.com', 'port': 587, 'ssl': False, 'starttls': True},
    'hotmail': {'host': 'smtp-mail.outlook.com', 'port': 587, 'ssl': False, 'starttls': True},
}


def get_skill_dir() -> Path:
    script_path = Path(__file__).resolve()
    return script_path.parent.parent


def get_config_paths() -> list:
    """
    Get configuration file paths in priority order.
    
    Priority:
    1. Skill directory root: .env (user config, gitignored)
    2. Config directory: config/.env (alternative location)
    
    Returns:
        List of Path objects in priority order
    """
    skill_dir = get_skill_dir()
    return [
        skill_dir / '.env',
        skill_dir / 'config' / '.env',
    ]


def get_config_template_path() -> Path:
    """Get the path to the configuration template file."""
    skill_dir = get_skill_dir()
    template_path = skill_dir / 'config' / '.env.example'
    if template_path.exists():
        return template_path
    legacy_path = skill_dir / '.env.example'
    if legacy_path.exists():
        return legacy_path
    return template_path


def load_config() -> Dict[str, Any]:
    """
    Load configuration from multiple sources.
    
    Configuration sources (in order of priority):
    1. Environment variables (highest priority)
    2. .env file in skill directory root
    3. .env file in config directory
    4. Default values (lowest priority)
    
    Returns:
        Dictionary containing configuration values
    """
    config = {
        'smtp_server': None,
        'smtp_port': 465,
        'sender_email': None,
        'sender_password': None,
        'sender_name': '',
        'use_ssl': True,
        'use_starttls': False,
        'config_source': None,
    }
    
    config_paths = get_config_paths()
    
    for env_path in config_paths:
        if env_path.exists():
            if DOTENV_AVAILABLE:
                try:
                    load_dotenv(env_path, override=True)
                    config['config_source'] = str(env_path)
                    break
                except (IOError, OSError, PermissionError) as e:
                    print(f"Warning: Could not load config from {env_path}: {e}", file=sys.stderr)
                except Exception as e:
                    print(f"Warning: Unexpected error loading config from {env_path}: {e}", file=sys.stderr)
    
    try:
        config['smtp_server'] = os.getenv('SMTP_SERVER')
        port_str = os.getenv('SMTP_PORT', '465')
        config['smtp_port'] = int(port_str) if port_str.isdigit() else 465
    except (ValueError, TypeError) as e:
        print(f"Warning: Invalid SMTP_PORT value: {e}", file=sys.stderr)
        config['smtp_port'] = 465
    except Exception as e:
        print(f"Warning: Unexpected error parsing SMTP_PORT: {e}", file=sys.stderr)
        config['smtp_port'] = 465
    
    config['sender_email'] = os.getenv('SENDER_EMAIL')
    config['sender_password'] = os.getenv('SENDER_PASSWORD')
    config['sender_name'] = os.getenv('SENDER_NAME', '')
    
    try:
        use_ssl = os.getenv('SMTP_USE_SSL', 'true').lower()
        config['use_ssl'] = use_ssl in ('true', '1', 'yes', 'on')
    except Exception as e:
        print(f"Warning: Error parsing SMTP_USE_SSL: {e}", file=sys.stderr)
        config['use_ssl'] = True
    
    try:
        use_starttls = os.getenv('SMTP_USE_STARTTLS', 'false').lower()
        config['use_starttls'] = use_starttls in ('true', '1', 'yes', 'on')
    except Exception as e:
        print(f"Warning: Error parsing SMTP_USE_STARTTLS: {e}", file=sys.stderr)
        config['use_starttls'] = False
    
    if config['smtp_server']:
        for preset_name, preset_config in PRESET_SMTP_SERVERS.items():
            if preset_config['host'] == config['smtp_server']:
                config['use_ssl'] = preset_config.get('ssl', True)
                config['use_starttls'] = preset_config.get('starttls', False)
                break
    
    return config


def detect_email_provider(email: Optional[str]) -> Optional[str]:
    """
    Detect email provider from email address domain.
    
    Args:
        email: Email address to analyze
        
    Returns:
        Provider name or None if unknown
    """
    if not email or '@' not in email:
        return None
    
    try:
        domain = email.split('@')[-1].lower()
        provider_map = {
            '126.com': '126',
            '163.com': '163',
            'qq.com': 'qq',
            'gmail.com': 'gmail',
            'outlook.com': 'outlook',
            'hotmail.com': 'outlook',
            'live.com': 'outlook',
        }
        return provider_map.get(domain)
    except (IndexError, AttributeError) as e:
        print(f"Warning: Could not parse email domain: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Warning: Unexpected error detecting email provider: {e}", file=sys.stderr)
        return None


def get_smtp_config(email: Optional[str], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get SMTP configuration for an email address.
    
    If the email provider is known, use preset configuration.
    Otherwise, use configuration from config dict.
    
    Args:
        email: Sender email address
        config: Configuration dictionary
        
    Returns:
        SMTP configuration dictionary
    """
    provider = detect_email_provider(email)
    
    if provider and provider in PRESET_SMTP_SERVERS:
        preset = PRESET_SMTP_SERVERS[provider]
        return {
            'host': preset['host'],
            'port': preset['port'],
            'use_ssl': preset.get('ssl', True),
            'use_starttls': preset.get('starttls', False),
        }
    
    return {
        'host': config.get('smtp_server'),
        'port': config.get('smtp_port', 465),
        'use_ssl': config.get('use_ssl', True),
        'use_starttls': config.get('use_starttls', False),
    }


def validate_config() -> Dict[str, Any]:
    """
    Validate the current configuration.
    
    Returns:
        Dictionary with validation results
    """
    from datetime import datetime
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'valid': True,
        'errors': [],
        'warnings': [],
        'config': {},
        'config_source': None,
    }
    
    config = load_config()
    results['config_source'] = config.get('config_source')
    
    results['config'] = {
        'smtp_server': config['smtp_server'],
        'smtp_port': config['smtp_port'],
        'sender_email': config['sender_email'],
        'sender_name': config['sender_name'],
        'use_ssl': config['use_ssl'],
        'use_starttls': config['use_starttls'],
        'password_set': bool(config['sender_password']),
    }
    
    if not config['sender_email']:
        results['errors'].append({
            'field': 'SENDER_EMAIL',
            'message': 'Sender email address is not configured',
            'hint': 'Set SENDER_EMAIL in .env file'
        })
        results['valid'] = False
    
    if not config['sender_password']:
        results['errors'].append({
            'field': 'SENDER_PASSWORD',
            'message': 'SMTP password/authorization code is not configured',
            'hint': 'Set SENDER_PASSWORD in .env file (use authorization code, not login password)'
        })
        results['valid'] = False
    
    if not config['smtp_server']:
        provider = detect_email_provider(config['sender_email'])
        if provider and provider in PRESET_SMTP_SERVERS:
            preset = PRESET_SMTP_SERVERS[provider]
            results['warnings'].append({
                'field': 'SMTP_SERVER',
                'message': f'SMTP server not set, but can auto-detect: {preset["host"]}',
                'hint': f'Consider setting SMTP_SERVER={preset["host"]} explicitly'
            })
        else:
            results['errors'].append({
                'field': 'SMTP_SERVER',
                'message': 'SMTP server is not configured',
                'hint': 'Set SMTP_SERVER in .env file (e.g., smtp.126.com)'
            })
            results['valid'] = False
    
    config_paths = get_config_paths()
    config_exists = any(p.exists() for p in config_paths)
    if not config_exists:
        template_path = get_config_template_path()
        results['warnings'].append({
            'field': '.env',
            'message': 'No .env configuration file found',
            'hint': f'Copy {template_path.name} to .env and configure your settings'
        })
    
    return results


def get_setup_instructions() -> str:
    """
    Get setup instructions for the user.
    
    Returns:
        Setup instructions string
    """
    template_path = get_config_template_path()
    skill_dir = get_skill_dir()
    
    return f"""
x-mail-sender Configuration Setup
=================================

1. Copy the template file:
   cp "{template_path}" "{skill_dir / '.env'}"

2. Edit the .env file with your email settings:
   - SMTP_SERVER: Your SMTP server (e.g., smtp.126.com)
   - SMTP_PORT: Port number (usually 465 for SSL)
   - SENDER_EMAIL: Your email address
   - SENDER_PASSWORD: Your authorization code (NOT login password)

3. Getting authorization codes:
   - 126/163: Settings -> POP3/SMTP/IMAP -> Enable SMTP -> Get authorization code
   - QQ Mail: Settings -> Account -> Enable SMTP -> Get authorization code
   - Gmail: Google Account -> Security -> 2-Step Verification -> App passwords
   - Outlook: Microsoft Account -> Security -> App passwords

Configuration file location: {skill_dir / '.env'}
Template file location: {template_path}
""".strip()
