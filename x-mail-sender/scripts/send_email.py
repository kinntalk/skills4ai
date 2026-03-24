#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
x-mail-sender: Local email sender with attachment support
Supports: 126, 163, QQ, Gmail, Outlook and custom SMTP servers
Features: Attachment support, HTML emails, CC/BCC, history tracking
"""

import os
import sys
import json
import smtplib
import argparse
import mimetypes
import socket
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr, formatdate
from pathlib import Path

try:
    from config_loader import load_config, get_smtp_config, get_skill_dir, get_setup_instructions
    CONFIG_LOADER_AVAILABLE = True
except ImportError:
    CONFIG_LOADER_AVAILABLE = False

try:
    from email_history import add_email_record
    HISTORY_AVAILABLE = True
except ImportError:
    HISTORY_AVAILABLE = False


def create_message(to_emails, subject, body, from_email, from_name=None, 
                   cc=None, bcc=None, is_html=False, attachments=None):
    msg = MIMEMultipart()
    
    if from_name:
        msg['From'] = formataddr((from_name, from_email))
    else:
        msg['From'] = from_email
    
    if isinstance(to_emails, str):
        to_emails = [e.strip() for e in to_emails.split(',')]
    msg['To'] = ', '.join(to_emails)
    
    if cc:
        if isinstance(cc, str):
            cc = [e.strip() for e in cc.split(',')]
        msg['Cc'] = ', '.join(cc)
    
    if bcc:
        if isinstance(bcc, str):
            bcc = [e.strip() for e in bcc.split(',')]
    
    msg['Subject'] = subject
    msg['Date'] = formatdate(localtime=True)
    
    content_type = 'html' if is_html else 'plain'
    msg.attach(MIMEText(body, content_type, 'utf-8'))
    
    if attachments:
        if isinstance(attachments, str):
            attachments = [a.strip() for a in attachments.split(',')]
        
        for file_path in attachments:
            file_path = file_path.strip('"\'')
            if not os.path.exists(file_path):
                continue
            
            ctype, encoding = mimetypes.guess_type(file_path)
            if ctype is None or encoding is not None:
                ctype = 'application/octet-stream'
            
            maintype, subtype = ctype.split('/', 1)
            
            try:
                with open(file_path, 'rb') as f:
                    part = MIMEBase(maintype, subtype)
                    part.set_payload(f.read())
            except (IOError, OSError, PermissionError, FileNotFoundError) as e:
                print(f"Warning: Could not read attachment {file_path}: {e}", file=sys.stderr)
                continue
            except Exception as e:
                print(f"Warning: Unexpected error reading attachment {file_path}: {e}", file=sys.stderr)
                continue
            
            encoders.encode_base64(part)
            
            filename = os.path.basename(file_path)
            try:
                from email.header import Header
                encoded_filename = Header(filename, 'utf-8').encode()
                part.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=encoded_filename
                )
            except (UnicodeEncodeError, ValueError) as e:
                print(f"Warning: Could not encode filename {filename}: {e}", file=sys.stderr)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{filename}"'
                )
            except Exception as e:
                print(f"Warning: Unexpected error encoding filename {filename}: {e}", file=sys.stderr)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{filename}"'
                )
            
            msg.attach(part)
    
    return msg, to_emails, cc or [], bcc or []


def validate_email_address(email):
    """Basic email address validation"""
    if not email or '@' not in email:
        return False
    parts = email.split('@')
    if len(parts) != 2:
        return False
    local, domain = parts
    if not local or not domain or '.' not in domain:
        return False
    return True


def get_attachment_names(attachments):
    """Extract attachment filenames from paths"""
    if not attachments:
        return []
    if isinstance(attachments, str):
        attachments = [a.strip() for a in attachments.split(',')]
    return [os.path.basename(a.strip('"\'')) for a in attachments if os.path.exists(a.strip('"\''))]


def send_email(to, subject, body, attachments=None, is_html=False, cc=None, bcc=None):
    if CONFIG_LOADER_AVAILABLE:
        config = load_config()
    else:
        config = _fallback_load_config()
    
    if not config.get('sender_email') or not config.get('sender_password'):
        result = {
            'success': False,
            'error': 'Missing email configuration',
            'error_code': 'CONFIG_MISSING',
            'hint': 'Please configure SENDER_EMAIL and SENDER_PASSWORD in .env file',
            'setup_instructions': get_setup_instructions() if CONFIG_LOADER_AVAILABLE else 'See config/.env.example'
        }
        _record_history(to, subject, False, result['error'], attachments, cc, bcc, None)
        return result
    
    if CONFIG_LOADER_AVAILABLE:
        smtp_config = get_smtp_config(config['sender_email'], config)
    else:
        smtp_config = _fallback_get_smtp_config(config['sender_email'], config)
    
    if not smtp_config.get('host'):
        result = {
            'success': False,
            'error': 'SMTP server not configured',
            'error_code': 'SMTP_SERVER_MISSING',
            'hint': 'Please configure SMTP_SERVER in .env file or use a supported email provider'
        }
        _record_history(to, subject, False, result['error'], attachments, cc, bcc, None)
        return result
    
    to_emails = [e.strip() for e in to.split(',')] if isinstance(to, str) else to
    invalid_emails = [e for e in to_emails if not validate_email_address(e)]
    if invalid_emails:
        result = {
            'success': False,
            'error': f'Invalid email address(es): {", ".join(invalid_emails)}',
            'error_code': 'INVALID_EMAIL',
            'hint': 'Please verify all recipient email addresses are valid'
        }
        _record_history(to, subject, False, result['error'], attachments, cc, bcc, smtp_config['host'])
        return result
    
    missing_attachments = []
    if attachments:
        att_list = [a.strip().strip('"\'') for a in attachments.split(',')] if isinstance(attachments, str) else attachments
        for att in att_list:
            if not os.path.exists(att):
                missing_attachments.append(att)
    
    if missing_attachments:
        result = {
            'success': False,
            'error': f'Attachment file(s) not found: {", ".join(missing_attachments)}',
            'error_code': 'ATTACHMENT_NOT_FOUND',
            'hint': 'Please verify all attachment file paths are correct'
        }
        _record_history(to, subject, False, result['error'], attachments, cc, bcc, smtp_config['host'])
        return result
    
    try:
        msg, to_list, cc_list, bcc_list = create_message(
            to_emails=to,
            subject=subject,
            body=body,
            from_email=config['sender_email'],
            from_name=config.get('sender_name'),
            cc=cc,
            bcc=bcc,
            is_html=is_html,
            attachments=attachments
        )
        
        recipients = to_list + cc_list + bcc_list
        
        if smtp_config['use_ssl']:
            server = smtplib.SMTP_SSL(smtp_config['host'], smtp_config['port'], timeout=30)
        else:
            server = smtplib.SMTP(smtp_config['host'], smtp_config['port'], timeout=30)
            if smtp_config['use_starttls']:
                server.starttls()
        
        try:
            server.login(config['sender_email'], config['sender_password'])
            server.sendmail(config['sender_email'], recipients, msg.as_string())
        finally:
            server.quit()
        
        attachment_names = get_attachment_names(attachments)
        
        result = {
            'success': True,
            'message': 'Email sent successfully',
            'recipient': to,
            'subject': subject,
            'attachments': attachment_names,
            'timestamp': datetime.now().isoformat(),
            'smtp_server': smtp_config['host'],
            'from': config['sender_email']
        }
        
        _record_history(to, subject, True, None, attachments, cc, bcc, smtp_config['host'])
        return result
        
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f'SMTP Authentication Error: {str(e)}'
        result = {
            'success': False,
            'error': error_msg,
            'error_code': 'AUTH_FAILED',
            'hint': 'Please check your email authorization code (not login password)',
            'smtp_server': smtp_config['host'],
            'troubleshooting': [
                'Verify you are using authorization code, not login password',
                'Check if SMTP service is enabled in your email settings',
                'For Gmail: Ensure 2-Step Verification is enabled and use App Password',
                'For 126/163/QQ: Get authorization code from email settings'
            ]
        }
        _record_history(to, subject, False, error_msg, attachments, cc, bcc, smtp_config['host'])
        return result
        
    except smtplib.SMTPRecipientsRefused as e:
        error_msg = f'Recipient refused: {str(e)}'
        result = {
            'success': False,
            'error': error_msg,
            'error_code': 'RECIPIENT_REFUSED',
            'hint': 'The recipient email address may be invalid or blocked',
            'smtp_server': smtp_config['host']
        }
        _record_history(to, subject, False, error_msg, attachments, cc, bcc, smtp_config['host'])
        return result
        
    except smtplib.SMTPDataError as e:
        error_msg = f'SMTP Data Error: {str(e)}'
        result = {
            'success': False,
            'error': error_msg,
            'error_code': 'DATA_ERROR',
            'hint': 'The message content may be too large or contain invalid data',
            'smtp_server': smtp_config['host']
        }
        _record_history(to, subject, False, error_msg, attachments, cc, bcc, smtp_config['host'])
        return result
        
    except socket.timeout:
        error_msg = 'Connection timeout'
        result = {
            'success': False,
            'error': error_msg,
            'error_code': 'TIMEOUT',
            'hint': 'SMTP server did not respond in time',
            'smtp_server': smtp_config['host'],
            'troubleshooting': [
                'Check your network connection',
                'Verify SMTP server address and port',
                'Try alternative port (465 for SSL, 587 for STARTTLS)',
                'Check if firewall blocks SMTP connections'
            ]
        }
        _record_history(to, subject, False, error_msg, attachments, cc, bcc, smtp_config['host'])
        return result
        
    except socket.gaierror as e:
        error_msg = f'DNS resolution failed: {str(e)}'
        result = {
            'success': False,
            'error': error_msg,
            'error_code': 'DNS_ERROR',
            'hint': 'Could not resolve SMTP server hostname',
            'smtp_server': smtp_config['host']
        }
        _record_history(to, subject, False, error_msg, attachments, cc, bcc, smtp_config['host'])
        return result
        
    except smtplib.SMTPException as e:
        error_msg = f'SMTP Error: {str(e)}'
        result = {
            'success': False,
            'error': error_msg,
            'error_code': 'SMTP_ERROR',
            'hint': 'Please check SMTP server settings and network connection',
            'smtp_server': smtp_config['host']
        }
        _record_history(to, subject, False, error_msg, attachments, cc, bcc, smtp_config['host'])
        return result
        
    except Exception as e:
        error_msg = f'Unexpected error: {type(e).__name__}: {str(e)}'
        result = {
            'success': False,
            'error': error_msg,
            'error_code': 'UNKNOWN_ERROR',
            'hint': 'Please check your configuration and try again',
            'error_type': type(e).__name__
        }
        _record_history(to, subject, False, error_msg, attachments, cc, bcc, smtp_config.get('host') if smtp_config else None)
        return result


def _record_history(to, subject, success, error, attachments, cc, bcc, smtp_server):
    """Record email sending attempt to history"""
    if not HISTORY_AVAILABLE:
        return
    
    try:
        attachment_names = get_attachment_names(attachments)
        add_email_record(
            to=to,
            subject=subject,
            success=success,
            error=error,
            attachments=attachment_names,
            cc=cc,
            bcc=bcc,
            smtp_server=smtp_server
        )
    except Exception:
        pass


def _fallback_load_config():
    """Fallback configuration loader when config_loader is not available"""
    config = {
        'smtp_server': os.getenv('SMTP_SERVER'),
        'smtp_port': 465,
        'sender_email': os.getenv('SENDER_EMAIL'),
        'sender_password': os.getenv('SENDER_PASSWORD'),
        'sender_name': os.getenv('SENDER_NAME', ''),
        'use_ssl': True,
        'use_starttls': False,
    }
    
    try:
        from dotenv import load_dotenv
        script_path = Path(__file__).resolve()
        skill_dir = script_path.parent.parent
        env_file = skill_dir / '.env'
        if env_file.exists():
            load_dotenv(env_file)
        config['smtp_server'] = os.getenv('SMTP_SERVER')
        config['smtp_port'] = int(os.getenv('SMTP_PORT', 465))
        config['sender_email'] = os.getenv('SENDER_EMAIL')
        config['sender_password'] = os.getenv('SENDER_PASSWORD')
        config['sender_name'] = os.getenv('SENDER_NAME', '')
    except Exception:
        pass
    
    return config


def _fallback_get_smtp_config(email, config):
    """Fallback SMTP config when config_loader is not available"""
    PRESET_SMTP_SERVERS = {
        '126': {'host': 'smtp.126.com', 'port': 465, 'ssl': True},
        '163': {'host': 'smtp.163.com', 'port': 465, 'ssl': True},
        'qq': {'host': 'smtp.qq.com', 'port': 465, 'ssl': True},
        'gmail': {'host': 'smtp.gmail.com', 'port': 465, 'ssl': True},
        'outlook': {'host': 'smtp.office365.com', 'port': 587, 'ssl': False, 'starttls': True},
    }
    
    if email and '@' in email:
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
        provider = provider_map.get(domain)
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
    parser = argparse.ArgumentParser(
        description='Send email via SMTP with attachment support',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python send_email.py --to "user@example.com" --subject "Hello" --body "Test message"
  python send_email.py --to "user@example.com" --subject "Report" --body "See attachment" --attachments "report.pdf"
  python send_email.py --to "user@example.com" --subject "Files" --body "Multiple files" --attachments "file1.pdf,file2.xlsx"
  python send_email.py --validate-config
  python send_email.py --history
        '''
    )
    
    parser.add_argument('--to', help='Recipient email address(es), comma-separated')
    parser.add_argument('--subject', help='Email subject')
    parser.add_argument('--body', help='Email body content')
    parser.add_argument('--attachments', help='Attachment file path(s), comma-separated')
    parser.add_argument('--html', action='store_true', help='Body is HTML format')
    parser.add_argument('--cc', help='CC email address(es), comma-separated')
    parser.add_argument('--bcc', help='BCC email address(es), comma-separated')
    parser.add_argument('--validate-config', action='store_true', help='Validate email configuration')
    parser.add_argument('--history', action='store_true', help='Show recent email history')
    
    args = parser.parse_args()
    
    if args.validate_config:
        try:
            import validate_config as vc
            results = vc.validate_config()
            try:
                print(json.dumps(results, ensure_ascii=False, indent=2))
            except (TypeError, ValueError) as e:
                print(json.dumps({
                    'success': False,
                    'error': f'Could not serialize validation results: {e}',
                    'error_code': 'SERIALIZATION_ERROR'
                }, ensure_ascii=False, indent=2))
            sys.exit(0 if results.get('valid', False) else 1)
        except ImportError as e:
            print(json.dumps({
                'success': False,
                'error': f'validate_config.py not found: {e}',
                'hint': 'Ensure validate_config.py is in the same directory'
            }, ensure_ascii=False, indent=2))
            sys.exit(1)
        except Exception as e:
            print(json.dumps({
                'success': False,
                'error': f'Unexpected error during validation: {e}',
                'error_code': 'VALIDATION_ERROR'
            }, ensure_ascii=False, indent=2))
            sys.exit(1)
    
    if args.history:
        try:
            import email_history as eh
            emails = eh.get_recent_emails(10)
            stats = eh.get_stats()
            try:
                print(json.dumps({
                    'stats': stats,
                    'recent_emails': emails
                }, ensure_ascii=False, indent=2))
            except (TypeError, ValueError) as e:
                print(json.dumps({
                    'success': False,
                    'error': f'Could not serialize history: {e}',
                    'error_code': 'SERIALIZATION_ERROR'
                }, ensure_ascii=False, indent=2))
            sys.exit(0)
        except ImportError as e:
            print(json.dumps({
                'success': False,
                'error': f'email_history.py not found: {e}',
                'hint': 'Ensure email_history.py is in the same directory'
            }, ensure_ascii=False, indent=2))
            sys.exit(1)
        except Exception as e:
            print(json.dumps({
                'success': False,
                'error': f'Unexpected error retrieving history: {e}',
                'error_code': 'HISTORY_ERROR'
            }, ensure_ascii=False, indent=2))
            sys.exit(1)
    
    if not args.to or not args.subject or not args.body:
        parser.error('--to, --subject, and --body are required for sending email')
    
    result = send_email(
        to=args.to,
        subject=args.subject,
        body=args.body,
        attachments=args.attachments,
        is_html=args.html,
        cc=args.cc,
        bcc=args.bcc
    )
    
    try:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (TypeError, ValueError) as e:
        print(json.dumps({
            'success': False,
            'error': f'Could not serialize result: {e}',
            'error_code': 'SERIALIZATION_ERROR'
        }, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': f'Unexpected output error: {e}',
            'error_code': 'OUTPUT_ERROR'
        }, ensure_ascii=False, indent=2))
    
    sys.exit(0 if result.get('success', False) else 1)


if __name__ == '__main__':
    main()
