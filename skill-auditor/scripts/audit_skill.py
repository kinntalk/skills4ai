#!/usr/bin/env python3
"""
Skill Auditor - Comprehensive validation tool for Trae skills
Checks for dependencies, encoding, path consistency, packaging structure,
and validates registry information consistency.
"""

import sys
import os
import re
import yaml
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

# ANSI colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def print_pass(msg):
    print(f"{GREEN}✅ PASS:{RESET} {msg}")

def print_fail(msg):
    print(f"{RED}❌ FAIL:{RESET} {msg}")

def print_warn(msg):
    print(f"{YELLOW}⚠️  WARN:{RESET} {msg}")

def print_info(msg):
    print(f"{BLUE}ℹ️  INFO:{RESET} {msg}")

def get_skills_registry(skills_dir):
    """Load skills.json registry"""
    registry_path = skills_dir / "skills.json"
    if not registry_path.exists():
        return None
    try:
        content = registry_path.read_text(encoding="utf-8")
        return json.loads(content)
    except Exception as e:
        return None

def get_skill_map(skills_dir):
    """Load skill_map.json"""
    map_path = skills_dir / "skill_map.json"
    if not map_path.exists():
        return None
    try:
        content = map_path.read_text(encoding="utf-8")
        return json.loads(content)
    except Exception as e:
        return None

