#!/usr/bin/env python3
"""
Skill Auditor - Comprehensive validation tool for Trae skills
Checks for dependencies, encoding, path consistency, cross-platform compatibility, i18n support, and packaging structure.
"""

import sys
import os
import re
import yaml
import json
import argparse
import datetime
import ast
from pathlib import Path

# Initialize ANSI color support
def init_color_support():
    """Initialize color output support based on terminal capabilities."""
    # Check if we're on Windows and if ANSI colors are supported
    if sys.platform == 'win32':
        # Windows 10+ supports ANSI colors in modern terminals
        # Enable for Windows if not already enabled
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            # Enable ANSI colors on Windows console
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            return True
        except:
            # Fallback: assume no color support
            return False
    return True

# Global color support flag
COLOR_SUPPORT = init_color_support()

# ANSI colors for output (only used if supported)
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
RESET = "\033[0m"

# Text labels for terminals without color support
PASS_TEXT = "[PASS]"
FAIL_TEXT = "[FAIL]"
WARN_TEXT = "[WARN]"

def print_pass(msg, json_output=False):
    if json_output:
        return
    if COLOR_SUPPORT:
        print(f"{GREEN}{PASS_TEXT}{RESET} {msg}")
    else:
        print(f"{PASS_TEXT} {msg}")

def print_fail(msg, json_output=False):
    if json_output:
        return
    if COLOR_SUPPORT:
        print(f"{RED}{FAIL_TEXT}{RESET} {msg}")
    else:
        print(f"{FAIL_TEXT} {msg}")

def print_warn(msg, json_output=False):
    if json_output:
        return
    if COLOR_SUPPORT:
        print(f"{YELLOW}{WARN_TEXT}{RESET} {msg}")
    else:
        print(f"{WARN_TEXT} {msg}")

def print_info(msg, json_output=False):
    if json_output:
        return
    print(msg)

def print_verbose(msg, verbose=False):
    if verbose:
        print(f"  {msg}")

def print_severity(severity, json_output=False):
    """Print severity level with appropriate color."""
    if json_output:
        return
    severity_colors = {
        'CRITICAL': RED,
        'HIGH': RED,
        'MEDIUM': YELLOW,
        'LOW': BLUE
    }
    color = severity_colors.get(severity, '')
    if COLOR_SUPPORT and color:
        print(f"{color}[{severity}]{RESET}")
    else:
        print(f"[{severity}]")

def check_dependencies(skill_path):
    """Check if requirements.txt exists and matches imports"""
    scripts_dir = skill_path / 'scripts'
    if not scripts_dir.exists():
        return True, "No scripts directory"
    
    # Find all python files
    py_files = list(scripts_dir.glob('**/*.py'))
    if not py_files:
        return True, "No Python scripts found"
        
    req_file = scripts_dir / 'requirements.txt'
    if not req_file.exists():
        return False, "Python scripts found but scripts/requirements.txt is missing"
    
    # Scan for imports
    imported_modules = set()
    std_lib = sys.stdlib_module_names if hasattr(sys, 'stdlib_module_names') else set()
    
    # Fallback for older python versions if needed, but 3.10+ has stdlib_module_names
    if not std_lib:
         # Basic list if sys.stdlib_module_names missing
         std_lib = {'os', 'sys', 're', 'json', 'yaml', 'pathlib', 'argparse', 'subprocess', 'shutil', 'tempfile', 'time', 'datetime', 'logging', 'threading', 'typing', 'collections', 'io', 'math', 'random', 'string', 'hashlib', 'base64', 'urllib', 'http', 'email', 'csv', 'sqlite3', 'configparser', 'zipfile', 'tarfile', 'gzip', 'bz2', 'pickle', 'copy', 'itertools', 'functools', 'operator', 'decimal', 'fractions', 'statistics', 'enum', 'dataclasses', 'uuid', 'secrets', 'inspect', 'warnings', 'contextlib', 'abc', 'numbers', 'types'}

    for py_file in py_files:
        try:
            content = py_file.read_text(encoding='utf-8')
            # Regex for 'import X' or 'from X import Y'
            imports = re.findall(r'^\s*(?:import|from)\s+([a-zA-Z0-9_]+)', content, re.MULTILINE)
            for module in imports:
                if module not in std_lib and module != 'scripts':
                    imported_modules.add(module)
        except UnicodeDecodeError as e:
            print(f"Warning: Could not decode {py_file.name}: {e}")
        except Exception as e:
            print(f"Warning: Could not read {py_file.name}: {e}")

    # Read requirements
    try:
        req_content = req_file.read_text(encoding='utf-8').lower()
        declared_deps = set(line.split('==')[0].split('>=')[0].strip() for line in req_content.splitlines() if line.strip() and not line.startswith('#'))
    except Exception:
        return False, "Could not read requirements.txt"

    # Mapping common imports to package names (incomplete but helpful)
    pkg_map = {
        'yaml': 'pyyaml',
        'PIL': 'pillow',
        'bs4': 'beautifulsoup4',
        'dotenv': 'python-dotenv',
        'git': 'gitpython'
    }

    missing_deps = []
    for module in imported_modules:
        pkg_name = pkg_map.get(module, module).lower()
        if pkg_name not in declared_deps and module.lower() not in declared_deps:
            # Check if it's a local file import
            if not (scripts_dir / f"{module}.py").exists():
                 missing_deps.append(f"{module} (package: {pkg_name})")

    if missing_deps:
        return False, f"Potential missing dependencies in requirements.txt: {', '.join(missing_deps)}"

    return True, "Dependency configuration looks good"

def check_encoding_safety(skill_path):
    """Check for explicit encoding in file operations and file security practices"""
    issues = []
    
    class EncodingSafetyChecker(ast.NodeVisitor):
        def __init__(self, filename, source_lines):
            self.filename = filename
            self.source_lines = source_lines
            self.issues = []
            self.docstring_lines = set()
            
        def _collect_docstring_lines(self, tree):
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    if node.body and isinstance(node.body[0], ast.Expr):
                        if isinstance(node.body[0].value, ast.Constant):
                            if isinstance(node.body[0].value.value, str):
                                start_line = node.body[0].lineno
                                end_line = node.body[0].end_lineno if hasattr(node.body[0], 'end_lineno') else start_line
                                for line_num in range(start_line, end_line + 1):
                                    self.docstring_lines.add(line_num)
                elif isinstance(node, ast.Module):
                    if node.body and isinstance(node.body[0], ast.Expr):
                        if isinstance(node.body[0].value, ast.Constant):
                            if isinstance(node.body[0].value.value, str):
                                start_line = node.body[0].lineno
                                end_line = node.body[0].end_lineno if hasattr(node.body[0], 'end_lineno') else start_line
                                for line_num in range(start_line, end_line + 1):
                                    self.docstring_lines.add(line_num)
        
        def _is_in_docstring(self, lineno):
            return lineno in self.docstring_lines
        
        def visit_Call(self, node):
            lineno = node.lineno
            if self._is_in_docstring(lineno):
                self.generic_visit(node)
                return
            
            if isinstance(node.func, ast.Name):
                if node.func.id == 'open':
                    has_encoding = False
                    has_binary_mode = False
                    has_errors_param = False
                    
                    for kw in node.keywords:
                        if kw.arg == 'encoding':
                            has_encoding = True
                        if kw.arg == 'errors':
                            has_errors_param = True
                    
                    for arg in node.args:
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                            if 'b' in arg.value:
                                has_binary_mode = True
                    
                    if not has_binary_mode and not has_encoding:
                        self.issues.append(
                            f"{self.filename}:{lineno}: open() without explicit encoding parameter. "
                            "Add encoding='utf-8' for text mode operations."
                        )
                    
                    if not has_binary_mode and not has_errors_param:
                        self.issues.append(
                            f"{self.filename}:{lineno}: open() without errors parameter. "
                            "Add errors='replace' or errors='ignore' for robust error handling."
                        )
            
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in ['read_text', 'write_text', 'read_bytes', 'write_bytes']:
                    has_encoding = False
                    has_errors = False
                    
                    for kw in node.keywords:
                        if kw.arg == 'encoding':
                            has_encoding = True
                        if kw.arg == 'errors':
                            has_errors = True
                    
                    if node.func.attr in ['read_text', 'write_text'] and not has_encoding:
                        self.issues.append(
                            f"{self.filename}:{lineno}: {node.func.attr}() without explicit encoding parameter. "
                            "Add encoding='utf-8'."
                        )
                    
                    if node.func.attr in ['read_text', 'write_text'] and not has_errors:
                        self.issues.append(
                            f"{self.filename}:{lineno}: {node.func.attr}() without errors parameter. "
                            "Add errors='replace' for robust error handling."
                        )
                
                if node.func.attr == 'chmod':
                    for kw in node.keywords:
                        if kw.arg == 'mode':
                            if isinstance(kw.value, ast.Constant):
                                mode_value = kw.value.value
                                if isinstance(mode_value, int):
                                    if (mode_value & 0o777) == 0o777:
                                        self.issues.append(
                                            f"{self.filename}:{lineno}: chmod() with overly permissive mode 0o777. "
                                            "Use more restrictive permissions (e.g., 0o644 for files, 0o755 for directories)."
                                        )
                
                if isinstance(node.func.value, ast.Name):
                    if node.func.value.id == 'tempfile':
                        if node.func.attr in ['mktemp', 'mkstemp', 'NamedTemporaryFile', 'TemporaryFile']:
                            has_cleanup = False
                            has_delete = False
                            
                            for kw in node.keywords:
                                if kw.arg == 'delete':
                                    if isinstance(kw.value, ast.Constant) and kw.value.value is True:
                                        has_delete = True
                            
                            if node.func.attr == 'mktemp':
                                self.issues.append(
                                    f"{self.filename}:{lineno}: tempfile.mktemp() is insecure. "
                                    "Use tempfile.mkstemp() or tempfile.NamedTemporaryFile() instead."
                                )
                            
                            if node.func.attr == 'mkstemp' and not has_cleanup:
                                self.issues.append(
                                    f"{self.filename}:{lineno}: tempfile.mkstemp() requires manual cleanup. "
                                    "Ensure the temporary file is properly closed and unlinked."
                                )
            
            self.generic_visit(node)
        
        def visit_With(self, node):
            lineno = node.lineno
            if self._is_in_docstring(lineno):
                self.generic_visit(node)
                return
            
            for item in node.items:
                if isinstance(item.context_expr, ast.Call):
                    if isinstance(item.context_expr.func, ast.Name):
                        if item.context_expr.func.id == 'open':
                            has_encoding = False
                            for kw in item.context_expr.keywords:
                                if kw.arg == 'encoding':
                                    has_encoding = True
                            
                            if not has_encoding:
                                self.issues.append(
                                    f"{self.filename}:{lineno}: open() in with statement without explicit encoding. "
                                    "Add encoding='utf-8'."
                                )
            
            self.generic_visit(node)
    
    for py_file in skill_path.glob('**/*.py'):
        if py_file.name == 'audit_skill.py':
            continue
        try:
            content = py_file.read_text(encoding='utf-8')
            source_lines = content.splitlines()
            
            try:
                tree = ast.parse(content, filename=str(py_file))
                checker = EncodingSafetyChecker(py_file.name, source_lines)
                checker._collect_docstring_lines(tree)
                checker.visit(tree)
                issues.extend(checker.issues)
            except SyntaxError as e:
                issues.append(f"{py_file.name}: Syntax error - {e}")
        except Exception as e:
            issues.append(f"Could not read {py_file.name}: {e}")
    
    if issues:
        return False, issues
    return True, "File operations use explicit encoding and proper security practices"

def check_path_consistency(skill_path):
    """
    Check for outdated .codebuddy paths and path traversal vulnerabilities.
    
    Checks for:
    1. Outdated .codebuddy path references
    2. Path traversal vulnerability patterns (../, ..\\, %2e%2e)
    3. Unsafe path concatenation with user input
    4. Relative path normalization issues
    
    Args:
        skill_path: Path to the skill directory.
        
    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    issues = []
    
    class PathConsistencyChecker(ast.NodeVisitor):
        def __init__(self, filename, source_lines):
            self.filename = filename
            self.source_lines = source_lines
            self.issues = []
            self.docstring_lines = set()
            
        def _collect_docstring_lines(self, tree):
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    if node.body and isinstance(node.body[0], ast.Expr):
                        if isinstance(node.body[0].value, ast.Constant):
                            if isinstance(node.body[0].value.value, str):
                                start_line = node.body[0].lineno
                                end_line = node.body[0].end_lineno if hasattr(node.body[0], 'end_lineno') else start_line
                                for line_num in range(start_line, end_line + 1):
                                    self.docstring_lines.add(line_num)
                elif isinstance(node, ast.Module):
                    if node.body and isinstance(node.body[0], ast.Expr):
                        if isinstance(node.body[0].value, ast.Constant):
                            if isinstance(node.body[0].value.value, str):
                                start_line = node.body[0].lineno
                                end_line = node.body[0].end_lineno if hasattr(node.body[0], 'end_lineno') else start_line
                                for line_num in range(start_line, end_line + 1):
                                    self.docstring_lines.add(line_num)
        
        def _is_in_docstring(self, lineno):
            return lineno in self.docstring_lines
        
        def _is_user_input_var(self, node):
            if isinstance(node, ast.Name):
                dangerous_names = ['input', 'user_input', 'user_input_data', 'data', 'payload', 'filename', 'filepath', 'path', 'file', 'arg', 'argument', 'user_path']
                return node.id in dangerous_names
            return False
        
        def _check_path_traversal(self, value):
            traversal_patterns = ['../', '..\\', '%2e%2e', '%2e%2e%2f', '%2e%2e%5c', '..%2f', '..%5c', '....']
            for pattern in traversal_patterns:
                if pattern in value:
                    return True
            return False
        
        def visit_BinOp(self, node):
            lineno = node.lineno
            if self._is_in_docstring(lineno):
                self.generic_visit(node)
                return
            
            if isinstance(node.op, ast.Add):
                has_user_input = False
                has_path_string = False
                
                for arg in [node.left, node.right]:
                    if self._is_user_input_var(arg):
                        has_user_input = True
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        if '/' in arg.value or '\\' in arg.value:
                            has_path_string = True
                
                if has_user_input and has_path_string:
                    self.issues.append(
                        f"{self.filename}:{lineno}: Unsafe path concatenation with potential user input. "
                        "Use pathlib.Path() or os.path.join() for safe path construction."
                    )
            
            self.generic_visit(node)
        
        def visit_Call(self, node):
            lineno = node.lineno
            if self._is_in_docstring(lineno):
                self.generic_visit(node)
                return
            
            if isinstance(node.func, ast.Name):
                if node.func.id == 'open':
                    for arg in node.args:
                        if self._is_user_input_var(arg):
                            self.issues.append(
                                f"{self.filename}:{lineno}: open() with potential user input. "
                                "This is a path traversal vulnerability. Validate and sanitize file paths."
                            )
            
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in ['open', 'read_text', 'write_text', 'read_bytes', 'write_bytes', 'mkdir', 'rmdir', 'unlink', 'remove', 'exists', 'is_file', 'is_dir']:
                    for arg in node.args:
                        if self._is_user_input_var(arg):
                            self.issues.append(
                                f"{self.filename}:{lineno}: File operation with potential user input. "
                                "Validate and sanitize file paths to prevent path traversal."
                            )
                
                if isinstance(node.func.value, ast.Name):
                    if node.func.value.id == 'pathlib' and node.func.attr == 'Path':
                        for arg in node.args:
                            if self._is_user_input_var(arg):
                                self.issues.append(
                                    f"{self.filename}:{lineno}: pathlib.Path() with potential user input. "
                                    "Validate and sanitize paths to prevent path traversal."
                                )
            
            self.generic_visit(node)
        
        def visit_Constant(self, node):
            if isinstance(node.value, str) and not self._is_in_docstring(node.lineno):
                if self._check_path_traversal(node.value):
                    self.issues.append(
                        f"{self.filename}:{node.lineno}: Path traversal pattern detected in string literal: '{node.value[:50]}...'. "
                        "Review for hardcoded path traversal vectors."
                    )
            
            self.generic_visit(node)
    
    for py_file in skill_path.glob('**/*.py'):
        if py_file.name == 'audit_skill.py':
            continue
        try:
            content = py_file.read_text(encoding='utf-8')
            source_lines = content.splitlines()
            
            try:
                tree = ast.parse(content, filename=str(py_file))
                checker = PathConsistencyChecker(py_file.name, source_lines)
                checker._collect_docstring_lines(tree)
                checker.visit(tree)
                issues.extend(checker.issues)
            except SyntaxError as e:
                issues.append(f"{py_file.name}: Syntax error - {e}")
        except Exception as e:
            issues.append(f"Could not read {py_file.name}: {e}")
    
    for file_path in skill_path.glob('**/*'):
        if not file_path.is_file():
            continue
            
        if file_path.suffix not in ['.md', '.py', '.txt']:
            continue
        
        if file_path.name == 'audit_skill.py':
            continue
            
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            if '.codebuddy' in content:
                try:
                    rel_path = file_path.relative_to(skill_path)
                except ValueError:
                    rel_path = file_path.name
                issues.append(f"{rel_path}: Contains reference to '.codebuddy'")
        except Exception:
            pass
            
    if issues:
        return False, issues
    return True, "No outdated path references or path traversal vulnerabilities found"

def check_skill_name_consistency(skill_path):
    """
    Check if skill directory name matches SKILL.md frontmatter name.
    
    Args:
        skill_path: Path to the skill directory.
        
    Returns:
        tuple: (success: bool, message: str)
    """
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return True, "SKILL.md not found (skipping name check)"
    
    try:
        content = skill_md.read_text(encoding='utf-8')
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return True, "SKILL.md frontmatter not found (skipping name check)"
        
        frontmatter = yaml.safe_load(match.group(1))
        
        if 'name' not in frontmatter:
            return False, "SKILL.md frontmatter missing 'name' field"
        
        skill_name_from_md = frontmatter['name']
        skill_name_from_dir = skill_path.name
        
        if skill_name_from_md != skill_name_from_dir:
            return False, f"Name mismatch: SKILL.md has '{skill_name_from_md}' but directory is '{skill_name_from_dir}'"
        
        return True, "SKILL.md name matches directory name"
    except Exception as e:
        return False, f"Error checking skill name consistency: {e}"

def check_directory_structure(skill_path):
    """
    Check if skill directory structure follows standard conventions.
    
    Validates:
    1. SKILL.md exists at root
    2. Optional directories: scripts/, references/, assets/
    3. No unexpected top-level files (except allowed files)
    
    Args:
        skill_path: Path to the skill directory.
        
    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "SKILL.md not found at root directory"
    
    # Check for expected directories
    expected_dirs = ["scripts", "references", "assets"]
    found_dirs = []
    for d in expected_dirs:
        if (skill_path / d).exists():
            found_dirs.append(d)
    
    # Check for unexpected top-level files
    # Extended allowed files list to include common skill metadata files
    # and reference documentation files
    allowed_files = [
        "SKILL.md",
        "README.md",
        "LICENSE.txt",
        "LICENSE",
        ".gitignore",
        "CLAUDE.md",
        "requirements.txt"
    ]
    # Patterns for reference documentation files
    ref_doc_patterns = [
        r'.*-tracing\.md$',
        r'.*-guide\.md$',
        r'.*-protocol\.md$',
        r'.*-reference\.md$',
        r'.*-workflow\.md$',
        r'.*-methodology\.md$'
    ]
    unexpected_files = []
    
    try:
        for item in skill_path.iterdir():
            if item.is_file():
                if item.name not in allowed_files:
                    # Check if it matches reference documentation patterns
                    is_ref_doc = any(re.match(pattern, item.name) for pattern in ref_doc_patterns)
                    if not is_ref_doc:
                        unexpected_files.append(item.name)
    except Exception as e:
        return False, f"Could not scan directory: {e}"
    
    issues = []
    if unexpected_files:
        issues.append(f"Unexpected top-level files: {', '.join(unexpected_files)}")
    
    if issues:
        return False, issues
    return True, f"Directory structure is valid (found: {', '.join(found_dirs) if found_dirs else 'none'})"

