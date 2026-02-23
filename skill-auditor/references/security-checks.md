# Security Checks Reference

This document provides detailed information about security checks performed by the skill-auditor, including examples of vulnerable and secure patterns, severity levels, and remediation steps.

## Severity Levels

- **CRITICAL**: Must fix immediately. These are security vulnerabilities that can lead to code injection, data breaches, or system compromise.
- **HIGH**: Should fix soon. These are significant issues that can lead to security risks, data exposure, or system instability.
- **MEDIUM**: Should fix. These are quality and reliability issues that can impact maintainability and user experience.
- **LOW**: Nice to fix. These are optimization and style improvements that enhance code quality and efficiency.

## Security Checks

### 1. Malicious Script Injection

**Severity:** CRITICAL

**Description:** Detects patterns of malicious script injection including dynamic code execution (eval, exec, compile), unsafe subprocess calls with user input, arbitrary file system access patterns, and network requests to untrusted sources.

#### Vulnerable Patterns

```python
# DANGEROUS: Direct eval with user input
user_code = input("Enter code to execute: ")
eval(user_code)  # CRITICAL: Arbitrary code execution

# DANGEROUS: exec with user input
user_script = input("Enter script: ")
exec(user_script)  # CRITICAL: Arbitrary code execution

# DANGEROUS: subprocess with shell=True and user input
user_command = input("Enter command: ")
subprocess.run(user_command, shell=True)  # CRITICAL: Command injection

# DANGEROUS: compile with user input
user_code = input("Enter code: ")
code_obj = compile(user_code, '<string>', 'exec')
exec(code_obj)  # CRITICAL: Arbitrary code execution
```

#### Secure Patterns

```python
# SECURE: Avoid eval/exec entirely
# Use safe alternatives based on your use case

# For mathematical expressions, use ast.literal_eval or safe parsers
import ast
user_input = input("Enter a number: ")
try:
    value = ast.literal_eval(user_input)  # Safe for literals only
except (ValueError, SyntaxError):
    print("Invalid input")

# For subprocess, avoid shell=True and validate input
import subprocess
import shlex

# SECURE: Use list arguments without shell
subprocess.run(['ls', '-la'], check=True)

# SECURE: If user input is needed, validate and sanitize
allowed_commands = {'list': ['ls', '-la'], 'status': ['git', 'status']}
user_choice = input("Choose command (list/status): ")
if user_choice in allowed_commands:
    subprocess.run(allowed_commands[user_choice], check=True)
else:
    print("Invalid command")

# SECURE: Use specific subprocess methods
subprocess.check_output(['echo', 'safe'])
subprocess.check_call(['echo', 'safe'])
```

#### Remediation Steps

1. **Remove eval/exec/compile** with user input entirely
2. **Use safe alternatives**:
   - For data parsing: `json.loads()`, `yaml.safe_load()`, `ast.literal_eval()`
   - For commands: Use subprocess with list arguments, not shell=True
3. **Validate and sanitize** all user input before use
4. **Use allowlists** for commands, filenames, or operations
5. **Implement sandboxing** if code execution is absolutely necessary

---

### 2. Permission Abuse

**Severity:** HIGH

**Description:** Identifies potential permission abuse risks including excessive file system access requests, network access without proper validation, system command execution without safeguards, and sensitive data access patterns.

#### Vulnerable Patterns

```python
# DANGEROUS: Excessive file operations without limits
def process_all_files():
    for root, dirs, files in os.walk('/'):
        for file in files:
            # Process every file on system - excessive access
            with open(os.path.join(root, file)) as f:
                process(f.read())

# DANGEROUS: Multiple network operations without validation
def fetch_data(urls):
    for url in urls:
        # No validation of URLs
        response = requests.get(url)
        process(response.text)

# DANGEROUS: System commands without safeguards
def execute_commands(commands):
    for cmd in commands:
        # No validation or limits
        os.system(cmd)

# DANGEROUS: Sensitive data access without checks
def export_all_data():
    # Exports all data without filtering
    data = database.query("SELECT * FROM users")
    save_to_file(data, 'all_users.json')
```

#### Secure Patterns

