---
name: image-generation
description: Converts Markdown documents to high-quality images (PNG/JPG) using Python and headless browser rendering. Ideal for creating social media posts, documentation screenshots, and sharing rich text content as images.
---

# Image Generation

## Overview

The `image-generation` skill provides a robust way to convert Markdown content into beautifully formatted images. It uses Python to parse Markdown into HTML and `html2image` (via headless Chrome/Edge) to render the final output. This ensures that all Markdown features—including code blocks, tables, and typography—are rendered perfectly.

## Features

- **Rich Markdown Support**: Supports tables, code blocks (with syntax highlighting), blockquotes, and more.
- **Modern Styling**: Built-in CSS provides a clean, professional look similar to GitHub or Notion.
- **High Fidelity**: Uses a real browser engine for rendering, ensuring accurate layout and font handling.
- **CLI Interface**: Simple command-line usage for automation.

## Usage

### Generate an Image

Run the script with your markdown file as input:

```bash
python .trae/skills/image-generation/scripts/generate_image.py input.md
```

This will create `input.png` in the same directory.

### Custom Output and Width

You can specify the output filename and the content width:

```bash
python .trae/skills/image-generation/scripts/generate_image.py input.md -o output.jpg --width 1000
```

## System Requirements

- **Python 3.6+**
- **Web Browser**: A headless-capable browser (Chrome, Edge, or Chromium) must be installed on the system.
    - Windows: Microsoft Edge (pre-installed) works out of the box.
    - macOS/Linux: Chrome or Chromium is recommended.


## Technical Implementation Details

### Cross-Platform Robustness

This skill implements several techniques to ensure reliable operation across Windows, macOS, and Linux:

1.  **Data URI Rendering**: Instead of creating temporary HTML files (which can cause path encoding issues on Windows or permission errors), the HTML content is encoded as a Base64 Data URI. This allows the browser to render content directly from memory without touching the file system for input.
    
2.  **Safe Temporary Filenames**: Output images are first written to a temporary file with a UUID-based ASCII name (e.g., `render_a1b2...png`). This prevents the browser from failing to write to paths containing non-ASCII characters (like Chinese or Emoji), which is a common issue in headless browser automation.

3.  **Async File System Polling**: The script includes a retry loop that waits for the browser to fully flush the image file to disk before attempting to rename it to the final destination. This mitigates race conditions where the browser process returns success before the OS file lock is released.

These implementations make the skill particularly resilient when handling non-English filenames or running in environments with strict file locking (like Windows).
## Troubleshooting

### Browser Not Found
- You may need to set the `CHROME_BIN` environment variable to point to your browser executable if it's in a non-standard location.

### Text Rendering Issues
- Ensure your system has standard fonts installed (Arial, Segoe UI, or San Francisco).
- If Chinese/Japanese characters are missing, ensure a CJK font (like Microsoft YaHei) is available on the system.
