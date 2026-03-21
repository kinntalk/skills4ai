# WeChat HTML Specification

This document outlines the HTML constraints and requirements for WeChat Official Account articles.

## Supported HTML Tags

WeChat Official Account editor supports a limited subset of HTML tags:

### Allowed Tags

| Tag | Notes |
|-----|-------|
| `<p>` | Paragraph |
| `<br>` | Line break |
| `<h1>` - `<h3>` | Headings (h4-h6 not recommended) |
| `<strong>`, `<b>` | Bold text |
| `<em>`, `<i>` | Italic text |
| `<u>` | Underline |
| `<s>`, `<del>` | Strikethrough |
| `<a>` | Links (converted to footnotes) |
| `<img>` | Images (must be uploaded) |
| `<ul>`, `<ol>`, `<li>` | Lists |
| `<blockquote>` | Quote blocks |
| `<pre>`, `<code>` | Code blocks |
| `<table>`, `<tr>`, `<th>`, `<td>` | Tables |
| `<section>` | Generic container |
| `<span>` | Inline container |

### Unsupported Tags

The following tags are **NOT** supported and will be stripped:

- `<script>` - JavaScript
- `<style>` - External CSS
- `<iframe>` - Embedded content
- `<form>` - Forms
- `<input>` - Input fields
- `<video>` - Videos (use video upload instead)
- `<audio>` - Audio (use audio upload instead)
- `<object>`, `<embed>` - Plugins
- `<meta>`, `<link>` - Meta tags

## CSS Constraints

### Inline CSS Only

WeChat does **NOT** support:
- External stylesheets (`<link rel="stylesheet">`)
- `<style>` blocks
- CSS classes

All styling must be done via **inline `style` attributes**:

```html
<p style="color: #333; font-size: 16px;">Content</p>
```

### Supported CSS Properties

| Property | Notes |
|----------|-------|
| `color` | Text color (hex or named) |
| `background` | Background color |
| `font-size` | Use px or em |
| `font-weight` | bold, normal, 100-900 |
| `font-family` | Limited font support |
| `text-align` | left, center, right, justify |
| `line-height` | Use unitless or px |
| `margin` | Spacing |
| `padding` | Internal spacing |
| `border` | Borders |
| `border-radius` | Rounded corners |
| `max-width` | Image sizing |
| `width` | Fixed width |

### Unsupported CSS Properties

- `position` (fixed, absolute, sticky)
- `display` (flex, grid)
- `transform`
- `animation`
- `transition`
- `z-index`
- `overflow` (limited support)

## Image Requirements

| Requirement | Limit |
|-------------|-------|
| Max file size | 10 MB |
| Supported formats | JPG, PNG, GIF |
| Recommended width | ≤ 900px |
| Max per article | 100 images |

## Content Limits

| Element | Limit |
|---------|-------|
| Title | 64 characters |
| Digest/Summary | 120 characters |
| Article length | 20,000 characters |
| Author name | 8 characters |

## Best Practices

1. **Use semantic HTML** - Proper heading hierarchy
2. **Keep paragraphs short** - 3-4 sentences max
3. **Use high-contrast colors** - Ensure readability
4. **Optimize images** - Compress before uploading
5. **Test on mobile** - WeChat is primarily mobile
6. **Avoid external links** - Convert to footnotes

## Example Valid HTML

```html
<section style="padding: 20px; font-family: sans-serif;">
  <h1 style="font-size: 24px; color: #000; margin-bottom: 15px;">
    Article Title
  </h1>
  <p style="font-size: 16px; line-height: 1.8; color: #333;">
    This is a paragraph with <strong style="font-weight: bold;">bold text</strong>
    and <em style="font-style: italic;">italic text</em>.
  </p>
  <img src="image.jpg" style="max-width: 100%; display: block; margin: 15px auto;">
  <blockquote style="border-left: 4px solid #e0e0e0; padding: 10px 15px; background: #f9f9f9;">
    This is a quote.
  </blockquote>
</section>
```
