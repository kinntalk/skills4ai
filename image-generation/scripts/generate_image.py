#!/usr/bin/env python3
"""
Generate Image from Markdown
Converts a Markdown file to a PNG/JPG image using HTML rendering and browser screenshot.
"""

import sys
import os
import argparse
import markdown
import logging
from pathlib import Path
from html2image import Html2Image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('generate_image.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_themes_dir():
    return Path(__file__).parent.parent / 'themes'

def print_error(error_msg, suggestions=None, exit_code=None):
    """Print error message with optional suggestions and optionally exit."""
    logger.error(error_msg)
    print(error_msg)
    if suggestions:
        print(f"\n建议:")
        for suggestion in suggestions:
            print(f"  - {suggestion}")
    if exit_code is not None:
        sys.exit(exit_code)
    return False

def load_theme(theme_name='github'):
    """Load CSS theme from file."""
    themes_dir = get_themes_dir()
    theme_file = themes_dir / f'{theme_name}.css'
    
    if not theme_file.exists():
        available_themes = [f.stem for f in themes_dir.glob('*.css')] if themes_dir.exists() else []
        logger.warning(f"Theme '{theme_name}' not found at {theme_file}. Available: {available_themes}")
        return ""
    
    try:
        css_content = theme_file.read_text(encoding='utf-8', errors='replace')
        return css_content
    except UnicodeDecodeError as e:
        logger.error(f"Theme file encoding error: {e}")
        return ""
    except (IOError, OSError) as e:
        logger.error(f"Error loading theme file: {e}")
        return ""

def validate_input_file(input_path):
    """Validate input file existence and readability."""
    if not input_path.exists():
        return print_error(
            f"Input file '{input_path}' does not exist",
            ["Check if file path is correct", "Verify filename spelling", "Use absolute or relative path"]
        )
    
    if not input_path.is_file():
        return print_error(
            f"'{input_path}' is not a valid file",
            ["Ensure path points to a file, not a directory"]
        )
    
    if not os.access(input_path, os.R_OK):
        return print_error(
            f"Cannot read file '{input_path}' (insufficient permissions)",
            ["Check file permissions", "Ensure you have read access", "Try running with elevated privileges"]
        )
    
    try:
        with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
            f.read(1)
    except (IOError, OSError, PermissionError) as e:
        print_error(
            f"Error reading file '{input_path}': {e}",
            ["File may be in use by another program", "Check if file is corrupted", "Close programs using the file"],
            exit_code=1
        )
    except UnicodeDecodeError as e:
        print_error(
            f"Error reading file '{input_path}': {e}",
            ["File may have encoding issues", "Ensure file is saved with UTF-8 encoding", "Check for special characters"],
            exit_code=1
        )
    except (ValueError, TypeError, RuntimeError) as e:
        print_error(
            f"Error reading file '{input_path}': {e}",
            ["Markdown content may be invalid", "Check Markdown syntax", "Ensure markdown library is installed"],
            exit_code=1
        )
    
    return True

def validate_output_directory(output_path):
    """Validate output directory writability."""
    output_dir = output_path.parent
    
    if not output_dir.exists():
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except (IOError, OSError, PermissionError) as e:
            return print_error(
                f"Cannot create output directory '{output_dir}': {e}",
                ["Check parent directory write permissions", "Try a different output path", "Use current directory as output location"],
                exit_code=1
            )
    
    if not os.access(output_dir, os.W_OK):
        return print_error(
            f"Cannot write to output directory '{output_dir}' (insufficient permissions)",
            ["Check directory permissions", "Ensure you have write access", "Try running as administrator"],
            exit_code=1
        )
    
    if output_path.exists() and not os.access(output_path, os.W_OK):
        return print_error(
            f"Cannot overwrite existing file '{output_path}' (insufficient permissions)",
            ["File may be open in another program", "Close programs using the file", "Try a different output filename"],
            exit_code=1
        )
    
    return True

def generate_image(input_file, output_file, width=880, quality=95, theme='github'):
    input_path = Path(input_file)
    output_path = Path(output_file)
    
    logger.info(f"Starting image generation: {input_path} -> {output_path}")
    
    # Validate input file
    if not validate_input_file(input_path):
        sys.exit(1)
    
    # Validate output directory
    if not validate_output_directory(output_path):
        sys.exit(1)

    # Read Markdown content
    try:
        md_content = input_path.read_text(encoding='utf-8', errors='replace')
    except UnicodeDecodeError as e:
        print_error(
            f"File encoding error: cannot read file with UTF-8 encoding",
            ["Ensure file is saved with UTF-8 encoding", "Check for special characters", "Convert file to UTF-8 encoding"],
            exit_code=1
        )
    except (IOError, OSError) as e:
        print_error(
            f"Error reading input file: {e}",
            ["File may be in use by another program", "Check if file is corrupted", "Check log file for details: generate_image.log"],
            exit_code=1
        )

    # Load theme CSS
    theme_css = load_theme(theme)

    # Convert Markdown to HTML
    try:
        html_body = markdown.markdown(md_content, extensions=['extra', 'codehilite', 'nl2br'])
    except (ValueError, TypeError) as e:
        print_error(
            f"Markdown conversion failed: {e}",
            ["Check Markdown syntax", "Ensure markdown library is installed", "Check log file for details: generate_image.log"],
            exit_code=1
        )
    
    # Wrap in complete HTML
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            {theme_css}
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
    import time
    import base64

    # Initialize Html2Image
    try:
        hti = Html2Image(output_path=str(output_path.parent))
    except (ValueError, RuntimeError, ImportError) as e:
        print_error(
            f"Failed to initialize Html2Image: {e}",
            ["Ensure html2image library is installed: pip install html2image", "Check if browser is installed (Chrome, Edge, or Chromium)", "Check log file for details: generate_image.log"],
            exit_code=1
        )
    
    # Use Data URI scheme to pass HTML content directly to the browser
    try:
        html_base64 = base64.b64encode(full_html.encode('utf-8')).decode('utf-8')
        data_uri = f"data:text/html;charset=utf-8;base64,{html_base64}"
    except (ValueError, UnicodeEncodeError) as e:
        print_error(
            f"HTML encoding failed: {e}",
            ["Check HTML content for invalid characters", "Check log file for details: generate_image.log"],
            exit_code=1
        )
    
    # Use a safe temporary filename for the image output
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
        
        # Wait for file to appear with timeout
        max_attempts = 10
        for i in range(max_attempts):
            if temp_img_path.exists():
                src_file = temp_img_path
                break
            elif generated_files and Path(generated_files[0]).exists():
                src_file = Path(generated_files[0])
                break
            time.sleep(0.5)
        
        # Check if file was found
        if src_file is None:
            print_error(
                f"Image generation failed: temporary file not created after {max_attempts} attempts",
                ["Check if browser is properly installed", "Ensure html2image library is installed", "Check log file for details: generate_image.log"],
                exit_code=1
            )
        
        # Move/Rename to final destination
        if src_file:
             # Move/Rename to final destination
             if output_path.exists():
                 try:
                    output_path.unlink()
                 except PermissionError as e:
                    print_error(
                        f"Cannot delete existing file {output_path}",
                        ["Close programs using the file", "Try a different output filename", "Check if file is open in image viewer"],
                        exit_code=1
                    )
                 except (IOError, OSError) as e:
                    print_error(
                        f"Error deleting file: {e}",
                        ["Check file permissions", "Check log file for details: generate_image.log"],
                        exit_code=1
                    )
             
             try:
                 src_file.rename(output_path)
                 print(f"Image saved to: {output_path}")
             except (PermissionError, IOError, OSError) as e:
                 print_error(
                     f"Failed to move file to final destination: {e}",
                     ["Check target directory write permissions", "Ensure sufficient disk space", "Check log file for details: generate_image.log"],
                     exit_code=1
                 )
        else:
             print_error(
                 f"Temporary image file not found",
                 [f"Expected at: {temp_img_path}", f"Library reported: {generated_files}", "Check if browser is properly installed", "Ensure sufficient disk space", "Check log file for details: generate_image.log"],
                 exit_code=1
             )

    except PermissionError as e:
        print_error(
            f"Permission error: {e}",
            ["Check output directory write permissions", "Try running as administrator", "Use current directory as output location"],
            exit_code=1
        )
    except OSError as e:
        print_error(
            f"System error: {e}",
            ["Ensure sufficient disk space", "Check if file path is too long", "Check log file for details: generate_image.log"],
            exit_code=1
        )
    except (RuntimeError, ValueError, TypeError) as e:
        print_error(
            f"Error generating image: {e}",
            ["Ensure web browser is installed (Chrome, Edge, or Chromium)", "Check Markdown content for unsupported formats", "Check log file for details: generate_image.log", "Try with simpler Markdown content"],
            exit_code=1
        )

def main():
    parser = argparse.ArgumentParser(description="Convert Markdown to Image")
    parser.add_argument("input_file", help="Path to input markdown file")
    parser.add_argument("-o", "--output", help="Path to output image file (default: input_filename.png)")
    parser.add_argument("--width", type=int, default=800, help="Image width in pixels (default: 800)")
    parser.add_argument("--quality", type=int, default=95, help="Output image quality (1-100, default: 95). Higher values produce better quality but larger file sizes. Applies to both PNG and JPG formats.")
    parser.add_argument("--theme", type=str, default="github", 
                        help="CSS theme to use (default: github). Available themes: github, notion, dark")
    
    try:
        args = parser.parse_args()
    except SystemExit as e:
        print(f"参数解析错误: {e}")
        sys.exit(1)
    
    if args.quality < 1 or args.quality > 100:
        print_error(
            f"Quality parameter must be between 1 and 100. Current value: {args.quality}",
            ["Use --quality parameter to set a value between 1-100", "Default value is 95, which provides good quality and file size balance"],
            exit_code=1
        )
    
    if args.width < 100 or args.width > 5000:
        print_error(
            f"Width parameter must be between 100 and 5000. Current value: {args.width}",
            ["Use --width parameter to set a value between 100-5000", "Default value is 800"],
            exit_code=1
        )
    
    input_path = Path(args.input_file)
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_suffix('.png')
        
    generate_image(args.input_file, output_path, args.width, args.quality, args.theme)

if __name__ == "__main__":
    main()
