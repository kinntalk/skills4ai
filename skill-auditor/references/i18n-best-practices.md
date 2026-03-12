# Internationalization (i18n) Best Practices / 国际化最佳实践

## Overview / 概述

This guide explains internationalization best practices for Trae skills.

本指南解释了 Trae skills 的国际化最佳实践。

## Core Principles / 核心原则

### 1. No Emoji in Skill Code / Skill 代码中不允许使用 Emoji

**Rule: Emoji characters are not allowed in skill code output.**

**规则：Skill 代码输出中不允许使用 Emoji 字符。**

**Why?**
- Emoji can cause encoding issues in some terminals
- Not all terminals support emoji rendering
- Text labels are universally supported

**为什么？**
- Emoji 在某些终端中可能导致编码问题
- 并非所有终端都支持 emoji 渲染
- 文本标签具有普遍兼容性

**Correct:**
```python
from colorama import Fore, Style

PASS_TEXT = "[PASS]"
FAIL_TEXT = "[FAIL]"
WARN_TEXT = "[WARN]"

print(f"{Fore.GREEN}{PASS_TEXT}{Style.RESET_ALL} Check passed")
print(f"{Fore.RED}{FAIL_TEXT}{Style.RESET_ALL} Check failed")
print(f"{Fore.YELLOW}{WARN_TEXT}{Style.RESET_ALL} Warning issued")
```

**Incorrect:**
```python
print("Check passed ✓")  # Emoji not allowed
print("Check failed ✗")   # Emoji not allowed
```

### 2. Terminal Color Output with colorama / 终端颜色输出使用 colorama

**Rule: All terminal color output must use the colorama library.**

**规则：所有终端颜色输出必须使用 colorama 库。**

**Why?**
- Cross-platform color support (Windows/Linux/macOS)
- Consistent color scheme across all skills
- Easy to maintain and update

**为什么？**
- 跨平台颜色支持 (Windows/Linux/macOS)
- 所有 skills 使用一致的颜色方案
- 易于维护和更新

**Standard Color Scheme / 标准颜色方案:**

| Status | Color | colorama |
|--------|-------|----------|
| `[PASS]` | Green | `Fore.GREEN` |
| `[FAIL]` | Red | `Fore.RED` |
| `[WARN]` | Yellow | `Fore.YELLOW` |
| `[INFO]` | Default | (no color) |
| `[CRITICAL]` | Red | `Fore.RED` |
| `[HIGH]` | Red | `Fore.RED` |
| `[MEDIUM]` | Yellow | `Fore.YELLOW` |
| `[LOW]` | Blue | `Fore.BLUE` |

**Implementation / 实现:**
```python
from colorama import init as colorama_init, Fore, Style

colorama_init()

PASS_TEXT = "[PASS]"
FAIL_TEXT = "[FAIL]"
WARN_TEXT = "[WARN]"

def print_pass(msg, json_output=False):
    if json_output:
        return
    print(f"{Fore.GREEN}{PASS_TEXT}{Style.RESET_ALL} {msg}")

def print_fail(msg, json_output=False):
    if json_output:
        return
    print(f"{Fore.RED}{FAIL_TEXT}{Style.RESET_ALL} {msg}")

def print_warn(msg, json_output=False):
    if json_output:
        return
    print(f"{Fore.YELLOW}{WARN_TEXT}{Style.RESET_ALL} {msg}")

def print_info(msg, json_output=False):
    if json_output:
        return
    print(msg)
```

### 3. i18n Message Dictionary / 国际化消息字典

**Rule: All user-facing output text must use a message dictionary.**

**规则：所有面向用户的输出文本必须使用消息字典。**

**Why?**
- Enables multi-language support
- Centralized message management
- Easy to translate and maintain
- Consistent messaging across the skill

**为什么？**
- 启用多语言支持
- 集中消息管理
- 易于翻译和维护
- skill 内消息一致性

**Message Dictionary Structure / 消息字典结构:**
```python
# messages.py
import os
from typing import Dict, Any

DEFAULT_LANG = 'en'
CURRENT_LANG = os.environ.get('SKILL_LANG', 'en')

MESSAGES: Dict[str, Dict[str, Any]] = {
    'en': {
        'status': {
            'pass': '[PASS]',
            'fail': '[FAIL]',
            'warn': '[WARN]',
        },
        'audit': {
            'title': '[*] Auditing Skill: {name}',
            'path': '   Path: {path}',
        },
        'results': {
            'success': '[*] Skill passed all checks!',
            'errors': '[!] Audit completed with errors.',
            'warnings': '[!] Audit completed with warnings.',
        },
        'issues': {
            'file_not_found': '[FAIL] File not found: {file}',
            'permission_denied': '[FAIL] Permission denied: {file}',
        },
    },
    'zh': {
        'status': {
            'pass': '[通过]',
            'fail': '[失败]',
            'warn': '[警告]',
        },
        'audit': {
            'title': '[*] 审计技能: {name}',
            'path': '   路径: {path}',
        },
        'results': {
            'success': '[*] 技能通过所有检查!',
            'errors': '[!] 审计完成但存在错误。',
            'warnings': '[!] 审计完成但存在警告。',
        },
        'issues': {
            'file_not_found': '[失败] 文件未找到: {file}',
            'permission_denied': '[失败] 权限被拒绝: {file}',
        },
    },
}

def get_message(key: str, lang: str = None, **kwargs) -> str:
    """Get a localized message by key."""
    if lang is None:
        lang = CURRENT_LANG
    
    if lang not in MESSAGES:
        lang = DEFAULT_LANG
    
    keys = key.split('.')
    msg = MESSAGES.get(lang, MESSAGES[DEFAULT_LANG])
    
    for k in keys:
        if isinstance(msg, dict):
            msg = msg.get(k)
        if msg is None:
            return key
    
    if isinstance(msg, str) and kwargs:
        try:
            return msg.format(**kwargs)
        except KeyError:
            return msg
    
    return msg
```

