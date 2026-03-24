#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
x-mail-sender: Email history manager
Tracks sent emails for debugging and auditing purposes
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any


def get_skill_dir() -> Path:
    script_path = Path(__file__).resolve()
    return script_path.parent.parent


def get_history_dir() -> Path:
    skill_dir = get_skill_dir()
    history_dir = skill_dir / 'history'
    history_dir.mkdir(exist_ok=True)
    return history_dir


def get_history_file() -> Path:
    return get_history_dir() / 'email_history.json'


def load_history() -> Dict[str, Any]:
    history_file = get_history_file()
    default_history = {'emails': [], 'stats': {'total': 0, 'successful': 0, 'failed': 0}}
    if history_file.exists():
        try:
            with open(history_file, 'r', encoding='utf-8', errors='replace') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError, OSError, PermissionError) as e:
            print(f"Warning: Could not load history file: {e}", file=sys.stderr)
            return default_history
        except Exception as e:
            print(f"Warning: Unexpected error loading history: {e}", file=sys.stderr)
            return default_history
    return default_history


def save_history(history: Dict[str, Any]) -> bool:
    history_file = get_history_file()
    try:
        with open(history_file, 'w', encoding='utf-8', errors='replace') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        return True
    except (IOError, OSError, PermissionError) as e:
        print(f"Warning: Could not save history: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Warning: Unexpected error saving history: {e}", file=sys.stderr)
        return False


def add_email_record(
    to: str,
    subject: str,
    success: bool,
    error: Optional[str] = None,
    attachments: Optional[List[str]] = None,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
    smtp_server: Optional[str] = None
) -> Dict[str, Any]:
    history = load_history()
    
    record = {
        'id': f"email_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(history['emails'])}",
        'timestamp': datetime.now().isoformat(),
        'to': to,
        'subject': subject,
        'success': success,
        'error': error,
        'attachments': attachments or [],
        'cc': cc,
        'bcc': bcc,
        'smtp_server': smtp_server
    }
    
    history['emails'].append(record)
    history['stats']['total'] += 1
    if success:
        history['stats']['successful'] += 1
    else:
        history['stats']['failed'] += 1
    
    max_records = 100
    if len(history['emails']) > max_records:
        history['emails'] = history['emails'][-max_records:]
    
    save_history(history)
    return record


def get_recent_emails(limit: int = 10) -> List[Dict[str, Any]]:
    history = load_history()
    return history['emails'][-limit:]


def get_stats() -> Dict[str, Any]:
    history = load_history()
    return history['stats']


def clear_history() -> bool:
    history_file = get_history_file()
    try:
        if history_file.exists():
            history_file.unlink()
        return True
    except IOError:
        return False


def export_history(output_path: Optional[str] = None) -> str:
    history = load_history()
    
    if output_path:
        output_file = Path(output_path)
    else:
        output_file = get_history_dir() / f"email_history_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(output_file, 'w', encoding='utf-8', errors='replace') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        return str(output_file)
    except (IOError, OSError, PermissionError) as e:
        print(f"Warning: Could not export history: {e}", file=sys.stderr)
        return ""
    except Exception as e:
        print(f"Warning: Unexpected error exporting history: {e}", file=sys.stderr)
        return ""


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Manage email sending history'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    list_parser = subparsers.add_parser('list', help='List recent emails')
    list_parser.add_argument('--limit', type=int, default=10, help='Number of emails to show')
    list_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    stats_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    clear_parser = subparsers.add_parser('clear', help='Clear history')
    clear_parser.add_argument('--confirm', action='store_true', help='Confirm clearing')
    
    export_parser = subparsers.add_parser('export', help='Export history')
    export_parser.add_argument('--output', help='Output file path')
    
    args = parser.parse_args()
    
    if args.command == 'list':
        emails = get_recent_emails(args.limit)
        if args.json:
            try:
                print(json.dumps(emails, ensure_ascii=False, indent=2))
            except (TypeError, ValueError) as e:
                print(json.dumps({'error': f'Could not serialize emails: {e}'}, ensure_ascii=False, indent=2))
            except Exception as e:
                print(json.dumps({'error': f'Unexpected error: {e}'}, ensure_ascii=False, indent=2))
        else:
            if not emails:
                print("No email history found.")
                return
            
            print(f"\nRecent {len(emails)} emails:")
            print("-" * 80)
            for email in reversed(emails):
                status = "SUCCESS" if email['success'] else "FAILED"
                print(f"[{status}] {email['timestamp']}")
                print(f"  To: {email['to']}")
                print(f"  Subject: {email['subject']}")
                if email['attachments']:
                    print(f"  Attachments: {', '.join(email['attachments'])}")
                if email['error']:
                    print(f"  Error: {email['error']}")
                print()
    
    elif args.command == 'stats':
        stats = get_stats()
        if args.json:
            try:
                print(json.dumps(stats, ensure_ascii=False, indent=2))
            except (TypeError, ValueError) as e:
                print(json.dumps({'error': f'Could not serialize stats: {e}'}, ensure_ascii=False, indent=2))
            except Exception as e:
                print(json.dumps({'error': f'Unexpected error: {e}'}, ensure_ascii=False, indent=2))
        else:
            print("\nEmail Statistics:")
            print("-" * 40)
            print(f"Total emails: {stats['total']}")
            print(f"Successful: {stats['successful']}")
            print(f"Failed: {stats['failed']}")
            if stats['total'] > 0:
                success_rate = (stats['successful'] / stats['total']) * 100
                print(f"Success rate: {success_rate:.1f}%")
    
    elif args.command == 'clear':
        if args.confirm:
            if clear_history():
                print("History cleared successfully.")
            else:
                print("Failed to clear history.")
        else:
            print("Use --confirm to actually clear the history.")
    
    elif args.command == 'export':
        output_path = export_history(args.output)
        print(f"History exported to: {output_path}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
