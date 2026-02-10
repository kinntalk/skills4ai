#!/usr/bin/env python3
"""
Generate Image from Markdown
Converts a Markdown file to a PNG/JPG image using HTML rendering and browser screenshot.
"""

import sys
import os
import argparse
import tempfile
import markdown
from pathlib import Path
from html2image import Html2Image

# Default CSS for GitHub-like styling
DEFAULT_CSS = """
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
    font-size: 16px;
    line-height: 1.5;
    word-wrap: break-word;
    color: #24292e;
    background-color: #ffffff;
    margin: 0;
    padding: 40px;
    max-width: 800px; /* Constrain width for better readability in image */
    margin: 0 auto;
}

h1, h2, h3, h4, h5, h6 {
    margin-top: 24px;
    margin-bottom: 16px;
    font-weight: 600;
    line-height: 1.25;
}

h1 { font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
h2 { font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
h3 { font-size: 1.25em; }

p { margin-top: 0; margin-bottom: 16px; }

code {
    padding: 0.2em 0.4em;
    margin: 0;
    font-size: 85%;
    background-color: #f6f8fa;
    border-radius: 6px;
    font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
}

pre {
    padding: 16px;
    overflow: auto;
    font-size: 85%;
    line-height: 1.45;
    background-color: #f6f8fa;
    border-radius: 6px;
    margin-bottom: 16px;
}

pre code {
    display: inline;
    padding: 0;
    margin: 0;
    overflow: visible;
    line-height: inherit;
    word-wrap: normal;
    background-color: transparent;
    border: 0;
}

blockquote {
    padding: 0 1em;
    color: #6a737d;
    border-left: 0.25em solid #dfe2e5;
    margin: 0 0 16px 0;
}

ul, ol { padding-left: 2em; margin-bottom: 16px; }

table {
    border-spacing: 0;
    border-collapse: collapse;
    margin-bottom: 16px;
    width: 100%;
}

table th, table td {
    padding: 6px 13px;
    border: 1px solid #dfe2e5;
}

table tr:nth-child(2n) { background-color: #f6f8fa; }

img { max-width: 100%; box-sizing: content-box; background-color: #fff; }

hr {
    height: 0.25em;
    padding: 0;
    margin: 24px 0;
    background-color: #e1e4e8;
    border: 0;
}
"""

def generate_image(input_file, output_file, width=880):
    input_path = Path(input_file)
    output_path = Path(output_file)
    
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' not found.")
        sys.exit(1)

    # Read Markdown content
    try:
        md_content = input_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)

    # Convert Markdown to HTML
    # Extensions: extra (tables, etc.), codehilite (syntax highlighting)
    html_body = markdown.markdown(md_content, extensions=['extra', 'codehilite', 'nl2br'])
    
    # Wrap in complete HTML
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            {DEFAULT_CSS}
            /* Override body width if needed, or let html2image handle viewport */
            body {{ width: {width}px; max-width: none; }}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """

    print(f"Generating image from {input_path.name}...")
    
    import uuid
    import shutil
    import time
    import base64

    # Initialize Html2Image
    # We specify output path to current directory to ensure we find the image
    hti = Html2Image(output_path=str(output_path.parent))
    
    # Use Data URI scheme to pass HTML content directly to the browser
    # This avoids all file system related issues (permissions, encoding, race conditions, file not found errors)
    # Especially important on Windows where file:/// paths with non-ASCII characters often fail in headless browsers
    html_base64 = base64.b64encode(full_html.encode('utf-8')).decode('utf-8')
    data_uri = f"data:text/html;charset=utf-8;base64,{html_base64}"
    
    # Use a safe temporary filename for the image output
    # Using UUID ensures ASCII-only path for the browser to write to
    temp_img_name = f"render_{uuid.uuid4().hex}.png"
    temp_img_path = output_path.parent / temp_img_name
    
    # Generate image
    try:
        generated_files = hti.screenshot(
            url=data_uri,
            save_as=temp_img_name,
            size=(width + 100, 2000) 
        )
        
        # Verify and Rename
        src_file = None
        
        # Wait for file to appear (async filesystem delay mitigation)
        # Browser might report success before file system lock is released or file is fully flushed
        for i in range(10):
            if temp_img_path.exists():
                src_file = temp_img_path
                break
            elif generated_files and Path(generated_files[0]).exists():
                src_file = Path(generated_files[0])
                break
            time.sleep(0.5)
        
        if src_file:
             # Move/Rename to final destination (Python handles Unicode paths correctly)
             if output_path.exists():
                 try:
                    output_path.unlink() # Overwrite existing
                 except PermissionError:
                    print(f"Error: Could not delete existing file {output_path}. Is it open?")
                    sys.exit(1)
             
             src_file.rename(output_path)
             print(f"✅ Image saved to: {output_path}")
        else:
             print(f"❌ Error: Temporary image file not found.")
             print(f"Expected at: {temp_img_path}")
             print(f"Library reported: {generated_files}")

    except Exception as e:
        print(f"Error generating image: {e}")
        print("Ensure you have a web browser (Chrome, Edge, or Chromium) installed.")
        # Only print traceback in verbose mode if we had one, keeping clean for now
        # import traceback
        # traceback.print_exc()

def main():
    parser = argparse.ArgumentParser(description="Convert Markdown to Image")
    parser.add_argument("input_file", help="Path to input markdown file")
    parser.add_argument("-o", "--output", help="Path to output image file (default: input_filename.png)")
    parser.add_argument("--width", type=int, default=800, help="Image width in pixels (default: 800)")
    
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_suffix('.png')
        
    generate_image(args.input_file, output_path, args.width)

if __name__ == "__main__":
    main()