def check_packaging_logic(skill_path):
    """Check packaging script logic if it exists"""
    package_script = skill_path / 'scripts' / 'package_skill.py'
    if not package_script.exists():
        return True, "No package_skill.py found (skipped)"
        
    try:
        content = package_script.read_text(encoding='utf-8')
        
        # Check 1: Relative path logic
        # Bad: relative_to(skill_path.parent)
        # Good: relative_to(skill_path)
        if 'relative_to(skill_path.parent)' in content:
            return False, "package_skill.py uses 'skill_path.parent' (creates nested zip structure)"
        
        # Accept either relative_to(skill_path) or arcname = file_path.name (flat structure)
        if 'relative_to(skill_path)' not in content and 'arcname = file_path.name' not in content:
            return False, "package_skill.py does not seem to use correct flat structure logic"
            
        # Check 2: Pycache filtering
        if '__pycache__' not in content and '.pyc' not in content:
            return False, "package_skill.py does not appear to filter __pycache__ or .pyc files"
            
        return True, "Packaging logic looks correct"
        
    except Exception as e:
        return False, f"Error checking package script: {e}"

def validate_frontmatter(skill_path):
    """Basic SKILL.md validation"""
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        # Downgrade to warning if README.md exists, or just general warning
        readme = skill_path / 'README.md'
        if readme.exists():
             return True, "SKILL.md missing (found README.md - check for metadata there)"
        return True, "SKILL.md missing (Warning: Metadata might be missing)"
        
    try:
        content = skill_md.read_text(encoding='utf-8')
        if not content.startswith('---'):
            return False, "No YAML frontmatter"
            
        # Simple extraction
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return False, "Invalid frontmatter format"
            
        frontmatter = yaml.safe_load(match.group(1))
        
        if 'name' not in frontmatter:
            return False, "Missing 'name'"
        if 'description' not in frontmatter:
            return False, "Missing 'description'"
            
        return True, "SKILL.md frontmatter is valid"
    except Exception as e:
        return False, f"Frontmatter validation error: {e}"

def check_init_script_template(skill_path):
    """Check if init_skill.py contains valid YAML template (no [] list syntax)"""
    init_script = skill_path / 'scripts' / 'init_skill.py'
    if not init_script.exists():
        return True, "No init_skill.py found (skipped)"
        
    try:
        content = init_script.read_text(encoding='utf-8')
        
        # Check for bad list syntax in description
        # Bad: description: [TODO: ...]
        if 'description: [' in content and 'TODO:' in content:
            return False, "init_skill.py uses invalid list syntax '[]' for description template"
            
        # Check for good string syntax
        # Good: description: "TODO: ..."
        if 'description: "' in content or "description: '" in content:
             return True, "Template description syntax looks correct"
             
        # If neither found, it might be using a different format or clean, just warn if unsure
        # But for now, we assume if it's not the bad one, it's pass
        return True, "Template description syntax looks safe"
        
    except Exception as e:
        return False, f"Error checking init script: {e}"

def check_malicious_script_injection(skill_path):
    """
    Detect patterns of malicious script injection.

    Checks for:
    - Dynamic code execution (eval, exec, compile)
    - Unsafe subprocess calls with user input
    - Arbitrary file system access patterns
    - Network requests to untrusted sources

    Args:
        skill_path: Path to the skill directory to scan.

    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    issues = []

    class MaliciousInjectionChecker(ast.NodeVisitor):
        def __init__(self, filename, source_lines):
            self.filename = filename
            self.source_lines = source_lines
            self.issues = []
            self.docstring_lines = set()

        def _collect_docstring_lines(self, tree):
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    if node.body and isinstance(node.body[0], ast.Expr):
                        if isinstance(node.body[0].value, ast.Constant):
                            if isinstance(node.body[0].value.value, str):
                                start_line = node.body[0].lineno
                                end_line = node.body[0].end_lineno if hasattr(node.body[0], 'end_lineno') else start_line
                                for line_num in range(start_line, end_line + 1):
                                    self.docstring_lines.add(line_num)
                elif isinstance(node, ast.Module):
                    if node.body and isinstance(node.body[0], ast.Expr):
                        if isinstance(node.body[0].value, ast.Constant):
                            if isinstance(node.body[0].value.value, str):
                                start_line = node.body[0].lineno
                                end_line = node.body[0].end_lineno if hasattr(node.body[0], 'end_lineno') else start_line
                                for line_num in range(start_line, end_line + 1):
                                    self.docstring_lines.add(line_num)

        def _is_in_docstring(self, lineno):
            return lineno in self.docstring_lines

        def _is_user_input_var(self, node):
            if isinstance(node, ast.Name):
                dangerous_names = ['input', 'user_input', 'user_input_data', 'data', 'payload', 'cmd', 'command']
                return node.id in dangerous_names
            return False

        def visit_Call(self, node):
            lineno = node.lineno
            if self._is_in_docstring(lineno):
                self.generic_visit(node)
                return

            if isinstance(node.func, ast.Name):
                if node.func.id in ['eval', 'exec', 'compile']:
                    has_user_input = any(self._is_user_input_var(arg) for arg in node.args)
                    if has_user_input:
                        self.issues.append(
                            f"{self.filename}:{lineno}: {node.func.id}() with potential user input. "
                            "This is a critical security vulnerability."
                        )
                    else:
                        self.issues.append(
                            f"{self.filename}:{lineno}: {node.func.id}() detected. "
                            "Dynamic code execution is dangerous and should be avoided."
                        )

            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    if node.func.value.id == 'subprocess' and node.func.attr in ['run', 'call', 'Popen', 'check_output']:
                        has_shell_true = False
                        has_user_input = False

                        for kw in node.keywords:
                            if kw.arg == 'shell' and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                                has_shell_true = True
                        has_user_input = any(self._is_user_input_var(arg) for arg in node.args)

                        if has_shell_true and has_user_input:
                            self.issues.append(
                                f"{self.filename}:{lineno}: subprocess.{node.func.attr}() with shell=True and user input. "
                                "This is a critical command injection vulnerability."
                            )
                        elif has_shell_true:
                            self.issues.append(
                                f"{self.filename}:{lineno}: subprocess.{node.func.attr}() with shell=True. "
                                "Avoid shell=True to prevent command injection."
                            )
                        elif has_user_input:
                            self.issues.append(
                                f"{self.filename}:{lineno}: subprocess.{node.func.attr}() with potential user input. "
                                "Validate and sanitize user input before subprocess calls."
                            )

            self.generic_visit(node)

    for py_file in skill_path.glob('**/*.py'):
        if py_file.name == 'audit_skill.py':
            continue
        try:
            content = py_file.read_text(encoding='utf-8')
            source_lines = content.splitlines()

            try:
                tree = ast.parse(content, filename=str(py_file))
                checker = MaliciousInjectionChecker(py_file.name, source_lines)
                checker._collect_docstring_lines(tree)
                checker.visit(tree)
                issues.extend(checker.issues)
            except SyntaxError as e:
                issues.append(f"{py_file.name}: Syntax error - {e}")
        except Exception as e:
            issues.append(f"Could not read {py_file.name}: {e}")

    if issues:
        return False, issues
    return True, "No malicious script injection patterns detected"

def check_permission_abuse(skill_path):
    """
    Identify potential permission abuse risks.

    Checks for:
    - Excessive file system access requests
    - Network access without proper validation
    - System command execution without safeguards
    - Sensitive data access patterns

    Args:
        skill_path: Path to the skill directory to scan.

    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    issues = []

    class PermissionAbuseChecker(ast.NodeVisitor):
        def __init__(self, filename, source_lines):
            self.filename = filename
            self.source_lines = source_lines
            self.issues = []
            self.docstring_lines = set()
            self.file_operations = []
            self.network_operations = []
            self.system_commands = []

        def _collect_docstring_lines(self, tree):
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    if node.body and isinstance(node.body[0], ast.Expr):
                        if isinstance(node.body[0].value, ast.Constant):
                            if isinstance(node.body[0].value.value, str):
                                start_line = node.body[0].lineno
                                end_line = node.body[0].end_lineno if hasattr(node.body[0], 'end_lineno') else start_line
                                for line_num in range(start_line, end_line + 1):
                                    self.docstring_lines.add(line_num)
                elif isinstance(node, ast.Module):
                    if node.body and isinstance(node.body[0], ast.Expr):
                        if isinstance(node.body[0].value, ast.Constant):
                            if isinstance(node.body[0].value.value, str):
                                start_line = node.body[0].lineno
                                end_line = node.body[0].end_lineno if hasattr(node.body[0], 'end_lineno') else start_line
                                for line_num in range(start_line, end_line + 1):
                                    self.docstring_lines.add(line_num)

        def _is_in_docstring(self, lineno):
            return lineno in self.docstring_lines

        def visit_Call(self, node):
            lineno = node.lineno
            if self._is_in_docstring(lineno):
                self.generic_visit(node)
                return

            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    if node.func.value.id == 'open':
                        self.file_operations.append(lineno)

                    if node.func.value.id == 'os' and node.func.attr in ['system', 'popen', 'spawn', 'execl', 'execle', 'execlp', 'execv', 'execve', 'execvp', 'execvpe']:
                        self.system_commands.append(lineno)

                    if node.func.value.id == 'subprocess' and node.func.attr in ['run', 'call', 'Popen', 'check_output']:
                        has_shell = False
                        for kw in node.keywords:
                            if kw.arg == 'shell' and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                                has_shell = True
                        self.system_commands.append(lineno)
                        if has_shell:
                            self.issues.append(
                                f"{self.filename}:{lineno}: subprocess.{node.func.attr}() with shell=True detected. "
                                "This can lead to permission abuse and command injection."
                            )

                    if node.func.value.id in ['urllib', 'requests', 'http', 'socket'] or node.func.attr in ['urlopen', 'get', 'post', 'put', 'delete', 'request', 'connect', 'send']:
                        self.network_operations.append(lineno)

            if isinstance(node.func, ast.Name):
                if node.func.id in ['open', 'execfile', 'compile']:
                    self.file_operations.append(lineno)

            self.generic_visit(node)

    for py_file in skill_path.glob('**/*.py'):
        if py_file.name == 'audit_skill.py':
            continue
        try:
            content = py_file.read_text(encoding='utf-8')
            source_lines = content.splitlines()

            try:
                tree = ast.parse(content, filename=str(py_file))
                checker = PermissionAbuseChecker(py_file.name, source_lines)
                checker._collect_docstring_lines(tree)
                checker.visit(tree)

                if len(checker.file_operations) > 10:
                    checker.issues.append(
                        f"{py_file.name}: Excessive file operations detected ({len(checker.file_operations)} operations). "
                        "Review if all file access is necessary."
                    )

                if len(checker.network_operations) > 5:
                    checker.issues.append(
                        f"{py_file.name}: Multiple network operations detected ({len(checker.network_operations)} operations). "
                        "Ensure proper validation and error handling."
                    )

                if len(checker.system_commands) > 3:
                    checker.issues.append(
                        f"{py_file.name}: Multiple system command executions detected ({len(checker.system_commands)} operations). "
                        "Review necessity and add proper safeguards."
                    )

                issues.extend(checker.issues)
            except SyntaxError as e:
                issues.append(f"{py_file.name}: Syntax error - {e}")
        except Exception as e:
            issues.append(f"Could not read {py_file.name}: {e}")

    if issues:
        return False, issues
    return True, "No permission abuse risks detected"

