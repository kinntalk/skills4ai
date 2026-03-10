---
name: xhs-search
description: Search Xiaohongshu (小红书) notes and comments, save results to Obsidian vault. Use when user wants to search xiaohongshu.com, extract notes, get comments, or save xiaohongshu content to Obsidian. Supports both Chinese and English keywords like "搜索 英语学习" or "search Learning English".
allowed-tools: Bash(python *), Bash(agent-browser:*)
---

# XHS Search to Obsidian

A specialized variant of `url-to-obsidian` for Xiaohongshu (小红书). Search notes and comments, save results as Obsidian Flavored Markdown.

## Features

- **Keyword Search**: Search Xiaohongshu notes by keyword (supports Chinese/English)
- **Comment Extraction**: Extract comments from specific notes
- **Obsidian Output**: Auto-format results as OFM with frontmatter, wikilinks, callouts
- **Login State**: Persistent login state via agent-browser sessions
- **Auto Vault Detection**: Automatically finds your Obsidian vault

## Script Directory

**Important**: All scripts are located in the `scripts/` subdirectory.

**Agent Execution Instructions**:
1. Determine this SKILL.md file's directory path as `SKILL_DIR`
2. Script path = `${SKILL_DIR}/scripts/<script-name>.py`
3. Replace all `${SKILL_DIR}` in this document with the actual path

## Quick Start

```bash
# Search notes by keyword (Chinese)
python ${SKILL_DIR}/scripts/xhs_search.py search "英语学习"

# Search notes by keyword (English)
python ${SKILL_DIR}/scripts/xhs_search.py search "Learning English"

# Extract comments from a note
python ${SKILL_DIR}/scripts/xhs_search.py comments "https://www.xiaohongshu.com/explore/xxxxx"

# Configure vault path
python ${SKILL_DIR}/scripts/xhs_search.py config set-vault "D:/Obsidian/MyVault"
```

## Commands

### search - Search Notes by Keyword

```bash
python ${SKILL_DIR}/scripts/xhs_search.py search <keyword> [options]
```

| Option | Description |
|--------|-------------|
| `<keyword>` | Search keyword (Chinese or English) |
| `-o, --output <path>` | Custom output file name |
| `--limit <n>` | Max number of results (default: 20) |
| `--sort <type>` | Sort by: `general`, `newest`, `hottest` |
| `--no-images` | Skip image downloading |
| `--tags <tags>` | Additional tags (comma-separated) |
| `--subfolder <path>` | Subfolder within vault |

**Examples**:
```bash
# Basic search
python ${SKILL_DIR}/scripts/xhs_search.py search "英语学习"

# With options
python ${SKILL_DIR}/scripts/xhs_search.py search "Learning English" --limit 10 --sort newest --tags language,learning

# Save to specific subfolder
python ${SKILL_DIR}/scripts/xhs_search.py search "摄影技巧" --subfolder "小红书/摄影"
```

### comments - Extract Note Comments

```bash
python ${SKILL_DIR}/scripts/xhs_search.py comments <note_url_or_id> [options]
```

| Option | Description |
|--------|-------------|
| `<note_url_or_id>` | Note URL or ID |
| `-o, --output <path>` | Custom output file name |
| `--limit <n>` | Max number of comments (default: 50) |
| `--hot` | Sort by hottest comments |

**Examples**:
```bash
# Extract comments by URL
python ${SKILL_DIR}/scripts/xhs_search.py comments "https://www.xiaohongshu.com/explore/65abc123"

# Extract by note ID
python ${SKILL_DIR}/scripts/xhs_search.py comments "65abc123" --limit 30 --hot
```

### note - Get Single Note Details

```bash
python ${SKILL_DIR}/scripts/xhs_search.py note <note_url_or_id> [options]
```

| Option | Description |
|--------|-------------|
| `<note_url_or_id>` | Note URL or ID |
| `-o, --output <path>` | Custom output file name |
| `--with-comments` | Include comments in output |

### config - Configuration Management

```bash
python ${SKILL_DIR}/scripts/xhs_search.py config <command> [options]
```

| Command | Description |
|---------|-------------|
| `set <key> <value>` | Set a configuration value |
| `get <key>` | Get a configuration value |
| `list` | List all configuration |
| `set-vault <path>` | Set Obsidian vault path |

## Configuration

Configuration is stored at `~/.xhs-search/config.json`

### Configuration Structure

```json
{
  "vault_path": null,
  "auto_detect_vault": true,
  "output": {
    "subfolder": "xiaohongshu",
    "filename_template": "{type}-{keyword}-{date}",
    "add_frontmatter": true,
    "default_tags": ["xhs-search"]
  },
  "assets": {
    "folder": null,
    "download": true,
    "wikilink": true
  },
  "browser": {
    "session_name": "xhs-search",
    "timeout": 30000,
    "headed": false
  },
  "search": {
    "default_limit": 20,
    "request_delay": 2.0
  }
}
```

## Output Format

### Search Results

