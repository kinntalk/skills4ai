#!/usr/bin/env python3
"""
Audit Configuration for skill-auditor
Centralized configuration for thresholds, patterns, and settings.
"""

SEVERITY_CRITICAL = 'CRITICAL'
SEVERITY_HIGH = 'HIGH'
SEVERITY_MEDIUM = 'MEDIUM'
SEVERITY_LOW = 'LOW'

FILE_OPS_THRESHOLD = 15
NETWORK_OPS_THRESHOLD = 8
SYSTEM_CMDS_THRESHOLD = 5

PRINT_COUNT_THRESHOLD = 30
LOG_COUNT_THRESHOLD = 40
CONSECUTIVE_PRINT_THRESHOLD = 5

FUNCTION_LENGTH_THRESHOLD = 60
COMMENT_LENGTH_THRESHOLD = 250
SKILL_MD_LENGTH_THRESHOLD = 10000
PARAGRAPH_LENGTH_THRESHOLD = 500

SENSITIVE_DATA_PATTERNS = [
    r'password\s*=\s*["\'][^"\']+["\']',
    r'api_key\s*=\s*["\'][^"\']+["\']',
    r'apikey\s*=\s*["\'][^"\']+["\']',
    r'secret\s*=\s*["\'][^"\']+["\']',
    r'token\s*=\s*["\'][^"\']+["\']',
    r'auth\s*=\s*["\'][^"\']+["\']',
    r'credential\s*=\s*["\'][^"\']+["\']',
    r'private_key\s*=\s*["\'][^"\']+["\']',
    r'ssh_key\s*=\s*["\'][^"\']+["\']',
    r'access_token\s*=\s*["\'][^"\']+["\']',
    r'refresh_token\s*=\s*["\'][^"\']+["\']',
    r'bearer\s+["\'][^"\']+["\']',
]

PII_PATTERNS = [
    r'email\s*=\s*["\'][^"\']+@[^"\']+["\']',
    r'phone\s*=\s*["\'][\d\s\-\(\)]+["\']',
    r'ssn\s*=\s*["\'][\d\s\-]+["\']',
    r'credit_card\s*=\s*["\'][\d\s\-]+["\']',
]

PLACEHOLDER_KEYWORDS = ['todo', 'xxx', 'none', 'null', 'example', 'test']

REDUNDANT_PHRASES = [
    'please note that',
    'it is important to',
    'keep in mind that',
    'it should be noted that',
    'it is worth mentioning that',
]

VAGUE_PATTERNS = [
    r'\b(do it|make it|fix it|handle it)\b',
    r'\b(appropriate|suitable|proper|correct)\s+(way|manner|method)',
]

RISKY_FUNCS_EXCEPTION_MAP = {
    'open': 'FileNotFoundError, PermissionError, OSError',
    'Path.open': 'FileNotFoundError, PermissionError, OSError',
    'read_text': 'FileNotFoundError, PermissionError, OSError, UnicodeDecodeError',
    'write_text': 'FileNotFoundError, PermissionError, OSError',
    'json.load': 'FileNotFoundError, json.JSONDecodeError, ValueError',
    'json.loads': 'json.JSONDecodeError, ValueError',
    'json.dump': 'FileNotFoundError, PermissionError, TypeError, ValueError',
    'json.dumps': 'TypeError, ValueError',
    'yaml.safe_load': 'FileNotFoundError, yaml.YAMLError',
    'yaml.load': 'FileNotFoundError, yaml.YAMLError',
    'yaml.safe_dump': 'FileNotFoundError, PermissionError, yaml.YAMLError',
    'subprocess.run': 'subprocess.CalledProcessError, FileNotFoundError, PermissionError',
    'subprocess.check_output': 'subprocess.CalledProcessError, FileNotFoundError, PermissionError',
    'subprocess.Popen': 'FileNotFoundError, PermissionError, ValueError',
    'Path.unlink': 'FileNotFoundError, PermissionError, OSError',
    'Path.mkdir': 'FileExistsError, PermissionError, OSError',
    'Path.rmdir': 'FileNotFoundError, PermissionError, OSError',
    'Path.rename': 'FileNotFoundError, PermissionError, OSError',
    'Path.stat': 'FileNotFoundError, PermissionError, OSError',
}

OS_DANGEROUS_FUNCS = {
    'system', 'popen', 'spawn', 'execl', 'execle', 'execlp',
    'execv', 'execve', 'execvp', 'execvpe'
}

OS_PERMISSION_FUNCS = {'chmod', 'chown', 'chroot'}
OS_LINK_FUNCS = {'link', 'symlink'}
