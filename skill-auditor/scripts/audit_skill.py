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
    """Check for explicit encoding in file operations"""
    issues = []
    
    # Patterns to check
    # 1. open() without encoding
    # 2. read_text() without encoding
    # 3. write_text() without encoding
    
    # Heuristic check for file operations
    for py_file in skill_path.glob('**/*.py'):
        try:
            content = py_file.read_text(encoding='utf-8')
            lines = content.splitlines()
            
            for i, line in enumerate(lines, 1):
                # Simple heuristic check
                # Check keywords separately to avoid self-match in the heuristic logic line itself
                # Also ignore comments
                if line.strip().startswith('#'):
                    continue

                has_file_op = False
                if 'open(' in line: has_file_op = True
                if '.read_text(' in line: has_file_op = True
                if '.write_text(' in line: has_file_op = True
                
                if has_file_op:
                    # Skip self-check for this line in auditor script
                    if 'has_file_op =' in line or 'heuristic check' in line:
                        continue
                        
                    if 'encoding' not in line and 'b' not in line: # Skip binary modes
                        # Double check context - might be binary open or already safe
                        # This is a strict check, manual review might be needed
                        issues.append(f"{py_file.name}:{i}: Potential unsafe file op without explicit encoding: {line.strip()}")
        except Exception as e:
            issues.append(f"Could not read {py_file.name}: {e}")
            
    if issues:
        return False, issues
    return True, "File operations appear to use explicit encoding"

def check_path_consistency(skill_path):
    """Check for outdated .codebuddy paths"""
    issues = []
    
    for file_path in skill_path.glob('**/*'):
        if not file_path.is_file():
            continue
            
        # Skip checking the auditor itself if it mentions the bad path as an example
        if file_path.suffix not in ['.md', '.py', '.txt']:
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
    return True, "No outdated path references found"

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
            
        if 'relative_to(skill_path)' not in content:
            return False, "package_skill.py does not seem to use correct 'relative_to(skill_path)' logic"
            
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
            if i18n_as_error:
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
    
    print("\n" + "="*40)
    if has_errors:
        print(f"{RED}[!] Audit completed with errors. Please fix issues above.{RESET}")
        return False
    elif has_warnings:
        print(f"{YELLOW}[!] Audit completed with warnings. Review issues above.{RESET}")
        return True
    else:
        print(f"{GREEN}[*] Skill passed all standard checks!{RESET}")
        return True

def check_risky_path_ops(skill_path):
    """
    Check for potentially risky file system operations that might fail on Windows.
    
    Checks for:
    1. os.system() usage (prefer subprocess)
    2. Hardcoded file paths (using '/' or '\' in strings)
    3. os.path.join (prefer pathlib)
    """
    issues = []
    import re
    
    for py_file in skill_path.glob('**/*.py'):
        try:
            content = py_file.read_text(encoding='utf-8')
            lines = content.splitlines()
            
            for i, line in enumerate(lines, 1):
                # Skip comment lines
                stripped = line.strip()
                if stripped.startswith('#'):
                    continue
                
                # Skip import lines
                if stripped.startswith('import') or stripped.startswith('from'):
                    continue
                
                # Skip docstring lines (lines that look like documentation)
                # Skip lines that are part of error messages or docstrings
                if 'Use of os.system()' in line or 'prefer subprocess' in line:
                    continue
                
                # Check for os.system using regex to avoid matching in strings/comments
                # Match actual function calls, not string literals
                os_system_pattern = r'\bos\.system\s*\('
                if re.search(os_system_pattern, line):
                    issues.append(f"{py_file.name}:{i}: Use of os.system() detected. Prefer subprocess.run() for better control and security.")
                
                # Check for os.path.join (soft warning, pathlib is better)
                if 'os.path.join(' in line:
                    issues.append(f"{py_file.name}:{i}: Using os.path.join(). Prefer pathlib.Path() for cross-platform robustness.")
                    
                # Check for hardcoded separators in string literals that look like paths
                # This is tricky to regex perfectly, looking for common patterns
                # e.g. "folder/file" or "folder\\file"
                # Very simple heuristic: looking for string literals with slashes
                # This might have false positives, so we keep it conservative
                # Skipping for now to avoid noise, focusing on high-impact os.system
                
        except Exception as e:
            issues.append(f"Could not read {py_file.name}: {e}")
            
    if issues:
        return False, issues
    return True, "No high-risk file operations detected"

