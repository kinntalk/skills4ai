# Quality Checks Reference

This document provides detailed information about quality checks performed by the skill-auditor, including examples of good and bad patterns, improvement suggestions, and best practices.

## Quality Checks

### 1. Error Handling Patterns

**Severity:** MEDIUM

**Description:** Validates error handling patterns including missing try-except blocks in risky operations, bare except clauses, exception handling specificity, and proper error propagation.

#### Bad Patterns

```python
# BAD: Bare except clause
try:
    risky_operation()
except:  # Catches all exceptions, including SystemExit
    print("Error occurred")

# BAD: Generic Exception handler
try:
    risky_operation()
except Exception as e:  # Too generic
    print(f"Error: {e}")

# BAD: No error handling for risky operations
def read_file(filename):
    with open(filename) as f:  # Can raise FileNotFoundError, PermissionError
        return f.read()

# BAD: Swallowing exceptions
try:
    risky_operation()
except ValueError:
    pass  # Silent failure
```

#### Good Patterns

```python
# GOOD: Specific exception types
try:
    risky_operation()
except ValueError as e:
    print(f"Invalid value: {e}")
except IOError as e:
    print(f"I/O error: {e}")

# GOOD: Proper error handling for risky operations
def read_file(filename):
    try:
        with open(filename) as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filename}")
    except PermissionError:
        raise PermissionError(f"Permission denied: {filename}")
    except IOError as e:
        raise IOError(f"Error reading file {filename}: {e}")

# GOOD: Proper error propagation
def process_data(data):
    try:
        result = transform(data)
        return result
    except ValueError as e:
        logger.error(f"Data transformation failed: {e}")
        raise  # Re-raise for caller to handle

# GOOD: Context-specific error handling
def process_user_input(user_input):
    try:
        value = int(user_input)
        return value
    except ValueError:
        raise ValueError(f"Invalid integer input: {user_input}")
```

#### Improvement Suggestions

1. **Use specific exception types** instead of bare except or generic Exception
2. **Handle risky operations** with appropriate try-except blocks
3. **Log errors** before re-raising for debugging
4. **Provide context** in error messages
5. **Don't swallow exceptions** unless intentional
6. **Use finally** for cleanup code
7. **Consider custom exceptions** for application-specific errors

---

### 2. Logging Practices

**Severity:** LOW

**Description:** Validates logging best practices including proper logging level usage, sensitive data in logs, log message formatting, and structured logging patterns.

#### Bad Patterns

```python
# BAD: Logging sensitive data
import logging

def login(username, password):
    logging.info(f"User login: {username}, password: {password}")  # Sensitive!
    # ... login logic

# BAD: Using print instead of logging
def process_data(data):
    print("Processing data")  # Should use logging
    # ... processing logic

# BAD: Wrong log level
def debug_function():
    logging.critical("Debug information")  # Should be logging.debug()

# BAD: Inconsistent log format
logging.info("Processing started")
logging.warning("Warning: something happened")
logging.error("Error occurred!")
```

#### Good Patterns

```python
# GOOD: Avoid logging sensitive data
import logging

def login(username, password):
    logging.info(f"User login attempt: {username}")
    # ... login logic (never log password)

# GOOD: Using proper logging
import logging

logger = logging.getLogger(__name__)

def process_data(data):
    logger.info("Processing data")
    try:
        result = transform(data)
        logger.info(f"Successfully processed {len(data)} items")
        return result
    except Exception as e:
        logger.error(f"Failed to process data: {e}")
        raise

# GOOD: Appropriate log levels
def debug_function():
    logger.debug("Debug information")  # Use debug for detailed info

def warning_function():
    logger.warning("Warning: something unexpected but not critical")

def error_function():
    logger.error("Error occurred that needs attention")

# GOOD: Structured logging
logger.info("Processing started", extra={
    'user_id': user_id,
    'action': 'process',
    'timestamp': datetime.now().isoformat()
})

# GOOD: Consistent log format with context
logger.info(
    "Processing started",
    extra={'user_id': user_id, 'action': 'process'}
)
```

#### Improvement Suggestions

1. **Never log sensitive data** (passwords, tokens, API keys)
2. **Use appropriate log levels**:
   - DEBUG: Detailed diagnostic information
   - INFO: General informational messages
   - WARNING: Something unexpected but not critical
   - ERROR: Error occurred that needs attention
   - CRITICAL: Serious error, application may not continue
