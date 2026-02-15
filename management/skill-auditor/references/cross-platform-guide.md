# Cross-Platform Development Guide / 跨平台开发指南

## Overview / 概述

This guide explains best practices for developing cross-platform Trae skills that work correctly on Windows, macOS, and Linux.

本指南解释了开发跨平台 Trae skills 的最佳实践，确保在 Windows、macOS 和 Linux 上正确运行。

## Core Principles / 核心原则

### 1. Use pathlib Instead of os.path / 使用 pathlib 而非 os.path

**Why?**
- `pathlib` provides a more modern, object-oriented API
- `pathlib` automatically handles path separators
- `pathlib` works consistently across platforms

**为什么？**
- `pathlib` 提供更现代的面向对象 API
- `pathlib` 自动处理路径分隔符
- `pathlib` 在各平台上工作一致

**Bad practice / 不良实践：**
```python
import os

# Platform-dependent / 平台相关
path = os.path.join('folder', 'file.txt')

# Hardcoded separator / 硬编码分隔符
path = 'folder\\file.txt'  # Windows only / 仅 Windows
path = 'folder/file.txt'   # Unix only / 仅 Unix
```

**Good practice / 良好实践：**
```python
from pathlib import Path

# Cross-platform / 跨平台
path = Path('folder') / 'file.txt'

# Multiple levels / 多级
path = Path('folder') / 'subfolder' / 'file.txt'
```

### 2. No Platform-Specific Commands / 不使用平台特定命令

**Avoid:**
- `dir`, `del` on Windows
- `ls`, `rm` on Unix
- Platform-specific shell commands

**避免：**
- Windows 上的 `dir`, `del`
- Unix 上的 `ls`, `rm`
- 平台特定的 shell 命令

**Bad practice / 不良实践：**
```python
import os

# Windows only / 仅 Windows
os.system('dir')

# Unix only / 仅 Unix
os.system('ls -la')
```

**Good practice / 良好实践：**
```python
from pathlib import Path
import shutil

# List files / 列出文件
for file in Path('.').iterdir():
    print(file.name)

# Delete directory / 删除目录
shutil.rmtree('directory')
```

### 3. No Hardcoded Absolute Paths / 不使用硬编码绝对路径

**Bad practice / 不良实践：**
```python
# Windows absolute path / Windows 绝对路径
path = 'C:\\Users\\username\\file.txt'

# Unix absolute path / Unix 绝对路径
path = '/home/username/file.txt'

# macOS absolute path / macOS 绝对路径
path = '/Users/username/file.txt'
```

**Good practice / 良好实践：**
```python
from pathlib import Path

# Relative paths / 相对路径
path = Path('file.txt')

# Use current directory / 使用当前目录
path = Path.cwd() / 'file.txt'

# Use skill directory / 使用 skill 目录
skill_dir = Path(__file__).parent.parent
path = skill_dir / 'file.txt'
```

### 4. Use Subprocess Properly / 正确使用 Subprocess

**For subprocess calls, use `subprocess.run()` instead of `os.system()`.**

**对于子进程调用，使用 `subprocess.run()` 而非 `os.system()`。**

**Bad practice / 不良实践：**
```python
import os

# Less control / 控制较少
os.system('python script.py')

# Security risk / 安全风险
os.system(f'rm {user_input}')
```

**Good practice / 良好实践：**
```python
import subprocess

# More control / 更多控制
result = subprocess.run(
    ['python', 'script.py'],
    capture_output=True,
    text=True,
    encoding='utf-8',
    errors='replace'  # Handle encoding errors / 处理编码错误
)

# Safer / 更安全
result = subprocess.run(
    ['rm', user_input],
    capture_output=True
)
```

### 5. Handle Path Separators Correctly / 正确处理路径分隔符

**Never hardcode path separators in string literals.**

**永远不要在字符串字面量中硬编码路径分隔符。**

**Bad practice / 不良实践：**
```python
# Hardcoded Windows separator / 硬编码 Windows 分隔符
path = 'folder\\subfolder\\file.txt'

# Hardcoded Unix separator / 硬编码 Unix 分隔符
path = 'folder/subfolder/file.txt'

# Mixed separators / 混合分隔符
path = 'folder\\subfolder/file.txt'
```