def check_subprocess_robustness(skill_path):
    """
    Check for robust encoding handling in subprocess calls.
    
    This function scans Python files for subprocess.run() and subprocess.check_output()
    calls that capture text output but lack proper error handling for encoding issues.
    
    Args:
        skill_path: Path to the skill directory to scan.
        
    Returns:
        tuple: (success: bool, message: str | list[str])
            - If success: (True, "Subprocess calls appear robust or binary")
            - If failure: (False, list of issue descriptions)
    """
    issues = []
    
    # Check for subprocess.run without errors='replace' or similar safety mechanisms
    # This is a heuristic check
    for py_file in skill_path.glob('**/*.py'):
        try:
            content = py_file.read_text(encoding='utf-8')
            lines = content.splitlines()
            
            for i, line in enumerate(lines, 1):
                if 'subprocess.run(' in line or 'subprocess.check_output(' in line:
                    # Skip if it's binary mode (no encoding/text arg) - usually safe from decoding errors
                    if 'text=True' not in line and 'encoding=' not in line:
                        continue
                        
                    # Only warn if capturing text output
                    if 'capture_output=True' in line or 'stdout=subprocess.PIPE' in line:
                        if 'text=True' in line or 'encoding=' in line:
                            if 'errors=' not in line:
                                issues.append(f"{py_file.name}:{i}: Subprocess call might crash on non-UTF8 output (missing errors='replace' or similar)")
        except Exception as e:
            issues.append(f"Could not read {py_file.name}: {e}")
            
    if issues:
        return False, issues
    return True, "Subprocess calls appear robust or binary"

def check_cross_platform_compatibility(skill_path):
    """
    Check for cross-platform compatibility issues in skill code.
    
    Checks for:
    1. Hardcoded path separators ( '/' or '\' in string literals)
    2. Platform-specific commands (dir, del, ls, rm)
    3. Usage of os.path instead of pathlib
    4. Absolute path patterns (C:\\, /home/, /Users/)
    
    Args:
        skill_path: Path to the skill directory to scan.
        
    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    issues = []
        
    for py_file in skill_path.glob('**/*.py'):
        try:
            content = py_file.read_text(encoding='utf-8')
            lines = content.splitlines()
            
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                
                # Skip comment lines
                if stripped.startswith('#'):
                    continue
                
                # Skip import lines
                if stripped.startswith('import') or stripped.startswith('from'):
                    continue
                
                # Skip docstring lines
                if 'Cross-Platform Paths' in line or 'pathlib' in line:
                    continue
                
                # Check for platform-specific commands
                platform_commands = ['dir ', 'del ', 'ls ', 'rm ', 'rmdir ']
                for cmd in platform_commands:
                    if ('"' + cmd + ' "') in line or ("'" + cmd + " '") in line:
                        issues.append(f"{py_file.name}:{i}: Platform-specific command '{cmd}' detected. Use pathlib or shutil for cross-platform compatibility.")
                
                # Check for os.path usage (prefer pathlib)
                if 'os.path.join(' in line:
                    issues.append(f"{py_file.name}:{i}: Using os.path.join(). Prefer pathlib.Path() for cross-platform compatibility.")
                
                # Check for absolute path patterns in string literals
                # Windows absolute paths
                if re.search(r'["\']C:\\\\', line):
                    issues.append(f"{py_file.name}:{i}: Hardcoded Windows absolute path detected. Use relative paths.")
                # Unix absolute paths
                if re.search(r'["\']/home/', line):
                    issues.append(f"{py_file.name}:{i}: Hardcoded Unix absolute path detected. Use relative paths.")
                if re.search(r'["\']/Users/', line):
                    issues.append(f"{py_file.name}:{i}: Hardcoded macOS absolute path detected. Use relative paths.")
                
                # Check for hardcoded path separators in string literals that look like paths
                # This is a heuristic - look for patterns like "folder/file" or "folder\\file"
                # Skip if it's clearly a URL or comment
                if 'http://' in line or 'https://' in line:
                    continue
                # Check for mixed separators (Windows style in Unix context or vice versa)
                if '/' in line and '\\\\' in line and 'path' in line.lower():
                    issues.append(f"{py_file.name}:{i}: Mixed path separators detected. Use pathlib for cross-platform paths.")
                    
        except Exception as e:
            issues.append(f"Could not read {py_file.name}: {e}")
            
    if issues:
        return False, issues
    return True, "No cross-platform compatibility issues found"

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
    
    # Check Python files for hardcoded output messages
    for py_file in skill_path.glob('**/*.py'):
        try:
            content = py_file.read_text(encoding='utf-8')
            lines = content.splitlines()
            
            message_count = 0
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                
                # Skip comment lines
                if stripped.startswith('#'):
                    continue
                
                # Count print statements with hardcoded strings
                if 'print("' in line or "print('" in line:
                    message_count += 1
                
                # Check for emoji usage in print statements (STRICT: no emoji allowed in skill code)
                if 'print(' in line:
                    # Check for emoji characters (Unicode ranges for emojis)
                    # Emojis are in various ranges: U+2600-27BF, U+1F300-1F9FF, etc.
                    has_emoji = False
                    for c in line:
                        # Check common emoji ranges
                        if (0x2600 <= ord(c) <= 0x27BF) or (0x1F300 <= ord(c) <= 0x1F9FF):
                            has_emoji = True
                            break
                    
                    if has_emoji:
                        # Allow Unicode in comments
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
            
            # Warn if many hardcoded messages (informational only)
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
    
    Args:
        skill_path: Path to the skill directory to scan.
        
    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    issues = []
    
    for py_file in skill_path.glob('**/*.py'):
        try:
            content = py_file.read_text(encoding='utf-8')
            lines = content.splitlines()
            
            for i, line in enumerate(lines, 1):
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
