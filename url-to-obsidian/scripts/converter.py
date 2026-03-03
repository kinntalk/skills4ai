"""
Core converter module for url-to-obsidian skill.

Handles:
- Web content fetching via CDP (Chrome DevTools Protocol)
- Automatic login detection
- Content extraction and conversion
- Integration with Obsidian vault
"""

import subprocess
import json
import re
import sys
from pathlib import Path
from typing import Optional, Tuple, Callable
from datetime import datetime
from urllib.parse import urlparse

try:
    from .config_manager import ConfigManager, get_config_manager
    from .ofm_formatter import format_ofm, generate_filename, sanitize_filename
    from .asset_handler import AssetHandler
    from .vault_detector import get_vault_attachment_folder, detect_vault_path
    from .cdp_client import run_capture_sync, capture_page
    from .html_converter import process_extracted_content
except ImportError:
    from config_manager import ConfigManager, get_config_manager
    from ofm_formatter import format_ofm, generate_filename, sanitize_filename
    from asset_handler import AssetHandler
    from vault_detector import get_vault_attachment_folder, detect_vault_path
    from cdp_client import run_capture_sync, capture_page
    from html_converter import process_extracted_content


class UrlToObsidianConverter:
    """Main converter class for url-to-obsidian functionality."""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """Initialize converter.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager or get_config_manager()
    
    def convert(
        self,
        url: str,
        output_path: Optional[Path] = None,
        tags: Optional[list] = None,
        add_frontmatter: bool = True,
        add_source_info: bool = True,
        download_assets: Optional[bool] = None,
        use_wikilink: bool = False,
        wait_for_login: bool = True,
        headless: bool = False,
        on_status: Optional[Callable[[str], None]] = None
    ) -> Tuple[bool, str, Optional[Path]]:
        """Convert a URL to Obsidian Flavored Markdown.
        
        This method uses CDP to capture page content with automatic login detection.
        
        Args:
            url: URL to convert
            output_path: Optional output file path
            tags: Optional list of tags
            add_frontmatter: Whether to add YAML frontmatter
            add_source_info: Whether to add source callout
            download_assets: Whether to download images/assets. If None, uses config setting.
            use_wikilink: Whether to use wikilink format for images
            wait_for_login: Whether to wait for login if detected
            headless: Whether to run browser in headless mode
            on_status: Optional callback for status updates
            
        Returns:
            Tuple of (success, message, output_file_path)
        """
        try:
            if on_status:
                on_status(f"Capturing: {url}")
            
            extracted = run_capture_sync(
                url,
                wait_for_login=wait_for_login,
                headless=headless,
                on_status=on_status
            )
            
            if not extracted.get("html"):
                return False, "Failed to extract page content", None
            
            result = process_extracted_content(extracted)
            
            title = result.get("title", "Untitled")
            markdown = result.get("markdown", "")
            
            if not markdown.strip():
                return False, "No content extracted from page", None
            
            config_tags = self.config_manager.get('output.default_tags', [])
            if tags is None:
                tags = config_tags
            else:
                tags = list(set(tags + config_tags))
            
            formatted_content = format_ofm(
                markdown,
                url=url,
                title=title,
                tags=tags,
                add_source_info=add_source_info,
                add_frontmatter=add_frontmatter
            )
            
            vault_path = self.config_manager.get_vault_path_with_auto_detect()
            if output_path is None:
                if vault_path is None:
                    return False, "Vault path not configured and auto-detection failed. Run: web2obs config set-vault <path>", None
                
                subfolder = self.config_manager.get('output.subfolder', 'web-clippings')
                output_dir = vault_path / subfolder
                output_dir.mkdir(parents=True, exist_ok=True)
                
                filename = generate_filename(title or "untitled")
                output_path = output_dir / filename
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            assets_config = self.config_manager.get_assets_config()
            should_download = download_assets if download_assets is not None else assets_config.get('download', True)
            
            if should_download and vault_path:
                formatted_content = self._download_assets(
                    formatted_content, 
                    vault_path, 
                    title, 
                    assets_config, 
                    use_wikilink
                )
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
            
            return True, f"Successfully converted to {output_path}", output_path
            
        except Exception as e:
            return False, f"Error: {str(e)}", None
    
    def _download_assets(
        self,
        content: str,
        vault_path: Path,
        title: str,
        assets_config: dict,
        use_wikilink: bool
    ) -> str:
        """Download and process assets in content.
        
        Args:
            content: Markdown content
            vault_path: Path to Obsidian vault
            title: Note title
            assets_config: Assets configuration
            use_wikilink: Whether to use wikilink format
            
        Returns:
            Content with updated asset links
        """
        assets_folder = assets_config.get('folder')
        if not assets_folder:
            assets_folder = get_vault_attachment_folder(vault_path)
        
        naming_template = assets_config.get('naming', '{title}-{timestamp}-{index}')
        final_wikilink = use_wikilink or assets_config.get('wikilink', False)
        
        try:
            from ofm_formatter import extract_image_urls, convert_image_links
            
            asset_handler = AssetHandler(
                vault_path=vault_path,
                assets_folder=assets_folder,
                naming_template=naming_template
            )
            
            assets_path = vault_path / assets_folder
            assets_path.mkdir(parents=True, exist_ok=True)
            
            images = extract_image_urls(content)
            
            if images:
                url_mapping = {}
                note_title = title or "untitled"
                
                for idx, (alt_text, img_url, full_match) in enumerate(images):
                    if img_url in url_mapping:
                        continue
                    
                    if img_url.startswith('data:'):
                        continue
                    
                    success_download, msg, local_path = asset_handler.download_asset(
                        url=img_url,
                        note_title=note_title,
                        index=idx + 1
                    )
                    
                    if success_download and local_path:
                        relative_path = f"{assets_folder}/{local_path.name}"
                        url_mapping[img_url] = relative_path
                
                if url_mapping:
                    content = convert_image_links(content, url_mapping, final_wikilink)
        except ImportError:
            pass
        
        return content
    
    def convert_with_wait(
        self,
        url: str,
        output_path: Optional[Path] = None,
        tags: Optional[list] = None,
        add_frontmatter: bool = True,
        add_source_info: bool = True,
        download_assets: Optional[bool] = None,
        use_wikilink: bool = False,
        on_status: Optional[Callable[[str], None]] = None
    ) -> Tuple[bool, str, Optional[Path]]:
        """Convert a URL with wait mode for manual login.
        
        This is now equivalent to convert() with wait_for_login=True,
        but kept for backward compatibility.
        
        Args:
            url: URL to convert
            output_path: Optional output file path
            tags: Optional list of tags
            add_frontmatter: Whether to add YAML frontmatter
            add_source_info: Whether to add source callout
            download_assets: Whether to download images/assets
            use_wikilink: Whether to use wikilink format for images
            on_status: Optional callback for status updates
            
        Returns:
            Tuple of (success, message, output_file_path)
        """
        return self.convert(
            url=url,
            output_path=output_path,
            tags=tags,
            add_frontmatter=add_frontmatter,
            add_source_info=add_source_info,
            download_assets=download_assets,
            use_wikilink=use_wikilink,
            wait_for_login=True,
            headless=False,
            on_status=on_status
        )
    
    def _convert_captured_markdown(
        self,
        markdown_content: str,
        url: str,
        output_path: Optional[Path] = None,
        tags: Optional[list] = None,
        add_frontmatter: bool = True,
        add_source_info: bool = True,
        download_assets: Optional[bool] = None,
        use_wikilink: bool = False
    ) -> Tuple[bool, str, Optional[Path]]:
        """Convert captured markdown content to OFM.
        
        This method processes markdown that was already captured,
        extracts its frontmatter, and reformats it with OFM features.
        
        Args:
            markdown_content: Markdown content with YAML frontmatter
            url: Source URL
            output_path: Optional output file path
            tags: Optional list of tags
            add_frontmatter: Whether to add YAML frontmatter
            add_source_info: Whether to add source callout
            download_assets: Whether to download images/assets
            use_wikilink: Whether to use wikilink format for images
            
        Returns:
            Tuple of (success, message, output_file_path)
        """
        title = None
        content = markdown_content
        
        if markdown_content.startswith('---'):
            parts = markdown_content.split('---', 2)
            if len(parts) >= 3:
                frontmatter_text = parts[1].strip()
                content = parts[2].strip()
                
                for line in frontmatter_text.split('\n'):
                    if line.startswith('title:'):
                        title = line.split(':', 1)[1].strip().strip('"\'')
                    elif line.startswith('url:'):
                        extracted_url = line.split(':', 1)[1].strip()
                        if not url:
                            url = extracted_url
        
        config_tags = self.config_manager.get('output.default_tags', [])
        if tags is None:
            tags = config_tags
        else:
            tags = list(set(tags + config_tags))
        
        formatted_content = format_ofm(
            content,
            url=url,
            title=title,
            tags=tags,
            add_source_info=add_source_info,
            add_frontmatter=add_frontmatter
        )
        
        vault_path = self.config_manager.get_vault_path_with_auto_detect()
        if output_path is None:
            if vault_path is None:
                return False, "Vault path not configured and auto-detection failed. Run: web2obs config set-vault <path>", None
            
            subfolder = self.config_manager.get('output.subfolder', 'web-clippings')
            output_dir = vault_path / subfolder
            output_dir.mkdir(parents=True, exist_ok=True)
            
            filename = generate_filename(title or "captured-page")
            output_path = output_dir / filename
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        assets_config = self.config_manager.get_assets_config()
        should_download = download_assets if download_assets is not None else assets_config.get('download', True)
        
        if should_download and vault_path:
            formatted_content = self._download_assets(
                formatted_content,
                vault_path,
                title or "captured-page",
                assets_config,
                use_wikilink
            )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(formatted_content)
        
        return True, f"Successfully converted to {output_path}", output_path


WebToObsidianConverter = UrlToObsidianConverter


def convert_url(
    url: str,
    output_path: Optional[Path] = None,
    tags: Optional[list] = None,
    wait: bool = False,
    config_manager: Optional[ConfigManager] = None,
    download_assets: Optional[bool] = None,
    use_wikilink: bool = False,
    on_status: Optional[Callable[[str], None]] = None
) -> Tuple[bool, str, Optional[Path]]:
    """Convert a URL to Obsidian Flavored Markdown.
    
    Args:
        url: URL to convert
        output_path: Optional output file path
        tags: Optional list of tags
        wait: Whether to use wait mode (wait for login)
        config_manager: Optional configuration manager
        download_assets: Whether to download images/assets
        use_wikilink: Whether to use wikilink format for images
        on_status: Optional callback for status updates
        
    Returns:
        Tuple of (success, message, output_file_path)
    """
    converter = UrlToObsidianConverter(config_manager)
    
    return converter.convert(
        url=url,
        output_path=output_path,
        tags=tags,
        download_assets=download_assets,
        use_wikilink=use_wikilink,
        wait_for_login=wait,
        headless=False,
        on_status=on_status
    )


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert URL to Obsidian Markdown")
    parser.add_argument("url", help="URL to convert")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("--tags", help="Comma-separated tags")
    parser.add_argument("--wait", action="store_true", help="Wait for manual login")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    
    args = parser.parse_args()
    
    output_path = Path(args.output) if args.output else None
    tags = args.tags.split(',') if args.tags else None
    
    def print_status(msg: str) -> None:
        print(f"[STATUS] {msg}")
    
    success, message, path = convert_url(
        args.url,
        output_path=output_path,
        tags=tags,
        wait=args.wait,
        on_status=print_status
    )
    
    print(message)
    if success:
        print(f"Output: {path}")
    else:
        sys.exit(1)
