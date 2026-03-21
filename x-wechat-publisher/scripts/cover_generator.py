#!/usr/bin/env python3
"""
Cover Image Generator for WeChat Articles

Generates cover images for WeChat Official Account articles.
Supports multiple templates and customizable styles.
"""

import argparse
import json
import math
import random
import sys
from pathlib import Path
from typing import Optional, Tuple, List

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except ImportError:
    print("Error: Pillow not installed. Run: pip install Pillow")
    sys.exit(1)


class CoverGenerator:
    """Generate cover images for WeChat articles."""

    WECHAT_COVER_SIZE = (900, 383)
    DEFAULT_FONTS = [
        "msyh.ttc",
        "msyhbd.ttc",
        "simhei.ttf",
        "simsun.ttc",
        "Arial Unicode MS",
    ]

    COLOR_THEMES = {
        "tech": {
            "bg_colors": ["#1a1a2e", "#16213e", "#0f3460"],
            "text_color": "#ffffff",
            "accent_color": "#e94560",
        },
        "business": {
            "bg_colors": ["#2c3e50", "#34495e", "#1a252f"],
            "text_color": "#ffffff",
            "accent_color": "#3498db",
        },
        "lifestyle": {
            "bg_colors": ["#ff6b6b", "#ee5a24", "#f39c12"],
            "text_color": "#ffffff",
            "accent_color": "#ffffff",
        },
        "nature": {
            "bg_colors": ["#27ae60", "#2ecc71", "#1abc9c"],
            "text_color": "#ffffff",
            "accent_color": "#f1c40f",
        },
        "minimal": {
            "bg_colors": ["#ffffff", "#f5f5f5", "#ecf0f1"],
            "text_color": "#2c3e50",
            "accent_color": "#e74c3c",
        },
        "gradient_blue": {
            "bg_colors": ["#667eea", "#764ba2"],
            "text_color": "#ffffff",
            "accent_color": "#ffffff",
        },
        "gradient_sunset": {
            "bg_colors": ["#fa709a", "#fee140"],
            "text_color": "#ffffff",
            "accent_color": "#ffffff",
        },
        "gradient_ocean": {
            "bg_colors": ["#2193b0", "#6dd5ed"],
            "text_color": "#ffffff",
            "accent_color": "#ffffff",
        },
    }

    def __init__(self):
        self.font = self._load_font()

    def _load_font(self, size: int = 48) -> Optional[ImageFont.FreeTypeFont]:
        """Load a suitable font for Chinese text."""
        for font_name in self.DEFAULT_FONTS:
            try:
                return ImageFont.truetype(font_name, size)
            except (OSError, IOError):
                continue
        
        try:
            return ImageFont.load_default()
        except:
            return None

    def _get_text_size(self, text: str, font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
        """Get the size of text when rendered with given font."""
        bbox = font.getbbox(text)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """Wrap text to fit within max_width."""
        lines = []
        current_line = ""
        
        for char in text:
            test_line = current_line + char
            width, _ = self._get_text_size(test_line, font)
            
            if width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = char
        
        if current_line:
            lines.append(current_line)
        
        return lines

    def _create_gradient_bg(
        self, size: Tuple[int, int], colors: List[str], direction: str = "horizontal"
    ) -> Image.Image:
        """Create a gradient background image."""
        img = Image.new("RGB", size)
        draw = ImageDraw.Draw(img)
        
        if direction == "horizontal":
            for x in range(size[0]):
                ratio = x / size[0]
                if len(colors) == 1:
                    color = colors[0]
                else:
                    idx = ratio * (len(colors) - 1)
                    i = int(idx)
                    if i >= len(colors) - 1:
                        color = colors[-1]
                    else:
                        r1, g1, b1 = int(colors[i][1:3], 16), int(colors[i][3:5], 16), int(colors[i][5:7], 16)
                        r2, g2, b2 = int(colors[i+1][1:3], 16), int(colors[i+1][3:5], 16), int(colors[i+1][5:7], 16)
                        t = idx - i
                        r, g, b = int(r1 + (r2 - r1) * t), int(g1 + (g2 - g1) * t), int(b1 + (b2 - b1) * t)
                        color = f"#{r:02x}{g:02x}{b:02x}"
                draw.line([(x, 0), (x, size[1])], fill=color)
        else:
            for y in range(size[1]):
                ratio = y / size[1]
                if len(colors) == 1:
                    color = colors[0]
                else:
                    idx = ratio * (len(colors) - 1)
                    i = int(idx)
                    if i >= len(colors) - 1:
                        color = colors[-1]
                    else:
                        r1, g1, b1 = int(colors[i][1:3], 16), int(colors[i][3:5], 16), int(colors[i][5:7], 16)
                        r2, g2, b2 = int(colors[i+1][1:3], 16), int(colors[i+1][3:5], 16), int(colors[i+1][5:7], 16)
                        t = idx - i
                        r, g, b = int(r1 + (r2 - r1) * t), int(g1 + (g2 - g1) * t), int(b1 + (b2 - b1) * t)
                        color = f"#{r:02x}{g:02x}{b:02x}"
                draw.line([(0, y), (size[0], y)], fill=color)
        
        return img

    def _add_decorations(
        self, draw: ImageDraw.ImageDraw, size: Tuple[int, int], accent_color: str, style: str = "circles"
    ):
        """Add decorative elements to the cover."""
        if style == "circles":
            for _ in range(5):
                x = random.randint(0, size[0])
                y = random.randint(0, size[1])
                r = random.randint(20, 80)
                opacity = random.randint(20, 60)
                draw.ellipse([x - r, y - r, x + r, y + r], outline=accent_color, width=2)
        
        elif style == "lines":
            for _ in range(3):
                y = random.randint(0, size[1])
                draw.line([(0, y), (size[0], y)], fill=accent_color, width=1)
        
        elif style == "dots":
            for _ in range(50):
                x = random.randint(0, size[0])
                y = random.randint(0, size[1])
                r = random.randint(2, 6)
                draw.ellipse([x - r, y - r, x + r, y + r], fill=accent_color)

    def generate(
        self,
        title: str,
        output_path: Path,
        theme: str = "tech",
        subtitle: Optional[str] = None,
        size: Tuple[int, int] = None,
        decoration_style: Optional[str] = "circles",
    ) -> Path:
        """Generate a cover image with title."""
        if size is None:
            size = self.WECHAT_COVER_SIZE

        theme_config = self.COLOR_THEMES.get(theme, self.COLOR_THEMES["tech"])
        bg_colors = theme_config["bg_colors"]
        text_color = theme_config["text_color"]
        accent_color = theme_config["accent_color"]

        img = self._create_gradient_bg(size, bg_colors, "horizontal")
        draw = ImageDraw.Draw(img)

        if decoration_style:
            self._add_decorations(draw, size, accent_color, decoration_style)

        title_font = self._load_font(52)
        if title_font is None:
            title_font = ImageFont.load_default()

        max_width = size[0] - 80
        lines = self._wrap_text(title, title_font, max_width)

        line_height = 70
        total_height = len(lines) * line_height
        start_y = (size[1] - total_height) // 2

        for i, line in enumerate(lines):
            text_width, _ = self._get_text_size(line, title_font)
            x = (size[0] - text_width) // 2
            y = start_y + i * line_height
            draw.text((x, y), line, fill=text_color, font=title_font)

        if subtitle:
            subtitle_font = self._load_font(28)
            if subtitle_font:
                sub_width, _ = self._get_text_size(subtitle, subtitle_font)
                sub_x = (size[0] - sub_width) // 2
                sub_y = start_y + len(lines) * line_height + 20
                draw.text((sub_x, sub_y), subtitle, fill=accent_color, font=subtitle_font)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, quality=95)
        print(f"Cover image saved: {output_path}")
        
        return output_path

    def generate_from_metadata(
        self, metadata: dict, output_path: Path, theme: Optional[str] = None
    ) -> Optional[Path]:
        """Generate cover image from article metadata."""
        title = metadata.get("title", "")
        if not title:
            print("Warning: No title found in metadata")
            return None

        subtitle = metadata.get("digest", "")
        if len(subtitle) > 50:
            subtitle = subtitle[:50] + "..."

        if theme is None:
            theme = metadata.get("theme", "tech")

        return self.generate(
            title=title,
            output_path=output_path,
            theme=theme,
            subtitle=subtitle if subtitle else None,
        )


def main():
    parser = argparse.ArgumentParser(description='Generate cover image for WeChat article')
    parser.add_argument('--title', type=str, required=True, help='Article title')
    parser.add_argument('--output', type=Path, required=True, help='Output image path')
    parser.add_argument('--theme', type=str, default='tech', 
                        choices=list(CoverGenerator.COLOR_THEMES.keys()),
                        help='Color theme')
    parser.add_argument('--subtitle', type=str, help='Subtitle (optional)')
    parser.add_argument('--metadata', type=Path, help='JSON file with article metadata')
    parser.add_argument('--width', type=int, default=900, help='Image width')
    parser.add_argument('--height', type=int, default=383, help='Image height')
    parser.add_argument('--no-decoration', action='store_true', help='Disable decorations')

    args = parser.parse_args()

    generator = CoverGenerator()

    if args.metadata and args.metadata.exists():
        with open(args.metadata, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        generator.generate_from_metadata(metadata, args.output, args.theme)
    else:
        generator.generate(
            title=args.title,
            output_path=args.output,
            theme=args.theme,
            subtitle=args.subtitle,
            size=(args.width, args.height),
            decoration_style=None if args.no_decoration else "circles",
        )


if __name__ == "__main__":
    main()
