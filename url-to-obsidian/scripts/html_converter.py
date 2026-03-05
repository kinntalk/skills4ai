"""
HTML to Markdown converter for url-to-obsidian skill.

This module provides HTML to Markdown conversion using Readability
for content extraction and markdownify for conversion.
"""

import re
import ipaddress
from typing import Optional, Tuple
from urllib.parse import urlparse

try:
    from readability import Document
except ImportError:
    print("readability-lxml not installed. Run: pip install readability-lxml")
    raise

try:
    from markdownify import markdownify as md
except ImportError:
    print("markdownify not installed. Run: pip install markdownify")
    raise

try:
    import html2text
except ImportError:
    print("html2text not installed. Run: pip install html2text")
    raise

from bs4 import BeautifulSoup


MIN_CONTENT_LENGTH = 120
GOOD_CONTENT_LENGTH = 900

DANGEROUS_TAGS = [
    'script', 'object', 'embed', 'applet', 'link',
    'meta', 'base', 'basefont', 'frame', 'frameset',
    'iframe', 'noframes', 'noscript', 'portal', 'svg'
]

DANGEROUS_ATTRS = [
    'onerror', 'onload', 'onclick', 'onmouseover', 'onmouseout',
    'onmousedown', 'onmouseup', 'onfocus', 'onblur', 'oninput',
    'onchange', 'onsubmit', 'onreset', 'onkeydown', 'onkeyup',
    'onkeypress', 'onanimationstart', 'onanimationend', 'onanimationiteration',
    'ontransitionend', 'ontouchstart', 'ontouchend', 'ontouchmove', 'ontouchcancel'
]

DANGEROUS_CSS_PROPS = [
    'expression', 'behavior', '-moz-binding', 'binding'
]

CONTENT_SELECTORS = [
    ".dw-doc-content",
    ".dw-main-content[role='content']",
    "article",
    "main article",
    "[role='main'] article",
    "[itemprop='articleBody']",
    ".article-content",
    ".article-body",
    ".post-content",
    ".entry-content",
    ".story-body",
    "main",
    "[role='main']",
    "#content",
    ".content",
    ".sect1",
    "#preamble",
    ".sectionbody",
    ".theme-doc-markdown",
    "article.markdown",
    ".theme-default-content",
    ".notion-page-content",
    ".postArticle-content",
    ".Post-RichText",
    ".article_body",
    "[class*='chat']",
    "[class*='message']",
    "[class*='conversation']",
    "[class*='dialog']",
    "[class*='thread']",
    "[class*='messages']",
    "[data-testid*='chat']",
    "[data-testid*='message']",
    "[data-testid*='conversation']",
    ".markdown-body",
    ".prose",
    ".chat-content",
    ".message-content",
    ".conversation-content",
]

DEFAULT_REMOVE_SELECTORS = [
    "script",
    "style",
    "noscript",
    "template",
    "iframe",
    "svg",
    "path",
    "nav",
    "aside",
    "footer",
    "header",
    "form",
    ".advertisement",
    ".ads",
    ".social-share",
    ".related-articles",
    ".comments",
    ".newsletter",
    ".cookie-banner",
    ".cookie-consent",
    "[role='navigation']",
    "[aria-label*='cookie' i]",
    ".copy",
    ".copy-button",
    "button.copy",
    ".btn-copy",
    "[data-copy]",
    ".code-actions",
    ".source-toolbox",
    ".code-copy-btn",
    "button.code-copy-btn",
    "pre button",
]


def validate_url(url: str) -> bool:
    """Validate URL to prevent SSRF attacks.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL is safe, False otherwise
    """
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        
        if parsed.scheme not in ('http', 'https'):
            return False
        
        hostname = parsed.hostname
        if not hostname:
            return False
        
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_reserved or ip.is_loopback:
                return False
        except ValueError:
            pass
        
        private_patterns = ['.local', '.intra', '.corp', '.internal', '.lan']
        if any(hostname.endswith(p) for p in private_patterns):
            return False
        
        if hostname.startswith('0.') or hostname.startswith('127.'):
            return False
        
        if hostname in ('localhost', 'localhost.localdomain'):
            return False
        
        return True
    except Exception:
        return False


