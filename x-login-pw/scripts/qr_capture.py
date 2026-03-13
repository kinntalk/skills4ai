#!/usr/bin/env python3
"""
X-Login-PW: Universal Login QR Code Capture
Capture QR codes from desktop applications.
"""

import argparse
import json
import sys
from pathlib import Path

from universal_app_capture import UniversalAppCapture
from app_profile_manager import AppProfileManager

SKILL_DIR = Path(__file__).parent.parent

MSG = {
    "en": {
        "app_not_supported": "Error: Application '{app_id}' not supported",
        "supported_apps": "Supported applications: {apps}",
        "supported_apps_header": "Supported applications:",
        "json_output_error": "Error: Failed to serialize output to JSON"
    }
}


def get_msg(lang: str = "en") -> dict:
    return MSG.get(lang, MSG["en"])


def get_default_output_path(app_id: str) -> str:
    output_dir = SKILL_DIR / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return str(output_dir / f"{app_id}_login_qr.png")


def capture_command(args, profile_manager: AppProfileManager, app_capture: UniversalAppCapture, msg: dict) -> int:
    app_id = args.app_id
    identifier = args.identifier or app_id
    
    supported_apps = profile_manager.list_apps()
    if app_id not in supported_apps:
        print(msg["app_not_supported"].format(app_id=app_id), file=sys.stderr, flush=True)
        print(msg["supported_apps"].format(apps=", ".join(supported_apps.keys())), file=sys.stderr, flush=True)
        return 1
    
    output_path = args.output or get_default_output_path(app_id)
    
    result = app_capture.capture_qr_code(
        identifier=identifier,
        app_id=app_id,
        output_path=output_path,
        force_refresh=getattr(args, 'refresh', False)
    )
    
    try:
        print(json.dumps(result, indent=2, ensure_ascii=False), flush=True)
    except (TypeError, ValueError) as e:
        print(f"{msg['json_output_error']}: {e}", file=sys.stderr, flush=True)
        return 1
    
    return 0 if result.get('success') else 1


def list_command(profile_manager: AppProfileManager, msg: dict) -> int:
    apps = profile_manager.list_apps()
    print(msg["supported_apps_header"], flush=True)
    for app_id, app_name in apps.items():
        print(f"  {app_id}: {app_name}", flush=True)
    return 0


def main():
    parser = argparse.ArgumentParser(
        description='Capture login QR codes from desktop applications',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python qr_capture.py capture feishu
  python qr_capture.py capture wechat
  python qr_capture.py capture dingtalk
  python qr_capture.py list
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    capture_parser = subparsers.add_parser('capture', help='Capture QR code from application')
    capture_parser.add_argument('app_id', help='Application ID (feishu, wechat, dingtalk)')
    capture_parser.add_argument('-o', '--output', help='Output file path (default: {skill_dir}/output/{app_id}_login_qr.png)')
    capture_parser.add_argument('-p', '--padding', type=int, help='Padding around QR code (px)')
    capture_parser.add_argument('-i', '--identifier', help='Window identifier (title or process name)')
    capture_parser.add_argument('-r', '--refresh', action='store_true', help='Force refresh QR code before capture')
    
    list_parser = subparsers.add_parser('list', help='List supported applications')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    msg = get_msg("en")
    profile_manager = AppProfileManager()
    app_capture = UniversalAppCapture(profile_manager)
    
    if args.command == 'capture':
        exit_code = capture_command(args, profile_manager, app_capture, msg)
        sys.exit(exit_code)
    
    elif args.command == 'list':
        exit_code = list_command(profile_manager, msg)
        sys.exit(exit_code)


if __name__ == '__main__':
    main()
