---
name: x-file-manager
description: Local file perception and retrieval tool for AI Agents. Use when user wants to search files by name, type, size, hash, find duplicates, scan large files, or analyze local file system. Supports both Chinese and English queries like "查找大文件" or "find large files".
allowed-tools: Bash(python *)
---

# X File Manager

A comprehensive local file scanning and analysis skill for AI Agents. Provides powerful file perception capabilities including search, duplicate detection, hash calculation, and large file discovery.

## Features

- **File Name Search**: Fuzzy and regex-based file name search
- **File Type Filtering**: Filter by extension (e.g., .pdf, .mp4, .jpg)
- **File Size Filtering**: Find files by size range (e.g., >100MB)
- **Hash Calculation**: Calculate MD5, SHA1, SHA256 hashes
- **Duplicate Detection**: Find duplicate files based on content hash
- **Large File Scanner**: Identify the largest files in directories
- **Empty Directory Detection**: Find empty directories
- **Safety Mechanisms**: Timeout limits, file count limits, loop detection

## Script Directory

**Important**: All scripts are located in the `scripts/` subdirectory.

**Agent Execution Instructions**:
1. Determine this SKILL.md file's directory path as `SKILL_DIR`
2. Script path = `${SKILL_DIR}/scripts/<script-name>.py`
3. Replace all `${SKILL_DIR}` in this document with the actual path

## Quick Start

```bash
# Search files by name
python ${SKILL_DIR}/scripts/file_scanner.py search "D:/Documents" -n "report" --ext pdf

# Find largest files
python ${SKILL_DIR}/scripts/file_scanner.py large "C:/" --top 20

# Find duplicate files
python ${SKILL_DIR}/scripts/file_scanner.py duplicates "D:/Downloads" --min-size 1MB

# Calculate file hash
python ${SKILL_DIR}/scripts/file_scanner.py hash "D:/file.pdf" --algo md5 sha256

# Find empty directories
python ${SKILL_DIR}/scripts/file_scanner.py empty-dirs "D:/Projects"
```

## Commands

### search - Search Files by Name

```bash
python ${SKILL_DIR}/scripts/file_scanner.py search <path> -n <pattern> [options]
```

| Option | Description |
|--------|-------------|
| `<path>` | Root directory to search |
| `-n, --name` | File name pattern (required) |
| `--ext` | File extensions to include (space-separated) |
| `--min-size` | Minimum file size (e.g., 100MB, 1GB) |
| `--max-size` | Maximum file size |
| `--fuzzy` | Enable fuzzy matching (default: true) |
| `--case-sensitive` | Case sensitive search |
| `--max-depth` | Maximum search depth |
| `--format` | Output format: json (default) or text |

**Examples**:
```bash
# Search for PDF files containing "report"
python ${SKILL_DIR}/scripts/file_scanner.py search "D:/Documents" -n "report" --ext pdf

# Search for large video files
python ${SKILL_DIR}/scripts/file_scanner.py search "C:/" -n "video" --ext mp4 mkv --min-size 100MB

# Case-sensitive exact match
python ${SKILL_DIR}/scripts/file_scanner.py search "D:/Projects" -n "README.md" --case-sensitive --fuzzy false
```

### large - Find Largest Files

```bash
python ${SKILL_DIR}/scripts/file_scanner.py large <path> [options]
```

| Option | Description |
|--------|-------------|
| `<path>` | Root directory to scan |
| `--top` | Number of files to return (default: 20) |
| `--ext` | File extensions to include |
| `--format` | Output format: json (default) or text |

**Examples**:
```bash
# Find top 10 largest files
python ${SKILL_DIR}/scripts/file_scanner.py large "D:/" --top 10

# Find largest video files
python ${SKILL_DIR}/scripts/file_scanner.py large "C:/Users" --ext mp4 mkv avi --top 5
```

### duplicates - Find Duplicate Files

```bash
python ${SKILL_DIR}/scripts/file_scanner.py duplicates <path> [options]
```

| Option | Description |
|--------|-------------|
| `<path>` | Root directory to scan |
| `--ext` | File extensions to include |
| `--min-size` | Minimum file size to check |
| `--max-size` | Maximum file size to check |
| `--no-hash` | Compare by size only (faster but less accurate) |
| `--format` | Output format: json (default) or text |

**Examples**:
```bash
# Find all duplicate files
python ${SKILL_DIR}/scripts/file_scanner.py duplicates "D:/Downloads"

# Find duplicate images
python ${SKILL_DIR}/scripts/file_scanner.py duplicates "D:/Pictures" --ext jpg png gif

# Find duplicate files larger than 10MB
python ${SKILL_DIR}/scripts/file_scanner.py duplicates "D:/" --min-size 10MB
```

### hash - Calculate File Hash

```bash
python ${SKILL_DIR}/scripts/file_scanner.py hash <file> [options]
```

| Option | Description |
|--------|-------------|
| `<file>` | File path |
| `--algo` | Hash algorithms (default: md5 sha256) |
| `--format` | Output format: json (default) or text |

**Examples**:
```bash
# Calculate MD5 and SHA256
python ${SKILL_DIR}/scripts/file_scanner.py hash "D:/file.pdf"

# Calculate only MD5
python ${SKILL_DIR}/scripts/file_scanner.py hash "D:/file.pdf" --algo md5

# Calculate multiple hashes
python ${SKILL_DIR}/scripts/file_scanner.py hash "D:/file.pdf" --algo md5 sha1 sha256
```

### empty-dirs - Find Empty Directories