def sanitize_html(html: str) -> str:
    """Sanitize HTML to prevent XSS attacks.
    
    Args:
        html: Raw HTML content
        
    Returns:
        Sanitized HTML
    """
    soup = BeautifulSoup(html, "html.parser")
    
    for tag in soup(DANGEROUS_TAGS):
        tag.decompose()
    
    for el in soup.find_all(True):
        attrs_to_remove = []
        for attr in list(el.attrs):
            if attr.lower().startswith('on') or attr.lower() in DANGEROUS_ATTRS:
                attrs_to_remove.append(attr)
        
        for attr in attrs_to_remove:
            del el[attr]
        
        if el.name == 'a' and el.get('href'):
            href = el['href'].lower().strip()
            if href.startswith('javascript:') or href.startswith('data:') or href.startswith('vbscript:'):
                if el.string:
                    el.replace_with(el.string)
                else:
                    el.unwrap()
        
        if el.get('style'):
            style = el['style'].lower()
            for dangerous_prop in DANGEROUS_CSS_PROPS:
                if dangerous_prop in style:
                    del el['style']
                    break
        
        for attr in ['src', 'href', 'data', 'action']:
            if el.get(attr):
                val = el[attr].lower()
                if 'javascript:' in val or 'data:' in val:
                    if attr == 'src' and el.name == 'img':
                        el.unwrap()
                    else:
                        del el[attr]
    
    return str(soup)


def clean_html(html: str, remove_selectors: Optional[list] = None) -> str:
    """Clean HTML by removing unwanted elements.
    
    Args:
        html: Raw HTML content
        remove_selectors: List of CSS selectors to remove
        
    Returns:
        Cleaned HTML
    """
    if remove_selectors is None:
        remove_selectors = DEFAULT_REMOVE_SELECTORS
    
    soup = BeautifulSoup(html, "html.parser")
    
    for selector in remove_selectors:
        for element in soup.select(selector):
            element.decompose()
    
    soup = BeautifulSoup(sanitize_html(str(soup)), "html.parser")
    
    for a in soup.find_all('a', href=True):
        if a['href'].strip().lower().startswith('javascript:'):
            del a['href']
    
    return str(soup)


def extract_with_readability(html: str) -> Tuple[Optional[str], str]:
    """Extract main content using Readability.
    
    Args:
        html: Raw HTML content
        
    Returns:
        Tuple of (title, cleaned_html)
    """
    try:
        doc = Document(html)
        title = doc.title()
        content = doc.summary()
        
        text = BeautifulSoup(content, "html.parser").get_text()
        if len(text.strip()) < MIN_CONTENT_LENGTH:
            return None, ""
        
        return title, content
    except Exception:
        return None, ""


def extract_with_selector(html: str, remove_selectors: Optional[list] = None) -> Tuple[Optional[str], str]:
    """Extract content using CSS selectors.
    
    Args:
        html: Raw HTML content
        remove_selectors: List of CSS selectors to remove
        
    Returns:
        Tuple of (title, cleaned_html)
    """
    if remove_selectors is None:
        remove_selectors = DEFAULT_REMOVE_SELECTORS
        
    soup = BeautifulSoup(html, "html.parser")
    
    for selector in CONTENT_SELECTORS:
        elements = soup.select(selector)
        if elements:
            # For selectors that match multiple sections (like .sect1),
            # combine all matching elements
            if len(elements) > 1:
                combined_html = ""
                for element in elements:
                    for remove_selector in remove_selectors:
                        for el in element.select(remove_selector):
                            el.decompose()
                    combined_html += str(element)
                
                text = BeautifulSoup(combined_html, "html.parser").get_text()
                if len(text.strip()) >= MIN_CONTENT_LENGTH:
                    title = soup.find("title")
                    title_text = title.get_text().strip() if title else None
                    return title_text, combined_html
            else:
                element = elements[0]
                for remove_selector in remove_selectors:
                    for el in element.select(remove_selector):
                        el.decompose()
                
                text = element.get_text()
                if len(text.strip()) >= MIN_CONTENT_LENGTH:
                    title = soup.find("title")
                    title_text = title.get_text().strip() if title else None
                    return title_text, str(element)
    
    return None, ""


