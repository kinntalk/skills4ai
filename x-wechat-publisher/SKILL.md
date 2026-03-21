---
name: x-wechat-publisher
description: WeChat Official Account publishing workflow with AI-powered content creation, Markdown-to-WeChat HTML rendering, and hybrid-drive synchronization. Use this skill whenever the user mentions "发布公众号", "微信公众号", "同步微信", "公众号草稿", "WeChat Official Account", "post to WeChat", or wants to create, format, or sync articles to WeChat Official Account, even if they don't explicitly ask for a 'publisher' or 'WeChat'.
---

# x-wechat-publisher

A Python + Agent based skill for automated WeChat Official Account publishing workflow. This skill enables AI-powered content creation, Markdown-to-WeChat HTML rendering with inline CSS, and hybrid-drive synchronization to WeChat draft box.

## Core Workflow

```
User Topic → AI Creation → Obsidian MD → Renderer → WeChat HTML → Sync Engine → Draft Box
```

## When to Use This Skill

Use this skill when the user wants to:
1. Create articles for WeChat Official Account
2. Convert Markdown to WeChat-compatible HTML
3. Sync content to WeChat draft box
4. Generate structured content with proper frontmatter

## Workflow Steps

### Step 1: AI Structured Content Creation

Generate Obsidian-compatible Markdown with proper YAML frontmatter.

**Required frontmatter fields:**
```yaml
---
title: Article Title (max 64 characters)
digest: Article summary (max 120 characters)
cover: cover.png
author: Author name
---
```

**Content structure guidelines:**
- Title: ≤ 28 characters for optimal mobile display
- Lead paragraph: ≤ 80 characters
- Maximum heading depth: 2 levels (##)
- Avoid nested lists deeper than 2 levels
- Use short paragraphs for mobile reading

### Step 2: Markdown to WeChat HTML Rendering

Use the bundled script to convert Markdown to WeChat-safe HTML:

```bash
python scripts/md_to_wechat_html.py <input.md> --theme <theme_name> --output <output.html>
```

**Available themes:**
- `default` - Clean, professional style
- `tech` - Modern tech-focused design
- `minimal` - Simple, elegant layout

Read `references/wechat_html_spec.md` for WeChat HTML constraints.

### Step 3: Hybrid-Drive Sync to WeChat Draft Box

Use the sync engine to publish content:

```bash
python scripts/wechat_sync.py --html <content.html> --cover <cover.png>
```

**Sync modes:**
1. **Fast path (default)**: Playwright CDP injection (< 5 seconds)
2. **Fallback**: Agent visual takeover on DOM failure

The sync engine automatically:
- Manages browser sessions (first run requires QR code scan)
- Handles image uploads
- Injects HTML content into WeChat editor
- Saves to draft box

## Session Management

First-time setup requires browser login:

```bash
python scripts/session_manager.py --setup
```

This opens a browser for QR code scanning. Session data is encrypted and stored locally for subsequent runs.

## File Structure

```
x-wechat-publisher/
├── SKILL.md                 # This file
├── scripts/
│   ├── md_to_wechat_html.py # Markdown renderer
│   ├── wechat_sync.py       # Sync engine
│   └── session_manager.py   # Browser session handler
├── references/
│   ├── wechat_html_spec.md  # WeChat HTML constraints
│   └── themes_guide.md      # Theme customization
├── themes/
│   ├── default.json
│   ├── tech.json
│   └── minimal.json
└── evals/
    └── evals.json
```

## Error Handling

The skill handles errors gracefully:

1. **DOM selector failure**: Automatically falls back to Agent visual mode
2. **Session expired**: Prompts user to re-authenticate
3. **Image upload failure**: Retries with alternative method
4. **Network timeout**: Retries with exponential backoff (max 3 attempts)

## Constraints

- No API key dependency (browser-based only)
- No external third-party services
- Works with personal subscription accounts
- Maximum 3 implementation approaches per module
- No infinite loops - all operations have timeout limits

## Dependencies

- Python 3.10+
- Playwright
- markdown-it-py
- premailer (for CSS inlining)

Install dependencies:
```bash
pip install playwright markdown-it-py premailer
playwright install chromium
```

## Example Usage

**User prompt:**
> "Create a tech article about AI agents and sync it to my WeChat Official Account"

**Agent workflow:**
1. Generate structured Markdown with frontmatter
2. Convert to WeChat HTML using tech theme
3. Sync to WeChat draft box
4. Return draft preview link
