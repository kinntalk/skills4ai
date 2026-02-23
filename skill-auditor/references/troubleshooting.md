# Troubleshooting Guide

This document provides solutions to common issues encountered when using the skill-auditor, including false positives, security issues, quality issues, and frequently asked questions.

## Table of Contents

- [Common False Positives](#common-false-positives)
- [Security Issues Solutions](#security-issues-solutions)
- [Quality Issues Solutions](#quality-issues-solutions)
- [Frequently Asked Questions](#frequently-asked-questions)

## Common False Positives

### Issue: "eval() detected" but it's safe

**Problem:** The auditor flags `eval()` usage even though you're using it safely with trusted data.

**Solution:**
```python
# If you're using eval with trusted data only, add a comment to document this
# SECURITY: eval is used only with trusted configuration data
config_value = eval(config_string)  # Only trusted config data
```

**Better approach:** Use safer alternatives:
```python
# Use ast.literal_eval for literals
import ast
config_value = ast.literal_eval(config_string)

# Or use json.loads for JSON data
import json
config_value = json.loads(config_string)
```

---

### Issue: "Sensitive data in logs" but it's not sensitive

**Problem:** The auditor flags log messages containing words like "password", "token", or "key" even when they're not logging actual sensitive values.

**Solution:**
```python
# BAD: Auditor flags this
logger.info("User password reset requested")

# GOOD: Use different wording
logger.info("User account recovery requested")

# GOOD: Or use structured logging without sensitive keywords
logger.info("Password reset", extra={'user_id': user_id})
```

---

### Issue: "User input in subprocess" but input is validated

**Problem:** The auditor flags subprocess calls with user input even though you've validated it beforehand.

**Solution:**
```python
# Add validation comment and use allowlist
ALLOWED_COMMANDS = {'ls', 'pwd', 'cat'}

def execute_command(user_command):
    # Validate command is in allowlist
    if user_command not in ALLOWED_COMMANDS:
        raise ValueError(f"Command not allowed: {user_command}")
    
    # Use list arguments, not shell=True
    subprocess.run([user_command], check=True)
```

---

### Issue: "Hardcoded absolute path" but it's a system path

**Problem:** The auditor flags absolute paths to system directories like `/tmp` or `C:\Windows`.

**Solution:**
```python
# BAD: Hardcoded absolute path
temp_dir = "/tmp/myapp"

# GOOD: Use pathlib and relative paths
import tempfile
from pathlib import Path

temp_dir = Path(tempfile.gettempdir()) / "myapp"

# GOOD: Or use environment variables
import os
temp_dir = Path(os.getenv('TEMP', '/tmp')) / "myapp"
```

---

## Security Issues Solutions

### Issue: Code Injection (eval/exec)

**Problem:** Using `eval()` or `exec()` with user input.

**Solution:**
```python
# VULNERABLE:
def calculate(expression):
    return eval(expression)

# SECURE: Use ast.literal_eval for literals
import ast

def calculate(expression):
    try:
        return ast.literal_eval(expression)
    except (ValueError, SyntaxError):
        raise ValueError("Invalid expression")

# SECURE: Use a safe expression evaluator
import operator

def safe_calculate(expression):
    ops = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv
    }
    
    # Parse and validate expression
    tokens = expression.split()
    if len(tokens) != 3:
        raise ValueError("Invalid expression format")
    
    a, op, b = tokens
    if op not in ops:
        raise ValueError(f"Invalid operator: {op}")
    
    try:
        a, b = float(a), float(b)
    except ValueError:
        raise ValueError("Invalid numbers")
    
    return ops[op](a, b)
```

---

### Issue: Command Injection (subprocess with shell=True)

**Problem:** Using `subprocess.run()` with `shell=True` and user input.

**Solution:**
```python
# VULNERABLE:
def run_command(cmd):
    subprocess.run(cmd, shell=True)

# SECURE: Use list arguments without shell
def run_command(cmd_args):
    # cmd_args should be a list like ['ls', '-la']
    subprocess.run(cmd_args, check=True)

# SECURE: Validate and use allowlist
ALLOWED_COMMANDS = {
    'list': ['ls', '-la'],
    'status': ['git', 'status']
}

def run_command(command_name):
    if command_name not in ALLOWED_COMMANDS:
        raise ValueError(f"Command not allowed: {command_name}")
    
    subprocess.run(ALLOWED_COMMANDS[command_name], check=True)
```

---

### Issue: Path Traversal

**Problem:** User input used in file paths without validation.

**Solution:**
```python
# VULNERABLE:
def read_file(filename):
    with open(filename) as f:
        return f.read()

# SECURE: Validate path is within allowed directory
from pathlib import Path

def read_file(filename):
    file_path = Path(filename).resolve()
    allowed_dir = Path('/data/files').resolve()
    
    # Check if file is within allowed directory
    try:
        file_path.relative_to(allowed_dir)
    except ValueError:
        raise PermissionError("File not in allowed directory")
    
    with open(file_path) as f:
        return f.read()

# SECURE: Use safe path joining
def safe_path_join(base, *parts):
    base_path = Path(base).resolve()
    result = base_path
    for part in parts:
        result = (result / part).resolve()
    
    # Ensure result is still within base
    try:
        result.relative_to(base_path)
    except ValueError:
        raise PermissionError("Path traversal detected")
    
    return result
```

---

### Issue: Hardcoded Sensitive Data

**Problem:** API keys, passwords, or tokens hardcoded in source code.

**Solution:**
```python
# VULNERABLE:
api_key = "sk-1234567890abcdef"
password = "mysecretpassword"

# SECURE: Use environment variables
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('API_KEY')
if not api_key:
    raise ValueError("API_KEY environment variable not set")

password = os.getenv('DB_PASSWORD')
if not password:
    raise ValueError("DB_PASSWORD environment variable not set")

# SECURE: Use configuration file (not in version control)
import yaml

with open('config/secrets.yaml', encoding='utf-8') as f:
    secrets = yaml.safe_load(f)

api_key = secrets['api_key']
password = secrets['database']['password']

# SECURE: Use secret management service
# For production, use AWS Secrets Manager, Azure Key Vault, etc.
```

---

## Quality Issues Solutions

### Issue: Bare Except Clause

**Problem:** Using `except:` without specifying exception type.

**Solution:**
```python
# BAD:
try:
    risky_operation()
except:
    print("Error occurred")

# GOOD: Use specific exception types
try:
    risky_operation()
except ValueError as e:
    print(f"Invalid value: {e}")
except IOError as e:
    print(f"I/O error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
    raise  # Re-raise if unexpected

# GOOD: Or use finally for cleanup
try:
    risky_operation()
except ValueError as e:
    print(f"Invalid value: {e}")
finally:
    cleanup()
```

---

### Issue: No Input Validation

**Problem:** Functions don't validate input parameters.

**Solution:**
```python
# BAD:
def process_data(data):
    return data.upper()

# GOOD: Add type and value validation
def process_data(data):
    if not isinstance(data, str):
        raise TypeError("data must be a string")
    
    if len(data) == 0:
        raise ValueError("data cannot be empty")
    
    if len(data) > 1000:
        raise ValueError("data too long (max 1000 characters)")
    
    return data.upper()

# GOOD: Use type hints and validation libraries
from typing import Union
from pydantic import BaseModel, validator

class DataInput(BaseModel):
    value: str
    
    @validator('value')
    def validate_value(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('value cannot be empty')
        if len(v) > 1000:
            raise ValueError('value too long')
        return v.strip()

def process_data(input_data: DataInput) -> str:
    return input_data.value.upper()
```

---

### Issue: Excessive Print Statements

**Problem:** Too many print statements making output verbose.

**Solution:**
```python
# BAD: Too many print statements
def process_data(data):
    print("Starting processing...")
    print(f"Data length: {len(data)}")
    for i, item in enumerate(data):
        print(f"Processing item {i+1}...")
        result = transform(item)
        print(f"Item {i+1} processed")
    print("Done!")
    return result

# GOOD: Use logging with appropriate levels
import logging

logger = logging.getLogger(__name__)

def process_data(data):
    logger.info(f"Processing {len(data)} items")
    results = []
    for item in data:
        result = transform(item)
        results.append(result)
        logger.debug(f"Processed item: {item}")
    logger.info("Processing complete")
    return results

# GOOD: Or use progress bars for long operations
from tqdm import tqdm

def process_data(data):
    results = []
    for item in tqdm(data, desc="Processing"):
        result = transform(item)
        results.append(result)
    return results
```

---

### Issue: Long Functions

**Problem:** Functions are too long and complex.

**Solution:**
```python
# BAD: 100+ line function
def process_order(order):
    # 50 lines of validation
    # 30 lines of processing
    # 20 lines of saving
    pass

# GOOD: Split into smaller functions
def validate_order(order):
    """Validate order data."""
    if not order.get('customer_id'):
        raise ValueError("Missing customer_id")
    if not order.get('items'):
        raise ValueError("No items in order")
    # ... more validation
    return True

def calculate_total(order):
    """Calculate order total."""
    total = 0
    for item in order['items']:
        total += item['price'] * item['quantity']
    return total

def save_order(order):
    """Save order to database."""
    # ... save logic
    pass

def process_order(order):
    """Process order with validation, calculation, and saving."""
    validate_order(order)
    order['total'] = calculate_total(order)
    save_order(order)
    return order
```

---

## Frequently Asked Questions

### General Questions

**Q: What check level should I use?**

A: 
- Use `relaxed` during initial development for quick feedback
- Use `standard` for regular development and testing (default)
- Use `strict` before publishing to production or for security-critical applications

**Q: How do I ignore a specific check?**

A: Currently, the skill-auditor doesn't support ignoring specific checks. If you believe a check is a false positive, consider:
1. Refactoring code to avoid the pattern
2. Adding comments to document why the pattern is safe
3. Reporting the issue for improvement

**Q: Can I run the auditor in CI/CD?**

A: Yes! See the CI/CD integration example in SKILL.md. You can use JSON output for programmatic parsing and fail the build if critical issues are found.

**Q: How often should I run the auditor?**

A: 
- Run it locally before committing changes
- Run it in CI/CD on every pull request
- Run it in CI/CD on every push to main branch
- Run it with strict mode before releases

---

### Security Questions

**Q: Why is eval() always flagged as critical?**

A: `eval()` and `exec()` are flagged as critical because they can execute arbitrary code. Even if you think the input is trusted, it's easy for vulnerabilities to be introduced later. Use safer alternatives like `ast.literal_eval()` or JSON parsing.

**Q: What's the difference between shell=True and shell=False in subprocess?**

A: 
- `shell=True`: Uses the system shell, which is vulnerable to command injection if user input is included
- `shell=False` (default): Executes the command directly without shell, which is much safer

Always use `shell=False` with list arguments when possible.

**Q: How do I handle file uploads securely?**

A: 
1. Validate file type and size
2. Use safe file paths (within allowed directories)
3. Scan uploaded files for malware
4. Store files outside web root
5. Use random filenames to prevent overwrites
6. Set appropriate file permissions

```python
from pathlib import Path
import uuid

def handle_upload(file, allowed_types, max_size):
    # Validate file type
    if file.content_type not in allowed_types:
        raise ValueError("Invalid file type")
    
    # Validate file size
    if len(file.read()) > max_size:
        raise ValueError("File too large")
    file.seek(0)
    
    # Generate safe filename
    ext = Path(file.filename).suffix
    safe_filename = f"{uuid.uuid4()}{ext}"
    
    # Save to allowed directory
    upload_dir = Path('/data/uploads')
    upload_dir.mkdir(exist_ok=True)
    
    file_path = upload_dir / safe_filename
    with open(file_path, 'wb') as f:
        f.write(file.read())
    
    return file_path
```

---

### Quality Questions

**Q: Why should I use specific exception types instead of generic Exception?**

A: Using specific exception types:
1. Makes it clear what errors you're handling
2. Prevents catching unexpected errors (like SystemExit)
3. Allows different handling for different error types
4. Makes code more maintainable and debuggable

**Q: How do I choose the right log level?**

A: 
- **DEBUG**: Detailed diagnostic information for developers
- **INFO**: General informational messages about normal operation
- **WARNING**: Something unexpected but not critical (e.g., deprecated API usage)
- **ERROR**: Error occurred that needs attention but application can continue
- **CRITICAL**: Serious error, application may not continue

**Q: What's the recommended function length?**

A: Generally, functions should be:
- Less than 50 lines for most cases
- Less than 100 lines for complex logic
- Split into smaller functions if they're doing multiple things

If a function is doing multiple things, use the Single Responsibility Principle to split it.

---

### Output Quality Questions

**Q: Why does the auditor flag long comments?**

A: Long comments can indicate:
1. Complex code that needs refactoring
2. Poor code structure
3. Better suited for documentation files

Consider moving long explanations to:
- Docstrings
- README files
- Separate documentation
- Inline code improvements

**Q: How do I reduce token usage?**

A: 
1. Remove redundant code
2. Consolidate similar functions
3. Remove verbose comments (move to documentation)
4. Use more concise algorithms
5. Remove unused imports and variables
6. Use list comprehensions instead of loops where appropriate

**Q: What's the difference between print() and logging?**

A: 
- **print()**: Simple output to stdout, no levels or filtering, not suitable for production
- **logging**: Structured logging with levels, can be filtered, supports handlers (file, syslog, etc.), better for production

Use logging for production code, print() only for quick debugging or CLI tools.

---

## Getting Help

If you encounter issues not covered in this guide:

1. **Check the documentation**: Review SKILL.md, security-checks.md, and quality-checks.md
2. **Search for similar issues**: Look at existing skills for patterns
3. **Ask for help**: Consult with your team or community
4. **Report bugs**: If you believe the auditor is incorrect, report the issue

## Best Practices

1. **Run the auditor regularly**: Make it part of your development workflow
2. **Fix issues promptly**: Don't let security issues accumulate
3. **Use strict mode before releases**: Ensure production code meets all standards
4. **Review false positives**: Understand why something is flagged before dismissing
5. **Keep dependencies updated**: Regularly update to get latest security checks
6. **Document exceptions**: Add comments when you need to use a pattern that's flagged
7. **Use CI/CD integration**: Automate audits in your pipeline
8. **Educate your team**: Share knowledge about security and quality best practices