```python
# SECURE: Limit file operations to specific directories
def process_files_in_directory(target_dir):
    # Validate directory is within allowed paths
    allowed_dirs = ['/data/processed', '/data/input']
    if not any(target_dir.startswith(d) for d in allowed_dirs):
        raise PermissionError("Directory not allowed")
    
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            with open(os.path.join(root, file)) as f:
                process(f.read())

# SECURE: Validate URLs before network access
def fetch_data(urls):
    allowed_domains = {'api.example.com', 'data.example.org'}
    for url in urls:
        parsed = urllib.parse.urlparse(url)
        if parsed.netloc not in allowed_domains:
            raise ValueError(f"Domain not allowed: {parsed.netloc}")
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        process(response.text)

# SECURE: Use subprocess with validation and limits
def execute_commands(commands):
    allowed_commands = {
        'backup': ['rsync', '-av', '/data/', '/backup/'],
        'clean': ['rm', '-rf', '/tmp/cache/']
    }
    
    if len(commands) > 5:
        raise ValueError("Too many commands")
    
    for cmd_name in commands:
        if cmd_name not in allowed_commands:
            raise ValueError(f"Command not allowed: {cmd_name}")
        
        subprocess.run(allowed_commands[cmd_name], check=True)

# SECURE: Filter sensitive data before export
def export_user_data(user_id):
    # Only export specific user's data
    data = database.query(
        "SELECT id, name, email FROM users WHERE id = ?",
        (user_id,)
    )
    # Remove sensitive fields
    filtered_data = [{k: v for k, v in row.items() 
                     if k not in ['password', 'token']} 
                    for row in data]
    save_to_file(filtered_data, f'user_{user_id}.json')
```

#### Remediation Steps

1. **Implement allowlists** for directories, domains, and commands
2. **Validate all inputs** before file or network operations
3. **Limit the scope** of operations (e.g., specific directories, not entire filesystem)
4. **Add rate limiting** and operation count limits
5. **Filter sensitive data** before export or logging
6. **Use principle of least privilege** - only request necessary permissions

---

### 3. Prompt Injection

**Severity:** HIGH

**Description:** Detects potential prompt injection vectors including user-controlled prompt concatenation, unvalidated prompt modifications, instruction override patterns, and role manipulation attempts.

#### Vulnerable Patterns

```python
# DANGEROUS: Direct user input in prompts
def generate_response(user_query):
    prompt = f"You are a helpful assistant. {user_query}"
    return ai_client.generate(prompt)

# DANGEROUS: String concatenation with user input
def chat_with_ai(user_message):
    system_prompt = "You are a helpful assistant."
    full_prompt = system_prompt + " " + user_message
    return ai_client.generate(full_prompt)

# DANGEROUS: Unvalidated prompt modifications
def modify_prompt(base_prompt, user_modifications):
    # User can override instructions
    modified = base_prompt + " " + user_modifications
    return ai_client.generate(modified)

# DANGEROUS: Role manipulation
def set_role_and_query(role, query):
    # User can set arbitrary roles
    prompt = f"You are {role}. {query}"
    return ai_client.generate(prompt)
```

#### Secure Patterns

```python
# SECURE: Use structured prompts with validation
def generate_response(user_query):
    # Validate user input
    if len(user_query) > 1000:
        raise ValueError("Query too long")
    
    # Check for injection patterns
    injection_keywords = ['ignore', 'override', 'system:', 'assistant:']
    if any(kw in user_query.lower() for kw in injection_keywords):
        raise ValueError("Invalid query detected")
    
    # Use structured prompt with clear boundaries
    prompt = {
        'system': 'You are a helpful assistant.',
        'user': user_query
    }
    return ai_client.generate(prompt)

# SECURE: Use template with escaping
import re

def sanitize_user_input(text):
    # Remove or escape dangerous patterns
    text = re.sub(r'\bignore\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\boverride\b', '', text, flags=re.IGNORECASE)
    return text.strip()

def chat_with_ai(user_message):
    sanitized = sanitize_user_input(user_message)
    
    prompt = {
        'system': 'You are a helpful assistant. Answer only the user question.',
        'user': sanitized
    }
    return ai_client.generate(prompt)

# SECURE: Use allowlisted modifications
ALLOWED_MODIFICATIONS = ['more detail', 'simpler', 'examples']

def modify_prompt(base_prompt, user_modifications):
    modifications = [m.strip() for m in user_modifications.split(',')]
    
    # Validate each modification
    for mod in modifications:
        if mod.lower() not in ALLOWED_MODIFICATIONS:
            raise ValueError(f"Modification not allowed: {mod}")
    
    # Apply only allowed modifications
    modified = base_prompt
    if 'more detail' in modifications:
        modified += " Provide detailed explanations."
    if 'simpler' in modifications:
        modified += " Keep explanations simple and concise."
    
    return ai_client.generate(modified)

# SECURE: Fixed role with validation
ALLOWED_ROLES = {'assistant', 'expert', 'analyst'}

def set_role_and_query(role, query):
    if role.lower() not in ALLOWED_ROLES:
        raise ValueError(f"Role not allowed: {role}")
    
    role_prompts = {
        'assistant': 'You are a helpful assistant.',
        'expert': 'You are an expert in the field.',
        'analyst': 'You are a data analyst.'
    }
    
    prompt = {
        'system': role_prompts[role.lower()],
        'user': query
    }
    return ai_client.generate(prompt)
```

