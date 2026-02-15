# File Encoding Guide / 文件编码指南

## Overview / 概述

This guide explains best practices for file encoding in Trae skills development.

本指南解释了 Trae skills 开发中文件编码的最佳实践。

## Key Principles / 关键原则

### 1. UTF-8 is Recommended for Chinese Content / UTF-8 是中文内容的推荐选择

**For Chinese text files:**
- Use `encoding='utf-8'` when reading/writing files containing Chinese characters
- This ensures consistent behavior across platforms

**对于中文文本文件：**
- 读取/写入包含中文字符的文件时使用 `encoding='utf-8'`
- 这确保了跨平台的一致性

**Example:**
```python
# Recommended for Chinese content / 中文内容推荐
content = Path('file.txt').read_text(encoding='utf-8')
Path('file.txt').write_text(content, encoding='utf-8')

# Alternative: system default encoding / 替代方案：系统默认编码
content = Path('file.txt').read_text()  # Uses system locale
```

### 2. Encoding is Context-Dependent / 编码取决于实际场景

**Important: encoding='utf-8' is NOT mandatory**
- Use UTF-8 for Chinese text files (recommended)
- Use ASCII for pure English text
- Use binary mode for non-text files
- Match the actual encoding of the file you're reading

**重要：encoding='utf-8' 不是强制的**
- UTF-8 用于中文文本文件（推荐）
- ASCII 用于纯英文文本
- 二进制模式用于非文本文件
- 匹配您正在读取文件的实际编码

**Examples:**
```python
# Chinese text / 中文文本
Path('chinese.txt').read_text(encoding='utf-8')

# English text / 英文文本
Path('english.txt').read_text(encoding='ascii')

# Binary file / 二进制文件
Path('image.png').read_bytes()

# System default / 系统默认
Path('file.txt').read_text()
```

### 3. Always Specify Encoding Explicitly / 始终明确指定编码

**Why?**
- Python's default encoding varies by platform and locale
- On Windows, it might be CP1252 or GBK
- On Unix, it's typically UTF-8
- Explicit encoding prevents crashes when reading files

**为什么？**
- Python 的默认编码因平台和区域设置而异
- 在 Windows 上，可能是 CP1252 或 GBK
- 在 Unix 上，通常是 UTF-8
- 明确指定编码可防止读取文件时崩溃

**Bad practice / 不良实践：**
```python
# Might crash on Windows with Chinese files / 在 Windows 上处理中文文件可能崩溃
content = open('chinese.txt').read()
```

**Good practice / 良好实践：**
```python
# Explicit encoding / 明确指定编码
content = open('chinese.txt', 'r', encoding='utf-8').read()
```

## Common Use Cases / 常见用例

### Reading SKILL.md
```python
# SKILL.md typically contains both English and Chinese
skill_md = Path('SKILL.md').read_text(encoding='utf-8')
```

### Reading Configuration Files
```python
# JSON files are UTF-8 by default
config = json.loads(Path('config.json').read_text(encoding='utf-8'))

# YAML files are UTF-8 by default
config = yaml.safe_load(Path('config.yaml').read_text(encoding='utf-8'))
```

### Writing Output Files
```python
# For Chinese output
Path('output.txt').write_text(chinese_text, encoding='utf-8')

# For English output
Path('output.txt').write_text(english_text, encoding='ascii', errors='ignore')
```

## Summary / 总结

| Scenario / 场景 | Recommended Encoding / 推荐编码 |
|----------------|----------------------------|
| Chinese text / 中文文本 | `encoding='utf-8'` |
| English text / 英文文本 | `encoding='ascii'` or `encoding='utf-8'` |
| Mixed language / 混合语言 | `encoding='utf-8'` |
| Binary files / 二进制文件 | Use `read_bytes()` / 使用 `read_bytes()` |
| System-dependent / 系统相关 | Omit encoding or use default / 省略编码或使用默认 |

**Remember: Choose encoding based on actual file content, not arbitrary rules.**

**记住：根据实际文件内容选择编码，而不是任意规则。**