def extract_title(html: str) -> Optional[str]:
    """Extract title from HTML.
    
    Args:
        html: Raw HTML content
        
    Returns:
        Title string or None
    """
    soup = BeautifulSoup(html, "html.parser")
    
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        return og_title["content"].strip()
    
    twitter_title = soup.find("meta", attrs={"name": "twitter:title"})
    if twitter_title and twitter_title.get("content"):
        return twitter_title["content"].strip()
    
    title_tag = soup.find("title")
    if title_tag:
        title = title_tag.get_text().strip()
        cleaned = re.split(r'\s*[-|–—]\s*', title)[0].strip()
        if cleaned:
            return cleaned
    
    h1 = soup.find("h1")
    if h1:
        return h1.get_text().strip()
    
    return None


def extract_description(html: str) -> Optional[str]:
    """Extract description from HTML.
    
    Args:
        html: Raw HTML content
        
    Returns:
        Description string or None
    """
    soup = BeautifulSoup(html, "html.parser")
    
    for attr in [("property", "og:description"), ("name", "description"), ("name", "twitter:description")]:
        meta = soup.find("meta", attrs={attr[0]: attr[1]})
        if meta and meta.get("content"):
            return meta["content"].strip()
    
    return None


def extract_published_time(html: str) -> Optional[str]:
    """Extract published time from HTML.
    
    Args:
        html: Raw HTML content
        
    Returns:
        Published time string or None
    """
    soup = BeautifulSoup(html, "html.parser")
    
    selectors = [
        ("meta", {"property": "article:published_time"}),
        ("meta", {"name": "pubdate"}),
        ("meta", {"name": "publishdate"}),
        ("meta", {"name": "date"}),
    ]
    
    for tag, attrs in selectors:
        meta = soup.find(tag, attrs)
        if meta and meta.get("content"):
            return meta["content"].strip()
    
    time_el = soup.find("time")
    if time_el and time_el.get("datetime"):
        return time_el["datetime"].strip()
    
    return None