3. **Use structured logging** with context (user_id, action, timestamp)
4. **Configure log format** consistently across application
5. **Use logger instances** instead of module-level logging
6. **Log exceptions** with traceback information
7. **Avoid excessive logging** that impacts performance

---

### 3. Input Validation

**Severity:** HIGH

**Description:** Validates input validation implementation including user input sanitization, type checking, and boundary validation.

#### Bad Patterns

```python
# BAD: No input validation
def process_user_input(user_input):
    return user_input.upper()  # What if user_input is not a string?

# BAD: Trusting user input
def execute_command(command):
    os.system(command)  # Dangerous!

# BAD: No boundary checking
def get_array_element(arr, index):
    return arr[index]  # IndexError possible

# BAD: No type checking
def calculate_discount(price, discount):
    return price * discount  # What if inputs are not numbers?
```

#### Good Patterns

```python
# GOOD: Comprehensive input validation
def process_user_input(user_input):
    if not isinstance(user_input, str):
        raise TypeError("Input must be a string")
    
    if len(user_input) == 0:
        raise ValueError("Input cannot be empty")
    
    if len(user_input) > 1000:
        raise ValueError("Input too long (max 1000 characters)")
    
    # Sanitize input
    sanitized = user_input.strip()
    return sanitized.upper()

# GOOD: Validate and sanitize commands
ALLOWED_COMMANDS = {'ls', 'pwd', 'echo'}

def execute_command(command):
    if not isinstance(command, str):
        raise TypeError("Command must be a string")
    
    # Split and validate
    parts = command.split()
    if not parts:
        raise ValueError("Empty command")
    
    if parts[0] not in ALLOWED_COMMANDS:
        raise ValueError(f"Command not allowed: {parts[0]}")
    
    # Execute safely
    subprocess.run(parts, check=True)

# GOOD: Boundary checking
def get_array_element(arr, index):
    if not isinstance(arr, (list, tuple)):
        raise TypeError("arr must be a list or tuple")
    
    if not isinstance(index, int):
        raise TypeError("index must be an integer")
    
    if index < 0 or index >= len(arr):
        raise IndexError(f"Index {index} out of bounds (length: {len(arr)})")
    
    return arr[index]

# GOOD: Type checking and validation
def calculate_discount(price, discount):
    # Type checking
    if not isinstance(price, (int, float)):
        raise TypeError("price must be a number")
    
    if not isinstance(discount, (int, float)):
        raise TypeError("discount must be a number")
    
    # Value validation
    if price < 0:
        raise ValueError("price cannot be negative")
    
    if discount < 0 or discount > 1:
        raise ValueError("discount must be between 0 and 1")
    
    return price * discount

# GOOD: Using validation libraries
from pydantic import BaseModel, validator

class UserInput(BaseModel):
    name: str
    age: int
    email: str
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('name cannot be empty')
        return v.strip()
    
    @validator('age')
    def age_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('age must be positive')
        return v
    
    @validator('email')
    def email_must_be_valid(cls, v):
        if '@' not in v:
            raise ValueError('invalid email format')
        return v
```

#### Improvement Suggestions

1. **Always validate user input** before processing
2. **Check types** using isinstance() or type hints
3. **Validate boundaries** (length, range, min/max values)
4. **Sanitize input** to remove dangerous characters
5. **Use allowlists** for commands, filenames, etc.
6. **Consider validation libraries** (pydantic, marshmallow)
7. **Provide clear error messages** for validation failures
8. **Validate at the boundary** (API endpoints, user input handlers)

---

### 4. Output Sanitization

**Severity:** MEDIUM

**Description:** Validates output sanitization including HTML/XML escaping, JSON serialization safety, and user output encoding.

#### Bad Patterns

```python
# BAD: No HTML escaping
def render_user_name(name):
    return f"<div>{name}</div>"  # XSS vulnerability if name contains HTML

# BAD: Unsafe JSON serialization
def serialize_data(data):
    return json.dumps(data.__dict__)  # May expose sensitive fields

# BAD: Direct user output
def display_user_input(user_input):
    print(user_input)  # May contain control characters

# BAD: No encoding validation
def read_and_display(filename):
    with open(filename) as f:
        print(f.read())  # May contain binary or invalid encoding
```

