# Theme Customization Guide

This guide explains how to create and customize themes for the WeChat HTML renderer.

## Theme Structure

Themes are JSON files that define CSS styles for HTML elements. Each theme file contains a mapping of HTML tags to style properties.

### Basic Structure

```json
{
  "body": {
    "font-family": "sans-serif",
    "font-size": "16px",
    "line-height": "1.8"
  },
  "h1": {
    "font-size": "24px",
    "font-weight": "bold"
  }
}
```

## Supported Elements

The following elements can be styled:

| Element | Description |
|---------|-------------|
| `body` | Container styles |
| `h1` | Main heading |
| `h2` | Section heading |
| `h3` | Subsection heading |
| `p` | Paragraph |
| `blockquote` | Quote block |
| `code` | Inline code |
| `pre` | Code block |
| `img` | Image |
| `ul` | Unordered list |
| `ol` | Ordered list |
| `li` | List item |
| `a` | Link |
| `table` | Table container |
| `th` | Table header |
| `td` | Table cell |

## Style Properties

### Typography

```json
{
  "font-family": "-apple-system, BlinkMacSystemFont, sans-serif",
  "font-size": "16px",
  "font-weight": "bold",
  "font-style": "italic",
  "line-height": "1.8",
  "text-align": "justify",
  "color": "#333333"
}
```

### Spacing

```json
{
  "margin": "10px 0",
  "padding": "15px"
}
```

### Backgrounds

```json
{
  "background": "#f5f5f5",
  "background-color": "#ffffff"
}
```

### Borders

```json
{
  "border": "1px solid #e0e0e0",
  "border-left": "4px solid #007bff",
  "border-radius": "5px"
}
```

## Creating a Custom Theme

1. Create a new JSON file in the `themes/` directory
2. Define styles for each element
3. Use the theme with `--theme <name>` flag

### Example: Custom Theme

```json
{
  "body": {
    "font-family": "'PingFang SC', 'Microsoft YaHei', sans-serif",
    "font-size": "16px",
    "line-height": "1.75",
    "color": "#2c3e50",
    "padding": "20px"
  },
  "h1": {
    "font-size": "26px",
    "font-weight": "bold",
    "color": "#1a1a1a",
    "margin": "25px 0 15px 0",
    "text-align": "center"
  },
  "h2": {
    "font-size": "22px",
    "font-weight": "bold",
    "color": "#2c3e50",
    "margin": "20px 0 10px 0",
    "border-bottom": "2px solid #3498db"
  },
  "p": {
    "margin": "12px 0",
    "text-align": "justify"
  },
  "blockquote": {
    "border-left": "4px solid #3498db",
    "padding": "12px 16px",
    "margin": "15px 0",
    "background": "#ecf0f1",
    "color": "#7f8c8d"
  },
  "code": {
    "font-family": "'Fira Code', monospace",
    "background": "#f8f9fa",
    "padding": "2px 6px",
    "border-radius": "4px",
    "font-size": "14px",
    "color": "#e74c3c"
  },
  "pre": {
    "background": "#2c3e50",
    "padding": "15px",
    "border-radius": "6px",
    "overflow-x": "auto",
    "margin": "15px 0"
  },
  "img": {
    "max-width": "100%",
    "height": "auto",
    "display": "block",
    "margin": "15px auto",
    "border-radius": "8px"
  }
}
```

## Theme Recommendations

### For Tech Articles

- Use monospace fonts for code
- Dark background for code blocks
- Blue accent colors
- Clean, minimal design

### For Lifestyle Content

- Warm, inviting colors
- Larger font sizes
- More spacing between elements
- Rounded corners

### For Business Content

- Professional color palette
- Clear hierarchy
- Subtle borders
- Justified text alignment

## Testing Themes

After creating a theme, test it:

```bash
python scripts/md_to_wechat_html.py test.md --theme custom --output test.html
```

Open the output HTML in a browser to verify the styling.