#### Remediation Steps

1. **Validate and sanitize** all user input before including in prompts
2. **Use structured prompts** with clear system/user boundaries
3. **Implement allowlists** for roles, modifications, and operations
4. **Check for injection patterns** like "ignore", "override", "system:"
5. **Limit prompt length** to prevent overflow attacks
6. **Use prompt templates** instead of string concatenation
7. **Implement rate limiting** to prevent abuse

---

### 4. Code Execution Safety

**Severity:** CRITICAL

**Description:** Validates code execution safety including eval(), exec(), compile() usage, unsafe dynamic code patterns, and subprocess call safety.

#### Vulnerable Patterns

```python
# DANGEROUS: eval with any input
def calculate(expression):
    return eval(expression)  # CRITICAL

# DANGEROUS: exec with dynamic code
def run_script(script_content):
    exec(script_content)  # CRITICAL

# DANGEROUS: compile and exec
def execute_code(code):
    compiled = compile(code, '<string>', 'exec')
    exec(compiled)  # CRITICAL

# DANGEROUS: subprocess with shell=True
def run_command(cmd):
    subprocess.run(cmd, shell=True)  # HIGH risk
```

#### Secure Patterns

```python
# SECURE: Use ast.literal_eval for literals
def calculate(expression):
    try:
        # Only evaluates literals, not code
        return ast.literal_eval(expression)
    except (ValueError, SyntaxError):
        raise ValueError("Invalid expression")

# SECURE: Use specific libraries for calculations
import operator

def safe_calculate(expression):
    ops = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv
    }
    
    # Simple calculator with safe operations
    tokens = expression.split()
    if len(tokens) != 3:
        raise ValueError("Invalid expression")
    
    try:
        a, op, b = tokens
        a, b = float(a), float(b)
        if op not in ops:
            raise ValueError("Invalid operator")
        return ops[op](a, b)
    except (ValueError, ZeroDivisionError):
        raise ValueError("Calculation error")

# SECURE: Use subprocess without shell
def run_command(cmd_args):
    # cmd_args should be a list, not a string
    subprocess.run(cmd_args, check=True)

# SECURE: Validate before subprocess
def safe_run_command(command_name, *args):
    allowed_commands = {
        'ls': ['ls'],
        'grep': ['grep'],
        'cat': ['cat']
    }
    
    if command_name not in allowed_commands:
        raise ValueError(f"Command not allowed: {command_name}")
    
    cmd = [command_name] + list(args)
    subprocess.run(cmd, check=True)
```

#### Remediation Steps

1. **Never use eval/exec/compile** with user input
2. **Use safe alternatives**:
   - For data: `json.loads()`, `yaml.safe_load()`, `ast.literal_eval()`
   - For calculations: Use specific math libraries or safe parsers
3. **Avoid shell=True** in subprocess calls
4. **Use list arguments** for subprocess instead of strings
5. **Implement allowlists** for allowed commands and operations
6. **Validate all inputs** before processing

---

### 5. Filesystem Security

**Severity:** HIGH

**Description:** Validates filesystem security including path traversal vulnerabilities, unsafe file operations, and file permission handling.

#### Vulnerable Patterns

```python
# DANGEROUS: Path traversal vulnerability
def read_file(filename):
    with open(filename) as f:  # User can use ../../etc/passwd
        return f.read()

# DANGEROUS: Unsafe file operations
def write_user_file(user_id, content):
    filename = f"/data/{user_id}.txt"
    with open(filename, 'w') as f:
        f.write(content)

# DANGEROUS: No permission checks
def delete_file(filepath):
    os.remove(filepath)  # Can delete any file
```

#### Secure Patterns

