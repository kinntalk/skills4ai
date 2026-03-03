# URL to Obsidian Markdown Converter

Convert any web page to Obsidian Flavored Markdown (OFM) and save directly to your Obsidian vault.

## Script Directory

**Important**: All scripts are located in the `scripts/` subdirectory of this skill.

**Agent Execution Instructions**:
1. Determine this SKILL.md file's directory path as `SKILL_DIR`
2. Script path = `${SKILL_DIR}/scripts/<script-name>.py`
3. Replace all `${SKILL_DIR}` in this document with the actual path

**Script Reference**:
| Script | Purpose |
|--------|---------|
| `scripts/web2obs.py` | Main CLI entry point |
| `scripts/cdp_client.py` | Chrome DevTools Protocol client |
| `scripts/html_converter.py` | HTML to Markdown conversion |
| `scripts/config_manager.py` | Configuration management |
| `scripts/converter.py` | Core conversion logic |
| `scripts/ofm_formatter.py` | Obsidian Flavored Markdown formatting |
| `scripts/vault_detector.py` | Obsidian vault detection |
| `scripts/asset_handler.py` | Asset downloading |

## Features

- **Automatic Login Detection**: Detects login pages and waits for login completion automatically
- **Obsidian Vault Auto-Detection**: Automatically finds your Obsidian vault from global config
- **Obsidian Flavored Markdown**: Output includes YAML frontmatter, wikilinks, callouts, and tags
- **Asset Downloading**: Automatically downloads images to vault's attachment folder
- **Encrypted Credentials**: Securely store login credentials for frequently accessed sites
- **Pure Python**: No external CLI dependencies (uses CDP directly)

## Quick Start

```bash
# Basic usage - fetch and convert a URL (auto-detects login)
python ${SKILL_DIR}/scripts/web2obs.py convert <url>

# Format existing markdown as OFM
python ${SKILL_DIR}/scripts/web2obs.py format <input.md> -o output.md
```

## Configuration

### Initial Setup

```bash
# Set Obsidian vault path (optional - auto-detection is enabled by default)
python ${SKILL_DIR}/scripts/web2obs.py config set-vault "D:/Obsidian/MyVault"

# List current configuration
python ${SKILL_DIR}/scripts/web2obs.py config list
```

### Configuration File Location

Configuration is stored at `~/.web2obs/config.json`

### Configuration Structure

```json
{
  "vault_path": null,
  "auto_detect_vault": true,
  "output": {
    "subfolder": "web-clippings",
    "filename_template": "{title}-{date}",
    "add_frontmatter": true,
    "default_tags": ["web-clipping"]
  },
  "assets": {
    "folder": null,
    "download": true,
    "wikilink": false,
    "naming": "{title}-{timestamp}-{index}"
  },
  "credentials": {}
}
```

## Vault Auto-Detection

Skill automatically detects vault path from Obsidian global config:
- Windows: `%APPDATA%\obsidian\obsidian.json`
- macOS: `~/Library/Application Support/obsidian/obsidian.json`
- Linux: `~/.config/obsidian/obsidian.json`

Configuration priority: Manual config > Auto-detection

When `auto_detect_vault` is `true` and `vault_path` is not set, skill automatically detects the most recently opened vault.

## Automatic Login Detection

The skill automatically detects login pages by checking:
- URL patterns (login, signin, auth, etc.)
- Page title patterns
- Presence of password fields
- Login form elements

When a login page is detected:
1. Browser opens with the page
2. User logs in manually
3. Skill automatically detects successful login (URL change, login elements disappear)
4. Content is captured automatically

No manual Enter key press required!

## Asset Handling

When `assets.download` is `true`, skill automatically downloads images to vault's attachment folder.

Asset folder priority:
1. Config `assets.folder`
2. Vault's `.obsidian/app.json` `attachmentFolderPath`
3. Default: `assets`

### Image Link Formats

**Standard Markdown** (default):
```markdown
![description](assets/image-2024-01-01-1.png)
```

**Wikilink Format** (enable with `--wikilink` or `assets.wikilink: true`):
```markdown
![[image-2024-01-01-1.png|description]]
```

## CLI Commands

### Convert URL

```bash
python ${SKILL_DIR}/scripts/web2obs.py convert <url> [options]
```