**Good practice / 良好实践：**
```python
from pathlib import Path

# Automatic separator handling / 自动分隔符处理
path = Path('folder') / 'subfolder' / 'file.txt'

# String representation / 字符串表示
str_path = str(path)
```

## Common Cross-Platform Patterns / 常见跨平台模式

### File Operations / 文件操作

```python
from pathlib import Path

# Create directory / 创建目录
Path('new_folder').mkdir(exist_ok=True)

# Delete file / 删除文件
Path('file.txt').unlink()

# Copy file / 复制文件
import shutil
shutil.copy('source.txt', 'dest.txt')

# Move file / 移动文件
Path('old.txt').rename('new.txt')

# Check existence / 检查是否存在
if Path('file.txt').exists():
    print('File exists')
```

### Directory Traversal / 目录遍历

```python
from pathlib import Path

# List all files / 列出所有文件
for file in Path('.').iterdir():
    if file.is_file():
        print(file.name)

# Recursively list files / 递归列出文件
for file in Path('.').rglob('*.txt'):
    print(file)

# Find specific file / 查找特定文件
files = list(Path('.').glob('*.py'))
```

### Path Manipulation / 路径操作

```python
from pathlib import Path

# Get parent directory / 获取父目录
parent = Path('folder/file.txt').parent

# Get file extension / 获取文件扩展名
ext = Path('file.txt').suffix  # '.txt'

# Get file name without extension / 获取不带扩展名的文件名
name = Path('file.txt').stem  # 'file'

# Join paths / 连接路径
path = Path('folder') / 'subfolder' / 'file.txt'

# Resolve absolute path / 解析绝对路径
abs_path = Path('file.txt').resolve()
```

## Platform-Specific Considerations / 平台特定注意事项

### Windows / Windows
- Path separator: `\` (backslash) / 路径分隔符：`\`（反斜杠）
- Line separator: `\r\n` / 行分隔符：`\r\n`
- File system: case-insensitive / 文件系统：不区分大小写
- Common issues: encoding, path length limits / 常见问题：编码、路径长度限制

### Unix/Linux / Unix/Linux
- Path separator: `/` (forward slash) / 路径分隔符：`/`（正斜杠）
- Line separator: `\n` / 行分隔符：`\n`
- File system: case-sensitive / 文件系统：区分大小写
- Common issues: permissions, symbolic links / 常见问题：权限、符号链接

### macOS / macOS
- Path separator: `/` (forward slash) / 路径分隔符：`/`（正斜杠）
- Line separator: `\n` / 行分隔符：`\n`
- File system: case-insensitive (default) / 文件系统：不区分大小写（默认）
- Common issues: case sensitivity settings / 常见问题：区分大小写设置

## Summary / 总结

| Practice / 实践 | Recommendation / 推荐 |
|----------------|-------------------|
| Path operations / 路径操作 | Use `pathlib.Path()` / 使用 `pathlib.Path()` |
| Platform commands / 平台命令 | Avoid `dir`, `ls`, `rm` / 避免 `dir`, `ls`, `rm` |
| Absolute paths / 绝对路径 | Use relative paths / 使用相对路径 |
| Path separators / 路径分隔符 | Never hardcode / 永不硬编码 |
| Subprocess calls / 子进程调用 | Use `subprocess.run()` / 使用 `subprocess.run()` |
| File encoding / 文件编码 | Use `encoding='utf-8'` for Chinese / 中文使用 `encoding='utf-8'` |

**Key Takeaway / 关键要点:**
- Always use `pathlib` for path operations / 始终使用 `pathlib` 进行路径操作
- Avoid platform-specific commands and paths / 避免平台特定的命令和路径
- Use relative paths instead of absolute paths / 使用相对路径而非绝对路径
- Never hardcode path separators / 永不硬编码路径分隔符
- Test on multiple platforms when possible / 尽可能在多个平台上测试