```python
# SECURE: Validate and sanitize paths
from pathlib import Path

def read_file(filename):
    # Resolve to absolute path
    file_path = Path(filename).resolve()
    
    # Ensure it's within allowed directory
    allowed_dir = Path('/data/files').resolve()
    try:
        file_path.relative_to(allowed_dir)
    except ValueError:
        raise PermissionError("File not in allowed directory")
    
    with open(file_path) as f:
        return f.read()

# SECURE: Validate user input
def write_user_file(user_id, content):
    # Validate user_id
    if not re.match(r'^[a-zA-Z0-9_-]+$', user_id):
        raise ValueError("Invalid user ID")
    
    # Construct safe path
    filename = Path(f"/data/users/{user_id}.txt")
    
    # Ensure it's within allowed directory
    allowed_dir = Path('/data/users').resolve()
    try:
        filename.resolve().relative_to(allowed_dir)
    except ValueError:
        raise PermissionError("Invalid file path")
    
    with open(filename, 'w') as f:
        f.write(content)

# SECURE: Check permissions and ownership
def delete_file(filepath):
    file_path = Path(filepath).resolve()
    
    # Check if file exists
    if not file_path.exists():
        raise FileNotFoundError("File not found")
    
    # Check if in allowed directory
    allowed_dir = Path('/data/temp').resolve()
    try:
        file_path.relative_to(allowed_dir)
    except ValueError:
        raise PermissionError("Cannot delete files outside temp directory")
    
    # Check file ownership (if applicable)
    stat = file_path.stat()
    if stat.st_uid != os.getuid():
        raise PermissionError("Not file owner")
    
    os.remove(file_path)

# SECURE: Use pathlib for safe path operations
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

#### Remediation Steps

1. **Always validate and sanitize** file paths
2. **Use pathlib.Path** for path operations
3. **Resolve to absolute paths** and check against allowed directories
4. **Check for path traversal** patterns (`../`, `..\\`, URL-encoded variants)
5. **Implement allowlists** for directories and file types
6. **Check file permissions** and ownership before operations
7. **Use chroot or containers** for additional isolation

---

### 6. Network Security

**Severity:** MEDIUM

**Description:** Detects network security risks including untrusted URL patterns, missing validation, and potential data exfiltration.

#### Vulnerable Patterns

```python
# DANGEROUS: No URL validation
def fetch_data(url):
    response = requests.get(url)  # Can fetch from any URL
    return response.json()

# DANGEROUS: No timeout
def slow_request(url):
    return requests.get(url)  # Can hang indefinitely

# DANGEROUS: Unverified SSL
def insecure_request(url):
    return requests.get(url, verify=False)  # MITM vulnerability

# DANGEROUS: Data exfiltration risk
def send_data_to_server(data, url):
    # No validation of destination
    requests.post(url, json=data)
```

#### Secure Patterns

```python
# SECURE: Validate URLs with allowlist
from urllib.parse import urlparse

def fetch_data(url):
    parsed = urlparse(url)
    
    # Allowlist of trusted domains
    allowed_domains = {
        'api.example.com',
        'data.example.org',
        'cdn.example.net'
    }
    
    if parsed.netloc not in allowed_domains:
        raise ValueError(f"Domain not allowed: {parsed.netloc}")
    
    # Ensure HTTPS
    if parsed.scheme != 'https':
        raise ValueError("Only HTTPS URLs allowed")
    
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()

# SECURE: Add timeout and retry logic
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def robust_request(url):
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    
    # Add timeout
    response = session.get(url, timeout=10)
    response.raise_for_status()
    return response

# SECURE: Verify SSL certificates
def secure_request(url):
    # Default verify=True (verify SSL certificates)
    response = requests.get(
        url,
        timeout=10,
        verify=True,  # Explicitly verify SSL
        headers={'User-Agent': 'MyApp/1.0'}
    )
    response.raise_for_status()
    return response

# SECURE: Validate destination and sanitize data
def send_data_to_server(data, url):
    # Validate URL
    parsed = urlparse(url)
    allowed_endpoints = {
        'api.example.com': ['/api/v1/submit', '/api/v1/upload']
    }
    
    if parsed.netloc not in allowed_endpoints:
        raise ValueError("Domain not allowed")
    
    if parsed.path not in allowed_endpoints[parsed.netloc]:
        raise ValueError("Endpoint not allowed")
    
    # Sanitize data - remove sensitive fields
    sensitive_fields = ['password', 'token', 'secret']
    sanitized_data = {k: v for k, v in data.items() 
                     if k not in sensitive_fields}
    
    # Send with timeout
    response = requests.post(
        url,
        json=sanitized_data,
        timeout=10,
        headers={'Content-Type': 'application/json'}
    )
    response.raise_for_status()
    return response.json()
```

#### Remediation Steps

1. **Implement URL allowlists** for trusted domains and endpoints
2. **Always use HTTPS** and verify SSL certificates
3. **Add timeouts** to prevent hanging requests
4. **Validate and sanitize** data before sending
5. **Remove sensitive data** from network payloads
6. **Implement rate limiting** to prevent abuse
7. **Use retry logic** with exponential backoff for resilience
8. **Set appropriate User-Agent** headers

---

## Best Practices

1. **Never trust user input** - Always validate and sanitize
2. **Use allowlists** instead of blocklists for security
3. **Follow principle of least privilege** - Only request necessary permissions
4. **Implement defense in depth** - Multiple layers of security
5. **Keep dependencies updated** - Patch known vulnerabilities
6. **Use security libraries** - Don't roll your own crypto or security
7. **Log security events** - Monitor for suspicious activity
8. **Regular security audits** - Review code for vulnerabilities

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [CWE Top 25](https://cwe.mitre.org/top25/)
