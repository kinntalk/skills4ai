#!/usr/bin/env python3
"""
Markdown to WeChat HTML Renderer

Converts Markdown files to WeChat-compatible HTML with inline CSS.
Supports multiple themes and handles WeChat-specific constraints.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional, Tuple, Dict

try:
    from markdown_it import MarkdownIt
except ImportError:
    print("Error: markdown-it-py not installed. Run: pip install markdown-it-py")
    sys.exit(1)

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class WeChatHTMLRenderer:
    """Renders Markdown to WeChat-safe HTML with inline CSS."""

    WECHAT_UNSUPPORTED_TAGS = ['script', 'style', 'iframe', 'form', 'input']
    MAX_TITLE_LENGTH = 64
    MAX_DIGEST_LENGTH = 120
    FRONTMATTER_PATTERN = re.compile(r'^---\s*\n(.*?)\n---\s*\n(.*)$', re.DOTALL)

    def __init__(self, theme_path: Optional[Path] = None):
        self.theme = self._load_theme(theme_path)
        self.md = MarkdownIt("gfm-like", {"html": False})

    def _parse_frontmatter(self, content: str) -> Tuple[Optional[Dict], str]:
        """Parse YAML frontmatter and return (metadata, remaining_content)."""
        match = self.FRONTMATTER_PATTERN.match(content)
        if match:
            frontmatter_str = match.group(1)
            remaining = match.group(2)
            if YAML_AVAILABLE:
                try:
                    metadata = yaml.safe_load(frontmatter_str)
                    if isinstance(metadata, dict):
                        return metadata, remaining
                except yaml.YAMLError as e:
                    print(f"Warning: Failed to parse frontmatter: {e}")
            else:
                metadata = {}
                for line in frontmatter_str.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip()
                if metadata:
                    return metadata, remaining
        return None, content

    def _load_theme(self, theme_path: Optional[Path]) -> dict:
        """Load theme configuration from JSON file."""
        if theme_path and theme_path.exists():
            with open(theme_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self._default_theme()

    def _default_theme(self) -> dict:
        """Default theme configuration."""
        return {
            "body": {"font-family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", "font-size": "16px", "line-height": "1.8", "color": "#333333", "padding": "20px"},
            "h1": {"font-size": "24px", "font-weight": "bold", "margin": "20px 0 10px 0", "color": "#000000"},
            "h2": {"font-size": "20px", "font-weight": "bold", "margin": "18px 0 8px 0", "color": "#333333"},
            "h3": {"font-size": "18px", "font-weight": "bold", "margin": "16px 0 6px 0", "color": "#444444"},
            "p": {"margin": "10px 0", "text-align": "justify"},
            "blockquote": {"border-left": "4px solid #e0e0e0", "padding": "10px 15px", "margin": "15px 0", "background": "#f9f9f9", "color": "#666666"},
            "code": {"font-family": "'Courier New', monospace", "background": "#f5f5f5", "padding": "2px 6px", "border-radius": "3px", "font-size": "14px"},
            "pre": {"background": "#f5f5f5", "padding": "15px", "border-radius": "5px", "overflow-x": "auto", "margin": "15px 0"},
            "img": {"max-width": "100%", "height": "auto", "display": "block", "margin": "15px auto"},
            "ul": {"padding-left": "25px", "margin": "10px 0"},
            "ol": {"padding-left": "25px", "margin": "10px 0"},
            "li": {"margin": "5px 0"},
            "a": {"color": "#576b95", "text-decoration": "none"},
            "table": {"width": "100%", "border-collapse": "collapse", "margin": "15px 0"},
            "th": {"background": "#f5f5f5", "padding": "10px", "border": "1px solid #e0e0e0", "font-weight": "bold"},
            "td": {"padding": "10px", "border": "1px solid #e0e0e0"}
        }

    def _style_to_inline(self, style_dict: dict) -> str:
        """Convert style dictionary to inline CSS string."""
        return "; ".join(f"{k}: {v}" for k, v in style_dict.items())

    def _apply_inline_styles(self, html: str) -> str:
        """Apply inline CSS styles to HTML elements."""
        for tag, styles in self.theme.items():
            pattern = rf'<{tag}([^>]*)>'
            replacement = f'<{tag} style="{self._style_to_inline(styles)}"\\1>'
            html = re.sub(pattern, replacement, html)
        return html

    def _clean_unsupported_tags(self, html: str) -> str:
        """Remove WeChat-unsupported HTML tags."""
        for tag in self.WECHAT_UNSUPPORTED_TAGS:
            html = re.sub(rf'<{tag}[^>]*>.*?</{tag}>', '', html, flags=re.DOTALL | re.IGNORECASE)
            html = re.sub(rf'<{tag}[^>]*/?>', '', html, flags=re.IGNORECASE)
        return html

    def _convert_external_links(self, html: str) -> str:
        """Convert external links to footnote references for WeChat compatibility."""
        links = re.findall(r'<a[^>]*href="([^"]*)"[^>]*>([^<]*)</a>', html)
        if links:
            footnotes = "\n\n---\n**References:**\n"
            for i, (url, text) in enumerate(links, 1):
                footnotes += f"\n[{i}] {text}: {url}"
                html = html.replace(f'<a href="{url}">{text}</a>', f'{text}[{i}]', 1)
            html += footnotes
        return html

    def render(self, markdown_content: str) -> Tuple[Optional[Dict], str]:
        """Render Markdown to WeChat-compatible HTML.
        
        Returns:
            Tuple of (metadata_dict, html_content)
        """
        metadata, content = self._parse_frontmatter(markdown_content)
        html = self.md.render(content)
        html = self._apply_inline_styles(html)
        html = self._clean_unsupported_tags(html)
        html = self._convert_external_links(html)
        return metadata, html

    def render_file(self, input_path: Path, output_path: Optional[Path] = None) -> Tuple[Optional[Dict], str]:
        """Render a Markdown file to WeChat HTML.
        
        Returns:
            Tuple of (metadata_dict, html_content)
        """
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()

        metadata, html = self.render(content)

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)

        return metadata, html


def main():
    parser = argparse.ArgumentParser(description='Convert Markdown to WeChat HTML')
    parser.add_argument('input', type=Path, help='Input Markdown file')
    parser.add_argument('--theme', type=str, default='default', help='Theme name (default, tech, minimal)')
    parser.add_argument('--output', type=Path, help='Output HTML file (optional)')
    parser.add_argument('--theme-dir', type=Path, help='Custom theme directory')
    parser.add_argument('--metadata', type=Path, help='Output metadata JSON file (optional)')

    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    theme_path = None
    if args.theme_dir:
        theme_path = args.theme_dir / f"{args.theme}.json"
    else:
        script_dir = Path(__file__).parent.parent / "themes"
        theme_path = script_dir / f"{args.theme}.json"

    renderer = WeChatHTMLRenderer(theme_path if theme_path.exists() else None)
    metadata, html = renderer.render_file(args.input, args.output)

    if args.output:
        print(f"HTML saved to: {args.output}")

    if metadata:
        print(f"Metadata extracted: {metadata}")
        if args.metadata:
            with open(args.metadata, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            print(f"Metadata saved to: {args.metadata}")

    if not args.output:
        print(html)


if __name__ == "__main__":
    main()