```markdown
---
title: 小红书搜索 - 英语学习
date: 2026-03-09
tags:
  - xhs-search
  - 英语学习
source: https://www.xiaohongshu.com/search_result?keyword=英语学习
---

# 小红书搜索结果：英语学习

> [!info] 搜索信息
> - 关键词: 英语学习
> - 搜索时间: 2026-03-09 14:30:00
> - 结果数量: 20

## 笔记列表

### 1. 零基础学英语，3个月达到日常交流水平

![[xhs-image-2026-03-09-001.png|300]]

- **作者**: [[英语老师小王]]
- **点赞**: 12.5k
- **收藏**: 8.2k
- **评论**: 356
- **链接**: [查看原文](https://www.xiaohongshu.com/explore/xxxxx)

**摘要**: 分享我从零开始学习英语的方法，每天只需1小时...

---

### 2. 英语学习APP推荐，这几个就够了
...
```

### Note Details

```markdown
---
title: 零基础学英语，3个月达到日常交流水平
date: 2026-03-09
author: 英语老师小王
tags:
  - xhs-note
  - 英语学习
source: https://www.xiaohongshu.com/explore/xxxxx
---

# 零基础学英语，3个月达到日常交流水平

> [!info] 笔记信息
> - 作者: [[英语老师小王]]
> - 发布时间: 2026-03-01
> - 点赞: 12.5k | 收藏: 8.2k | 评论: 356

![[xhs-cover-2026-03-09-001.png|400]]

## 正文

分享我从零开始学习英语的方法，每天只需1小时...

## 图片

![[xhs-image-2026-03-09-002.png]]
![[xhs-image-2026-03-09-003.png]]

## 评论区精选

> [!quote] 用户A
> 太有用了，正在学习中！

> [!quote] 用户B
> 请问有配套资料吗？
```

## Dependencies

```bash
pip install beautifulsoup4 requests
```

Or use the requirements.txt:

```bash
pip install -r ${SKILL_DIR}/requirements.txt
```

## Login Management

Xiaohongshu requires login for searching. The skill uses agent-browser session management:

### Login Flow (Best Practices)

**IMPORTANT**: Always follow this login flow to avoid common issues:

1. **Step 1: Refresh page and check status**
   ```bash
   npx agent-browser --session xhs-search open "https://www.xiaohongshu.com"
   npx agent-browser --session xhs-search eval "document.body.innerText.includes('二维码已过期') ? 'expired' : (document.querySelector('.qrcode-img') ? 'need_scan' : (document.body.innerText.includes('登录') ? 'need_login' : 'logged_in'))"
   ```

2. **Step 2: Handle different states**
   - `logged_in`: Continue with task
   - `expired`: Refresh page and get new QR code
   - `need_scan`: Get QR code and wait for user to scan
   - `need_login`: Wait for login dialog to appear

3. **Step 3: Get QR code position**
   ```bash
   npx agent-browser --session xhs-search eval "const qr = document.querySelector('.qrcode-img'); qr ? qr.getBoundingClientRect().x + ',' + qr.getBoundingClientRect().y + ',' + qr.getBoundingClientRect().width + ',' + qr.getBoundingClientRect().height : 'no qr'"
   ```

4. **Step 4: Screenshot and crop QR code**
   - Screenshot the page
   - Crop QR code with 25px padding on all sides
   - Save and display to user

5. **Step 5: Wait for login (max 3 minutes)**
   - Loop check login status every 3-5 seconds
   - If `expired`, refresh and get new QR code
   - If `logged_in`, continue with task

### Key Lessons Learned

1. **Always check status first**: Don't assume QR code is valid
2. **QR code expires quickly**: Check for "二维码已过期" text
3. **Add padding to QR code**: 25px padding improves scan success rate
4. **Wait up to 3 minutes**: Don't end task while waiting for login

### Session Management

1. **First Run**: Browser opens, login manually, session is saved
2. **Subsequent Runs**: Session is automatically restored

```bash
# Force re-login (clear saved session)
python ${SKILL_DIR}/scripts/xhs_search.py login --reset
```

## How It Works

1. **Browser Launch**: Uses agent-browser for browser automation
2. **Login Check**: Detects if login is needed
3. **Search/Extract**: Navigates to search page, extracts results
4. **Content Parsing**: Parses HTML using BeautifulSoup
5. **OFM Formatting**: Converts to Obsidian Flavored Markdown
6. **Asset Download**: Downloads images to vault attachment folder
7. **Save to Vault**: Writes final file to Obsidian vault

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Login required | Run with `--headed` to login manually |
| Session expired | Run `xhs_search.py login --reset` |
| Vault not found | Run `xhs_search.py config set-vault <path>` |
| No results | Check keyword, try different sort option |
| Rate limited | Increase `search.request_delay` in config |

## Best Practices for Agent

### Terminal Working Directory

After executing commands, change terminal's working directory:

```bash
# After running any xhs_search command
cd d:\workspace1\yusuan
```

### Language Support

The skill supports both Chinese and English keywords:
- `search "英语学习"` (Chinese)
- `search "Learning English"` (English)

Both will search Xiaohongshu and return results.

## Version History

- **1.0.0**: Initial release with search, comments, note commands
