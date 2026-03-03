"""
HTML to Markdown converter for url-to-obsidian skill.

This module provides HTML to Markdown conversion using Readability
for content extraction and markdownify for conversion.
"""

import re
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

from bs4 import BeautifulSoup


MIN_CONTENT_LENGTH = 120
GOOD_CONTENT_LENGTH = 900

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
]

REMOVE_SELECTORS = [
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


def clean_html(html: str) -> str:
    """Clean HTML by removing unwanted elements.
    
    Args:
        html: Raw HTML content
        
    Returns:
        Cleaned HTML
    """
    soup = BeautifulSoup(html, "html.parser")
    
    for selector in REMOVE_SELECTORS:
        for element in soup.select(selector):
            element.decompose()
    
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


def extract_with_selector(html: str) -> Tuple[Optional[str], str]:
    """Extract content using CSS selectors.
    
    Args:
        html: Raw HTML content
        
    Returns:
        Tuple of (title, cleaned_html)
    """
    soup = BeautifulSoup(html, "html.parser")
    
    for selector in CONTENT_SELECTORS:
        elements = soup.select(selector)
        if elements:
            # For selectors that match multiple sections (like .sect1),
            # combine all matching elements
            if len(elements) > 1:
                combined_html = ""
                for element in elements:
                    for remove_selector in REMOVE_SELECTORS:
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
                for remove_selector in REMOVE_SELECTORS:
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


def html_to_markdown(html: str) -> str:
    """Convert HTML to Markdown.
    
    Args:
        html: HTML content
        
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
    cleaned = clean_html(html)
    
    markdown = md(
        cleaned,
        heading_style='ATX',
        strip=['script', 'style', 'iframe', 'noscript'],
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


def extract_content(html: str) -> dict:
    """Extract and convert content from HTML.
    
    Args:
        html: Raw HTML content
        
    Returns:
        Dictionary with title, description, author, published, markdown
    """
    title, content_html = extract_with_readability(html)
    
    # Try selector extraction and use it if it returns more content
    selector_title, selector_content = extract_with_selector(html)
    if selector_content:
        if not content_html or len(selector_content) > len(content_html):
            title = selector_title or title
            content_html = selector_content
    
    if not content_html:
        soup = BeautifulSoup(html, "html.parser")
        body = soup.find("body")
        if body:
            for selector in REMOVE_SELECTORS:
                for el in body.select(selector):
                    el.decompose()
            content_html = str(body)
    
    if not title:
        title = extract_title(html)
    
    description = extract_description(html)
    published = extract_published_time(html)
    
    markdown = html_to_markdown(content_html) if content_html else ""
    
    if not markdown.strip() and html:
        soup = BeautifulSoup(html, "html.parser")
        for selector in REMOVE_SELECTORS:
            for el in soup.select(selector):
                el.decompose()
        text = soup.get_text(separator='\n', strip=True)
        text = re.sub(r'\n{3,}', '\n\n', text)
        markdown = text
    
    return {
        "title": title or "Untitled",
        "description": description,
        "author": None,
        "published": published,
        "markdown": markdown
    }


def process_extracted_content(extracted: dict) -> dict:
    """Process extracted content from CDP client.
    
    Args:
        extracted: Dictionary from cdp_client.extract_page_content
        
    Returns:
        Dictionary with title, description, author, published, markdown, url
    """
    html = extracted.get("html", "")
    
    result = extract_content(html)
    
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