```bash
python ${SKILL_DIR}/scripts/file_scanner.py empty-dirs <path> [options]
```

| Option | Description |
|--------|-------------|
| `<path>` | Root directory to scan |
| `--format` | Output format: json (default) or text |

**Examples**:
```bash
# Find all empty directories
python ${SKILL_DIR}/scripts/file_scanner.py empty-dirs "D:/Projects"
```

### scan - General File Scan

```bash
python ${SKILL_DIR}/scripts/file_scanner.py scan <path> [options]
```

| Option | Description |
|--------|-------------|
| `<path>` | Root directory to scan |
| `--ext` | File extensions to include |
| `--min-size` | Minimum file size |
| `--max-size` | Maximum file size |
| `--max-depth` | Maximum scan depth |
| `--format` | Output format: json (default) or text |

**Examples**:
```bash
# Scan all PDF files
python ${SKILL_DIR}/scripts/file_scanner.py scan "D:/Documents" --ext pdf

# Scan large files
python ${SKILL_DIR}/scripts/file_scanner.py scan "C:/" --min-size 100MB
```

## Output Format

### Search Results (JSON)

```json
[
  {
    "path": "D:/Documents/report_2024.pdf",
    "size": 2458624,
    "size_human": "2.34 MB",
    "modified_time": "2024-03-10T14:30:00",
    "created_time": "2024-03-01T09:00:00",
    "extension": "pdf",
    "hash_md5": null,
    "hash_sha256": null
  }
]
```

### Duplicate Groups (JSON)

```json
[
  {
    "hash": "d41d8cd98f00b204e9800998ecf8427e",
    "size": 1024000,
    "size_human": "1000.00 KB",
    "file_count": 3,
    "wasted_space": 2048000,
    "wasted_space_human": "2000.00 KB",
    "files": [
      "D:/file1.txt",
      "D:/backup/file1.txt",
      "E:/copies/file1.txt"
    ]
  }
]
```

### Hash Results (JSON)

```json
{
  "md5": "d41d8cd98f00b204e9800998ecf8427e",
  "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
```

## Safety Mechanisms

The scanner includes built-in safety mechanisms to prevent runaway operations:

| Limit | Value | Description |
|-------|-------|-------------|
| MAX_FILES | 100,000 | Maximum files to process |
| MAX_DEPTH | 50 | Maximum directory depth |
| MAX_EXECUTION_TIME | 300s | Maximum execution time |
| MAX_FILE_SIZE_FOR_HASH | 1GB | Maximum file size for hash calculation |
| MAX_RESULTS | 10,000 | Maximum results to return |

When limits are exceeded, the scanner will:
1. Stop processing new files
2. Return results collected so far
3. Output a warning message to stderr

## Trigger Words

This skill is triggered when the user mentions:

**English**:
- "search files", "find files", "look for files"
- "duplicate files", "find duplicates", "duplicate detection"
- "large files", "big files", "largest files"
- "file hash", "calculate hash", "MD5", "SHA256"
- "empty directories", "empty folders"
- "file size", "file type", "file extension"

**Chinese**:
- "查找文件", "搜索文件", "找文件"
- "重复文件", "查重", "重复检测"
- "大文件", "最大的文件"
- "文件哈希", "计算哈希", "MD5", "SHA256"
- "空目录", "空文件夹"
- "文件大小", "文件类型", "文件扩展名"

## Best Practices for Agent

### Terminal Working Directory

After executing commands, change terminal's working directory:

```bash
# After running any file_scanner command
cd d:\workspace1\yusuan
```

### Performance Tips

1. **Use `--min-size` for duplicates**: When scanning for duplicates, always set a minimum size to avoid processing small files unnecessarily.

2. **Limit extensions**: Use `--ext` to filter specific file types for faster results.

3. **Set `--max-depth`**: Limit directory depth for large filesystems.

4. **Use `--no-hash` for quick check**: When you only need a quick estimate of potential duplicates, use `--no-hash` to compare by size only.

### Common Workflows

**Workflow 1: Find and clean duplicates**
```bash
# Step 1: Find duplicates larger than 10MB
python ${SKILL_DIR}/scripts/file_scanner.py duplicates "D:/" --min-size 10MB

# Step 2: Present results to user for confirmation
# Step 3: User decides which files to keep/delete
```

**Workflow 2: Analyze disk usage**
```bash
# Step 1: Find largest files
python ${SKILL_DIR}/scripts/file_scanner.py large "C:/" --top 20

# Step 2: Find empty directories
python ${SKILL_DIR}/scripts/file_scanner.py empty-dirs "C:/"

# Step 3: Present summary to user
```

**Workflow 3: Search and verify**
```bash
# Step 1: Search for files
python ${SKILL_DIR}/scripts/file_scanner.py search "D:/" -n "backup" --ext zip

# Step 2: Calculate hash for verification
python ${SKILL_DIR}/scripts/file_scanner.py hash "D:/backup_2024.zip"
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| FileNotFoundError | Path does not exist | Verify the path is correct |
| PermissionError | No read access | Run with appropriate permissions |
| ValueError | Invalid size format | Use format like "100MB", "1GB" |
| TimeoutError | Operation exceeded time limit | Reduce scope or increase limits |

## Dependencies

No external dependencies required. Uses only Python standard library:
- `hashlib` - Hash calculations
- `json` - Output formatting
- `pathlib` - Path handling
- `re` - Pattern matching
- `concurrent.futures` - Parallel processing

## Version History

- **1.0.0**: Initial release with search, large files, duplicates, hash, and empty-dirs commands