**Usage / 使用:**
```python
from messages import get_message

# Get message with default language
print(get_message('status.pass'))

# Get message with specific language
print(get_message('audit.title', lang='zh', name='my-skill'))

# Get message with format arguments
print(get_message('issues.file_not_found', file='config.yaml'))
```

### 4. Language Environment Variables / 语言环境变量

**Use consistent environment variable naming:**

**使用一致的环境变量命名：**

| Skill Type | Environment Variable |
|------------|---------------------|
| All skills | `SKILL_LANG` |

**Usage / 使用:**
```powershell
# English output (default)
python scripts/main.py

# Chinese output
$env:SKILL_LANG='zh'
python scripts/main.py

# Or in bash
SKILL_LANG=zh python scripts/main.py
```

### 5. Multi-Language Support in SKILL.md / SKILL.md 中的多语言支持

**Recommended: Include both English and Chinese keywords in SKILL.md.**

**推荐：在 SKILL.md 中包含英文和中文关键词。**

**Example:**
```yaml
---
name: example-skill
description: A comprehensive tool for example purposes.
description_zh: 用于示例目的的综合工具。
keywords:
  - example
  - tool
  - utility
  - 示例
  - 工具
  - 实用
---
```

### 6. Unicode Characters in Comments / 注释中允许使用 Unicode

**Unicode characters (including Chinese, Japanese, Korean, etc.) are allowed in code comments.**

**Unicode 字符（包括中文、日文、韩文等）允许在代码注释中使用。**

**Correct:**
```python
# 这是一个中文注释
# This is a Chinese comment

# 检查文件是否存在 / Check if file exists
if not path.exists():
    pass
```

**Incorrect:**
```python
print("这是一个中文输出")  # OK in content, but use message dictionary for i18n
```

## Complete Implementation Example / 完整实现示例

### File Structure / 文件结构

```
my-skill/
├── SKILL.md
├── scripts/
│   ├── main.py
│   ├── messages.py
│   └── requirements.txt
└── references/
    └── documentation.md
```

### requirements.txt

```
colorama>=0.4.6
```

### main.py

```python
#!/usr/bin/env python3
"""My Skill - A comprehensive tool."""

import sys
from pathlib import Path
from colorama import init as colorama_init, Fore, Style
from messages import get_message, get_lang, set_lang

colorama_init()

PASS_TEXT = get_message('status.pass')
FAIL_TEXT = get_message('status.fail')
WARN_TEXT = get_message('status.warn')

def print_pass(msg):
    print(f"{Fore.GREEN}{PASS_TEXT}{Style.RESET_ALL} {msg}")

def print_fail(msg):
    print(f"{Fore.RED}{FAIL_TEXT}{Style.RESET_ALL} {msg}")

def print_warn(msg):
    print(f"{Fore.YELLOW}{WARN_TEXT}{Style.RESET_ALL} {msg}")

def main():
    print(get_message('audit.title', name='my-skill'))
    
    # Do work...
    
    print_pass(get_message('results.success'))
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## Common Mistakes / 常见错误

### 1. Using Emoji in Output / 在输出中使用 Emoji
```python
# Don't / 不要这样做
print("Success! ✓")

# Do / 应该这样做
print_pass(get_message('results.success'))
```

### 2. Hardcoding All Messages / 硬编码所有消息
```python
# Hardcoded / 硬编码
print("File not found")
print("Permission denied")

# Better / 更好
print_fail(get_message('issues.file_not_found', file=path))
print_fail(get_message('issues.permission_denied', file=path))
```

### 3. Using ANSI Escape Codes / 使用 ANSI 转义码
```python
# Don't / 不要这样做
print("\033[92m[PASS]\033[0m Success")

# Do / 应该这样做
print(f"{Fore.GREEN}[PASS]{Style.RESET_ALL} Success")
```

### 4. Ignoring Encoding / 忽略编码
```python
# May fail with Chinese text / 中文文本可能失败
content = open('chinese.txt').read()

# Better / 更好
content = open('chinese.txt', 'r', encoding='utf-8', errors='replace').read()
```

## Summary / 总结

| Practice / 实践 | Status / 状态 |
|----------------|-------------|
| No emoji in output / 输出中无 emoji | **Required / 必须** |
| colorama for terminal colors / 终端颜色使用 colorama | **Required / 必须** |
| Message dictionary for i18n / i18n 消息字典 | **Required / 必须** |
| Multi-language SKILL.md / 多语言 SKILL.md | **Recommended / 推荐** |
| Unicode in comments / 注释中的 Unicode | **Allowed / 允许** |
| encoding='utf-8' for Chinese / 中文用 UTF-8 | **Recommended / 推荐** |

**Key Takeaways / 关键要点:**

1. **Never use emoji in skill code output** / Skill 代码输出中从不使用 emoji
2. **Always use colorama for terminal colors** / 终端颜色输出必须使用 colorama
3. **Use message dictionaries for all user-facing text** / 所有面向用户的文本使用消息字典
4. **Support at least English and Chinese** / 至少支持英文和中文
5. **Include both English and Chinese in SKILL.md for discoverability** / SKILL.md 中包含英文和中文以提高可发现性
