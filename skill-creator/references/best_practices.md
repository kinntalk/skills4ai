# Best Practices for Skill Development

This guide outlines best practices for creating robust and reliable skills, derived from real-world experience and common pitfalls.

## File System Operations

### Cross-Platform Path Handling

When developing skills that interact with the file system (especially those involving external tools like browsers or compilers), always assume the skill might run on Windows, macOS, or Linux.

**Critical Issues on Windows:**
- **File Locking**: Windows enforces strict file locking. If a process (like a browser or editor) has a file open, you cannot delete or move it.
- **Path Encoding**: Many external tools (especially those ported from Linux) struggle with non-ASCII characters in file paths.
- **URI Schemes**: `file:///` URLs on Windows behave differently than on Unix-like systems.

**Best Practices:**
1. **Use `pathlib`**: Always use Python's `pathlib` module instead of string manipulation for paths.
   ```python
   from pathlib import Path
   # Good
   path = Path("folder") / "file.txt"
   # Avoid
   path = "folder/file.txt" 
   ```
2. **Safe Temporary Filenames**: When generating temporary files for external tools, use UUIDs to ensure filenames are ASCII-only and unique.
   ```python
   import uuid
   temp_name = f"temp_{uuid.uuid4().hex}.html"
   ```
3. **Data URIs**: If possible, avoid temporary files entirely by passing content via Data URIs.
   ```python
   import base64
   data_uri = f"data:text/html;base64,{base64.b64encode(content).decode()}"
   ```

### Async Operations & Race Conditions

When invoking external processes (like headless browsers, compilers, or converters), the return of the process call doesn't always mean the file system is ready.

**The Problem**:
A tool might return "success" while the OS is still flushing buffers or releasing file locks. Immediate attempts to read/move the output file may fail with `FileNotFoundError` or `PermissionError`.

**The Solution**:
Implement a polling/retry mechanism for file verification.

```python
import time

# Wait for file to appear (mitigate async filesystem delays)
for i in range(10):
    if output_path.exists():
        break
    time.sleep(0.5)
```

## Tool Integration

### Headless Browsers (html2image, playwright, puppeteer)

1. **Avoid `file:///` for dynamic content**: On Windows, passing a local HTML file path to a headless browser often fails if the path contains spaces or non-ASCII characters. Prefer **Data URIs**.
2. **Explicit Output Paths**: Always explicitly set the output directory to `cwd` or a known temp location. Default behaviors vary wildly across platforms.
3. **Dependency Checks**: Always verify the tool (e.g., Chrome/Edge) is installed before running, and provide helpful error messages if missing.

## Error Handling

### Graceful Failure

Skills should never crash silently or leave the user in a broken state.

1. **Clean Up**: Use `try...finally` blocks to ensure temporary files are deleted, even if the script errors out.
2. **Informative Errors**: Catch generic exceptions and print actionable advice (e.g., "Please install Chrome", "Check file permissions").
3. **Backup/Restore**: For skills that modify user files (like `manage_skills.py`), implement a backup-before-modify strategy to allow rollback on failure.
