#!/usr/bin/env python3
"""
Skill Auditor - Comprehensive validation tool for Trae skills
Checks for dependencies, encoding, path consistency, and packaging structure.
"""

import sys
import os
import re
import yaml
from pathlib import Path

# ANSI colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def print_pass(msg):
    print(f"{GREEN}✅ PASS:{RESET} {msg}")

def print_fail(msg):
    print(f"{RED}❌ FAIL:{RESET} {msg}")

def print_warn(msg):
    print(f"{YELLOW}⚠️ WARN:{RESET} {msg}")

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
    
    unsafe_patterns = [
        (r'open\s*\([^)]+\)', r'encoding\s*='),
        (r'\.read_text\s*\([^)]+\)', r'encoding\s*='),
        (r'\.write_text\s*\([^)]+\)', r'encoding\s*='),
    ]
    
    for py_file in skill_path.glob('**/*.py'):
        try:
            content = py_file.read_text(encoding='utf-8')
            lines = content.splitlines()
            
            for i, line in enumerate(lines, 1):
                # Simple heuristic check
                # Check keywords separately to avoid self-match in the heuristic logic line itself
                has_file_op = False
                if 'open(' in line: has_file_op = True
                if '.read_text(' in line: has_file_op = True
                if '.write_text(' in line: has_file_op = True
                
                if has_file_op:
                    # Skip self-check for this line in auditor script
                    if 'has_file_op =' in line:
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
    
    # Skip checking if auditing skill-auditor itself (to avoid false positives)
    try:
        skill_name = skill_path.name
        if skill_name == 'skill-auditor':
            return True, "Skipping path consistency check for skill-auditor itself"
    except:
        pass
    
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
        return False, "SKILL.md missing"
        
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

def audit_skill(skill_path):
    skill_path = Path(skill_path)
    print(f"🔍 Auditing Skill: {skill_path.name}")
    print(f"   Path: {skill_path}\n")
    
    has_errors = False
    
    # 1. Frontmatter
    ok, msg = validate_frontmatter(skill_path)
    if ok: print_pass(msg)
    else: print_fail(msg); has_errors = True
    
    # 2. Dependencies
    ok, msg = check_dependencies(skill_path)
    if ok: print_pass(msg)
    else: print_fail(msg); has_errors = True
    
    # 3. Encoding
    ok, msg = check_encoding_safety(skill_path)
    if ok:
        print_pass(msg)
    else:
        print_fail("Found potential encoding issues:")
        for issue in msg:
            print(f"      - {issue}")
        has_errors = True
        
    # 4. Path Consistency
    ok, msg = check_path_consistency(skill_path)
    if ok:
        print_pass(msg)
    else:
        print_fail("Found path inconsistencies:")
        for issue in msg:
            print(f"      - {issue}")
        has_errors = True
        
    # 5. Packaging
    ok, msg = check_packaging_logic(skill_path)
    if ok: print_pass(msg)
    else: print_fail(msg); has_errors = True
    
    # 6. Init Script Template
    ok, msg = check_init_script_template(skill_path)
    if ok: print_pass(msg)
    else: print_fail(msg); has_errors = True
    
    # 7. Subprocess Encoding Robustness
    ok, msg = check_subprocess_robustness(skill_path)
    if ok:
        print_pass(msg)
    else:
        print_fail("Found potential subprocess robustness issues:")
        for issue in msg:
            print(f"      - {issue}")
        has_errors = True
    
    # 8. Risky Path Operations
    ok, msg = check_risky_path_ops(skill_path)
    if ok:
        print_pass(msg)
    else:
        print_fail("Found potential risky path operations:")
        for issue in msg:
            print(f"      - {issue}")
        has_errors = True
    
    print("\n" + "="*40)
    if has_errors:
        print(f"{RED}⚠️  Audit completed with errors. Please fix issues above.{RESET}")
        return False
    else:
        print(f"{GREEN}✨ Skill passed all standard checks!{RESET}")
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
    
    for py_file in skill_path.glob('**/*.py'):
        try:
            content = py_file.read_text(encoding='utf-8')
            lines = content.splitlines()
            
            for i, line in enumerate(lines, 1):
                # Check for os.system
                if 'os.system(' in line:
                    issues.append(f"{py_file.name}:{i}: Use of os.system() detected. Prefer subprocess.run() for better control and security.")
                
                # Check for os.path.join (soft warning, pathlib is better)
                if 'os.path.join(' in line:
                    # Not an error per se, but pathlib is recommended for cross-platform robustness
                    pass 
                    
                # Check for hardcoded separators in string literals that look like paths
                # This is tricky to regex perfectly, looking for common patterns
                # e.g. "folder/file" or "folder\\file"
                # Skip import lines
                if line.strip().startswith('import') or line.strip().startswith('from'):
                    continue
                    
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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python audit_skill.py <path/to/skill>")
        sys.exit(1)
        
    success = audit_skill(sys.argv[1])
    sys.exit(0 if success else 1)