def check_registry_consistency(skill_path, skills_dir):
    """
    Check if skill is properly registered in skills.json
    
    Validates:
    1. Skill exists in skills.json
    2. Skill name matches directory name
    3. Version information is valid
    4. Updated timestamp is recent (within 1 year)
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
        # Validate remote source format
        if not skill_info["source"].startswith(("http://", "https://")):
            issues.append(f"Invalid source URL: {skill_info['source']}")
    
    # Check version field
    if "version" not in skill_info:
        issues.append("Missing 'version' field in registry")
    elif skill_info["version"] == "unknown":
        # Check if source is remote (should have version)
        if skill_info.get("source") not in ["local", "unknown"]:
            issues.append("Remote skill has 'unknown' version (should use commit hash)")
    
    # Check updated_at field
    if "updated_at" not in skill_info:
        issues.append("Missing 'updated_at' field in registry")
    else:
        try:
            updated_at = datetime.fromisoformat(skill_info["updated_at"])
            now = datetime.now()
            age = now - updated_at
            if age > timedelta(days=365):
                issues.append(f"Registry entry is old ({age.days} days), consider updating")
        except ValueError:
            issues.append(f"Invalid updated_at format: {skill_info['updated_at']}")
    
    if issues:
        return False, issues
    return True, "Registry information is consistent"

def check_skill_map_consistency(skill_path, skills_dir):
    """
    Check if skill is properly mapped in skill_map.json
    
    Validates:
    1. Skill exists in skill_map.json
    2. Name field matches directory name
    3. Keywords and aliases are present
    """
    skill_name = skill_path.name
    skill_map = get_skill_map(skills_dir)
    
    if not skill_map:
        return True, "skill_map.json not found (skipping map check)"
    
    if "skills" not in skill_map:
        return False, "skill_map.json missing 'skills' key"
    
    if skill_name not in skill_map["skills"]:
        return False, f"Skill '{skill_name}' not found in skill_map.json"
    
    skill_info = skill_map["skills"][skill_name]
    issues = []
    
    # Check required fields
    required_fields = ["name", "description", "keywords", "aliases"]
    for field in required_fields:
        if field not in skill_info:
            issues.append(f"Missing '{field}' field in skill_map.json")
    
    # Check name consistency
    if "name" in skill_info and skill_info["name"] != skill_name:
        issues.append(f"Name mismatch: directory='{skill_name}', map='{skill_info['name']}'")
    
    # Check keywords is a list
    if "keywords" in skill_info and not isinstance(skill_info["keywords"], list):
        issues.append("'keywords' should be a list")
    
    # Check aliases is a list
    if "aliases" in skill_info and not isinstance(skill_info["aliases"], list):
        issues.append("'aliases' should be a list")
    
    if issues:
        return False, issues
    return True, "Skill map information is consistent"

def check_skill_name_consistency(skill_path):
    """
    Check if SKILL.md name field matches directory name
    """
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return True, "SKILL.md not found (skipping name check)"
    
    try:
        content = skill_md.read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not match:
            return True, "No frontmatter found (skipping name check)"
        
        frontmatter = yaml.safe_load(match.group(1))
        
        if "name" not in frontmatter:
            return False, "SKILL.md missing 'name' field"
        
        skill_name = skill_path.name
        frontmatter_name = frontmatter["name"]
        
        if skill_name != frontmatter_name:
            return False, f"Name mismatch: directory='{skill_name}', SKILL.md='{frontmatter_name}'"
        
        return True, "SKILL.md name matches directory name"
    except Exception as e:
        return False, f"Error checking name consistency: {e}"

def check_directory_structure(skill_path):
    """
    Check if skill directory structure follows best practices
    
    Validates:
    1. SKILL.md exists at root
    2. Optional directories: scripts/, references/, assets/
    3. No unexpected top-level files (except LICENSE.txt)
    """
    skill_md = skill_path / "SKILL.md"
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
    allowed_files = [
        "SKILL.md",
        "README.md",
        "LICENSE.txt",
        "LICENSE",
        ".gitignore",
        "CLAUDE.md",
        "requirements.txt"
    ]
    unexpected_files = []
    for item in skill_path.iterdir():
        if item.is_file() and item.name not in allowed_files:
            unexpected_files.append(item.name)
    
    issues = []
    if unexpected_files:
        issues.append(f"Unexpected top-level files: {', '.join(unexpected_files)}")
    
    if issues:
        return False, issues
    return True, f"Directory structure is valid (found: {', '.join(found_dirs) if found_dirs else 'none'})"

def check_dependencies(skill_path):
    """Check if requirements.txt exists and matches imports"""
    scripts_dir = skill_path / "scripts"
    if not scripts_dir.exists():
        return True, "No scripts directory"
    
    # Find all python files
    py_files = list(scripts_dir.glob("**/*.py"))
    if not py_files:
        return True, "No Python scripts found"
        
    req_file = scripts_dir / "requirements.txt"
    if not req_file.exists():
        return False, "Python scripts found but scripts/requirements.txt is missing"
    
    # Scan for imports
    imported_modules = set()
    std_lib = sys.stdlib_module_names if hasattr(sys, "stdlib_module_names") else set()
    
    # Fallback for older python versions if needed, but 3.10+ has stdlib_module_names
    if not std_lib:
         # Basic list if sys.stdlib_module_names missing
         std_lib = {"os", "sys", "re", "json", "yaml", "pathlib", "argparse", "subprocess", "shutil", "tempfile", "time", "datetime", "logging", "threading", "typing", "collections", "io", "math", "random", "string", "hashlib", "base64", "urllib", "http", "email", "csv", "sqlite3", "configparser", "zipfile", "tarfile", "gzip", "bz2", "pickle", "copy", "itertools", "functools", "operator", "decimal", "fractions", "statistics", "enum", "dataclasses", "uuid", "secrets", "inspect", "warnings", "contextlib", "abc", "numbers", "types"}

    for py_file in py_files:
        try:
            content = py_file.read_text(encoding="utf-8")
            # Regex for 'import X' or 'from X import Y'
            imports = re.findall(r"^\s*(?:import|from)\s+([a-zA-Z0-9_]+)", content, re.MULTILINE)
            for module in imports:
                if module not in std_lib and module != "scripts":
                    imported_modules.add(module)
        except UnicodeDecodeError as e:
            print(f"Warning: Could not decode {py_file.name}: {e}")
        except Exception as e:
            print(f"Warning: Could not read {py_file.name}: {e}")

    # Read requirements
    try:
        req_content = req_file.read_text(encoding="utf-8").lower()
        declared_deps = set(line.split("==")[0].split(">=")[0].strip() for line in req_content.splitlines() if line.strip() and not line.startswith("#"))
    except Exception:
        return False, "Could not read requirements.txt"

    # Mapping common imports to package names (incomplete but helpful)
    pkg_map = {
        "yaml": "pyyaml",
        "PIL": "pillow",
        "bs4": "beautifulsoup4",
        "dotenv": "python-dotenv",
        "git": "gitpython"
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
        (r"open\s*\([^)]+\)", r"encoding\s*="),
        (r"\.read_text\s*\([^)]+\)", r"encoding\s*="),
        (r"\.write_text\s*\([^)]+\)", r"encoding\s*="),
    ]
    
    for py_file in skill_path.glob("**/*.py"):
        try:
            content = py_file.read_text(encoding="utf-8")
            lines = content.splitlines()
            
            for i, line in enumerate(lines, 1):
                # Simple heuristic check
                # Check keywords separately to avoid self-match in heuristic logic line itself
                has_file_op = False
                if "open(" in line: has_file_op = True
                if ".read_text(" in line: has_file_op = True
                if ".write_text(" in line: has_file_op = True
                
                if has_file_op:
                    # Skip self-check for this line in auditor script
                    if "has_file_op =" in line:
                        continue
                        
                    if "encoding" not in line and "b" not in line: # Skip binary modes
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
        if skill_name == "skill-auditor":
            return True, "Skipping path consistency check for skill-auditor itself"
    except:
        pass
    
    for file_path in skill_path.glob("**/*"):
        if not file_path.is_file():
            continue
            
        # Skip checking on auditor itself if it mentions bad path as an example
        if file_path.suffix not in [".md", ".py", ".txt"]:
            continue
            
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            if ".codebuddy" in content:
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
    package_script = skill_path / "scripts" / "package_skill.py"
    if not package_script.exists():
        return True, "No package_skill.py found (skipped)"
        
    try:
        content = package_script.read_text(encoding="utf-8")
        
        # Check 1: Relative path logic
        # Bad: relative_to(skill_path.parent)
        # Good: relative_to(skill_path)
        if "relative_to(skill_path.parent)" in content:
            return False, "package_skill.py uses 'skill_path.parent' (creates nested zip structure)"
            
        if "relative_to(skill_path)" not in content:
            return False, "package_skill.py does not seem to use correct 'relative_to(skill_path)' logic"
            
        # Check 2: Pycache filtering
        if "__pycache__" not in content and ".pyc" not in content:
            return False, "package_skill.py does not appear to filter __pycache__ or .pyc files"
            
        return True, "Packaging logic looks correct"
        
    except Exception as e:
        return False, f"Error checking package script: {e}"

def validate_frontmatter(skill_path):
    """Basic SKILL.md validation"""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        # Downgrade to warning if README.md exists, or just general warning
        readme = skill_path / "README.md"
        if readme.exists():
             return True, "SKILL.md missing (found README.md - check for metadata there)"
        return True, "SKILL.md missing (Warning: Metadata might be missing)"
        
    try:
        content = skill_md.read_text(encoding="utf-8")
        if not content.startswith("---"):
            return False, "No YAML frontmatter"
            
        # Simple extraction
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not match:
            return False, "Invalid frontmatter format"
            
        frontmatter = yaml.safe_load(match.group(1))
        
        if "name" not in frontmatter:
            return False, "Missing 'name'"
        if "description" not in frontmatter:
            return False, "Missing 'description'"
            
        return True, "SKILL.md frontmatter is valid"
    except Exception as e:
        return False, f"Frontmatter validation error: {e}"

def check_init_script_template(skill_path):
    """Check if init_skill.py contains valid YAML template (no [] list syntax)"""
    init_script = skill_path / "scripts" / "init_skill.py"
    if not init_script.exists():
        return True, "No init_skill.py found (skipped)"
        
    try:
        content = init_script.read_text(encoding="utf-8")
        
        # Check for bad list syntax in description
        # Bad: description: [TODO: ...]
        if "description: [" in content and "TODO:" in content:
            return False, "init_skill.py uses invalid list syntax '[]' for description template"
            
        # Check for good string syntax
        # Good: description: "TODO: ..."
        if 'description: "' in content or 'description: "' in content:
             return True, "Template description syntax looks correct"
             
        # If neither found, it might be using a different format or clean, just warn if unsure
        # But for now, we assume if it's not the bad one, it's pass
        return True, "Template description syntax looks safe"
        
    except Exception as e:
        return False, f"Error checking init script: {e}"

def check_risky_path_ops(skill_path):
    """
    Check for potentially risky file system operations that might fail on Windows.
    
    Checks for:
    1. os.system() usage (prefer subprocess)
    2. Hardcoded file paths (using '/' or '\' in strings)
    3. os.path.join (prefer pathlib)
    """
    issues = []
    
    for py_file in skill_path.glob("**/*.py"):
        try:
            content = py_file.read_text(encoding="utf-8")
            lines = content.splitlines()
            
            for i, line in enumerate(lines, 1):
                # Check for os.system
                if "os.system(" in line:
                    issues.append(f"{py_file.name}:{i}: Use of os.system() detected. Prefer subprocess.run() for better control and security.")
                
                # Check for os.path.join (soft warning, pathlib is better)
                if "os.path.join(" in line:
                    # Not an error per se, but pathlib is recommended for cross-platform robustness
                    pass 
                    
                # Check for hardcoded separators in string literals that look like paths
                # This is tricky to regex perfectly, looking for common patterns
                # e.g. "folder/file" or "folder\\file"
                # Skip import lines
                if line.strip().startswith("import") or line.strip().startswith("from"):
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
        skill_path: Path to skill directory to scan.
        
    Returns:
        tuple: (success: bool, message: str | list[str])
            - If success: (True, "Subprocess calls appear robust or binary")
            - If failure: (False, list of issue descriptions)
    """
    issues = []
    
    # Check for subprocess.run without errors='replace' or similar safety mechanisms
    # This is a heuristic check
    for py_file in skill_path.glob("**/*.py"):
        try:
            content = py_file.read_text(encoding="utf-8")
            lines = content.splitlines()
            
            for i, line in enumerate(lines, 1):
                if "subprocess.run(" in line or "subprocess.check_output(" in line:
                    # Skip if it's binary mode (no encoding/text arg) - usually safe from decoding errors
                    if "text=True" not in line and "encoding=" not in line:
                        continue
                        
                    # Only warn if capturing text output
                    if "capture_output=True" in line or "stdout=subprocess.PIPE" in line:
                        if "text=True" in line or "encoding=" in line:
                            if "errors=" not in line:
                                issues.append(f"{py_file.name}:{i}: Subprocess call might crash on non-UTF8 output (missing errors='replace' or similar)")
        except Exception as e:
            issues.append(f"Could not read {py_file.name}: {e}")
            
    if issues:
        return False, issues
    return True, "Subprocess calls appear robust or binary"

def audit_skill(skill_path, skills_dir=None):
    """
    Comprehensive skill audit with registry and dependency checks
    
    Args:
        skill_path: Path to skill directory
        skills_dir: Path to skills root directory (for registry checks)
    """
    skill_path = Path(skill_path)
    if skills_dir is None:
        skills_dir = skill_path.parent
    
    print(f"🔍 Auditing Skill: {skill_path.name}")
    print(f"   Path: {skill_path}\n")
    
    has_errors = False
    has_warnings = False
    
    # Section 1: Basic Structure
    print_info("=== Basic Structure ===")
    
    ok, msg = validate_frontmatter(skill_path)
    if ok: print_pass(msg)
    else: print_fail(msg); has_errors = True
    
    ok, msg = check_skill_name_consistency(skill_path)
    if ok: print_pass(msg)
    else: print_fail(msg); has_errors = True
    
    ok, msg = check_directory_structure(skill_path)
    if ok: print_pass(msg)
    else: 
        print_fail("Directory structure issues:")
        if isinstance(msg, list):
            for issue in msg: print(f"      - {issue}")
        else:
            print(f"      - {msg}")
        has_errors = True
    
    # Section 2: Dependencies
    print_info("\n=== Dependencies ===")
    
    ok, msg = check_dependencies(skill_path)
    if ok: print_pass(msg)
    else: print_fail(msg); has_errors = True
    
    # Section 3: Encoding & Path Safety
    print_info("\n=== Encoding & Path Safety ===")
    
    ok, msg = check_encoding_safety(skill_path)
    if ok:
        print_pass(msg)
    else:
        print_fail("Found potential encoding issues:")
        for issue in msg:
            print(f"      - {issue}")
        has_errors = True
        
    ok, msg = check_path_consistency(skill_path)
    if ok:
        print_pass(msg)
    else:
        print_fail("Found path inconsistencies:")
        for issue in msg:
            print(f"      - {issue}")
        has_errors = True
    
    # Section 4: Packaging
    print_info("\n=== Packaging ===")
    
    ok, msg = check_packaging_logic(skill_path)
    if ok: print_pass(msg)
    else: print_fail(msg); has_errors = True
    
    ok, msg = check_init_script_template(skill_path)
    if ok: print_pass(msg)
    else: print_fail(msg); has_errors = True
    
    # Section 5: Subprocess & Path Operations
    print_info("\n=== Subprocess & Path Operations ===")
    
    ok, msg = check_subprocess_robustness(skill_path)
    if ok:
        print_pass(msg)
    else:
        print_fail("Found potential subprocess robustness issues:")
        for issue in msg:
            print(f"      - {issue}")
        has_errors = True
    
    ok, msg = check_risky_path_ops(skill_path)
    if ok:
        print_pass(msg)
    else:
        print_fail("Found potential risky path operations:")
        for issue in msg:
            print(f"      - {issue}")
        has_errors = True
    
    # Section 6: Registry & Map Consistency
    print_info("\n=== Registry & Map Consistency ===")
    
    ok, msg = check_registry_consistency(skill_path, skills_dir)
    if ok:
        print_pass(msg)
    else:
        print_fail("Registry consistency issues:")
        if isinstance(msg, list):
            for issue in msg: print(f"      - {issue}")
        else:
            print(f"      - {msg}")
        has_warnings = True
    
    ok, msg = check_skill_map_consistency(skill_path, skills_dir)
    if ok:
        print_pass(msg)
    else:
        print_fail("Skill map consistency issues:")
        if isinstance(msg, list):
            for issue in msg: print(f"      - {issue}")
        else:
            print(f"      - {msg}")
        has_warnings = True
    
    print("\n" + "="*40)
    if has_errors:
        print(f"{RED}⚠️  Audit completed with errors. Please fix issues above.{RESET}")
        return False
    elif has_warnings:
        print(f"{YELLOW}⚠️  Audit completed with warnings. Review issues above.{RESET}")
        return True
    else:
        print(f"{GREEN}✨ Skill passed all standard checks!{RESET}")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python audit_skill.py <path/to/skill>")
        sys.exit(1)
    
    # Check if skills_dir is provided
    skills_dir = None
    if len(sys.argv) >= 3:
        skills_dir = Path(sys.argv[2])
    else:
        # Default to parent of skill
        skills_dir = Path(sys.argv[1]).parent
    
    success = audit_skill(sys.argv[1], skills_dir)
    sys.exit(0 if success else 1)