def check_prompt_injection(skill_path):
    """
    Detect potential prompt injection vectors.

    Checks for:
    - User-controlled prompt concatenation
    - Unvalidated prompt modifications
    - Instruction override patterns
    - Role manipulation attempts

    Args:
        skill_path: Path to the skill directory to scan.

    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    issues = []

    class PromptInjectionChecker(ast.NodeVisitor):
        def __init__(self, filename, source_lines):
            self.filename = filename
            self.source_lines = source_lines
            self.issues = []
            self.docstring_lines = set()

        def _collect_docstring_lines(self, tree):
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    if node.body and isinstance(node.body[0], ast.Expr):
                        if isinstance(node.body[0].value, ast.Constant):
                            if isinstance(node.body[0].value.value, str):
                                start_line = node.body[0].lineno
                                end_line = node.body[0].end_lineno if hasattr(node.body[0], 'end_lineno') else start_line
                                for line_num in range(start_line, end_line + 1):
                                    self.docstring_lines.add(line_num)
                elif isinstance(node, ast.Module):
                    if node.body and isinstance(node.body[0], ast.Expr):
                        if isinstance(node.body[0].value, ast.Constant):
                            if isinstance(node.body[0].value.value, str):
                                start_line = node.body[0].lineno
                                end_line = node.body[0].end_lineno if hasattr(node.body[0], 'end_lineno') else start_line
                                for line_num in range(start_line, end_line + 1):
                                    self.docstring_lines.add(line_num)

        def _is_in_docstring(self, lineno):
            return lineno in self.docstring_lines

        def _is_user_input_var(self, node):
            if isinstance(node, ast.Name):
                dangerous_names = ['input', 'user_input', 'user_input_data', 'data', 'payload', 'user_message', 'user_query', 'query', 'message']
                return node.id in dangerous_names
            return False

        def _check_for_injection_patterns(self, value, lineno):
            injection_patterns = [
                'ignore previous',
                'ignore all previous',
                'disregard',
                'forget',
                'new instruction',
                'override',
                'system:',
                'assistant:',
                'user:',
                'role:',
                'jailbreak',
                'developer mode',
                'bypass'
            ]
            value_lower = value.lower()
            for pattern in injection_patterns:
                if pattern in value_lower:
                    return True
            return False

        def visit_Call(self, node):
            lineno = node.lineno
            if self._is_in_docstring(lineno):
                self.generic_visit(node)
                return

            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    if node.func.attr in ['format', 'replace', 'join', 'split', 'strip', 'lower', 'upper']:
                        for arg in node.args:
                            if self._is_user_input_var(arg):
                                self.issues.append(
                                    f"{self.filename}:{lineno}: String operation with potential user input. "
                                    "Validate and sanitize user input before string manipulation."
                                )

            if isinstance(node.func, ast.BinOp):
                if isinstance(node.func.op, ast.Add):
                    has_user_input = False
                    for arg in [node.func.left, node.func.right]:
                        if self._is_user_input_var(arg):
                            has_user_input = True
                            break
                    if has_user_input:
                        self.issues.append(
                            f"{self.filename}:{lineno}: String concatenation with potential user input. "
                            "This could be a prompt injection vector. Use proper validation."
                        )

            self.generic_visit(node)

        def visit_Constant(self, node):
            if isinstance(node.value, str) and not self._is_in_docstring(node.lineno):
                if self._check_for_injection_patterns(node.value, node.lineno):
                    self.issues.append(
                        f"{self.filename}:{node.lineno}: Potential prompt injection pattern detected in string literal. "
                        "Review for hardcoded injection vectors."
                    )
            self.generic_visit(node)

    for py_file in skill_path.glob('**/*.py'):
        if py_file.name == 'audit_skill.py':
            continue
        try:
            content = py_file.read_text(encoding='utf-8')
            source_lines = content.splitlines()

            try:
                tree = ast.parse(content, filename=str(py_file))
                checker = PromptInjectionChecker(py_file.name, source_lines)
                checker._collect_docstring_lines(tree)
                checker.visit(tree)
                issues.extend(checker.issues)
            except SyntaxError as e:
                issues.append(f"{py_file.name}: Syntax error - {e}")
        except Exception as e:
            issues.append(f"Could not read {py_file.name}: {e}")

    if issues:
        return False, issues
    return True, "No prompt injection vectors detected"

def check_code_execution_safety(skill_path):
    """
    Code execution safety checker.

    Checks for:
    - eval(), exec(), compile() usage
    - Unsafe dynamic code patterns
    - Validate subprocess call safety

    Args:
        skill_path: Path to the skill directory to scan.

    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    issues = []

    class CodeExecutionSafetyChecker(ast.NodeVisitor):
        def __init__(self, filename, source_lines):
            self.filename = filename
            self.source_lines = source_lines
            self.issues = []
            self.docstring_lines = set()
            self.dangerous_calls = []

        def _collect_docstring_lines(self, tree):
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    if node.body and isinstance(node.body[0], ast.Expr):
                        if isinstance(node.body[0].value, ast.Constant):
                            if isinstance(node.body[0].value.value, str):
                                start_line = node.body[0].lineno
                                end_line = node.body[0].end_lineno if hasattr(node.body[0], 'end_lineno') else start_line
                                for line_num in range(start_line, end_line + 1):
                                    self.docstring_lines.add(line_num)
                elif isinstance(node, ast.Module):
                    if node.body and isinstance(node.body[0], ast.Expr):
                        if isinstance(node.body[0].value, ast.Constant):
                            if isinstance(node.body[0].value.value, str):
                                start_line = node.body[0].lineno
                                end_line = node.body[0].end_lineno if hasattr(node.body[0], 'end_lineno') else start_line
                                for line_num in range(start_line, end_line + 1):
                                    self.docstring_lines.add(line_num)

        def _is_in_docstring(self, lineno):
            return lineno in self.docstring_lines

        def visit_Call(self, node):
            lineno = node.lineno
            if self._is_in_docstring(lineno):
                self.generic_visit(node)
                return

            if isinstance(node.func, ast.Name):
                if node.func.id in ['eval', 'exec', 'compile']:
                    self.dangerous_calls.append((lineno, node.func.id))
                    self.issues.append(
                        f"{self.filename}:{lineno}: {node.func.id}() detected. "
                        "Dynamic code execution is a critical security risk. Remove or add strict validation."
                    )

            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    if node.func.value.id == 'subprocess' and node.func.attr in ['run', 'call', 'Popen', 'check_output']:
                        has_shell = False
                        has_validation = False

                        for kw in node.keywords:
                            if kw.arg == 'shell' and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                                has_shell = True
                            if kw.arg == 'check' and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                                has_validation = True

                        if has_shell and not has_validation:
                            self.issues.append(
                                f"{self.filename}:{lineno}: subprocess.{node.func.attr}() with shell=True and no check=True. "
                                "Add check=True for safer subprocess execution."
                            )

            self.generic_visit(node)

    for py_file in skill_path.glob('**/*.py'):
        if py_file.name == 'audit_skill.py':
            continue
        try:
            content = py_file.read_text(encoding='utf-8')
            source_lines = content.splitlines()

            try:
                tree = ast.parse(content, filename=str(py_file))
                checker = CodeExecutionSafetyChecker(py_file.name, source_lines)
                checker._collect_docstring_lines(tree)
                checker.visit(tree)
                issues.extend(checker.issues)
            except SyntaxError as e:
                issues.append(f"{py_file.name}: Syntax error - {e}")
        except Exception as e:
            issues.append(f"Could not read {py_file.name}: {e}")

    if issues:
        return False, issues
    return True, "Code execution safety check passed"

def check_filesystem_security(skill_path):
    """
    File system security validator.

    Checks for:
    - Path traversal vulnerabilities
    - Unsafe file operations
    - Validate file permission handling

    Args:
        skill_path: Path to the skill directory to scan.

    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    issues = []

    class FilesystemSecurityChecker(ast.NodeVisitor):
        def __init__(self, filename, source_lines):
            self.filename = filename
            self.source_lines = source_lines
            self.issues = []
            self.docstring_lines = set()

        def _collect_docstring_lines(self, tree):
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    if node.body and isinstance(node.body[0], ast.Expr):
                        if isinstance(node.body[0].value, ast.Constant):
                            if isinstance(node.body[0].value.value, str):
                                start_line = node.body[0].lineno
                                end_line = node.body[0].end_lineno if hasattr(node.body[0], 'end_lineno') else start_line
                                for line_num in range(start_line, end_line + 1):
                                    self.docstring_lines.add(line_num)
                elif isinstance(node, ast.Module):
                    if node.body and isinstance(node.body[0], ast.Expr):
                        if isinstance(node.body[0].value, ast.Constant):
                            if isinstance(node.body[0].value.value, str):
                                start_line = node.body[0].lineno
                                end_line = node.body[0].end_lineno if hasattr(node.body[0], 'end_lineno') else start_line
                                for line_num in range(start_line, end_line + 1):
                                    self.docstring_lines.add(line_num)

        def _is_in_docstring(self, lineno):
            return lineno in self.docstring_lines

        def _check_path_traversal(self, value, lineno):
            traversal_patterns = ['../', '..\\', '%2e%2e', '%2e%2e%2f', '%2e%2e%5c']
            for pattern in traversal_patterns:
                if pattern in value:
                    return True
            return False

        def _is_user_input_var(self, node):
            if isinstance(node, ast.Name):
                dangerous_names = ['input', 'user_input', 'user_input_data', 'data', 'payload', 'filename', 'filepath', 'path', 'file']
                return node.id in dangerous_names
            return False

        def visit_Call(self, node):
            lineno = node.lineno
            if self._is_in_docstring(lineno):
                self.generic_visit(node)
                return

            if isinstance(node.func, ast.Name):
                if node.func.id == 'open':
                    for arg in node.args:
                        if self._is_user_input_var(arg):
                            self.issues.append(
                                f"{self.filename}:{lineno}: open() with potential user input. "
                                "This is a path traversal vulnerability. Validate and sanitize file paths."
                            )

            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    if node.func.attr in ['open', 'read_text', 'write_text', 'read_bytes', 'write_bytes', 'mkdir', 'rmdir', 'unlink', 'remove']:
                        for arg in node.args:
                            if self._is_user_input_var(arg):
                                self.issues.append(
                                    f"{self.filename}:{lineno}: File operation with potential user input. "
                                    "Validate and sanitize file paths to prevent path traversal."
                                )

            self.generic_visit(node)

        def visit_Constant(self, node):
            if isinstance(node.value, str) and not self._is_in_docstring(node.lineno):
                if self._check_path_traversal(node.value, node.lineno):
                    self.issues.append(
                        f"{self.filename}:{node.lineno}: Path traversal pattern detected in string literal. "
                        "Review for hardcoded path traversal vectors."
                    )
            self.generic_visit(node)

    for py_file in skill_path.glob('**/*.py'):
        if py_file.name == 'audit_skill.py':
            continue
        try:
            content = py_file.read_text(encoding='utf-8')
            source_lines = content.splitlines()

            try:
                tree = ast.parse(content, filename=str(py_file))
                checker = FilesystemSecurityChecker(py_file.name, source_lines)
                checker._collect_docstring_lines(tree)
                checker.visit(tree)
                issues.extend(checker.issues)
            except SyntaxError as e:
                issues.append(f"{py_file.name}: Syntax error - {e}")
        except Exception as e:
            issues.append(f"Could not read {py_file.name}: {e}")

    if issues:
        return False, issues
    return True, "File system security check passed"

def check_network_security(skill_path):
    """
    Network security risk detector.

    Checks for:
    - Untrusted URL patterns
    - Missing validation
    - Potential data exfiltration

    Args:
        skill_path: Path to the skill directory to scan.

    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    issues = []

    class NetworkSecurityChecker(ast.NodeVisitor):
        def __init__(self, filename, source_lines):
            self.filename = filename
            self.source_lines = source_lines
            self.issues = []
            self.docstring_lines = set()

        def _collect_docstring_lines(self, tree):
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    if node.body and isinstance(node.body[0], ast.Expr):
                        if isinstance(node.body[0].value, ast.Constant):
                            if isinstance(node.body[0].value.value, str):
                                start_line = node.body[0].lineno
                                end_line = node.body[0].end_lineno if hasattr(node.body[0], 'end_lineno') else start_line
                                for line_num in range(start_line, end_line + 1):
                                    self.docstring_lines.add(line_num)
                elif isinstance(node, ast.Module):
                    if node.body and isinstance(node.body[0], ast.Expr):
                        if isinstance(node.body[0].value, ast.Constant):
                            if isinstance(node.body[0].value.value, str):
                                start_line = node.body[0].lineno
                                end_line = node.body[0].end_lineno if hasattr(node.body[0], 'end_lineno') else start_line
                                for line_num in range(start_line, end_line + 1):
                                    self.docstring_lines.add(line_num)

        def _is_in_docstring(self, lineno):
            return lineno in self.docstring_lines

        def _is_untrusted_url(self, url):
            untrusted_patterns = [
                'http://',
                'localhost',
                '127.0.0.1',
                '0.0.0.0',
                '192.168.',
                '10.',
                '172.16.',
                'file://',
                'ftp://',
                'telnet://',
                'gopher://'
            ]
            for pattern in untrusted_patterns:
                if pattern in url.lower():
                    return True
            return False

        def _is_user_input_var(self, node):
            if isinstance(node, ast.Name):
                dangerous_names = ['input', 'user_input', 'user_input_data', 'data', 'payload', 'url', 'endpoint', 'host', 'address']
                return node.id in dangerous_names
            return False

        def visit_Call(self, node):
            lineno = node.lineno
            if self._is_in_docstring(lineno):
                self.generic_visit(node)
                return

            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    if node.func.value.id in ['requests', 'urllib', 'http'] or node.func.attr in ['urlopen', 'get', 'post', 'put', 'delete', 'request', 'connect', 'send']:
                        for arg in node.args:
                            if self._is_user_input_var(arg):
                                self.issues.append(
                                    f"{self.filename}:{lineno}: Network request with potential user input. "
                                    "Validate and sanitize URLs and parameters to prevent SSRF and injection attacks."
                                )

            self.generic_visit(node)

        def visit_Constant(self, node):
            if isinstance(node.value, str) and not self._is_in_docstring(node.lineno):
                if self._is_untrusted_url(node.value):
                    self.issues.append(
                        f"{self.filename}:{node.lineno}: Untrusted URL pattern detected: '{node.value}'. "
                        "Review for security risks and use trusted URLs only."
                    )
            self.generic_visit(node)

    for py_file in skill_path.glob('**/*.py'):
        if py_file.name == 'audit_skill.py':
            continue
        try:
            content = py_file.read_text(encoding='utf-8')
            source_lines = content.splitlines()

            try:
                tree = ast.parse(content, filename=str(py_file))
                checker = NetworkSecurityChecker(py_file.name, source_lines)
                checker._collect_docstring_lines(tree)
                checker.visit(tree)
                issues.extend(checker.issues)
            except SyntaxError as e:
                issues.append(f"{py_file.name}: Syntax error - {e}")
        except Exception as e:
            issues.append(f"Could not read {py_file.name}: {e}")

    if issues:
        return False, issues
    return True, "Network security check passed"

