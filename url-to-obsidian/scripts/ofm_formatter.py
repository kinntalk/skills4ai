"""
Obsidian Flavored Markdown formatter module.

Handles conversion of markdown content to Obsidian Flavored Markdown format,
including YAML frontmatter, wikilinks, callouts, and tags.
"""

import re
from datetime import datetime
from typing import Optional, List, Tuple, Dict
from pathlib import Path
from urllib.parse import urlparse


def clean_html_tags(content: str) -> str:
    """Clean HTML tags from markdown content.
    
    Converts common HTML elements to markdown equivalents and removes
    unnecessary HTML tags.
    
    Note: Tables are handled by markdownify in html_converter.py,
    so we don't process table tags here to preserve table structure.
    
    Note: Code blocks are protected to preserve their content.
    
    Args:
        content: Markdown content with HTML tags
        
    Returns:
        Cleaned markdown content
    """
    code_blocks = []
    def save_code_block(match):
        code_blocks.append(match.group(0))
        return f'__CODE_BLOCK_{len(code_blocks)-1}__'
    
    content = re.sub(r'```[\s\S]*?```', save_code_block, content)
    
    content = re.sub(
        r'<div class="obsidian-callout" data-type="([^"]+)"[^>]*>([^<]+)</div>',
        lambda m: f'> [!{m.group(1)}]\n> {m.group(2)}',
        content
    )
    
    content = re.sub(r'<i[^>]*title="([^"]*)"[^>]*></i>', r'> [!note] \1\n>', content)
    content = re.sub(r'<i[^>]*>([^<]*)</i>', r'*\1*', content)
    content = re.sub(r'<b[^>]*>([^<]*)</b>', r'**\1**', content)
    content = re.sub(r'<strong[^>]*>([^<]*)</strong>', r'**\1**', content)
    content = re.sub(r'<em[^>]*>([^<]*)</em>', r'*\1*', content)
    content = re.sub(r'<code[^>]*>([^<]*)</code>', r'`\1`', content)
    content = re.sub(r'<pre[^>]*>([^<]*)</pre>', r'\n```\n\1\n```\n', content)
    content = re.sub(r'<br\s*/?>', '\n', content)
    content = re.sub(r'<hr\s*/?>', '\n---\n', content)
    content = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>([^<]*)</a>', r'[\2](\1)', content)
    content = re.sub(r'<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*/?>', r'![\2](\1)', content)
    content = re.sub(r'<[^>]+>', '', content)
    content = re.sub(r'\n{3,}', '\n\n', content)
    content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
    content = re.sub(r'^\s*\|\s*$', '', content, flags=re.MULTILINE)
    
    content = re.sub(r'^Copy\s*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'(\S)Copy$', r'\1', content, flags=re.MULTILINE)
    content = re.sub(r'Copy(\s*__CODE_BLOCK_)', r'\1', content)
    
    for i, block in enumerate(code_blocks):
        content = content.replace(f'__CODE_BLOCK_{i}__', block)
    
    return content.strip()


def sanitize_filename(title: str, max_length: int = 100) -> str:
    """Sanitize a title for use as a filename.
    
    Args:
        title: Title string to sanitize
        max_length: Maximum filename length
        
    Returns:
        Sanitized filename
    """
    if not title:
        return "untitled"
    
    sanitized = re.sub(r'[<>:"/\\|?*]', '-', title)
    sanitized = re.sub(r'\s+', '-', sanitized)
    sanitized = re.sub(r'-+', '-', sanitized)
    sanitized = sanitized.strip('-_')
    
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.lower() or "untitled"


def extract_title(content: str, url: Optional[str] = None) -> str:
    """Extract title from markdown content.
    
    Args:
        content: Markdown content
        url: Source URL for fallback
        
    Returns:
        Extracted title
    """
    h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if h1_match:
        title = h1_match.group(1).strip()
        title = re.sub(r'^#+\s*', '', title)
        return title
    
    title_match = re.search(r'^title:\s*(.+)$', content, re.MULTILINE)
    if title_match:
        return title_match.group(1).strip()
    
    first_line = content.split('\n')[0].strip()
    if first_line and len(first_line) < 100:
        return first_line
    
    if url:
        path = urlparse(url).path
        slug = path.rstrip('/').split('/')[-1]
        if slug:
            return slug.replace('-', ' ').replace('_', ' ').title()
    
    return "Untitled"


def generate_frontmatter(
    title: str,
    url: str,
    tags: Optional[List[str]] = None,
    date: Optional[datetime] = None,
    extra: Optional[dict] = None
) -> str:
    """Generate YAML frontmatter for Obsidian note.
    
    Args:
        title: Note title
        url: Source URL
        tags: List of tags
        date: Creation date
        extra: Extra frontmatter fields
        
    Returns:
        YAML frontmatter string
    """
    if date is None:
        date = datetime.now()
    
    if tags is None:
        tags = ["web-clipping"]
    
    frontmatter = "---\n"
    frontmatter += f"title: {title}\n"
    frontmatter += f"date: {date.strftime('%Y-%m-%d')}\n"
    frontmatter += f"source: {url}\n"
    
    if tags:
        frontmatter += "tags:\n"
        for tag in tags:
            tag = tag.strip().lower().replace(' ', '-')
            if tag and not tag.startswith('#'):
                frontmatter += f"  - {tag}\n"
            elif tag:
                frontmatter += f"  - {tag[1:]}\n"
    
    if extra:
        for key, value in extra.items():
            if isinstance(value, str):
                frontmatter += f"{key}: {value}\n"
            elif isinstance(value, list):
                frontmatter += f"{key}:\n"
                for item in value:
                    frontmatter += f"  - {item}\n"
            else:
                frontmatter += f"{key}: {value}\n"
    
    frontmatter += "---\n"
    
    return frontmatter


def add_source_callout(url: str, date: datetime) -> str:
    """Add source information callout.
    
    Args:
        url: Source URL
        date: Capture date
        
    Returns:
        Callout string
    """
    return f"""> [!info] Source
> This note was created from [original page]({url}) on {date.strftime('%Y-%m-%d')}.\n"""


def convert_links_to_wikilinks(content: str) -> str:
    """Convert markdown links to Obsidian wikilinks where appropriate.
    
    This function converts internal reference links to wikilink format
    while preserving external links.
    
    Args:
        content: Markdown content
        
    Returns:
        Content with wikilinks where appropriate
    """
    def replace_link(match):
        text = match.group(1)
        url = match.group(2)
        
        if url.startswith('http://') or url.startswith('https://'):
            return match.group(0)
        
        if url.endswith('.md'):
            note_name = url[:-3]
            return f"[[{note_name}|{text}]]"
        
        return match.group(0)
    
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    return re.sub(pattern, replace_link, content)


def convert_highlights(content: str) -> str:
    """Convert ==highlight== syntax to Obsidian format.
    
    Args:
        content: Markdown content
        
    Returns:
        Content with Obsidian highlights
    """
    return content


def add_callouts_for_notes(content: str) -> str:
    """Convert note/tip/warning paragraphs to callouts.
    
    Args:
        content: Markdown content
        
    Returns:
        Content with callouts
    """
    patterns = [
        (r'^Note:\s*(.+)$', r'> [!note]\n> \1'),
        (r'^Tip:\s*(.+)$', r'> [!tip]\n> \1'),
        (r'^Warning:\s*(.+)$', r'> [!warning]\n> \1'),
        (r'^Important:\s*(.+)$', r'> [!important]\n> \1'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    return content


def format_ofm(
    content: str,
    url: str,
    title: Optional[str] = None,
    tags: Optional[List[str]] = None,
    add_source_info: bool = True,
    add_frontmatter: bool = True,
    clean_html: bool = True
) -> str:
    """Format markdown content as Obsidian Flavored Markdown.
    
    Args:
        content: Markdown content
        url: Source URL
        title: Note title (extracted if not provided)
        tags: List of tags
        add_source_info: Whether to add source callout
        add_frontmatter: Whether to add YAML frontmatter
        clean_html: Whether to clean HTML tags
        
    Returns:
        OFM formatted content
    """
    date = datetime.now()
    
    if title is None:
        title = extract_title(content, url)
    
    if clean_html:
        content = clean_html_tags(content)
    
    content = convert_highlights(content)
    content = add_callouts_for_notes(content)
    
    output = ""
    
    if add_frontmatter:
        output += generate_frontmatter(title, url, tags, date)
        output += "\n"
    
    h1_pattern = r'^#\s+.+$'
    if not re.search(h1_pattern, content, re.MULTILINE):
        output += f"# {title}\n\n"
    
    if add_source_info:
        output += add_source_callout(url, date)
        output += "\n"
    
    content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
    content = re.sub(r'^#\s+.+\n', '', content, count=1)
    
    output += content.strip()
    
    if not output.endswith('\n'):
        output += '\n'
    
    return output


def generate_filename(title: str, date: Optional[datetime] = None) -> str:
    """Generate a filename for the note.
    
    Args:
        title: Note title
        date: Date for the filename
        
    Returns:
        Filename with .md extension
    """
    if date is None:
        date = datetime.now()
    
    sanitized = sanitize_filename(title)
    date_str = date.strftime('%Y-%m-%d')
    
    return f"{sanitized}-{date_str}.md"


def extract_image_urls(content: str) -> List[Tuple[str, str, str]]:
    """Extract all image URLs from markdown content.
    
    Supports both markdown image syntax ![alt](url) and HTML <img> tags.
    
    Args:
        content: Markdown content to parse
        
    Returns:
        List of tuples (alt_text, url, full_match) for each image found
    """
    images = []
    
    md_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    for match in re.finditer(md_pattern, content):
        alt_text = match.group(1)
        url = match.group(2)
        full_match = match.group(0)
        images.append((alt_text, url, full_match))
    
    html_pattern = r'<img[^>]*src="([^"]+)"[^>]*alt="([^"]*)"[^>]*/?>'
    for match in re.finditer(html_pattern, content):
        url = match.group(1)
        alt_text = match.group(2)
        full_match = match.group(0)
        images.append((alt_text, url, full_match))
    
    html_pattern_no_alt = r'<img[^>]*src="([^"]+)"[^>]*/?>(?![^<]*alt="[^"]*")'
    for match in re.finditer(html_pattern_no_alt, content):
        url = match.group(1)
        full_match = match.group(0)
        if not any(img[1] == url for img in images):
            images.append(("", url, full_match))
    
    return images


def convert_image_links(
    content: str,
    url_mapping: Dict[str, str],
    use_wikilink: bool = False
) -> str:
    """Convert image links to new paths based on URL mapping.
    
    Args:
        content: Markdown content with image links
        url_mapping: Dictionary mapping original URLs to new paths
        use_wikilink: If True, use Obsidian wikilink format ![[filename|alt]]
                     If False, use relative path format ![alt](assets/filename)
        
    Returns:
        Content with converted image links
    """
    def replace_md_image(match):
        alt_text = match.group(1)
        url = match.group(2)
        
        if url not in url_mapping:
            return match.group(0)
        
        new_path = url_mapping[url]
        
        if use_wikilink:
            filename = Path(new_path).name
            if alt_text:
                return f"![[{filename}|{alt_text}]]"
            else:
                return f"![[{filename}]]"
        else:
            return f"![{alt_text}]({new_path})"
    
    md_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    content = re.sub(md_pattern, replace_md_image, content)
    
    def replace_html_image(match):
        full_match = match.group(0)
        src_match = re.search(r'src="([^"]+)"', full_match)
        
        if not src_match:
            return full_match
        
        url = src_match.group(1)
        
        if url not in url_mapping:
            return full_match
        
        new_path = url_mapping[url]
        alt_match = re.search(r'alt="([^"]*)"', full_match)
        alt_text = alt_match.group(1) if alt_match else ""
        
        if use_wikilink:
            filename = Path(new_path).name
            if alt_text:
                return f"![[{filename}|{alt_text}]]"
            else:
                return f"![[{filename}]]"
        else:
            return f"![{alt_text}]({new_path})"
    
    html_pattern = r'<img[^>]*src="[^"]+"[^>]*/?>'
    content = re.sub(html_pattern, replace_html_image, content)
    
    return content


def process_images_in_markdown(
    content: str,
    asset_handler,
    vault_path: Path,
    note_title: str,
    use_wikilink: bool = False
) -> Tuple[str, List[str]]:
    """Process all images in markdown content.
    
    Downloads images using the asset handler and converts image links
    to reference the downloaded files.
    
    Args:
        content: Markdown content with image links
        asset_handler: Asset handler object with download_asset method
                      that takes (url, vault_path, note_title) and returns
                      (local_path, filename) or None on failure
        vault_path: Path to the Obsidian vault
        note_title: Title of the note (used for organizing assets)
        use_wikilink: If True, use Obsidian wikilink format for images
        
    Returns:
        Tuple of (processed_content, list_of_downloaded_files)
    """
    images = extract_image_urls(content)
    
    if not images:
        return content, []
    
    url_mapping: Dict[str, str] = {}
    downloaded_files: List[str] = []
    
    for alt_text, url, full_match in images:
        if url in url_mapping:
            continue
        
        if url.startswith('data:'):
            continue
        
        result = asset_handler.download_asset(url, vault_path, note_title)
        
        if result:
            local_path, filename = result
            url_mapping[url] = local_path
            downloaded_files.append(filename)
    
    if url_mapping:
        content = convert_image_links(content, url_mapping, use_wikilink)
    
    return content, downloaded_files


if __name__ == "__main__":
    test_content = """
# Test Article

This is a test article with some content.

Note: This is an important note.

Tip: This is a helpful tip.

## Section 1

Some content here.

## Section 2

More content here.
"""
    
    formatted = format_ofm(
        test_content,
        url="https://example.com/test-article",
        tags=["test", "example"]
    )
    
    print(formatted)
    print("\nFilename:", generate_filename("Test Article"))