def convert_admonition_to_callout(html: str) -> str:
    """Convert Asciidoctor admonition blocks to Obsidian callouts.
    
    Asciidoctor uses:
    <div class="admonitionblock note">
      <table>
        <tbody>
          <tr>
            <td class="icon"><i class="fa icon-note" title="Note"></i></td>
            <td class="content">Content here</td>
          </tr>
        </tbody>
      </table>
    </div>
    
    Obsidian callout format:
    > [!note]
    > Content here
    
    Args:
        html: HTML content
        
    Returns:
        HTML with admonitions converted to callout-friendly format
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    admonition_map = {
        'note': 'note',
        'tip': 'tip',
        'warning': 'warning',
        'caution': 'warning',
        'important': 'important',
        'attention': 'warning',
        'hint': 'tip',
    }
    
    for adm in soup.select('.admonitionblock'):
        classes = adm.get('class', [])
        adm_type = 'note'
        for c in classes:
            if c in admonition_map:
                adm_type = admonition_map[c]
                break
        
        content_td = adm.select_one('.content')
        if content_td:
            content = content_td.get_text(strip=True)
            
            callout_div = soup.new_tag('div')
            callout_div['class'] = 'obsidian-callout'
            callout_div['data-type'] = adm_type
            callout_div.string = content
            
            adm.replace_with(callout_div)
    
    return str(soup)


def html_to_markdown_html2text(html: str) -> str:
    """Convert HTML to Markdown using html2text.
    
    This function is optimized for Tabbit chat pages and provides
    better conversion quality for complex HTML structures.
    
    Args:
        html: HTML content
        
    Returns:
        Markdown content
    """
    h = html2text.HTML2Text()
    
    # Configure html2text for better conversion quality
    h.ignore_links = False  # Preserve links
    h.ignore_images = False  # Preserve images
    h.ignore_emphasis = False  # Preserve emphasis
    h.body_width = 0  # Don't wrap lines
    h.unicode_snob = True  # Use Unicode characters
    h.skip_internal_links = False  # Keep all links
    h.inline_links = True  # Use inline links
    h.protect_links = True  # Protect links from line wrapping
    h.wrap_links = False  # Don't wrap links
    h.pad_tables = True  # Pad tables for better readability
    h.default_image_alt = ''  # Default alt text for images
    h.ignore_tables = False  # Convert tables
    h.ignore_images = False  # Convert images
    h.images_as_html = False  # Use Markdown image syntax
    h.images_to_alt = False  # Use alt text for images
    h.single_line_break = False  # Use two line breaks for paragraphs
    h.ul_item_mark = '-'  # Use - for unordered lists
    h.emphasis_mark = '*'  # Use * for emphasis
    h.strong_mark = '**'  # Use ** for strong
    
    # Convert HTML to Markdown
    markdown = h.handle(html)
    
    # Clean up excessive newlines
    markdown = re.sub(r'\n{3,}', '\n\n', markdown)
    
    return markdown.strip()


def html_to_markdown(html: str, remove_selectors: Optional[list] = None) -> str:
    """Convert HTML to Markdown.
    
    Args:
        html: HTML content
        remove_selectors: List of CSS selectors to remove
        
    Returns:
        Markdown content
    """
    html = convert_admonition_to_callout(html)
    
    soup = BeautifulSoup(html, 'html.parser')
    for callout in soup.select('.obsidian-callout'):
        callout_type = callout.get('data-type', 'note')
        callout_text = callout.get_text(strip=True)
        callout.replace_with(BeautifulSoup(f'\n> [!{callout_type}]\n> {callout_text}\n', 'html.parser'))
    
    html = str(soup)
    cleaned = clean_html(html, remove_selectors)
    
    markdown = md(
        cleaned,
        heading_style='ATX',
        strip=['script', 'style', 'iframe', 'noscript', 'link'],
        bullets='-',
        escape_asterisks=False,
        escape_underscores=False,
        escape_misc=False
    )
    
    return normalize_markdown(markdown)


def normalize_markdown(markdown: str) -> str:
    """Normalize Markdown content.
    
    Args:
        markdown: Raw Markdown content
        
    Returns:
        Normalized Markdown
    """
    markdown = re.sub(r'\r\n', '\n', markdown)
    markdown = re.sub(r'[ \t]+\n', '\n', markdown)
    markdown = re.sub(r'\n{3,}', '\n\n', markdown)
    
    return markdown.strip()


def format_text_content(text: str) -> str:
    """Format text content for better readability and structure.
    
    Args:
        text: Raw text content
        
    Returns:
        Formatted markdown content
    """
    if not text:
        return ""
    
    # Strip leading/trailing whitespace and normalize multiple newlines
    text = text.strip()
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text


def extract_content(html: str, remove_selectors: Optional[list] = None, text_content: Optional[str] = None, is_tabbit_chat: bool = False) -> dict:
    """Extract and convert content from HTML.
    
    Args:
        html: Raw HTML content
        remove_selectors: List of CSS selectors to remove
        text_content: Optional pre-extracted text content
        is_tabbit_chat: Whether this is a Tabbit chat page
        
    Returns:
        Dictionary with title, description, author, published, markdown
    """
    soup = BeautifulSoup(html, "html.parser")
    
    # Extract title
    title = extract_title(html)
    
    # Extract description
    description = extract_description(html)
    
    # Extract published time
    published = extract_published_time(html)
    
    markdown = ""
    
    if is_tabbit_chat:
        # For Tabbit chat pages, use html2text for better conversion quality
        print(f"[DEBUG] Converting HTML to Markdown using html2text for Tabbit chat page")
        markdown = html_to_markdown_html2text(html)
        print(f"[DEBUG] Markdown length: {len(markdown)}")
        
        # If html2text didn't produce good results, fall back to text_content
        if len(markdown.strip()) < 100 and text_content and len(text_content.strip()) > 50:
            print(f"[DEBUG] html2text produced insufficient content, falling back to text_content")
            markdown = format_text_content(text_content)
            print(f"[DEBUG] Formatted markdown length: {len(markdown)}")
    else:
        # For other pages, use the original logic
        if remove_selectors is None:
            remove_selectors = DEFAULT_REMOVE_SELECTORS
        
        # Strategy 1: Try selector-based extraction (preserves structure)
        for selector in CONTENT_SELECTORS:
            elements = soup.select(selector)
            if elements:
                combined_html = ""
                for element in elements:
                    for remove_selector in remove_selectors:
                        for el in element.select(remove_selector):
                            el.decompose()
                    combined_html += str(element)
                
                # Use html_to_markdown to preserve structure
                markdown = html_to_markdown(combined_html, remove_selectors)
                
                # Check if we got meaningful content
                if markdown and len(markdown.strip()) >= 100:
                    break
        
        # Strategy 2: If selector extraction failed, try Readability
        if not markdown or len(markdown.strip()) < 100:
            readability_title, content_html = extract_with_readability(html)
            if content_html:
                markdown = html_to_markdown(content_html, remove_selectors)
        
        # Strategy 3: If still no content, extract from body
        if not markdown or len(markdown.strip()) < 100:
            body = soup.find("body")
            if body:
                for selector in remove_selectors:
                    for el in body.select(selector):
                        el.decompose()
                
                main_content = body.find("main") or body.find("[role='main']")
                if main_content:
                    markdown = html_to_markdown(str(main_content), remove_selectors)
                else:
                    markdown = html_to_markdown(str(body), remove_selectors)
    
    return {
        "title": title or "Untitled",
        "description": description,
        "author": None,
        "published": published,
        "markdown": markdown
    }


def process_extracted_content(extracted: dict, remove_selectors: Optional[list] = None) -> dict:
    """Process extracted content from CDP client.
    
    Args:
        extracted: Dictionary from cdp_client.extract_page_content
        remove_selectors: List of CSS selectors to remove
        
    Returns:
        Dictionary with title, description, author, published, markdown, url
    """
    html = extracted.get("html", "")
    
    # For Tabbit chat pages, don't use remove selectors to preserve all chat content
    is_tabbit_chat = extracted.get("is_tabbit_chat", False)
    if is_tabbit_chat:
        remove_selectors = None
    
    # Get text content if available
    text_content = extracted.get("text_content")
    
    # Debug: print extracted content info
    print(f"[DEBUG] is_tabbit_chat: {is_tabbit_chat}")
    print(f"[DEBUG] text_content length: {len(text_content) if text_content else 0}")
    if text_content:
        print(f"[DEBUG] text_content first 200 chars: {text_content[:200]}")
    
    result = extract_content(html, remove_selectors, text_content, is_tabbit_chat)
    
    if extracted.get("title"):
        result["title"] = extracted["title"]
    
    if extracted.get("description"):
        result["description"] = extracted["description"]
    
    if extracted.get("author"):
        result["author"] = extracted["author"]
    
    if extracted.get("published"):
        result["published"] = extracted["published"]
    
    result["url"] = extracted.get("url", "")
    
    return result


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="HTML to Markdown converter")
    parser.add_argument("input", help="Input HTML file")
    parser.add_argument("-o", "--output", help="Output Markdown file")
    
    args = parser.parse_args()
    
    with open(args.input, "r", encoding="utf-8") as f:
        html = f.read()
    
    result = extract_content(html)
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result["markdown"])
        print(f"Written to {args.output}")
    else:
        print(f"Title: {result['title']}")
        print(f"Description: {result['description']}")
        print(f"\n{result['markdown'][:500]}...")