#### Good Patterns

```python
# GOOD: HTML escaping
import html

def render_user_name(name):
    escaped_name = html.escape(name)
    return f"<div>{escaped_name}</div>"

# GOOD: Using template engines with auto-escaping
from jinja2 import Template

template = Template("Hello, {{ name }}!")
def render_user_name(name):
    return template.render(name=name)  # Auto-escapes

# GOOD: Safe JSON serialization
def serialize_data(data):
    # Only include safe fields
    safe_data = {
        'id': data.id,
        'name': data.name,
        'email': data.email
        # Exclude: password, token, secret
    }
    return json.dumps(safe_data)

# GOOD: Using dataclasses with __dict__ filtering
from dataclasses import dataclass, asdict

@dataclass
class UserData:
    id: int
    name: str
    email: str
    password: str  # Sensitive
    
    def to_safe_dict(self):
        data = asdict(self)
        data.pop('password', None)
        return data

def serialize_data(data):
    return json.dumps(data.to_safe_dict())

# GOOD: Sanitize user output
import re

def sanitize_output(text):
    # Remove control characters
    text = re.sub(r'[\x00-\x1F\x7F]', '', text)
    # Limit length
    text = text[:1000]
    return text

def display_user_input(user_input):
    sanitized = sanitize_output(user_input)
    print(sanitized)

# GOOD: Encoding validation
def read_and_display(filename):
    try:
        with open(filename, encoding='utf-8') as f:
            content = f.read()
        print(content)
    except UnicodeDecodeError:
        print("[Error: File contains invalid encoding]")
    except IOError as e:
        print(f"[Error: {e}]")
```

#### Improvement Suggestions

1. **Always escape HTML/XML** before rendering user content
2. **Use template engines** with auto-escaping (Jinja2, Django templates)
3. **Filter sensitive fields** before serialization
4. **Sanitize output** to remove control characters
5. **Validate encoding** before displaying file content
6. **Use safe serialization** methods (exclude sensitive data)
7. **Limit output length** to prevent buffer overflows
8. **Consider Content Security Policy** for web applications

---

### 5. Dependency Security

**Severity:** MEDIUM

**Description:** Validates dependency security including known vulnerabilities, outdated packages, and insecure dependencies.

#### Bad Patterns

```python
# BAD: Using outdated vulnerable packages
# requirements.txt
flask==0.12.5  # Old version with known vulnerabilities
requests==2.18.0  # Old version with security issues

# BAD: No version pinning
# requirements.txt
flask
requests
django

# BAD: Using deprecated libraries
import hashlib
hash = hashlib.md5()  # MD5 is cryptographically broken

# BAD: Not updating dependencies
# Using packages from years ago without updates
```

#### Good Patterns

```python
# GOOD: Using secure, up-to-date packages
# requirements.txt
flask==3.0.0
requests==2.31.0
django==5.0.0

# GOOD: Using version ranges for updates
# requirements.txt
flask>=3.0.0,<4.0.0
requests>=2.31.0,<3.0.0

# GOOD: Using secure hash algorithms
import hashlib
hash = hashlib.sha256()  # SHA-256 is secure

# GOOD: Regular dependency updates
# Use tools like pip-audit, safety, or dependabot
# pip-audit checks for known vulnerabilities
# pip install pip-audit
# pip-audit

# GOOD: Using security-focused packages
# Use packages with active maintenance
# Check for security advisories
# Review package source code for critical functionality

# GOOD: Dependency scanning in CI/CD
# .github/workflows/security.yml
name: Security Scan
on: [push, pull_request]
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run pip-audit
        run: pip-audit
```

#### Improvement Suggestions

1. **Keep dependencies updated** to latest secure versions
2. **Use version pinning** to prevent accidental updates
3. **Scan for vulnerabilities** using tools like pip-audit, safety
4. **Review security advisories** for your dependencies
5. **Use secure algorithms** (SHA-256 instead of MD5, etc.)
6. **Implement automated scanning** in CI/CD pipeline
7. **Monitor dependency updates** with tools like Dependabot
8. **Review package source** for critical functionality

---

