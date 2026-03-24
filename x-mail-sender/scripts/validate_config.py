#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
x-mail-sender: Configuration validation and testing utility
Validates SMTP settings and tests email connectivity
"""

import os
import sys
import json
import smtplib
import socket
from pathlib import Path
from datetime import datetime

try:
    from config_loader import (
        load_config, 
        detect_email_provider, 
        get_smtp_config,
        get_skill_dir,
        get_config_paths,
        get_config_template_path,
        PRESET_SMTP_SERVERS
    )
    CONFIG_LOADER_AVAILABLE = True
except ImportError:
    CONFIG_LOADER_AVAILABLE = False
    PRESET_SMTP_SERVERS = {
        '126': {'host': 'smtp.126.com', 'port': 465, 'ssl': True},
        '163': {'host': 'smtp.163.com', 'port': 465, 'ssl': True},
        'qq': {'host': 'smtp.qq.com', 'port': 465, 'ssl': True},
        'gmail': {'host': 'smtp.gmail.com', 'port': 465, 'ssl': True},
        'outlook': {'host': 'smtp.office365.com', 'port': 587, 'ssl': False, 'starttls': True},
        'hotmail': {'host': 'smtp-mail.outlook.com', 'port': 587, 'ssl': False, 'starttls': True},
    }


def validate_config():
    """Validate email configuration and return detailed status"""
    results = {
        'timestamp': datetime.now().isoformat(),
        'valid': True,
        'errors': [],
        'warnings': [],
        'config': {},
        'connection_test': None,
        'config_source': None,
    }
    
    if CONFIG_LOADER_AVAILABLE:
        config = load_config()
        results['config_source'] = config.get('config_source')
    else:
        config = _fallback_load_config()
    
    results['config'] = {
        'smtp_server': config.get('smtp_server'),
        'smtp_port': config.get('smtp_port', 465),
        'sender_email': config.get('sender_email'),
        'sender_name': config.get('sender_name', ''),
        'use_ssl': config.get('use_ssl', True),
        'use_starttls': config.get('use_starttls', False),
        'password_set': bool(config.get('sender_password'))
    }
    
    if not config.get('sender_email'):
        results['errors'].append({
            'field': 'SENDER_EMAIL',
            'message': 'Sender email address is not configured',
            'hint': 'Set SENDER_EMAIL in .env file'
        })
        results['valid'] = False
    
    if not config.get('sender_password'):
        results['errors'].append({
            'field': 'SENDER_PASSWORD',
            'message': 'SMTP password/authorization code is not configured',
            'hint': 'Set SENDER_PASSWORD in .env file (use authorization code, not login password)'
        })
        results['valid'] = False
    
    if not config.get('smtp_server'):
        provider = detect_email_provider(config.get('sender_email')) if CONFIG_LOADER_AVAILABLE else _fallback_detect_provider(config.get('sender_email'))
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
    
    if config.get('sender_email'):
        provider = detect_email_provider(config.get('sender_email')) if CONFIG_LOADER_AVAILABLE else _fallback_detect_provider(config.get('sender_email'))
        if provider:
            preset = PRESET_SMTP_SERVERS.get(provider, {})
            if preset and config.get('smtp_server') != preset.get('host'):
                results['warnings'].append({
                    'field': 'SMTP_SERVER',
                    'message': f'Email domain suggests {preset.get("host")}, but configured as {config.get("smtp_server")}',
                    'hint': 'Verify SMTP server matches your email provider'
                })
    
    if CONFIG_LOADER_AVAILABLE:
        config_paths = get_config_paths()
        config_exists = any(p.exists() for p in config_paths)
        if not config_exists:
            template_path = get_config_template_path()
            results['warnings'].append({
                'field': '.env',
                'message': 'No .env configuration file found',
                'hint': f'Copy {template_path.name} to .env and configure your settings'
            })
    else:
        skill_dir = _fallback_get_skill_dir()
        env_file = skill_dir / '.env'
        if not env_file.exists():
            results['warnings'].append({
                'field': '.env',
                'message': '.env file does not exist',
                'hint': 'Copy config/.env.example to .env and configure your settings'
            })
    
    return results


def test_connection():
    """Test SMTP connection with current configuration"""
    if CONFIG_LOADER_AVAILABLE:
        config = load_config()
    else:
        config = _fallback_load_config()
    
    result = {
        'success': False,
        'message': '',
        'details': {}
    }
    
    if not all([config.get('smtp_server'), config.get('sender_email'), config.get('sender_password')]):
        result['message'] = 'Configuration incomplete, cannot test connection'
        return result
    
    if CONFIG_LOADER_AVAILABLE:
        smtp_config = get_smtp_config(config['sender_email'], config)
    else:
        smtp_config = _fallback_get_smtp_config(config['sender_email'], config)
    
    result['details']['host'] = smtp_config['host']
    result['details']['port'] = smtp_config['port']
    result['details']['ssl'] = smtp_config['use_ssl']
    result['details']['starttls'] = smtp_config['use_starttls']
    
    try:
        if smtp_config['use_ssl']:
            server = smtplib.SMTP_SSL(smtp_config['host'], smtp_config['port'], timeout=10)
        else:
            server = smtplib.SMTP(smtp_config['host'], smtp_config['port'], timeout=10)
            if smtp_config['use_starttls']:
                server.starttls()
        
        server.ehlo()
        
        try:
            server.login(config['sender_email'], config['sender_password'])
            result['success'] = True
            result['message'] = 'SMTP connection and authentication successful'
        except smtplib.SMTPAuthenticationError as e:
            result['message'] = 'Authentication failed'
            result['details']['error'] = str(e)
            result['details']['hint'] = 'Check if you are using authorization code (not login password)'
        finally:
            server.quit()
            
    except socket.timeout:
        result['message'] = 'Connection timeout'
        result['details']['hint'] = 'Check network connection and SMTP server address'
    except socket.gaierror as e:
        result['message'] = 'DNS resolution failed'
        result['details']['error'] = str(e)
        result['details']['hint'] = 'Check SMTP server address'
    except smtplib.SMTPConnectError as e:
        result['message'] = 'SMTP connection failed'
        result['details']['error'] = str(e)
    except smtplib.SMTPAuthenticationError as e:
        result['message'] = 'Authentication failed'
        result['details']['error'] = str(e)
        result['details']['hint'] = 'Check if you are using authorization code (not login password)'
    except smtplib.SMTPException as e:
        result['message'] = f'SMTP error: {type(e).__name__}'
        result['details']['error'] = str(e)
    except (OSError, IOError) as e:
        result['message'] = 'I/O error during connection'
        result['details']['error'] = str(e)
    except Exception as e:
        result['message'] = f'Unexpected error: {type(e).__name__}'
        result['details']['error'] = str(e)
        result['details']['error_type'] = type(e).__name__
    
    return result


def _fallback_get_skill_dir():
    """Fallback skill directory detection"""
    script_path = Path(__file__).resolve()
    return script_path.parent.parent


def _fallback_load_config():
    """Fallback configuration loader"""
    config = {
        'smtp_server': None,
        'smtp_port': 465,
        'sender_email': None,
        'sender_password': None,
        'sender_name': None,
        'use_ssl': True,
        'use_starttls': False,
    }
    
    try:
        from dotenv import load_dotenv
        skill_dir = _fallback_get_skill_dir()
        env_file = skill_dir / '.env'
        if env_file.exists():
            load_dotenv(env_file)
    except ImportError:
        pass
    except Exception:
        pass
    
    config['smtp_server'] = os.getenv('SMTP_SERVER')
    try:
        config['smtp_port'] = int(os.getenv('SMTP_PORT', 465))
    except (ValueError, TypeError):
        config['smtp_port'] = 465
    config['sender_email'] = os.getenv('SENDER_EMAIL')
    config['sender_password'] = os.getenv('SENDER_PASSWORD')
    config['sender_name'] = os.getenv('SENDER_NAME', '')
    
    use_ssl = os.getenv('SMTP_USE_SSL', 'true').lower()
    config['use_ssl'] = use_ssl in ('true', '1', 'yes')
    
    use_starttls = os.getenv('SMTP_USE_STARTTLS', 'false').lower()
    config['use_starttls'] = use_starttls in ('true', '1', 'yes')
    
    return config


def _fallback_detect_provider(email):
    """Fallback email provider detection"""
    if not email:
        return None
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


def _fallback_get_smtp_config(email, config):
    """Fallback SMTP config"""
    provider = _fallback_detect_provider(email)
    
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


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Validate and test x-mail-sender configuration'
    )
    parser.add_argument('--test-connection', action='store_true',
                       help='Test SMTP connection (requires valid credentials)')
    parser.add_argument('--json', action='store_true',
                       help='Output in JSON format')
    
    args = parser.parse_args()
    
    results = validate_config()
    
    if args.test_connection and results['valid']:
        results['connection_test'] = test_connection()
    
    if args.json:
        try:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        except (TypeError, ValueError) as e:
            print(json.dumps({
                'valid': False,
                'error': f'Could not serialize results: {e}',
                'error_code': 'SERIALIZATION_ERROR'
            }, ensure_ascii=False, indent=2))
        except Exception as e:
            print(json.dumps({
                'valid': False,
                'error': f'Unexpected output error: {e}',
                'error_code': 'OUTPUT_ERROR'
            }, ensure_ascii=False, indent=2))
    else:
        print("=" * 60)
        print("x-mail-sender Configuration Validation")
        print("=" * 60)
        print(f"\nTimestamp: {results['timestamp']}")
        print(f"Status: {'VALID' if results['valid'] else 'INVALID'}")
        
        if results.get('config_source'):
            print(f"Config Source: {results['config_source']}")
        
        if results['config']:
            print("\nConfiguration:")
            for key, value in results['config'].items():
                if key == 'password_set':
                    print(f"  {key}: {'Yes' if value else 'No'}")
                else:
                    print(f"  {key}: {value}")
        
        if results['errors']:
            print("\nErrors:")
            for err in results['errors']:
                print(f"  [{err['field']}] {err['message']}")
                if 'hint' in err:
                    print(f"    Hint: {err['hint']}")
        
        if results['warnings']:
            print("\nWarnings:")
            for warn in results['warnings']:
                print(f"  [{warn['field']}] {warn['message']}")
                if 'hint' in warn:
                    print(f"    Hint: {warn['hint']}")
        
        if results.get('connection_test'):
            ct = results['connection_test']
            print(f"\nConnection Test: {'SUCCESS' if ct['success'] else 'FAILED'}")
            print(f"  Message: {ct['message']}")
            if ct.get('details'):
                for key, value in ct['details'].items():
                    if key not in ('error', 'hint'):
                        print(f"  {key}: {value}")
                if 'error' in ct['details']:
                    print(f"  Error: {ct['details']['error']}")
                if 'hint' in ct['details']:
                    print(f"  Hint: {ct['details']['hint']}")
        
        print("\n" + "=" * 60)
    
    sys.exit(0 if results['valid'] else 1)


if __name__ == '__main__':
    main()