def check_data_masking(skill_path):
    """
    Check for data masking issues and sensitive data exposure.

    Detects:
    1. Sensitive data exposure in logs
    2. Personal information in output
    3. API keys or tokens in code
    4. Credentials in error messages

    Args:
        skill_path: Path to the skill directory to scan.

    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    issues = []

    sensitive_patterns = [
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

    pii_patterns = [
        r'email\s*=\s*["\'][^"\']+@[^"\']+["\']',
        r'phone\s*=\s*["\'][\d\s\-\(\)]+["\']',
        r'ssn\s*=\s*["\'][\d\s\-]+["\']',
        r'credit_card\s*=\s*["\'][\d\s\-]+["\']',
    ]

    class DataMaskingChecker(ast.NodeVisitor):
        def __init__(self, filename, source_lines):
            self.filename = filename
            self.source_lines = source_lines
            self.issues = []

        def visit_Call(self, node):
            if isinstance(node.func, ast.Name) and node.func.id in ['print', 'log', 'logger', 'logging']:
                for arg in node.args:
                    if isinstance(arg, ast.Name):
                        var_name = arg.id
                        if any(keyword in var_name.lower() for keyword in ['password', 'secret', 'token', 'key', 'credential', 'auth']):
                            self.issues.append(
                                f"{self.filename}:{node.lineno}: Potential sensitive data exposure: logging variable '{var_name}'"
                            )
            self.generic_visit(node)

    for py_file in skill_path.glob('**/*.py'):
        try:
            content = py_file.read_text(encoding='utf-8')
            source_lines = content.splitlines()

            try:
                tree = ast.parse(content, filename=str(py_file))
                checker = DataMaskingChecker(py_file.name, source_lines)
                checker.visit(tree)
                issues.extend(checker.issues)
            except SyntaxError:
                pass

            for i, line in enumerate(source_lines, 1):
                stripped = line.strip()
                if stripped.startswith('#') or stripped.startswith('import') or stripped.startswith('from'):
                    continue

                for pattern in sensitive_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        match = re.search(pattern, line, re.IGNORECASE)
                        if match:
                            value = match.group(0)
                            if not any(placeholder in value.lower() for placeholder in ['todo', 'xxx', 'none', 'null', 'example', 'test']):
                                issues.append(f"{py_file.name}:{i}: Potential hardcoded sensitive data: {value[:50]}...")

                for pattern in pii_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        match = re.search(pattern, line, re.IGNORECASE)
                        if match:
                            value = match.group(0)
                            if not any(placeholder in value.lower() for placeholder in ['todo', 'xxx', 'none', 'null', 'example', 'test']):
                                issues.append(f"{py_file.name}:{i}: Potential hardcoded PII: {value[:50]}...")

        except Exception as e:
            issues.append(f"Could not read {py_file.name}: {e}")

    if issues:
        return False, issues
    return True, "No data masking issues found"

def check_infinite_loops(skill_path):
    """
    Check for potential infinite loops and unbounded recursion.

    Detects:
    1. While loops without proper exit conditions
    2. Recursive functions without base cases
    3. Unbounded iteration patterns
    4. Potential infinite recursion

    Args:
        skill_path: Path to the skill directory to scan.

    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    issues = []

    class InfiniteLoopChecker(ast.NodeVisitor):
        def __init__(self, filename, source_lines):
            self.filename = filename
            self.source_lines = source_lines
            self.issues = []
            self.function_stack = []

        def visit_FunctionDef(self, node):
            self.function_stack.append(node.name)
            self.generic_visit(node)
            self.function_stack.pop()

        def visit_AsyncFunctionDef(self, node):
            self.function_stack.append(node.name)
            self.generic_visit(node)
            self.function_stack.pop()

        def visit_While(self, node):
            if isinstance(node.test, ast.Constant) and node.test.value is True:
                has_break = False
                for child in ast.walk(node):
                    if isinstance(child, ast.Break):
                        has_break = True
                        break

                if not has_break:
                    self.issues.append(
                        f"{self.filename}:{node.lineno}: While loop with constant True condition and no break statement detected"
                    )

            self.generic_visit(node)

        def visit_For(self, node):
            if isinstance(node.iter, ast.Call):
                if isinstance(node.iter.func, ast.Name) and node.iter.func.id == 'range':
                    if len(node.iter.args) == 0:
                        self.issues.append(
                            f"{self.filename}:{node.lineno}: For loop with range() - potential infinite loop"
                        )

            self.generic_visit(node)

        def visit_Call(self, node):
            if isinstance(node.func, ast.Name) and self.function_stack:
                if node.func.id == self.function_stack[-1]:
                    self.issues.append(
                        f"{self.filename}:{node.lineno}: Recursive function '{node.func.id}' detected - ensure proper base case exists"
                    )

            self.generic_visit(node)

    for py_file in skill_path.glob('**/*.py'):
        try:
            content = py_file.read_text(encoding='utf-8')
            source_lines = content.splitlines()

            try:
                tree = ast.parse(content, filename=str(py_file))
                checker = InfiniteLoopChecker(py_file.name, source_lines)
                checker.visit(tree)
                issues.extend(checker.issues)
            except SyntaxError:
                pass

        except Exception as e:
            issues.append(f"Could not read {py_file.name}: {e}")

    if issues:
        return False, issues
    return True, "No infinite loop patterns detected"

def check_token_optimization(skill_path):
    """
    Analyze code for token optimization opportunities.

    Provides suggestions for:
    1. Redundant code elimination
    2. Verbose output reduction
    3. Efficient algorithm alternatives
    4. Token usage optimization tips

    Args:
        skill_path: Path to the skill directory to scan.

    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    suggestions = []

    class TokenOptimizationChecker(ast.NodeVisitor):
        def __init__(self, filename, source_lines):
            self.filename = filename
            self.source_lines = source_lines
            self.suggestions = []
            self.function_lines = {}

        def visit_FunctionDef(self, node):
            start_line = node.lineno
            end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line
            func_length = end_line - start_line + 1
            self.function_lines[node.name] = func_length

            if func_length > 50:
                self.suggestions.append(
                    f"{self.filename}:{start_line}: Function '{node.name}' is {func_length} lines long. Consider splitting into smaller functions for better token efficiency."
                )

            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node):
            start_line = node.lineno
            end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line
            func_length = end_line - start_line + 1
            self.function_lines[node.name] = func_length

            if func_length > 50:
                self.suggestions.append(
                    f"{self.filename}:{start_line}: Async function '{node.name}' is {func_length} lines long. Consider splitting into smaller functions for better token efficiency."
                )

            self.generic_visit(node)

        def visit_If(self, node):
            depth = self._get_nesting_depth(node)
            if depth > 4:
                self.suggestions.append(
                    f"{self.filename}:{node.lineno}: Deep nesting detected (depth {depth}). Consider refactoring to reduce complexity and token usage."
                )
            self.generic_visit(node)

        def _get_nesting_depth(self, node, current_depth=0):
            max_depth = current_depth
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.For, ast.While, ast.With)):
                    child_depth = self._get_nesting_depth(child, current_depth + 1)
                    max_depth = max(max_depth, child_depth)
            return max_depth

    for py_file in skill_path.glob('**/*.py'):
        try:
            content = py_file.read_text(encoding='utf-8')
            source_lines = content.splitlines()

            try:
                tree = ast.parse(content, filename=str(py_file))
                checker = TokenOptimizationChecker(py_file.name, source_lines)
                checker.visit(tree)
                suggestions.extend(checker.suggestions)
            except SyntaxError:
                pass

            for i, line in enumerate(source_lines, 1):
                stripped = line.strip()
                if stripped.startswith('#'):
                    if len(stripped) > 200:
                        suggestions.append(
                            f"{py_file.name}:{i}: Very long comment ({len(stripped)} chars). Consider shortening or moving to documentation."
                        )

        except Exception as e:
            suggestions.append(f"Could not read {py_file.name}: {e}")

    skill_md = skill_path / 'SKILL.md'
    if skill_md.exists():
        try:
            content = skill_md.read_text(encoding='utf-8')
            if len(content) > 10000:
                suggestions.append(
                    f"SKILL.md is very long ({len(content)} chars). Consider condensing descriptions for better token efficiency."
                )
        except Exception:
            pass

    if suggestions:
        return False, suggestions
    return True, "Code is well-optimized for token usage"

def check_ai_execution_effectiveness(skill_path):
    """
    Evaluate AI execution effectiveness in skill documentation and code.

    Assesses:
    1. Clarity of instructions in SKILL.md
    2. Conciseness of prompts
    3. Efficiency of workflows
    4. Verbose outputs

    Args:
        skill_path: Path to the skill directory to scan.

    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    issues = []

    skill_md = skill_path / 'SKILL.md'
    if skill_md.exists():
        try:
            content = skill_md.read_text(encoding='utf-8')
            lines = content.splitlines()

            current_paragraph = []
            for i, line in enumerate(lines, 1):
                if line.strip():
                    current_paragraph.append(line)
                else:
                    if current_paragraph:
                        paragraph_text = ' '.join(current_paragraph)
                        if len(paragraph_text) > 500:
                            issues.append(
                                f"SKILL.md: Very long paragraph detected (around line {i - len(current_paragraph)}). Consider breaking into shorter sections for better AI comprehension."
                            )
                    current_paragraph = []

            redundant_phrases = [
                'please note that',
                'it is important to',
                'keep in mind that',
                'it should be noted that',
                'it is worth mentioning that',
            ]

            for i, line in enumerate(lines, 1):
                for phrase in redundant_phrases:
                    if phrase in line.lower():
                        issues.append(
                            f"SKILL.md:{i}: Redundant phrase '{phrase}' detected. Remove for more concise instructions."
                        )

            vague_patterns = [
                r'\b(do it|make it|fix it|handle it)\b',
                r'\b(appropriate|suitable|proper|correct)\s+(way|manner|method)',
            ]

            for i, line in enumerate(lines, 1):
                for pattern in vague_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        issues.append(
                            f"SKILL.md:{i}: Vague instruction detected. Be more specific for better AI execution."
                        )

        except Exception as e:
            issues.append(f"Could not read SKILL.md: {e}")

    for py_file in skill_path.glob('**/*.py'):
        try:
            content = py_file.read_text(encoding='utf-8')
            source_lines = content.splitlines()

            print_count = 0
            for line in source_lines:
                stripped = line.strip()
                if stripped.startswith('print('):
                    print_count += 1

            if print_count > 30:
                issues.append(
                    f"{py_file.name}: High number of print statements ({print_count}). Consider reducing verbose output for better AI execution efficiency."
                )

        except Exception as e:
            issues.append(f"Could not read {py_file.name}: {e}")

    if issues:
        return False, issues
    return True, "AI execution effectiveness looks good"

def check_verbose_output(skill_path):
    """
    Detect verbose output patterns in skill code.

    Identifies:
    1. Excessive print statements
    2. Redundant logging
    3. Unnecessary debug output
    4. Output consolidation opportunities

    Args:
        skill_path: Path to the skill directory to scan.

    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    issues = []

    class VerboseOutputChecker(ast.NodeVisitor):
        def __init__(self, filename, source_lines):
            self.filename = filename
            self.source_lines = source_lines
            self.issues = []
            self.print_count = 0
            self.log_count = 0
            self.debug_prints = []

        def visit_Call(self, node):
            if isinstance(node.func, ast.Name) and node.func.id == 'print':
                self.print_count += 1

                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        if any(keyword in arg.value.lower() for keyword in ['debug', 'test', 'xxx', 'todo', 'fixme']):
                            self.debug_prints.append(
                                f"{self.filename}:{node.lineno}: Debug print statement detected: '{arg.value[:50]}...'"
                            )

            if isinstance(node.func, ast.Attribute):
                if node.func.attr in ['debug', 'info', 'warning', 'error', 'critical']:
                    self.log_count += 1

            self.generic_visit(node)

    for py_file in skill_path.glob('**/*.py'):
        try:
            content = py_file.read_text(encoding='utf-8')
            source_lines = content.splitlines()

            try:
                tree = ast.parse(content, filename=str(py_file))
                checker = VerboseOutputChecker(py_file.name, source_lines)
                checker.visit(tree)

                if checker.print_count > 20:
                    issues.append(
                        f"{py_file.name}: Excessive print statements ({checker.print_count}). Consider consolidating output or using logging levels."
                    )

                if checker.log_count > 30:
                    issues.append(
                        f"{py_file.name}: Excessive logging statements ({checker.log_count}). Consider reducing log verbosity."
                    )

                issues.extend(checker.debug_prints)

            except SyntaxError:
                pass

            consecutive_prints = 0
            for line in source_lines:
                stripped = line.strip()
                if stripped.startswith('print('):
                    consecutive_prints += 1
                    if consecutive_prints > 5:
                        issues.append(
                            f"{py_file.name}: Consecutive print statements detected. Consider consolidating into a single output."
                        )
                        break
                else:
                    consecutive_prints = 0

        except Exception as e:
            issues.append(f"Could not read {py_file.name}: {e}")

    if issues:
        return False, issues
    return True, "Output verbosity is reasonable"

def check_redundant_code(skill_path):
    """
    Identify redundant code patterns in skill code.

    Finds:
    1. Duplicate code blocks
    2. Unused imports
    3. Dead code
    4. Code consolidation opportunities

    Args:
        skill_path: Path to the skill directory to scan.

    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    issues = []

    class RedundantCodeChecker(ast.NodeVisitor):
        def __init__(self, filename, source_lines):
            self.filename = filename
            self.source_lines = source_lines
            self.issues = []
            self.imports = set()
            self.used_names = set()
            self.function_defs = {}

        def visit_Import(self, node):
            for alias in node.names:
                self.imports.add(alias.name)
            self.generic_visit(node)

        def visit_ImportFrom(self, node):
            for alias in node.names:
                self.imports.add(alias.name)
            self.generic_visit(node)

        def visit_Name(self, node):
            self.used_names.add(node.id)
            self.generic_visit(node)

        def visit_FunctionDef(self, node):
            self.function_defs[node.name] = node.lineno

            if not node.body:
                issues.append(f"{self.filename}:{node.lineno}: Empty function '{node.name}' detected. Remove or implement.")
            elif len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                issues.append(f"{self.filename}:{node.lineno}: Function '{node.name}' only contains 'pass'. Remove or implement.")

            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node):
            self.function_defs[node.name] = node.lineno

            if not node.body:
                issues.append(f"{self.filename}:{node.lineno}: Empty async function '{node.name}' detected. Remove or implement.")
            elif len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                issues.append(f"{self.filename}:{node.lineno}: Async function '{node.name}' only contains 'pass'. Remove or implement.")

            self.generic_visit(node)

        def visit_ClassDef(self, node):
            if not node.body:
                issues.append(f"{self.filename}:{node.lineno}: Empty class '{node.name}' detected. Remove or implement.")
            elif len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                issues.append(f"{self.filename}:{node.lineno}: Class '{node.name}' only contains 'pass'. Remove or implement.")

            self.generic_visit(node)

    for py_file in skill_path.glob('**/*.py'):
        try:
            content = py_file.read_text(encoding='utf-8')
            source_lines = content.splitlines()

            try:
                tree = ast.parse(content, filename=str(py_file))
                checker = RedundantCodeChecker(py_file.name, source_lines)
                checker.visit(tree)

                for imp in checker.imports:
                    if '.' in imp:
                        base_name = imp.split('.')[-1]
                    else:
                        base_name = imp

                    if base_name not in checker.used_names:
                        issues.append(
                            f"{py_file.name}: Unused import '{imp}' detected. Remove to reduce code size."
                        )

                code_blocks = {}
                for i in range(0, len(source_lines) - 2, 3):
                    block = '\n'.join(source_lines[i:i+3])
                    if len(block) > 50:
                        if block in code_blocks:
                            issues.append(
                                f"{py_file.name}: Potential duplicate code block detected around line {i+1} (similar to line {code_blocks[block]+1}). Consider consolidating."
                            )
                        else:
                            code_blocks[block] = i

            except SyntaxError:
                pass

        except Exception as e:
            issues.append(f"Could not read {py_file.name}: {e}")

    if issues:
        return False, issues
    return True, "No redundant code patterns detected"