| Option | Description |
|--------|-------------|
| `<url>` | URL to fetch and convert |
| `-o, --output <path>` | Custom output file name |
| `--wait` | Wait for login (auto-detected by default) |
| `--no-wait` | Disable automatic login detection |
| `--headless` | Run browser in headless mode |
| `--no-frontmatter` | Skip YAML frontmatter generation |
| `--no-assets` | Disable asset (image) downloading |
| `--wikilink` | Use wikilink format for image links |
| `--tags <tags>` | Comma-separated tags to add |
| `--subfolder <path>` | Subfolder within vault to save to |

### Format Existing Markdown

```bash
python ${SKILL_DIR}/scripts/web2obs.py format <input.md> [options]
```

| Option | Description |
|--------|-------------|
| `<input>` | Input markdown file |
| `-o, --output <path>` | Output file path |
| `--url <url>` | Source URL |
| `--tags <tags>` | Comma-separated tags |
| `--in-place` | Overwrite input file |
| `--no-frontmatter` | Skip frontmatter |
| `--no-source` | Skip source callout |
| `--no-assets` | Disable asset downloading |
| `--wikilink` | Use wikilink format |

### Configuration Management

```bash
python ${SKILL_DIR}/scripts/web2obs.py config <command> [options]
```

| Command | Description |
|---------|-------------|
| `set <key> <value>` | Set a configuration value |
| `get <key>` | Get a configuration value |
| `list` | List all configuration |
| `set-vault <path>` | Set Obsidian vault path |

## Output Format

### File Naming

Default: `{page-title}-{YYYY-MM-DD}.md`

### Obsidian Flavored Markdown Structure

```markdown
---
title: Page Title
date: 2026-03-03
source: https://example.com/article
tags:
  - web-clipping
---

# Page Title

> [!info] Source
> This note was created from [original page](https://example.com/article) on 2026-03-03.

## Section 1

Content extracted from the page...

## Section 2

More content...

> [!tip] Key Point
> Important information highlighted as a callout.
```

## Dependencies

Install required Python packages:

```bash
pip install websockets requests readability-lxml markdownify beautifulsoup4 cryptography
```

## How It Works

1. **Browser Launch**: Uses Chrome DevTools Protocol (CDP) to control Chrome
2. **Login Detection**: Analyzes page content to detect login forms
3. **Login Wait**: Monitors page for login completion signals
4. **Content Extraction**: Uses Readability for main content extraction
5. **Markdown Conversion**: Converts HTML to clean Markdown
6. **OFM Formatting**: Adds frontmatter, callouts, and tags
7. **Asset Download**: Downloads images to vault attachment folder
8. **Save to Vault**: Writes final file to Obsidian vault

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Chrome not found | Set `URL_CHROME_PATH` environment variable |
| Login not detected | Use `--wait` flag to force wait mode |
| Vault path not found | Run `web2obs config set-vault <path>` |
| Import errors | Install dependencies: `pip install websockets requests readability-lxml markdownify beautifulsoup4 cryptography` |
| Content not extracted | Check if page requires JavaScript rendering |

## Examples

### Basic Public Page

```bash
python ${SKILL_DIR}/scripts/web2obs.py convert https://example.com/article
```

### Login-Required Page (Auto-Detected)

```bash
python ${SKILL_DIR}/scripts/web2obs.py convert https://docs.example.com/protected
```

### With Custom Tags

```bash
python ${SKILL_DIR}/scripts/web2obs.py convert <url> --tags tutorial,learning
```

### Headless Mode (No Browser UI)

```bash
python ${SKILL_DIR}/scripts/web2obs.py convert <url> --headless
```

## Version History

- **2.0.0**: Complete rewrite with native CDP support, automatic login detection, removed baoyu-url-to-markdown dependency
- **1.1.0**: Added `format` command, HTML cleaning
- **1.0.0**: Initial release

## Best Practices for Agent

### Terminal Working Directory

**IMPORTANT**: After executing commands in this skill's directory, change the terminal's working directory to prevent file locks.

```bash
# After running any web2obs command, change directory
cd d:\workspace1\yusuan
```

### Recommended Workflow

1. Execute skill commands
2. Immediately change terminal cwd to project root
3. Verify no lingering locks before attempting directory operations
