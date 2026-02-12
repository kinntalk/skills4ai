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
print("[PASS] Check passed")
print("[FAIL] Check failed")
print("[WARN] Warning issued")
```

**Incorrect:**
```python
print("Check passed ✓")  # Emoji not allowed
print("Check failed ✗")   # Emoji not allowed
```

### 2. Use Message Dictionary for Output / 使用消息字典输出

**For skills with significant user-facing output, consider using a message dictionary.**

**对于有大量面向用户输出的 skill，考虑使用消息字典。**

**Example:**
```python
MESSAGES = {
    'en': {
        'pass': '[PASS] Check passed',
        'fail': '[FAIL] Check failed',
        'warn': '[WARN] Warning issued',
    },
    'zh': {
        'pass': '[通过] 检查通过',
        'fail': '[失败] 检查失败',
        'warn': '[警告] 发出警告',
    }
}

def get_message(key, lang='en'):
    return MESSAGES.get(lang, {}).get(key, key)

# Use / 使用
print(get_message('pass', lang='en'))
print(get_message('pass', lang='zh'))
```

### 3. Multi-Language Support in SKILL.md / SKILL.md 中的多语言支持

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

### 4. Unicode Characters are Allowed in Comments / 注释中允许使用 Unicode

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
print("这是一个中文输出")  # OK in content, but consider message dictionary for i18n
```

## Language Detection / 语言检测

### Detect User Language / 检测用户语言

**Trae provides language context through `<response_language>` tag.**

**Trae 通过 `<response_language>` 标签提供语言上下文。**

```python
def get_language():
    """Detect user language from system or context."""
    # In Trae skills, language may come from context
    # Default to English if not specified
    return 'zh' if '<response_language>当前处于中文环境' in str(sys.modules) else 'en'
```

## When to Implement i18n / 何时实现 i18n

### High Priority (Recommended) / 高优先级（推荐）
- Skills with extensive user-facing messages
- Skills used internationally
- Skills with complex user interactions

### Low Priority (Optional) / 低优先级（可选）
- Utility skills with minimal output
- Skills used primarily by developers
- Skills with technical, domain-specific output

## Common Mistakes / 常见错误

### 1. Using Emoji in Output / 在输出中使用 Emoji
```python
# Don't / 不要这样做
print("Success! ✓")

# Do / 应该这样做
print("[PASS] Success!")
```

### 2. Hardcoding All Messages / 硬编码所有消息
```python
# Hardcoded / 硬编码
print("File not found")
print("Permission denied")

# Better / 更好
MESSAGES = {
    'file_not_found': '[FAIL] File not found',
    'permission_denied': '[FAIL] Permission denied',
}
print(MESSAGES['file_not_found'])
```

### 3. Ignoring Encoding / 忽略编码
```python
# May fail with Chinese text / 中文文本可能失败
content = open('chinese.txt').read()

# Better / 更好
content = open('chinese.txt', 'r', encoding='utf-8').read()
```

## Summary / 总结

| Practice / 实践 | Status / 状态 |
|----------------|-------------|
| No emoji in output / 输出中无 emoji | **Required / 必须** |
| Message dictionary for i18n / i18n 消息字典 | **Recommended / 推荐** |
| Multi-language SKILL.md / 多语言 SKILL.md | **Recommended / 推荐** |
| Unicode in comments / 注释中的 Unicode | **Allowed / 允许** |
| encoding='utf-8' for Chinese / 中文用 UTF-8 | **Recommended / 推荐** |

**Key Takeaway / 关键要点:**
- Never use emoji in skill code output / Skill 代码输出中从不使用 emoji
- Use message dictionaries for better i18n when needed / 需要时使用消息字典以实现更好的 i18n
- Include both English and Chinese in SKILL.md for discoverability / SKILL.md 中包含英文和中文以提高可发现性
- Always use encoding='utf-8' for Chinese text / 中文文本始终使用 encoding='utf-8'