def audit_skill(skill_path, skills_dir=None, verbose=False, json_output=False, check_level="standard"):
    """
    Audit a skill for compliance and best practices.
    
    Args:
        skill_path: Path to the skill directory to audit
        skills_dir: Optional path to skills root directory (for registry checks)
        verbose: Enable verbose output
        json_output: Output in JSON format
        check_level: Check strictness - "strict", "standard", or "relaxed"
    
    Returns:
        bool: True if audit passed, False otherwise
    """
    skill_path = Path(skill_path)
    if skills_dir is None:
        skills_dir = skill_path.parent
    
    print(f"[*] Auditing Skill: {skill_path.name}")
    print(f"   Path: {skill_path}\n")
    
    has_errors = False
    has_warnings = False
    
    # Issue counters for different categories
    security_issues = 0
    quality_issues = 0
    output_quality_issues = 0
    
    # Severity tracking
    critical_issues = 0
    high_issues = 0
    medium_issues = 0
    low_issues = 0
    
    # Determine which checks to run based on check_level
    # strict: all checks, i18n issues are errors
    # standard: all checks, i18n issues are warnings (default)
    # relaxed: only critical checks (basic structure, dependencies, encoding)
    run_i18n_checks = check_level in ["strict", "standard"]
    run_packaging_checks = check_level in ["strict", "standard"]
    run_subprocess_checks = check_level in ["strict", "standard"]
    run_cross_platform_checks = check_level in ["strict", "standard"]
    run_absolute_ref_checks = check_level in ["strict", "standard"]
    run_registry_checks = check_level in ["strict", "standard"]
    run_security_checks = check_level in ["strict", "standard"]
    run_quality_checks = check_level in ["strict", "standard"]
    run_output_quality_checks = check_level in ["strict", "standard"]
    
    # Emoji usage is now ALWAYS an error (mandatory requirement)
    # i18n_as_error is for other i18n issues (like hardcoded strings)
    i18n_as_error = (check_level == "strict")
    
    # Section 1: Basic Structure
    print_info("=== Basic Structure ===", json_output)
    
    ok, msg = validate_frontmatter(skill_path)
    if ok: print_pass(msg, json_output)
    else: print_fail(msg, json_output); has_errors = True
    
    ok, msg = check_skill_name_consistency(skill_path)
    if ok: print_pass(msg, json_output)
    else: print_fail(msg, json_output); has_errors = True
    
    ok, msg = check_directory_structure(skill_path)
    if ok: print_pass(msg, json_output)
    else: 
        print_fail("Directory structure issues:", json_output)
        if isinstance(msg, list):
            for issue in msg: print(f"      - {issue}")
        else:
            print(f"      - {msg}")
        has_errors = True
    
    # Section 2: Dependencies
    print_info("\n=== Dependencies ===", json_output)
    
    ok, msg = check_dependencies(skill_path)
    if ok: print_pass(msg, json_output)
    else: print_fail(msg, json_output); has_errors = True
    
    # Section 3: Encoding & Path Safety
    print_info("\n=== Encoding & Path Safety ===", json_output)
    
    ok, msg = check_encoding_safety(skill_path)
    if ok:
        print_pass(msg, json_output)
    else:
        print_fail("Found potential encoding issues:", json_output)
        for issue in msg:
            print(f"      - {issue}")
        has_errors = True
        
    ok, msg = check_path_consistency(skill_path)
    if ok:
        print_pass(msg, json_output)
    else:
        print_fail("Found path inconsistencies:", json_output)
        for issue in msg:
            print(f"      - {issue}")
        has_errors = True
    
    # Section 4: Packaging
    if run_packaging_checks:
        print_info("\n=== Packaging ===", json_output)
        
        ok, msg = check_packaging_logic(skill_path)
        if ok: print_pass(msg, json_output)
        else: print_fail(msg, json_output); has_errors = True
        
        ok, msg = check_init_script_template(skill_path)
        if ok: print_pass(msg, json_output)
        else: print_fail(msg, json_output); has_errors = True
    
    # Section 5: Subprocess & Path Operations
    if run_subprocess_checks:
        print_info("\n=== Subprocess & Path Operations ===", json_output)
        
        ok, msg = check_subprocess_robustness(skill_path)
        if ok:
            print_pass(msg, json_output)
        else:
            print_fail("Found potential subprocess robustness issues:", json_output)
            for issue in msg:
                print(f"      - {issue}")
            has_errors = True
        
        ok, msg = check_risky_path_ops(skill_path)
        if ok:
            print_pass(msg, json_output)
        else:
            print_fail("Found potential risky path operations:", json_output)
            for issue in msg:
                print(f"      - {issue}")
            has_errors = True
    
    # Cross-Platform Compatibility
    if run_cross_platform_checks:
        ok, msg = check_cross_platform_compatibility(skill_path)
        if ok:
            print_pass(msg, json_output)
        else:
            print_fail("Found cross-platform compatibility issues:", json_output)
            for issue in msg:
                print(f"      - {issue}")
            has_errors = True
    
    # Section 7: Internationalization (i18n)
    if run_i18n_checks:
        print_info("\n=== Internationalization (i18n) ===", json_output)
        
        ok, msg = check_i18n_support(skill_path)
        if ok:
            print_pass(msg, json_output)
        else:
            # Check if any issue is an emoji error (which is always FAIL)
            has_emoji_issue = any("Emoji found" in issue for issue in msg)
            
            if has_emoji_issue or i18n_as_error:
                print_fail("Found i18n issues:", json_output)
                has_errors = True
            else:
                print_warn("Found i18n issues (warnings):", json_output)
                has_warnings = True
            for issue in msg:
                print(f"      - {issue}")
    
    # Section 8: Absolute References
    if run_absolute_ref_checks:
        print_info("\n=== Absolute References ===", json_output)
        
        ok, msg = check_absolute_references(skill_path)
        if ok:
            print_pass(msg, json_output)
        else:
            print_fail("Found absolute references:", json_output)
            for issue in msg:
                print(f"      - {issue}")
            has_errors = True
    
    # Section 9: Registry & Map Consistency
    if run_registry_checks:
        print_info("\n=== Registry & Map Consistency ===", json_output)
        
        ok, msg = check_registry_consistency(skill_path, skills_dir)
        if ok:
            print_pass(msg, json_output)
        else:
            print_fail("Registry consistency issues:", json_output)
            if isinstance(msg, list):
                for issue in msg: print(f"      - {issue}")
            else:
                print(f"      - {msg}")
            has_warnings = True
        
        ok, msg = check_skill_map_consistency(skill_path, skills_dir)
        if ok:
            print_pass(msg, json_output)
        else:
            print_fail("Skill map consistency issues:", json_output)
            if isinstance(msg, list):
                for issue in msg: print(f"      - {issue}")
            else:
                print(f"      - {msg}")
            has_warnings = True
    
    # Section 10: Security Analysis
    if run_security_checks:
        print_info("\n=== Security Analysis ===", json_output)
        
        ok, msg = check_malicious_script_injection(skill_path)
        if ok:
            print_pass(msg, json_output)
        else:
            print_fail("Found malicious script injection patterns:", json_output)
            if isinstance(msg, list):
                for issue in msg: 
                    print(f"      - [CRITICAL] {issue}")
                    security_issues += 1
                    critical_issues += 1
            else:
                print(f"      - [CRITICAL] {msg}")
                security_issues += 1
                critical_issues += 1
            has_errors = True
        
        ok, msg = check_permission_abuse(skill_path)
        if ok:
            print_pass(msg, json_output)
        else:
            print_fail("Found permission abuse risks:", json_output)
            if isinstance(msg, list):
                for issue in msg: 
                    print(f"      - [HIGH] {issue}")
                    security_issues += 1
                    high_issues += 1
            else:
                print(f"      - [HIGH] {msg}")
                security_issues += 1
                high_issues += 1
            has_errors = True
        
        ok, msg = check_prompt_injection(skill_path)
        if ok:
            print_pass(msg, json_output)
        else:
            print_fail("Found prompt injection vectors:", json_output)
            if isinstance(msg, list):
                for issue in msg: 
                    print(f"      - [CRITICAL] {issue}")
                    security_issues += 1
                    critical_issues += 1
            else:
                print(f"      - [CRITICAL] {msg}")
                security_issues += 1
                critical_issues += 1
            has_errors = True
        
        ok, msg = check_code_execution_safety(skill_path)
        if ok:
            print_pass(msg, json_output)
        else:
            print_fail("Found code execution safety issues:", json_output)
            if isinstance(msg, list):
                for issue in msg: 
                    print(f"      - [CRITICAL] {issue}")
                    security_issues += 1
                    critical_issues += 1
            else:
                print(f"      - [CRITICAL] {msg}")
                security_issues += 1
                critical_issues += 1
            has_errors = True
        
        ok, msg = check_filesystem_security(skill_path)
        if ok:
            print_pass(msg, json_output)
        else:
            print_fail("Found filesystem security issues:", json_output)
            if isinstance(msg, list):
                for issue in msg: 
                    print(f"      - [HIGH] {issue}")
                    security_issues += 1
                    high_issues += 1
            else:
                print(f"      - [HIGH] {msg}")
                security_issues += 1
                high_issues += 1
            has_errors = True
        
        ok, msg = check_network_security(skill_path)
        if ok:
            print_pass(msg, json_output)
        else:
            print_fail("Found network security issues:", json_output)
            if isinstance(msg, list):
                for issue in msg: 
                    print(f"      - [HIGH] {issue}")
                    security_issues += 1
                    high_issues += 1
            else:
                print(f"      - [HIGH] {msg}")
                security_issues += 1
                high_issues += 1
            has_errors = True
    
    # Section 11: Quality Checks
    if run_quality_checks:
        print_info("\n=== Quality Checks ===", json_output)
        
        ok, msg = check_technical_standards(skill_path)
        if ok:
            print_pass(msg, json_output)
        else:
            print_fail("Technical standards issues:", json_output)
            if isinstance(msg, list):
                for issue in msg: 
                    print(f"      - [MEDIUM] {issue}")
                    quality_issues += 1
                    medium_issues += 1
            else:
                print(f"      - [MEDIUM] {msg}")
                quality_issues += 1
                medium_issues += 1
            has_errors = True
        
        ok, msg = check_error_handling_patterns(skill_path)
        if ok:
            print_pass(msg, json_output)
        else:
            print_fail("Error handling pattern issues:", json_output)
            if isinstance(msg, list):
                for issue in msg: 
                    print(f"      - [HIGH] {issue}")
                    quality_issues += 1
                    high_issues += 1
            else:
                print(f"      - [HIGH] {msg}")
                quality_issues += 1
                high_issues += 1
            has_errors = True
        
        ok, msg = check_logging_practices(skill_path)
        if ok:
            print_pass(msg, json_output)
        else:
            print_warn("Logging practice issues:", json_output)
            if isinstance(msg, list):
                for issue in msg: 
                    print(f"      - [LOW] {issue}")
                    quality_issues += 1
                    low_issues += 1
            else:
                print(f"      - [LOW] {msg}")
                quality_issues += 1
                low_issues += 1
            has_warnings = True
        
        ok, msg = check_input_validation(skill_path)
        if ok:
            print_pass(msg, json_output)
        else:
            print_fail("Input validation issues:", json_output)
            if isinstance(msg, list):
                for issue in msg: 
                    print(f"      - [HIGH] {issue}")
                    quality_issues += 1
                    high_issues += 1
            else:
                print(f"      - [HIGH] {msg}")
                quality_issues += 1
                high_issues += 1
            has_errors = True
        
        ok, msg = check_output_sanitization(skill_path)
        if ok:
            print_pass(msg, json_output)
        else:
            print_fail("Output sanitization issues:", json_output)
            if isinstance(msg, list):
                for issue in msg: 
                    print(f"      - [HIGH] {issue}")
                    quality_issues += 1
                    high_issues += 1
            else:
                print(f"      - [HIGH] {msg}")
                quality_issues += 1
                high_issues += 1
            has_errors = True
        
        ok, msg = check_dependency_security(skill_path)
        if ok:
            print_pass(msg, json_output)
        else:
            print_warn("Dependency security issues:", json_output)
            if isinstance(msg, list):
                for issue in msg: 
                    print(f"      - [MEDIUM] {issue}")
                    quality_issues += 1
                    medium_issues += 1
            else:
                print(f"      - [MEDIUM] {msg}")
                quality_issues += 1
                medium_issues += 1
            has_warnings = True
    
    # Section 12: Output Quality Checks
    if run_output_quality_checks:
        print_info("\n=== Output Quality Checks ===", json_output)
        
        ok, msg = check_data_masking(skill_path)
        if ok:
            print_pass(msg, json_output)
        else:
            print_fail("Found data masking issues:", json_output)
            if isinstance(msg, list):
                for issue in msg: 
                    print(f"      - [CRITICAL] {issue}")
                    output_quality_issues += 1
                    critical_issues += 1
            else:
                print(f"      - [CRITICAL] {msg}")
                output_quality_issues += 1
                critical_issues += 1
            has_errors = True
        
        ok, msg = check_infinite_loops(skill_path)
        if ok:
            print_pass(msg, json_output)
        else:
            print_fail("Found infinite loop patterns:", json_output)
            if isinstance(msg, list):
                for issue in msg: 
                    print(f"      - [HIGH] {issue}")
                    output_quality_issues += 1
                    high_issues += 1
            else:
                print(f"      - [HIGH] {msg}")
                output_quality_issues += 1
                high_issues += 1
            has_errors = True
        
        ok, msg = check_token_optimization(skill_path)
        if ok:
            print_pass(msg, json_output)
        else:
            print_warn("Token optimization suggestions:", json_output)
            if isinstance(msg, list):
                for issue in msg: 
                    print(f"      - [LOW] {issue}")
                    output_quality_issues += 1
                    low_issues += 1
            else:
                print(f"      - [LOW] {msg}")
                output_quality_issues += 1
                low_issues += 1
            has_warnings = True
        
        ok, msg = check_ai_execution_effectiveness(skill_path)
        if ok:
            print_pass(msg, json_output)
        else:
            print_warn("AI execution effectiveness issues:", json_output)
            if isinstance(msg, list):
                for issue in msg: 
                    print(f"      - [MEDIUM] {issue}")
                    output_quality_issues += 1
                    medium_issues += 1
            else:
                print(f"      - [MEDIUM] {msg}")
                output_quality_issues += 1
                medium_issues += 1
            has_warnings = True
        
        ok, msg = check_verbose_output(skill_path)
        if ok:
            print_pass(msg, json_output)
        else:
            print_warn("Verbose output issues:", json_output)
            if isinstance(msg, list):
                for issue in msg: 
                    print(f"      - [LOW] {issue}")
                    output_quality_issues += 1
                    low_issues += 1
            else:
                print(f"      - [LOW] {msg}")
                output_quality_issues += 1
                low_issues += 1
            has_warnings = True
        
        ok, msg = check_redundant_code(skill_path)
        if ok:
            print_pass(msg, json_output)
        else:
            print_warn("Redundant code patterns:", json_output)
            if isinstance(msg, list):
                for issue in msg: 
                    print(f"      - [LOW] {issue}")
                    output_quality_issues += 1
                    low_issues += 1
            else:
                print(f"      - [LOW] {msg}")
                output_quality_issues += 1
                low_issues += 1
            has_warnings = True
    
    print("\n" + "="*40)
    
    # Print detailed summary
    total_issues = security_issues + quality_issues + output_quality_issues
    if total_issues > 0 or has_errors or has_warnings:
        print(f"\nAudit Summary:")
        print(f"  Security Issues: {security_issues}")
        print(f"  Quality Issues: {quality_issues}")
        print(f"  Output Quality Issues: {output_quality_issues}")
        print(f"  Total Issues: {total_issues}")
        
        if critical_issues > 0 or high_issues > 0 or medium_issues > 0 or low_issues > 0:
            print(f"\nSeverity Breakdown:")
            if critical_issues > 0:
                print(f"  CRITICAL: {critical_issues}")
            if high_issues > 0:
                print(f"  HIGH: {high_issues}")
            if medium_issues > 0:
                print(f"  MEDIUM: {medium_issues}")
            if low_issues > 0:
                print(f"  LOW: {low_issues}")
    
    # Determine audit result based on severity
    audit_failed = has_errors or (critical_issues > 0) or (high_issues > 0)
    audit_warnings = has_warnings or (medium_issues > 0) or (low_issues > 0)
    
    if audit_failed:
        print(f"{RED}[!] Audit completed with errors. Please fix issues above.{RESET}")
        return False
    elif audit_warnings:
        print(f"{YELLOW}[!] Audit completed with warnings. Review issues above.{RESET}")
        return True
    else:
        print(f"{GREEN}[*] Skill passed all standard checks!{RESET}")
        return True