### 6. Technical Standards

**Severity:** MEDIUM

**Description:** Validates overall technical standards compliance across all quality dimensions including code style, documentation, testing, and best practices.

#### Bad Patterns

```python
# BAD: Inconsistent code style
def calculate(a,b):
    return a+b

def Calculate(x,y):
    return x*y

# BAD: No docstrings
def process(data):
    return data.upper()

# BAD: Magic numbers
def calculate_discount(price):
    return price * 0.1  # What is 0.1?

# BAD: Poor variable names
def process(a, b, c):
    d = a + b
    e = d * c
    return e
```

#### Good Patterns

```python
# GOOD: Consistent code style (PEP 8)
def calculate_sum(a, b):
    return a + b

def calculate_product(x, y):
    return x * y

# GOOD: Proper docstrings
def process_data(data):
    """
    Process the input data by converting to uppercase.
    
    Args:
        data: String data to process
        
    Returns:
        Uppercase version of the input data
        
    Raises:
        TypeError: If data is not a string
    """
    if not isinstance(data, str):
        raise TypeError("Data must be a string")
    return data.upper()

# GOOD: Named constants
DISCOUNT_RATE = 0.1

def calculate_discount(price):
    return price * DISCOUNT_RATE

# GOOD: Descriptive variable names
def calculate_total_price(base_price, tax_rate, shipping_cost):
    subtotal = base_price * (1 + tax_rate)
    total = subtotal + shipping_cost
    return total

# GOOD: Type hints
from typing import List, Optional

def process_items(items: List[str], filter_func: Optional[callable] = None) -> List[str]:
    """
    Process a list of items with optional filtering.
    
    Args:
        items: List of items to process
        filter_func: Optional function to filter items
        
    Returns:
        Processed list of items
    """
    if filter_func:
        items = [item for item in items if filter_func(item)]
    return [item.upper() for item in items]

# GOOD: Error handling with context
def load_config(filename: str) -> dict:
    """
    Load configuration from a JSON file.
    
    Args:
        filename: Path to the configuration file
        
    Returns:
        Dictionary containing configuration data
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config file is invalid JSON
    """
    try:
        with open(filename, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {filename}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in configuration file: {e}")
```

#### Improvement Suggestions

1. **Follow PEP 8** style guide for Python code
2. **Use descriptive names** for variables, functions, classes
3. **Add docstrings** to all public functions and classes
4. **Use type hints** for better code documentation
5. **Define constants** instead of magic numbers
6. **Handle errors** with appropriate exceptions
7. **Write tests** for critical functionality
8. **Keep functions small** and focused on single responsibility
9. **Use meaningful comments** to explain complex logic
10. **Format code consistently** using tools like black, autopep8

---

## Best Practices

### Code Quality

1. **Follow style guides** (PEP 8 for Python)
2. **Use type hints** for better documentation and IDE support
3. **Write docstrings** for all public APIs
4. **Keep functions small** and focused
5. **Use descriptive names** for variables and functions
6. **Avoid code duplication** (DRY principle)
7. **Write tests** for critical functionality
8. **Review code** regularly with peers

### Error Handling

1. **Handle specific exceptions** instead of generic ones
2. **Provide context** in error messages
3. **Log errors** appropriately
4. **Don't swallow exceptions** unless intentional
5. **Use custom exceptions** for application-specific errors
6. **Validate inputs** early
7. **Fail fast** with clear error messages

### Security

1. **Never trust user input**
2. **Validate and sanitize** all inputs
3. **Use secure algorithms** (SHA-256, not MD5)
4. **Keep dependencies updated**
5. **Scan for vulnerabilities** regularly
6. **Follow principle of least privilege**
7. **Log security events** appropriately

### Performance

1. **Profile code** before optimizing
2. **Use appropriate data structures**
3. **Avoid premature optimization**
4. **Cache expensive operations**
5. **Use generators** for large datasets
6. **Minimize I/O operations**
7. **Consider async/await** for I/O-bound tasks

## Additional Resources

- [PEP 8 Style Guide](https://peps.python.org/pep-0008/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [OWASP Security Guidelines](https://owasp.org/)
- [Python Testing Best Practices](https://docs.pytest.org/)
- [Code Review Checklist](https://google.github.io/eng-practices/review/)
