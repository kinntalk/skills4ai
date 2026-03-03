#!/usr/bin/env python3
"""
URL to Obsidian Markdown Converter CLI

Convert web pages to Obsidian Flavored Markdown and save to Obsidian vault.
Features:
- Automatic login detection
- Obsidian vault auto-detection
- Asset downloading
- OFM formatting
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

try:
    from config_manager import ConfigManager, get_config_manager
    from converter import convert_url, UrlToObsidianConverter
except ImportError:
    from .config_manager import ConfigManager, get_config_manager
    from .converter import convert_url, UrlToObsidianConverter


def cmd_convert(args, config: ConfigManager) -> int:
    """Handle convert command.
    
    Args:
        args: Parsed arguments
        config: Configuration manager
        
    Returns:
        Exit code
    """
    output_path = None
    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            vault_path = config.get_vault_path()
            if vault_path:
                subfolder = args.subfolder or config.get('output.subfolder', 'web-clippings')
                output_path = vault_path / subfolder / output_path
    
    tags = None
    if args.tags:
        tags = [t.strip() for t in args.tags.split(',')]
    
    download_assets = not args.no_assets and config.get('assets.download', True)
    use_wikilink = args.wikilink or config.get('assets.wikilink', False)
    
    wait_for_login = not args.no_wait
    
    def print_status(msg: str) -> None:
        print(f"[STATUS] {msg}")
    
    success, message, path = convert_url(
        url=args.url,
        output_path=output_path,
        tags=tags,
        wait=wait_for_login,
        config_manager=config,
        download_assets=download_assets,
        use_wikilink=use_wikilink,
        on_status=print_status
    )
    
    print(message)
    if path:
        print(f"Output: {path}")
    
    return 0 if success else 1


def cmd_format(args, config: ConfigManager) -> int:
    """Handle format command - format existing markdown as OFM.
    
    Args:
        args: Parsed arguments
        config: Configuration manager
        
    Returns:
        Exit code
    """
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        return 1
    
    content = input_path.read_text(encoding='utf-8')
    
    output_path = None
    if args.output:
        output_path = Path(args.output)
    elif args.in_place:
        output_path = input_path
    else:
        vault_path = config.get_vault_path()
        if vault_path:
            subfolder = config.get('output.subfolder', 'web-clippings')
            output_dir = vault_path / subfolder
            output_dir.mkdir(parents=True, exist_ok=True)
            from ofm_formatter import generate_filename, extract_title
            title = extract_title(content)
            filename = generate_filename(title)
            output_path = output_dir / filename
        else:
            print("Error: No output path specified and vault path not configured")
            return 1
    
    tags = None
    if args.tags:
        tags = [t.strip() for t in args.tags.split(',')]
    
    download_assets = not args.no_assets and config.get('assets.download', True)
    use_wikilink = args.wikilink or config.get('assets.wikilink', False)
    
    converter = UrlToObsidianConverter(config)
    success, message, path = converter._convert_captured_markdown(
        markdown_content=content,
        url=args.url or "",
        output_path=output_path,
        tags=tags,
        add_frontmatter=not args.no_frontmatter,
        add_source_info=not args.no_source,
        download_assets=download_assets,
        use_wikilink=use_wikilink
    )
    
    print(message)
    return 0 if success else 1


def cmd_config(args, config: ConfigManager) -> int:
    """Handle config command.
    
    Args:
        args: Parsed arguments
        config: Configuration manager
        
    Returns:
        Exit code
    """
    if args.config_cmd == 'list':
        import json
        data = config.load()
        if 'credentials' in data:
            data['credentials'] = {k: {'username': '***', 'password': '***'} 
                                   for k in data['credentials']}
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0
    
    elif args.config_cmd == 'get':
        value = config.get(args.key)
        if value is None:
            print(f"Key '{args.key}' not found")
            return 1
        print(value)
        return 0
    
    elif args.config_cmd == 'set':
        config.set(args.key, args.value)
        print(f"Set {args.key} = {args.value}")
        return 0
    
    elif args.config_cmd == 'set-vault':
        vault_path = Path(args.path)
        if not vault_path.exists():
            print(f"Warning: Path '{args.path}' does not exist")
        config.set_vault_path(args.path)
        print(f"Vault path set to: {args.path}")
        return 0
    
    elif args.config_cmd == 'add-credentials':
        domain = args.domain
        print(f"Adding credentials for: {domain}")
        username = input("Username: ")
        password = input("Password: ")
        config.set_credentials(domain, username, password)
        print(f"Credentials stored for {domain}")
        return 0
    
    elif args.config_cmd == 'remove-credentials':
        domain = args.domain
        if config.remove_credentials(domain):
            print(f"Credentials removed for {domain}")
            return 0
        else:
            print(f"No credentials found for {domain}")
            return 1
    
    elif args.config_cmd == 'list-credentials':
        domains = config.list_credentials()
        if domains:
            print("Stored credentials for:")
            for domain in domains:
                print(f"  - {domain}")
        else:
            print("No credentials stored")
        return 0
    
    return 1


def main() -> int:
    """Main entry point.
    
    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        prog='web2obs',
        description='Convert web pages to Obsidian Flavored Markdown (url-to-obsidian skill)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    convert_parser = subparsers.add_parser('convert', help='Convert a URL to OFM')
    convert_parser.add_argument('url', help='URL to convert')
    convert_parser.add_argument('-o', '--output', help='Output file name')
    convert_parser.add_argument('--tags', help='Comma-separated tags')
    convert_parser.add_argument('--wait', action='store_true', 
                                help='Wait for login (auto-detected by default)')
    convert_parser.add_argument('--no-wait', action='store_true',
                                help='Disable automatic login detection')
    convert_parser.add_argument('--headless', action='store_true',
                                help='Run browser in headless mode')
    convert_parser.add_argument('--subfolder', help='Subfolder within vault')
    convert_parser.add_argument('--no-frontmatter', action='store_true',
                                help='Skip frontmatter generation')
    convert_parser.add_argument('--no-assets', action='store_true',
                                help='Disable asset (image) downloading')
    convert_parser.add_argument('--wikilink', action='store_true',
                                help='Use wikilink format for image links')
    
    format_parser = subparsers.add_parser('format', help='Format existing markdown as OFM')
    format_parser.add_argument('input', help='Input markdown file')
    format_parser.add_argument('-o', '--output', help='Output file path')
    format_parser.add_argument('--url', help='Source URL (extracted from frontmatter if not provided)')
    format_parser.add_argument('--tags', help='Comma-separated tags')
    format_parser.add_argument('--in-place', action='store_true',
                               help='Overwrite input file')
    format_parser.add_argument('--no-frontmatter', action='store_true',
                               help='Skip frontmatter generation')
    format_parser.add_argument('--no-source', action='store_true',
                               help='Skip source callout')
    format_parser.add_argument('--no-assets', action='store_true',
                               help='Disable asset (image) downloading')
    format_parser.add_argument('--wikilink', action='store_true',
                               help='Use wikilink format for image links')
    
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_subparsers = config_parser.add_subparsers(dest='config_cmd', help='Config commands')
    
    config_list = config_subparsers.add_parser('list', help='List all configuration')
    
    config_get = config_subparsers.add_parser('get', help='Get a configuration value')
    config_get.add_argument('key', help='Configuration key')
    
    config_set = config_subparsers.add_parser('set', help='Set a configuration value')
    config_set.add_argument('key', help='Configuration key')
    config_set.add_argument('value', help='Configuration value')
    
    config_vault = config_subparsers.add_parser('set-vault', help='Set Obsidian vault path')
    config_vault.add_argument('path', help='Path to Obsidian vault')
    
    config_add_creds = config_subparsers.add_parser('add-credentials', 
                                                     help='Add credentials for a domain')
    config_add_creds.add_argument('domain', help='Domain name')
    
    config_remove_creds = config_subparsers.add_parser('remove-credentials',
                                                        help='Remove credentials for a domain')
    config_remove_creds.add_argument('domain', help='Domain name')
    
    config_list_creds = config_subparsers.add_parser('list-credentials',
                                                      help='List domains with stored credentials')
    
    args = parser.parse_args()
    
    config = get_config_manager()
    
    if args.command == 'config':
        return cmd_config(args, config)
    
    if args.command == 'convert':
        if hasattr(args, 'no_wait') and args.no_wait:
            args.wait = False
        return cmd_convert(args, config)
    
    if args.command == 'format':
        return cmd_format(args, config)
    
    if not args.command:
        parser.print_help()
        return 0
    
    parser.print_help()
    return 0


if __name__ == '__main__':
    sys.exit(main())