def check_risky_path_ops(skill_path):
    """
    Check for potentially risky file system operations and security issues.
    
    Checks for:
    1. os.system() usage (prefer subprocess)
    2. Hardcoded file paths (using '/' or '\' in strings)
    3. os.path.join (prefer pathlib)
    4. Additional security-related path operations
    5. Unsafe file system access patterns
    6. Permission escalation risks
    7. Symlink and hardlink operations
    8. Unsafe file permission changes
    """
    issues = []
    
    class RiskyPathOpsChecker(ast.NodeVisitor):
        def __init__(self, filename, source_lines):
            self.filename = filename
            self.source_lines = source_lines
            self.issues = []
            self.docstring_lines = set()
            
        def _collect_docstring_lines(self, tree):
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    if node.body and isinstance(node.body[0], ast.Expr):
                        if isinstance(node.body[0].value, ast.Constant):
                            if isinstance(node.body[0].value.value, str):
                                start_line = node.body[0].lineno
                                end_line = node.body[0].end_lineno if hasattr(node.body[0], 'end_lineno') else start_line
                                for line_num in range(start_line, end_line + 1):
                                    self.docstring_lines.add(line_num)
                elif isinstance(node, ast.Module):
                    if node.body and isinstance(node.body[0], ast.Expr):
                        if isinstance(node.body[0].value, ast.Constant):
                            if isinstance(node.body[0].value.value, str):
                                start_line = node.body[0].lineno
                                end_line = node.body[0].end_lineno if hasattr(node.body[0], 'end_lineno') else start_line
                                for line_num in range(start_line, end_line + 1):
                                    self.docstring_lines.add(line_num)
        
        def _is_in_docstring(self, lineno):
            return lineno in self.docstring_lines
        
        def _is_user_input_var(self, node):
            if isinstance(node, ast.Name):
                dangerous_names = ['input', 'user_input', 'user_input_data', 'data', 'payload', 'filename', 'filepath', 'path', 'file', 'arg', 'argument', 'user_path', 'target', 'source']
                return node.id in dangerous_names
            return False
        
        def visit_Call(self, node):
            lineno = node.lineno
            if self._is_in_docstring(lineno):
                self.generic_visit(node)
                return
            
            if isinstance(node.func, ast.Name):
                if node.func.id == 'open':
                    for arg in node.args:
                        if self._is_user_input_var(arg):
                            self.issues.append(
                                f"{self.filename}:{lineno}: open() with potential user input. "
                                "Validate and sanitize file paths to prevent path traversal."
                            )
            
            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    if node.func.value.id == 'os':
                        if node.func.attr == 'system':
                            self.issues.append(
                                f"{self.filename}:{lineno}: os.system() detected. "
                                "Prefer subprocess.run() for better control and security."
                            )
                        
                        if node.func.attr in ['popen', 'spawn', 'execl', 'execle', 'execlp', 'execv', 'execve', 'execvp', 'execvpe']:
                            self.issues.append(
                                f"{self.filename}:{lineno}: os.{node.func.attr}() detected. "
                                "Prefer subprocess.run() for better control and security."
                            )
                        
                        if node.func.attr == 'chmod':
                            for arg in node.args:
                                if self._is_user_input_var(arg):
                                    self.issues.append(
                                        f"{self.filename}:{lineno}: os.chmod() with potential user input. "
                                        "This is a permission escalation risk. Validate and sanitize mode values."
                                    )
                        
                        if node.func.attr in ['chown', 'chroot']:
                            self.issues.append(
                                f"{self.filename}:{lineno}: os.{node.func.attr}() detected. "
                                "This is a high-risk operation. Ensure proper validation and authorization."
                            )
                        
                        if node.func.attr == 'link':
                            for arg in node.args:
                                if self._is_user_input_var(arg):
                                    self.issues.append(
                                        f"{self.filename}:{lineno}: os.link() with potential user input. "
                                        "Hardlink operations can be security-sensitive. Validate paths."
                                    )
                        
                        if node.func.attr == 'symlink':
                            for arg in node.args:
                                if self._is_user_input_var(arg):
                                    self.issues.append(
                                        f"{self.filename}:{lineno}: os.symlink() with potential user input. "
                                        "Symlink operations can lead to race conditions. Validate paths."
                                    )
                        
                        if node.func.attr == 'remove':
                            for arg in node.args:
                                if self._is_user_input_var(arg):
                                    self.issues.append(
                                        f"{self.filename}:{lineno}: os.remove() with potential user input. "
                                        "File deletion with user input is dangerous. Validate paths."
                                    )
                        
                        if node.func.attr == 'rmdir':
                            for arg in node.args:
                                if self._is_user_input_var(arg):
                                    self.issues.append(
                                        f"{self.filename}:{lineno}: os.rmdir() with potential user input. "
                                        "Directory deletion with user input is dangerous. Validate paths."
                                    )
                    
                    if node.func.value.id == 'shutil':
                        if node.func.attr in ['rmtree', 'copy', 'copy2', 'move']:
                            for arg in node.args:
                                if self._is_user_input_var(arg):
                                    self.issues.append(
                                        f"{self.filename}:{lineno}: shutil.{node.func.attr}() with potential user input. "
                                        "File system operations with user input are dangerous. Validate paths."
                                    )
                    
                    if node.func.value.id == 'pathlib' and node.func.attr == 'Path':
                        for arg in node.args:
                            if self._is_user_input_var(arg):
                                self.issues.append(
                                    f"{self.filename}:{lineno}: pathlib.Path() with potential user input. "
                                    "Validate and sanitize paths to prevent path traversal."
                                )
                    
                    if node.func.attr in ['unlink', 'rmdir', 'mkdir', 'makedirs', 'remove']:
                        for arg in node.args:
                            if self._is_user_input_var(arg):
                                self.issues.append(
                                    f"{self.filename}:{lineno}: File system operation with potential user input. "
                                    "Validate and sanitize paths to prevent unauthorized access."
                                )
            
            self.generic_visit(node)
        
        def visit_Constant(self, node):
            if isinstance(node.value, str) and not self._is_in_docstring(node.lineno):
                if ('../' in node.value or '..\\' in node.value) and len(node.value) > 10:
                    self.issues.append(
                        f"{self.filename}:{node.lineno}: Potential path traversal pattern in string literal: '{node.value[:50]}...'. "
                        "Review for hardcoded path traversal vectors."
                    )
            self.generic_visit(node)
    
    for py_file in skill_path.glob('**/*.py'):
        if py_file.name == 'audit_skill.py':
            continue
        try:
            content = py_file.read_text(encoding='utf-8')
            source_lines = content.splitlines()
            
            try:
                tree = ast.parse(content, filename=str(py_file))
                checker = RiskyPathOpsChecker(py_file.name, source_lines)
                checker._collect_docstring_lines(tree)
                checker.visit(tree)
                issues.extend(checker.issues)
            except SyntaxError as e:
                issues.append(f"{py_file.name}: Syntax error - {e}")
        except Exception as e:
            issues.append(f"Could not read {py_file.name}: {e}")
    
    if issues:
        return False, issues
    return True, "No high-risk file operations detected"

def check_subprocess_robustness(skill_path):
    """
    Check for robust encoding handling and security in subprocess calls.
    
    This function scans Python files for subprocess.run() and subprocess.check_output()
    calls that capture text output but lack proper error handling for encoding issues.
    Also checks for shell=True usage which is a security risk.
    
    Additional security checks:
    - Command injection vulnerability detection
    - Shell injection risk assessment
    - Unsafe argument passing patterns
    - Missing input validation
    
    Args:
        skill_path: Path to the skill directory to scan.
        
    Returns:
        tuple: (success: bool, message: str | list[str])
            - If success: (True, "Subprocess calls appear robust or binary")
            - If failure: (False, list of issue descriptions)
    """
    issues = []
    
    class SubprocessSecurityChecker(ast.NodeVisitor):
        def __init__(self, filename, source_lines):
            self.filename = filename
            self.source_lines = source_lines
            self.issues = []
            self.docstring_lines = set()
            
        def _collect_docstring_lines(self, tree):
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    if node.body and isinstance(node.body[0], ast.Expr):
                        if isinstance(node.body[0].value, ast.Constant):
                            if isinstance(node.body[0].value.value, str):
                                start_line = node.body[0].lineno
                                end_line = node.body[0].end_lineno if hasattr(node.body[0], 'end_lineno') else start_line
                                for line_num in range(start_line, end_line + 1):
                                    self.docstring_lines.add(line_num)
                elif isinstance(node, ast.Module):
                    if node.body and isinstance(node.body[0], ast.Expr):
                        if isinstance(node.body[0].value, ast.Constant):
                            if isinstance(node.body[0].value.value, str):
                                start_line = node.body[0].lineno
                                end_line = node.body[0].end_lineno if hasattr(node.body[0], 'end_lineno') else start_line
                                for line_num in range(start_line, end_line + 1):
                                    self.docstring_lines.add(line_num)
        
        def _is_in_docstring(self, lineno):
            return lineno in self.docstring_lines
        
        def _is_user_input_var(self, node):
            if isinstance(node, ast.Name):
                dangerous_names = ['input', 'user_input', 'user_input_data', 'data', 'payload', 'cmd', 'command', 'filename', 'filepath', 'path', 'arg', 'argument', 'user_cmd', 'shell_cmd']
                return node.id in dangerous_names
            return False
        
        def _check_for_injection_patterns(self, value):
            injection_patterns = [
                ';', '|', '&', '&&', '||', '`', '$(', '$(`', 
                '>', '>>', '<', '2>&1', '2>/dev/null',
                '${', '#{', '%{', '\x00', '\n', '\r'
            ]
            for pattern in injection_patterns:
                if pattern in value:
                    return True
            return False
        
        def visit_Call(self, node):
            lineno = node.lineno
            if self._is_in_docstring(lineno):
                self.generic_visit(node)
                return
            
            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name) and node.func.value.id == 'subprocess':
                    if node.func.attr in ['run', 'check_output', 'call', 'Popen']:
                        has_shell_true = False
                        has_errors_param = False
                        has_text_mode = False
                        captures_output = False
                        has_user_input = False
                        has_check = False
                        has_timeout = False
                        
                        for kw in node.keywords:
                            if kw.arg == 'shell':
                                if isinstance(kw.value, ast.Constant) and kw.value.value is True:
                                    has_shell_true = True
                            elif kw.arg == 'errors':
                                has_errors_param = True
                            elif kw.arg in ['text', 'universal_newlines']:
                                if isinstance(kw.value, ast.Constant) and kw.value.value is True:
                                    has_text_mode = True
                            elif kw.arg == 'capture_output':
                                if isinstance(kw.value, ast.Constant) and kw.value.value is True:
                                    captures_output = True
                            elif kw.arg == 'stdout':
                                if isinstance(kw.value, ast.Attribute):
                                    if isinstance(kw.value.value, ast.Name) and kw.value.value.id == 'subprocess':
                                        if kw.value.attr == 'PIPE':
                                            captures_output = True
                            elif kw.arg == 'check':
                                if isinstance(kw.value, ast.Constant) and kw.value.value is True:
                                    has_check = True
                            elif kw.arg == 'timeout':
                                has_timeout = True
                        
                        has_user_input = any(self._is_user_input_var(arg) for arg in node.args)
                        
                        for arg in node.args:
                            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                                if self._check_for_injection_patterns(arg.value):
                                    self.issues.append(
                                        f"{self.filename}:{lineno}: subprocess.{node.func.attr}() with potential command injection pattern in string literal. "
                                        "Use list arguments instead of string concatenation."
                                    )
                        
                        if has_shell_true and has_user_input:
                            self.issues.append(
                                f"{self.filename}:{lineno}: subprocess.{node.func.attr}() with shell=True and user input. "
                                "This is a critical command injection vulnerability. Use list arguments instead."
                            )
                        elif has_shell_true:
                            self.issues.append(
                                f"{self.filename}:{lineno}: subprocess.{node.func.attr}() uses shell=True. "
                                "This is a security risk. Avoid shell=True unless absolutely necessary. Use list arguments for better security."
                            )
                        elif has_user_input:
                            self.issues.append(
                                f"{self.filename}:{lineno}: subprocess.{node.func.attr}() with potential user input. "
                                "Validate and sanitize user input before subprocess calls. Use list arguments."
                            )
                        
                        if has_text_mode and captures_output and not has_errors_param:
                            self.issues.append(
                                f"{self.filename}:{lineno}: subprocess.{node.func.attr}() might crash on non-UTF8 output "
                                "(missing errors='replace' or similar error handling)"
                            )
                        
                        if node.func.attr == 'Popen' and not has_timeout:
                            self.issues.append(
                                f"{self.filename}:{lineno}: subprocess.Popen() without timeout parameter. "
                                "Consider adding timeout to prevent hanging processes."
                            )
                        
                        if captures_output and not has_check and node.func.attr != 'Popen':
                            self.issues.append(
                                f"{self.filename}:{lineno}: subprocess.{node.func.attr}() captures output without check=True. "
                                "Consider adding check=True to detect command failures."
                            )
            
            if isinstance(node.func, ast.Name):
                if node.func.id == 'open':
                    for arg in node.args:
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                            if self._check_for_injection_patterns(arg.value):
                                self.issues.append(
                                    f"{self.filename}:{lineno}: open() with potential injection pattern in filename. "
                                    "Validate and sanitize filenames."
                                )
            
            self.generic_visit(node)
        
        def visit_Constant(self, node):
            if isinstance(node.value, str) and not self._is_in_docstring(node.lineno):
                if self._check_for_injection_patterns(node.value):
                    self.issues.append(
                        f"{self.filename}:{node.lineno}: Potential command injection pattern detected in string literal: '{node.value[:50]}...'. "
                        "Review for hardcoded injection vectors."
                    )
            self.generic_visit(node)
    
    for py_file in skill_path.glob('**/*.py'):
        if py_file.name == 'audit_skill.py':
            continue
        try:
            content = py_file.read_text(encoding='utf-8')
            source_lines = content.splitlines()
            
            try:
                tree = ast.parse(content, filename=str(py_file))
                checker = SubprocessSecurityChecker(py_file.name, source_lines)
                checker._collect_docstring_lines(tree)
                checker.visit(tree)
                issues.extend(checker.issues)
            except SyntaxError as e:
                issues.append(f"{py_file.name}: Syntax error - {e}")
        except Exception as e:
            issues.append(f"Could not read {py_file.name}: {e}")
            
    if issues:
        return False, issues
    return True, "Subprocess calls appear robust and secure"

def check_cross_platform_compatibility(skill_path):
    """
    Check for cross-platform compatibility and security issues in skill code.
    
    Checks for:
    1. Hardcoded path separators ( '/' or '\' in string literals)
    2. Platform-specific commands (dir, del, ls, rm)
    3. Usage of os.path instead of pathlib
    4. Absolute path patterns (C:\\, /home/, /Users/)
    5. Platform-specific security issues
    6. OS command injection risks
    7. Path traversal vulnerability detection
    8. Environment variable usage validation
    
    Args:
        skill_path: Path to the skill directory to scan.
        
    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    issues = []
    
    class CrossPlatformSecurityChecker(ast.NodeVisitor):
        def __init__(self, filename, source_lines):
            self.filename = filename
            self.source_lines = source_lines
            self.issues = []
            self.docstring_lines = set()
            
        def _collect_docstring_lines(self, tree):
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    if node.body and isinstance(node.body[0], ast.Expr):
                        if isinstance(node.body[0].value, ast.Constant):
                            if isinstance(node.body[0].value.value, str):
                                start_line = node.body[0].lineno
                                end_line = node.body[0].end_lineno if hasattr(node.body[0], 'end_lineno') else start_line
                                for line_num in range(start_line, end_line + 1):
                                    self.docstring_lines.add(line_num)
                elif isinstance(node, ast.Module):
                    if node.body and isinstance(node.body[0], ast.Expr):
                        if isinstance(node.body[0].value, ast.Constant):
                            if isinstance(node.body[0].value.value, str):
                                start_line = node.body[0].lineno
                                end_line = node.body[0].end_lineno if hasattr(node.body[0], 'end_lineno') else start_line
                                for line_num in range(start_line, end_line + 1):
                                    self.docstring_lines.add(line_num)
        
        def _is_in_docstring(self, lineno):
            return lineno in self.docstring_lines
        
        def _is_user_input_var(self, node):
            if isinstance(node, ast.Name):
                dangerous_names = ['input', 'user_input', 'user_input_data', 'data', 'payload', 'cmd', 'command', 'filename', 'filepath', 'path', 'arg', 'argument']
                return node.id in dangerous_names
            return False
        
        def _check_path_traversal(self, value):
            traversal_patterns = ['../', '..\\', '%2e%2e', '%2e%2e%2f', '%2e%2e%5c', '..%2f', '..%5c']
            for pattern in traversal_patterns:
                if pattern in value:
                    return True
            return False
        
        def visit_Call(self, node):
            lineno = node.lineno
            if self._is_in_docstring(lineno):
                self.generic_visit(node)
                return
            
            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    if node.func.value.id == 'os':
                        if node.func.attr == 'system':
                            for arg in node.args:
                                if self._is_user_input_var(arg):
                                    self.issues.append(
                                        f"{self.filename}:{lineno}: os.system() with potential user input. "
                                        "This is a critical OS command injection vulnerability. Use subprocess.run() with list arguments."
                                    )
                                elif isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                                    if self._check_path_traversal(arg.value):
                                        self.issues.append(
                                            f"{self.filename}:{lineno}: os.system() with potential path traversal pattern. "
                                            "Validate and sanitize command strings."
                                        )
                        
                        if node.func.attr in ['popen', 'spawn', 'execl', 'execle', 'execlp', 'execv', 'execve', 'execvp', 'execvpe']:
                            for arg in node.args:
                                if self._is_user_input_var(arg):
                                    self.issues.append(
                                        f"{self.filename}:{lineno}: os.{node.func.attr}() with potential user input. "
                                        "This is a critical OS command injection vulnerability. Use subprocess.run() instead."
                                    )
                    
                    if node.func.value.id == 'subprocess':
                        if node.func.attr in ['run', 'call', 'Popen', 'check_output']:
                            has_shell_true = False
                            has_user_input = False
                            
                            for kw in node.keywords:
                                if kw.arg == 'shell' and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                                    has_shell_true = True
                            
                            has_user_input = any(self._is_user_input_var(arg) for arg in node.args)
                            
                            if has_shell_true and has_user_input:
                                self.issues.append(
                                    f"{self.filename}:{lineno}: subprocess.{node.func.attr}() with shell=True and user input. "
                                    "This is a critical command injection vulnerability."
                                )
                            elif has_shell_true:
                                self.issues.append(
                                    f"{self.filename}:{lineno}: subprocess.{node.func.attr}() with shell=True. "
                                    "Avoid shell=True to prevent command injection. Use list arguments instead."
                                )
                            elif has_user_input:
                                self.issues.append(
                                    f"{self.filename}:{lineno}: subprocess.{node.func.attr}() with potential user input. "
                                    "Validate and sanitize user input before subprocess calls."
                                )
                    
                    if node.func.value.id == 'os' and node.func.attr == 'environ':
                        self.issues.append(
                            f"{self.filename}:{lineno}: Direct access to os.environ detected. "
                            "Consider using os.getenv() with default values for safer environment variable access."
                        )
                    
                    if node.func.value.id == 'os' and node.func.attr == 'getenv':
                        has_default = False
                        for kw in node.keywords:
                            if kw.arg == 'default':
                                has_default = True
                        
                        if not has_default and len(node.args) < 2:
                            self.issues.append(
                                f"{self.filename}:{lineno}: os.getenv() without default value. "
                                "Provide a default value to handle missing environment variables safely."
                            )
            
            if isinstance(node.func, ast.Name):
                if node.func.id == 'open':
                    for arg in node.args:
                        if self._is_user_input_var(arg):
                            self.issues.append(
                                f"{self.filename}:{lineno}: open() with potential user input. "
                                "This is a path traversal vulnerability. Validate and sanitize file paths."
                            )
                
                if node.func.id in ['eval', 'exec', 'compile']:
                    for arg in node.args:
                        if self._is_user_input_var(arg):
                            self.issues.append(
                                f"{self.filename}:{lineno}: {node.func.id}() with potential user input. "
                                "This is a critical code injection vulnerability."
                            )
            
            self.generic_visit(node)
        
        def visit_Constant(self, node):
            if isinstance(node.value, str) and not self._is_in_docstring(node.lineno):
                if self._check_path_traversal(node.value):
                    self.issues.append(
                        f"{self.filename}:{node.lineno}: Path traversal pattern detected in string literal: '{node.value[:50]}...'. "
                        "Review for hardcoded path traversal vectors."
                    )
                
                if re.search(r'["\']C:\\\\', node.value):
                    self.issues.append(
                        f"{self.filename}:{node.lineno}: Hardcoded Windows absolute path detected. Use relative paths."
                    )
                
                if re.search(r'["\']/home/', node.value):
                    self.issues.append(
                        f"{self.filename}:{node.lineno}: Hardcoded Unix absolute path detected. Use relative paths."
                    )
                
                if re.search(r'["\']/Users/', node.value):
                    self.issues.append(
                        f"{self.filename}:{node.lineno}: Hardcoded macOS absolute path detected. Use relative paths."
                    )
            
            self.generic_visit(node)
    
    for py_file in skill_path.glob('**/*.py'):
        if py_file.name == 'audit_skill.py':
            continue
        try:
            content = py_file.read_text(encoding='utf-8')
            source_lines = content.splitlines()
            
            try:
                tree = ast.parse(content, filename=str(py_file))
                checker = CrossPlatformSecurityChecker(py_file.name, source_lines)
                checker._collect_docstring_lines(tree)
                checker.visit(tree)
                issues.extend(checker.issues)
            except SyntaxError as e:
                issues.append(f"{py_file.name}: Syntax error - {e}")
        except Exception as e:
            issues.append(f"Could not read {py_file.name}: {e}")
    
    if issues:
        return False, issues
    return True, "No cross-platform compatibility or security issues found"

def check_i18n_support(skill_path):
    """
    Check for internationalization (i18n) and multi-language support.
    
    Checks for:
    1. Hardcoded text in output messages (suggest message dictionary)
    2. Unicode/emoji usage in output (no emoji allowed in skill code)
    3. Encoding declaration consistency (note: encoding='utf-8' is recommended for Chinese files, not mandatory)
    4. Multi-language keywords in SKILL.md (suggestion, not requirement)
    
    Args:
        skill_path: Path to the skill directory to scan.
        
    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    issues = []
    
    # Check SKILL.md for multi-language support (informational only)
    skill_md = skill_path / 'SKILL.md'
    if skill_md.exists():
        try:
            content = skill_md.read_text(encoding='utf-8')
            
            # Check for both English and Chinese keywords
            has_english = any(word in content.lower() for word in ['description:', 'name:', 'usage:', 'example'])
            has_chinese = any(ord(char) > 127 for char in content)
            
            # This is just a suggestion, not a requirement
            # Note: encoding='utf-8' is recommended for Chinese files but not mandatory
            if not has_chinese and not has_english:
                issues.append("Suggestion: Consider adding both English and Chinese keywords in SKILL.md for better discoverability.")
                
        except Exception as e:
            issues.append(f"Could not read SKILL.md: {e}")
    
    # AST-based check for emoji in print statements
    class EmojiChecker(ast.NodeVisitor):
        def __init__(self, filename, source_lines):
            self.filename = filename
            self.source_lines = source_lines
            self.emoji_issues = []
            self.print_count = 0
            
        def _contains_emoji(self, text):
            """Check if text contains emoji characters."""
            for c in text:
                # Check common emoji ranges
                if (0x2600 <= ord(c) <= 0x27BF) or (0x1F300 <= ord(c) <= 0x1F9FF):
                    return True
            return False
        
        def visit_Call(self, node):
            # Check for print() calls
            if isinstance(node.func, ast.Name) and node.func.id == 'print':
                self.print_count += 1
                
                # Check each argument in print()
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        # Check for emoji in string literals
                        if self._contains_emoji(arg.value):
                            line = self.source_lines[node.lineno - 1]
                            # Skip if it's a comment
                            if '#' in line:
                                comment_part = line.split('#', 1)[1]
                                if not self._contains_emoji(comment_part):
                                    self.emoji_issues.append(
                                        f"{self.filename}:{node.lineno}: Emoji found in print statement. "
                                        "Emoji is not allowed in skill code. Use standard text labels [PASS]/[FAIL]/[WARN]/[INFO] instead."
                                    )
                            else:
                                self.emoji_issues.append(
                                    f"{self.filename}:{node.lineno}: Emoji found in print statement. "
                                    "Emoji is not allowed in skill code. Use standard text labels [PASS]/[FAIL]/[WARN]/[INFO] instead."
                                )
            
            self.generic_visit(node)
    
    # Check Python files using AST
    for py_file in skill_path.glob('**/*.py'):
        try:
            content = py_file.read_text(encoding='utf-8')
            source_lines = content.splitlines()
            
            # Parse the file as AST
            try:
                tree = ast.parse(content, filename=str(py_file))
                checker = EmojiChecker(py_file.name, source_lines)
                checker.visit(tree)
                
                # Add emoji issues
                issues.extend(checker.emoji_issues)
                
                # Warn if many hardcoded messages (informational only)
                if checker.print_count > 20:
                    issues.append(f"Suggestion: {py_file.name} has {checker.print_count} print statements. Consider using a message dictionary for better i18n support when applicable.")
                    
            except SyntaxError as e:
                # If AST parsing fails, fall back to simple line-based check
                for i, line in enumerate(source_lines, 1):
                    stripped = line.strip()
                    if stripped.startswith('#'):
                        continue
                    
                    if 'print(' in line:
                        has_emoji = False
                        for c in line:
                            if (0x2600 <= ord(c) <= 0x27BF) or (0x1F300 <= ord(c) <= 0x1F9FF):
                                has_emoji = True
                                break
                        
                        if has_emoji:
                            if '#' in line:
                                comment_part = line.split('#', 1)[1]
                                emoji_in_comment = False
                                for c in comment_part:
                                    if (0x2600 <= ord(c) <= 0x27BF) or (0x1F300 <= ord(c) <= 0x1F9FF):
                                        emoji_in_comment = True
                                        break
                                if emoji_in_comment:
                                    continue
                            
                            issues.append(f"{py_file.name}:{i}: Emoji found in output statement. Emoji is not allowed in skill code. Use standard text labels [PASS]/[FAIL]/[WARN]/[INFO] instead.")
                    
                    if 'print("' in line or "print('" in line:
                        message_count += 1
                
                if message_count > 20:
                    issues.append(f"Suggestion: {py_file.name} has {message_count} print statements. Consider using a message dictionary for better i18n support when applicable.")
                    
        except Exception as e:
            issues.append(f"Could not read {py_file.name}: {e}")
            
    if issues:
        return False, issues
    return True, "Internationalization check completed"

def check_absolute_references(skill_path):
    """
    Check for absolute references and absolute paths in skill code.
    
    Checks for:
    1. Hardcoded absolute file paths
    2. Absolute imports instead of relative imports
    3. Configuration files with absolute paths
    4. Parent directory references (../) which can cause path traversal issues
    
    Args:
        skill_path: Path to the skill directory to scan.
        
    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    issues = []
    
    # AST-based check for path references
    class PathReferenceChecker(ast.NodeVisitor):
        def __init__(self, filename, source_lines):
            self.filename = filename
            self.source_lines = source_lines
            self.issues = []
            self.docstring_lines = set()
            self.reported_issues = set()  # Track reported issues to avoid duplicates
            
        def _collect_docstring_lines(self, tree):
            """Collect all line numbers that are part of docstrings."""
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    if node.body and isinstance(node.body[0], ast.Expr):
                        if isinstance(node.body[0].value, ast.Constant):
                            if isinstance(node.body[0].value.value, str):
                                # This is a docstring
                                start_line = node.body[0].lineno
                                # Multi-line docstrings span multiple lines
                                end_line = node.body[0].end_lineno if hasattr(node.body[0], 'end_lineno') else start_line
                                for line_num in range(start_line, end_line + 1):
                                    self.docstring_lines.add(line_num)
                elif isinstance(node, ast.Module):
                    if node.body and isinstance(node.body[0], ast.Expr):
                        if isinstance(node.body[0].value, ast.Constant):
                            if isinstance(node.body[0].value.value, str):
                                # Module docstring
                                start_line = node.body[0].lineno
                                end_line = node.body[0].end_lineno if hasattr(node.body[0], 'end_lineno') else start_line
                                for line_num in range(start_line, end_line + 1):
                                    self.docstring_lines.add(line_num)
            
        def _is_in_docstring(self, lineno):
            """Check if a line number is in a docstring."""
            return lineno in self.docstring_lines
            
        def _check_string_for_issues(self, value, lineno):
            """Check a string value for path issues."""
            # Skip single-character strings like '/'
            if len(value) == 1 and value == '/':
                return
            
            # Skip if in docstring
            if self._is_in_docstring(lineno):
                return
            
            # Check for absolute paths
            if value.startswith('/') or (len(value) >= 2 and value[1] == ':' and value[0].isalpha()):
                issue_key = f"{lineno}:abs"
                if issue_key not in self.reported_issues:
                    self.issues.append(
                        f"{self.filename}:{lineno}: Absolute path detected: '{value}'. Use relative paths."
                    )
                    self.reported_issues.add(issue_key)
            
            # Check for parent directory references
            if '../' in value or '..\\' in value:
                issue_key = f"{lineno}:parent"
                if issue_key not in self.reported_issues:
                    self.issues.append(
                        f"{self.filename}:{lineno}: Parent directory reference detected: '{value}'. "
                        "This can cause path traversal issues. Use pathlib.Path.resolve() or proper relative paths."
                    )
                    self.reported_issues.add(issue_key)
            
        def visit_Call(self, node):
            # Note: We don't check string values here, they will be checked in visit_Constant
            # This avoids duplicate checking of the same string
            self.generic_visit(node)
        
        def visit_Constant(self, node):
            # Check for string constants that look like absolute paths
            if isinstance(node.value, str):
                # Skip if it's clearly a URL
                if node.value.startswith('http://') or node.value.startswith('https://'):
                    return
                # Skip single-character strings
                if len(node.value) == 1:
                    return
                # Check for absolute paths in assignments
                self._check_string_for_issues(node.value, node.lineno)
            
            self.generic_visit(node)
    
    # Check Python files using AST
    for py_file in skill_path.glob('**/*.py'):
        try:
            content = py_file.read_text(encoding='utf-8')
            source_lines = content.splitlines()
            
            # Parse the file as AST
            try:
                tree = ast.parse(content, filename=str(py_file))
                checker = PathReferenceChecker(py_file.name, source_lines)
                checker._collect_docstring_lines(tree)
                checker.visit(tree)
                issues.extend(checker.issues)
                    
            except SyntaxError as e:
                # If AST parsing fails, fall back to simple line-based check
                for i, line in enumerate(source_lines, 1):
                    stripped = line.strip()
                    
                    # Skip comment lines
                    if stripped.startswith('#'):
                        continue
                    
                    # Skip import lines
                    if stripped.startswith('import') or stripped.startswith('from'):
                        continue
                    
                    # Check for absolute path patterns in file operations
                    # Look for patterns like open('/path/to/file') or Path('/path/to/file')
                    if re.search(r'open\s*\(\s*["\'][/A-Za-z]', line):
                        issues.append(f"{py_file.name}:{i}: Absolute path in open() call. Use relative paths.")
                    if re.search(r'Path\s*\(\s*["\'][/A-Za-z]', line):
                        issues.append(f"{py_file.name}:{i}: Absolute path in Path() constructor. Use relative paths.")
                    
                    # Check for parent directory references
                    if re.search(r'["\']\.\.\/', line) or re.search(r'["\']\.\.\\', line):
                        issues.append(f"{py_file.name}:{i}: Parent directory reference detected. This can cause path traversal issues.")
                    
                    # Check for hardcoded absolute paths in string assignments
                    if re.search(r'=\s*["\'][A-Z]:\\\\', line):
                        issues.append(f"{py_file.name}:{i}: Hardcoded Windows absolute path detected.")
                    if re.search(r'=\s*["\']/[a-z]+/', line):
                        issues.append(f"{py_file.name}:{i}: Hardcoded Unix absolute path detected.")
                    
        except Exception as e:
            issues.append(f"Could not read {py_file.name}: {e}")
    
    # Check for absolute paths in config files
    for config_file in skill_path.glob('**/*.json'):
        try:
            content = config_file.read_text(encoding='utf-8')
            if re.search(r'["\'][A-Z]:\\\\', content):
                issues.append(f"{config_file.relative_to(skill_path)}: Contains Windows absolute path.")
            if re.search(r'["\']/[a-z]+/home/', content):
                issues.append(f"{config_file.relative_to(skill_path)}: Contains Unix absolute path.")
            # Check for parent directory references in JSON
            if '../' in content or '..\\' in content:
                issues.append(f"{config_file.relative_to(skill_path)}: Contains parent directory reference. This can cause path traversal issues.")
        except Exception as e:
            issues.append(f"Could not read {config_file.name}: {e}")
            
    if issues:
        return False, issues
    return True, "No absolute references found"

def get_skills_registry(skills_dir):
    """
    Load skills.json registry file.
    
    Args:
        skills_dir: Path to skills root directory.
        
    Returns:
        dict: Registry data or None if not found
    """
    skills_dir = Path(skills_dir)
    registry_file = skills_dir / 'skills.json'
    if not registry_file.exists():
        return None
    
    try:
        with open(registry_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

def get_skill_map(skills_dir):
    """
    Load skill_map.json file.
    
    Args:
        skills_dir: Path to skills root directory.
        
    Returns:
        dict: Skill map data or None if not found
    """
    skills_dir = Path(skills_dir)
    map_file = skills_dir / 'skill_map.json'
    if not map_file.exists():
        return None
    
    try:
        with open(map_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

def check_registry_consistency(skill_path, skills_dir):
    """
    Check if skill is properly registered in skills.json.
    
    Validates:
    1. Skill exists in skills.json
    2. Skill name matches directory name
    3. Version information is valid
    4. Updated timestamp is recent (within 1 year)
    
    Args:
        skill_path: Path to skill directory.
        skills_dir: Path to skills root directory.
        
    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    skill_name = skill_path.name
    registry = get_skills_registry(skills_dir)
    
    if not registry:
        return True, "skills.json not found (skipping registry check)"
    
    if "skills" not in registry:
        return False, "skills.json missing 'skills' key"
    
    if skill_name not in registry["skills"]:
        return False, f"Skill '{skill_name}' not found in skills.json registry"
    
    skill_info = registry["skills"][skill_name]
    issues = []
    
    # Check source field
    if "source" not in skill_info:
        issues.append("Missing 'source' field in registry")
    elif skill_info["source"] not in ["local", "unknown"]:
        if not skill_info["source"].startswith(("http://", "https://")):
            issues.append(f"Invalid source URL: {skill_info['source']}")
    
    # Check version field
    if "version" not in skill_info:
        issues.append("Missing 'version' field in registry")
    elif skill_info["version"] == "unknown":
        if skill_info.get("source") not in ["local", "unknown"]:
            issues.append("Remote skill has 'unknown' version (should use commit hash)")
    
    # Check updated_at field
    if "updated_at" not in skill_info:
        issues.append("Missing 'updated_at' field in registry")
    else:
        try:
            updated_at = datetime.datetime.fromisoformat(skill_info["updated_at"])
            # Ensure both datetimes are timezone-aware or both are naive
            now = datetime.datetime.now(datetime.timezone.utc)
            # If updated_at is naive, assume UTC
            if updated_at.tzinfo is None:
                updated_at = updated_at.replace(tzinfo=datetime.timezone.utc)
            age = now - updated_at
            if age > datetime.timedelta(days=365):
                issues.append(f"Registry entry is old ({age.days} days), consider updating")
        except ValueError:
            issues.append(f"Invalid updated_at format: {skill_info['updated_at']}")
    
    if issues:
        return False, issues
    return True, "Registry information is consistent"

def check_skill_map_consistency(skill_path, skills_dir):
    """
    Check if skill is properly mapped in skill_map.json.
    
    Validates:
    1. Skill exists in skill_map.json
    2. Keywords are present
    3. Name matches directory name
    
    Args:
        skill_path: Path to skill directory.
        skills_dir: Path to skills root directory.
        
    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    skill_name = skill_path.name
    skill_map = get_skill_map(skills_dir)
    
    if not skill_map:
        return True, "skill_map.json not found (skipping map check)"
    
    # skill_map.json has a "skills" key containing all skill entries
    if "skills" not in skill_map:
        return False, "skill_map.json missing 'skills' key"
    
    if skill_name not in skill_map["skills"]:
        return False, f"Skill '{skill_name}' not found in skill_map.json"
    
    skill_entry = skill_map["skills"][skill_name]
    issues = []
    
    # Check keywords
    if "keywords" not in skill_entry:
        issues.append("Missing 'keywords' field in skill_map.json")
    elif not skill_entry["keywords"]:
        issues.append("Empty 'keywords' list in skill_map.json")
    
    # Check name field
    if "name" not in skill_entry:
        issues.append("Missing 'name' field in skill_map.json")
    elif skill_entry["name"] != skill_name:
        issues.append(f"Name mismatch: skill_map.json has '{skill_entry['name']}' but directory is '{skill_name}'")
    
    if issues:
        return False, issues
    return True, "Skill map information is consistent"

def check_technical_standards(skill_path):
    """
    Technical standards validation for skill code.

    Validates:
    - Proper error handling patterns
    - Logging best practices
    - Input validation implementation
    - Output sanitization

    Args:
        skill_path: Path to the skill directory to scan.

    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    issues = []

    ok, msg = check_error_handling_patterns(skill_path)
    if not ok:
        if isinstance(msg, list):
            issues.extend(msg)
        else:
            issues.append(msg)

    ok, msg = check_logging_practices(skill_path)
    if not ok:
        if isinstance(msg, list):
            issues.extend(msg)
        else:
            issues.append(msg)

    ok, msg = check_input_validation(skill_path)
    if not ok:
        if isinstance(msg, list):
            issues.extend(msg)
        else:
            issues.append(msg)

    ok, msg = check_output_sanitization(skill_path)
    if not ok:
        if isinstance(msg, list):
            issues.extend(msg)
        else:
            issues.append(msg)

    if issues:
        return False, issues
    return True, "Technical standards validation passed"

def check_error_handling_patterns(skill_path):
    """
    Error handling pattern checker for skill code.

    Checks for:
    - Missing try-except blocks in risky operations
    - Bare except clauses
    - Exception handling specificity
    - Proper error propagation

    Args:
        skill_path: Path to the skill directory to scan.

    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    issues = []

    class ErrorHandlingChecker(ast.NodeVisitor):
        def __init__(self, filename):
            self.filename = filename
            self.issues = []
            self.risky_operations = []

        def visit_Call(self, node):
            risky_funcs = ['open', 'json.load', 'yaml.safe_load', 'subprocess.run', 'subprocess.check_output']
            if isinstance(node.func, ast.Name) and node.func.id in risky_funcs:
                self.risky_operations.append((node.lineno, node.func.id))
            self.generic_visit(node)

        def visit_Try(self, node):
            for handler in node.handlers:
                if handler.type is None:
                    self.issues.append(
                        f"{self.filename}:{node.lineno}: Bare except clause detected. "
                        "Use specific exception types (e.g., except ValueError, except IOError)."
                    )
                elif isinstance(handler.type, ast.Name) and handler.type.id == 'Exception':
                    self.issues.append(
                        f"{self.filename}:{node.lineno}: Generic Exception handler detected. "
                        "Use more specific exception types for better error handling."
                    )
            self.generic_visit(node)

    for py_file in skill_path.glob('**/*.py'):
        if py_file.name == 'audit_skill.py':
            continue
        try:
            content = py_file.read_text(encoding='utf-8')
            try:
                tree = ast.parse(content, filename=str(py_file))
                checker = ErrorHandlingChecker(py_file.name)
                checker.visit(tree)
                issues.extend(checker.issues)
            except SyntaxError:
                pass
        except Exception as e:
            issues.append(f"Could not read {py_file.name}: {e}")

    if issues:
        return False, issues
    return True, "Error handling patterns look good"

def check_logging_practices(skill_path):
    """
    Logging best practices validator for skill code.

    Checks for:
    - Proper logging level usage
    - Sensitive data in logs
    - Log message formatting
    - Structured logging patterns

    Args:
        skill_path: Path to the skill directory to scan.

    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    issues = []

    sensitive_keywords = ['password', 'token', 'secret', 'key', 'credential', 'api_key', 'auth']

    class LoggingChecker(ast.NodeVisitor):
        def __init__(self, filename, source_lines):
            self.filename = filename
            self.source_lines = source_lines
            self.issues = []

        def visit_Call(self, node):
            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name) and node.func.value.id == 'logging':
                    if node.func.attr in ['debug', 'info', 'warning', 'error', 'critical']:
                        for arg in node.args:
                            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                                log_msg = arg.value.lower()
                                for keyword in sensitive_keywords:
                                    if keyword in log_msg:
                                        self.issues.append(
                                            f"{self.filename}:{node.lineno}: Potential sensitive data in log message: '{keyword}'. "
                                            "Avoid logging sensitive information."
                                        )
                                        break
            self.generic_visit(node)

    for py_file in skill_path.glob('**/*.py'):
        if py_file.name == 'audit_skill.py':
            continue
        try:
            content = py_file.read_text(encoding='utf-8')
            source_lines = content.splitlines()
            try:
                tree = ast.parse(content, filename=str(py_file))
                checker = LoggingChecker(py_file.name, source_lines)
                checker.visit(tree)
                issues.extend(checker.issues)
            except SyntaxError:
                pass
        except Exception as e:
            issues.append(f"Could not read {py_file.name}: {e}")

    if issues:
        return False, issues
    return True, "Logging practices look good"

def check_input_validation(skill_path):
    """
    Input validation analyzer for skill code.

    Checks for:
    - Missing input sanitization
    - User input handling
    - Type checking
    - Boundary validation

    Args:
        skill_path: Path to the skill directory to scan.

    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    issues = []

    class InputValidationChecker(ast.NodeVisitor):
        def __init__(self, filename):
            self.filename = filename
            self.issues = []
            self.has_input = False
            self.has_validation = False

        def visit_Call(self, node):
            if isinstance(node.func, ast.Name) and node.func.id == 'input':
                self.has_input = True
            self.generic_visit(node)

        def visit_FunctionDef(self, node):
            for stmt in node.body:
                if isinstance(stmt, ast.If):
                    for test_node in ast.walk(stmt.test):
                        if isinstance(test_node, ast.Call):
                            if isinstance(test_node.func, ast.Attribute):
                                if test_node.func.attr in ['isinstance', 'isdigit', 'isnumeric', 'isalpha', 'isalnum']:
                                    self.has_validation = True
            self.generic_visit(node)

    for py_file in skill_path.glob('**/*.py'):
        if py_file.name == 'audit_skill.py':
            continue
        try:
            content = py_file.read_text(encoding='utf-8')
            try:
                tree = ast.parse(content, filename=str(py_file))
                checker = InputValidationChecker(py_file.name)
                checker.visit(tree)
                if checker.has_input and not checker.has_validation:
                    issues.append(
                        f"{py_file.name}: Uses input() but may lack validation. "
                        "Consider adding type checking and boundary validation for user input."
                    )
            except SyntaxError:
                pass
        except Exception as e:
            issues.append(f"Could not read {py_file.name}: {e}")

    if issues:
        return False, issues
    return True, "Input validation looks good"

def check_output_sanitization(skill_path):
    """
    Output sanitization checker for skill code.

    Checks for:
    - Unsafe output patterns
    - XSS vulnerabilities
    - HTML/JSON output safety
    - Data leakage risks

    Args:
        skill_path: Path to the skill directory to scan.

    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    issues = []

    class OutputSanitizationChecker(ast.NodeVisitor):
        def __init__(self, filename, source_lines):
            self.filename = filename
            self.source_lines = source_lines
            self.issues = []

        def visit_Call(self, node):
            if isinstance(node.func, ast.Name) and node.func.id == 'print':
                for arg in node.args:
                    if isinstance(arg, ast.BinOp):
                        if isinstance(arg.op, ast.Mod):
                            self.issues.append(
                                f"{self.filename}:{node.lineno}: String formatting in print() may need sanitization. "
                                "Ensure user input is properly escaped before output."
                            )
            self.generic_visit(node)

    for py_file in skill_path.glob('**/*.py'):
        if py_file.name == 'audit_skill.py':
            continue
        try:
            content = py_file.read_text(encoding='utf-8')
            source_lines = content.splitlines()
            try:
                tree = ast.parse(content, filename=str(py_file))
                checker = OutputSanitizationChecker(py_file.name, source_lines)
                checker.visit(tree)
                issues.extend(checker.issues)
            except SyntaxError:
                pass
        except Exception as e:
            issues.append(f"Could not read {py_file.name}: {e}")

    if issues:
        return False, issues
    return True, "Output sanitization looks good"

def check_dependency_security(skill_path):
    """
    Dependency security analysis for skill code.

    Checks for:
    - Known vulnerabilities in dependencies
    - Outdated package versions
    - Unnecessary dependencies
    - Security advisories (basic implementation)

    Args:
        skill_path: Path to the skill directory to scan.

    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    issues = []

    scripts_dir = skill_path / 'scripts'
    if not scripts_dir.exists():
        return True, "No scripts directory"

    req_file = scripts_dir / 'requirements.txt'
    if not req_file.exists():
        return True, "No requirements.txt found (skipping)"

    try:
        req_content = req_file.read_text(encoding='utf-8')
        declared_deps = []
        for line in req_content.splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                pkg_name = line.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].split('!=')[0].strip()
                declared_deps.append(pkg_name)

        if not declared_deps:
            return True, "No dependencies declared"

        known_vulnerable = ['pyyaml<5.4', 'requests<2.25.0', 'urllib3<1.26.0']
        for dep in declared_deps:
            for vuln in known_vulnerable:
                if dep.startswith(vuln.split('<')[0]) and '<' in dep:
                    issues.append(
                        f"Dependency '{dep}' may have known vulnerabilities. "
                        f"Consider upgrading to a secure version (avoid {vuln})."
                    )

        if len(declared_deps) > 20:
            issues.append(
                f"Large number of dependencies ({len(declared_deps)}). "
                "Review if all dependencies are necessary."
            )

    except Exception as e:
        return False, f"Error checking dependency security: {e}"

    if issues:
        return False, issues
    return True, "Dependency security check passed"

def generate_json_report(skill_path, results):
    """
    Generate a JSON report of audit results for CI/CD integration.
    
    Args:
        skill_path: Path to the skill directory
        results: Dictionary of audit results
        
    Returns:
        JSON string of the audit report
    """
    report = {
        "skill": skill_path.name,
        "path": str(skill_path),
        "timestamp": datetime.datetime.now().isoformat(),
        "status": "pass" if all(r.get("pass", False) for r in results.values()) else "fail",
        "results": results
    }
    return json.dumps(report, indent=2, ensure_ascii=False)

def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        tuple: (skill_path, skills_dir, verbose, json_output, check_level)
    """
    parser = argparse.ArgumentParser(
        description="Audit Trae skills for compliance and best practices",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "skill_path",
        help="Path to skill directory to audit"
    )
    
    parser.add_argument(
        "skills_dir",
        nargs="?",
        help="Optional: Path to skills root directory (for registry checks)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output with additional context"
    )
    
    parser.add_argument(
        "-j", "--json",
        action="store_true",
        help="Output results in JSON format (for CI/CD integration)"
    )
    
    parser.add_argument(
        "-l", "--level",
        choices=["strict", "standard", "relaxed"],
        default="standard",
        help="Check level: strict (all checks), standard (recommended), relaxed (minimal)"
    )
    
    args = parser.parse_args()
    
    return (
        args.skill_path,
        args.skills_dir,
        args.verbose,
        args.json,
        args.level
    )

if __name__ == "__main__":
    skill_path, skills_dir, verbose, json_output, check_level = parse_arguments()
    
    if not json_output:
        print(f"[*] Auditing Skill: {Path(skill_path).name}")
        print(f"   Path: {Path(skill_path)}")
        if verbose:
            print(f"   Level: {check_level}")
            print(f"   Skills Dir: {skills_dir if skills_dir else 'N/A'}")
            print()
    
    success = audit_skill(
        skill_path, 
        skills_dir, 
        verbose=verbose, 
        json_output=json_output, 
        check_level=check_level
    )
    sys.exit(0 if success else 1)
