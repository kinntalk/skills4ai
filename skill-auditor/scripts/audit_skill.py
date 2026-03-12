#!/usr/bin/env python3
"""
Skill Auditor - Comprehensive validation tool for Trae skills
Main entry point that orchestrates all checks.
Always outputs standardized audit report format.
"""

import sys
import re
import yaml
import json
import argparse
from pathlib import Path
from typing import List, Tuple
from datetime import datetime
from colorama import init as colorama_init, Fore, Style

colorama_init()

try:
    from base_checker import BaseASTChecker
    from audit_config import SEVERITY_CRITICAL, SEVERITY_HIGH, SEVERITY_MEDIUM, SEVERITY_LOW
    from messages import get_message, get_lang, set_lang, get_available_languages
    from file_param_checker import check_encoding_parameter, check_errors_replace
    from security_checks import (
        check_malicious_script_injection, check_permission_abuse,
        check_prompt_injection, check_code_execution_safety,
        check_filesystem_security, check_network_security, check_data_masking
    )
    from quality_checks import (
        check_error_handling_patterns, check_exception_handling,
        check_logging_practices, check_input_validation,
        check_output_sanitization, check_technical_standards
    )
    from output_quality_checks import (
        check_token_optimization, check_ai_execution_effectiveness,
        check_verbose_output, check_redundant_code
    )
    from report_generator import AuditReportGenerator, AuditData, AuditIssue, create_audit_data
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from base_checker import BaseASTChecker
    from audit_config import SEVERITY_CRITICAL, SEVERITY_HIGH, SEVERITY_MEDIUM, SEVERITY_LOW
    from messages import get_message, get_lang, set_lang, get_available_languages
    from file_param_checker import check_encoding_parameter, check_errors_replace
    from security_checks import (
        check_malicious_script_injection, check_permission_abuse,
        check_prompt_injection, check_code_execution_safety,
        check_filesystem_security, check_network_security, check_data_masking
    )
    from quality_checks import (
        check_error_handling_patterns, check_exception_handling,
        check_logging_practices, check_input_validation,
        check_output_sanitization, check_technical_standards
    )
    from output_quality_checks import (
        check_token_optimization, check_ai_execution_effectiveness,
        check_verbose_output, check_redundant_code
    )
    from report_generator import AuditReportGenerator, AuditData, AuditIssue, create_audit_data


class AuditCollector:
    """Collects audit results and generates standardized output."""

    def __init__(self, skill_path: Path, audit_level: str):
        self.skill_path = skill_path
        self.skill_name = skill_path.name
        self.audit_level = audit_level
        self.audit_date = datetime.now().strftime("%Y-%m-%d")
        self.issues: List[AuditIssue] = []
        self.key_findings: List[str] = []
        self.recommended_actions: List[str] = []
        self.passed_checks: List[str] = []
        self._has_errors = False
        self._has_warnings = False

    def add_pass(self, message: str):
        self.passed_checks.append(message)

    def add_issue(self, file: str, line: int, severity: str, description: str, suggestion: str = ""):
        self.issues.append(AuditIssue(
            file=file,
            line=line,
            severity=severity,
            description=description,
            suggestion=suggestion
        ))
        if severity in [SEVERITY_CRITICAL, SEVERITY_HIGH]:
            self._has_errors = True
        else:
            self._has_warnings = True

    def add_issues_from_check(self, result: Tuple[bool, str | List[str]], severity: str, check_name: str):
        ok, msg = result
        if ok:
            self.add_pass(msg if isinstance(msg, str) else check_name)
        else:
            if isinstance(msg, list):
                for issue in msg:
                    self._parse_and_add_issue(issue, severity)
            else:
                self.add_issue("", 0, severity, str(msg))

    def _parse_and_add_issue(self, issue_str: str, severity: str):
        parts = issue_str.split(":", 2)
        if len(parts) >= 2:
            file = parts[0].strip()
            try:
                line = int(parts[1].strip())
            except ValueError:
                line = 0
            description = parts[2].strip() if len(parts) > 2 else issue_str
        else:
            file = ""
            line = 0
            description = issue_str
        self.add_issue(file, line, severity, description)

    @property
    def has_errors(self) -> bool:
        return self._has_errors or self.critical_count > 0 or self.high_count > 0

    @property
    def has_warnings(self) -> bool:
        return self._has_warnings or self.medium_count > 0 or self.low_count > 0

    @property
    def critical_count(self) -> int:
        return len([i for i in self.issues if i.severity == SEVERITY_CRITICAL])

    @property
    def high_count(self) -> int:
        return len([i for i in self.issues if i.severity == SEVERITY_HIGH])

    @property
    def medium_count(self) -> int:
        return len([i for i in self.issues if i.severity == SEVERITY_MEDIUM])

    @property
    def low_count(self) -> int:
        return len([i for i in self.issues if i.severity == SEVERITY_LOW])

    def build_findings(self):
        if self.critical_count > 0:
            self.key_findings.append(f"Found {self.critical_count} CRITICAL issues requiring immediate attention")
        if self.high_count > 0:
            self.key_findings.append(f"Found {self.high_count} HIGH priority issues")
        if self.medium_count > 0:
            self.key_findings.append(f"Found {self.medium_count} MEDIUM priority issues")
        if self.low_count > 0:
            self.key_findings.append(f"Found {self.low_count} LOW priority issues")
        if not self.key_findings:
            self.key_findings.append("No significant issues found")

    def build_actions(self):
        priority_order = {SEVERITY_CRITICAL: 0, SEVERITY_HIGH: 1, SEVERITY_MEDIUM: 2, SEVERITY_LOW: 3}
        sorted_issues = sorted(self.issues, key=lambda x: priority_order.get(x.severity, 4))
        for issue in sorted_issues[:5]:
            action = f"Fix {issue.severity} issue in {issue.file}:{issue.line}" if issue.file else f"Fix {issue.severity} issue: {issue.description[:50]}"
            self.recommended_actions.append(action)
        if not self.recommended_actions:
            self.recommended_actions.append("No immediate actions required")

    def get_assessment(self) -> str:
        if self.has_errors:
            return "Audit failed with errors"
        elif self.has_warnings:
            return "Audit passed with warnings"
        return "Audit passed successfully"

    def to_audit_data(self) -> AuditData:
        self.build_findings()
        self.build_actions()
        return create_audit_data(
            skill_name=self.skill_name,
            skill_path=self.skill_path,
            audit_level=self.audit_level,
            issues=[(i.file, i.line, i.severity, i.description, i.suggestion) for i in self.issues],
            overall_assessment=self.get_assessment(),
            key_findings=self.key_findings,
            recommended_actions=self.recommended_actions,
        )


def check_dependencies(skill_path):
    scripts_dir = skill_path / 'scripts'
    if not scripts_dir.exists():
        return True, "No scripts directory"
    
    py_files = list(scripts_dir.glob('**/*.py'))
    if not py_files:
        return True, "No Python scripts found"
        
    req_file = scripts_dir / 'requirements.txt'
    if not req_file.exists():
        return False, "Python scripts found but scripts/requirements.txt is missing"
    
    imported_modules = set()
    std_lib = sys.stdlib_module_names if hasattr(sys, 'stdlib_module_names') else {
        'os', 'sys', 're', 'json', 'yaml', 'pathlib', 'argparse', 'subprocess', 
        'shutil', 'tempfile', 'time', 'datetime', 'logging', 'threading', 'typing',
        'collections', 'io', 'math', 'random', 'string', 'hashlib', 'base64',
        'urllib', 'http', 'email', 'csv', 'sqlite3', 'configparser', 'zipfile',
        'tarfile', 'gzip', 'bz2', 'pickle', 'copy', 'itertools', 'functools',
        'operator', 'decimal', 'fractions', 'statistics', 'enum', 'dataclasses',
        'uuid', 'secrets', 'inspect', 'warnings', 'contextlib', 'abc', 'numbers', 'types'
    }

    for py_file in py_files:
        try:
            content = py_file.read_text(encoding='utf-8', errors='replace')
            imports = re.findall(r'^\s*(?:import|from)\s+([a-zA-Z0-9_]+)', content, re.MULTILINE)
            for module in imports:
                if module not in std_lib and module != 'scripts':
                    imported_modules.add(module)
        except (FileNotFoundError, PermissionError, UnicodeDecodeError):
            pass

    try:
        req_content = req_file.read_text(encoding='utf-8', errors='replace').lower()
        declared_deps = set(line.split('==')[0].split('>=')[0].strip() 
                          for line in req_content.splitlines() 
                          if line.strip() and not line.startswith('#'))
    except (FileNotFoundError, PermissionError):
        return False, "requirements.txt not found"

    pkg_map = {'yaml': 'pyyaml', 'PIL': 'pillow', 'bs4': 'beautifulsoup4', 
               'dotenv': 'python-dotenv', 'git': 'gitpython',
               'win32gui': 'pywin32', 'win32con': 'pywin32', 'win32process': 'pywin32',
               'win32api': 'pywin32', 'win32file': 'pywin32', 'win32event': 'pywin32',
               'cv2': 'opencv-python', 'numpy': 'numpy', 'np': 'numpy'}

    missing_deps = []
    for module in imported_modules:
        pkg_name = pkg_map.get(module, module).lower()
        if pkg_name not in declared_deps and module.lower() not in declared_deps:
            if not (scripts_dir / f"{module}.py").exists():
                missing_deps.append(f"{module} (package: {pkg_name})")

    if missing_deps:
        return False, f"Potential missing dependencies: {', '.join(missing_deps)}"

    return True, "Dependency configuration looks good"


def validate_frontmatter(skill_path):
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        readme = skill_path / 'README.md'
        if readme.exists():
            return True, "SKILL.md missing (found README.md)"
        return True, "SKILL.md missing"
        
    try:
        content = skill_md.read_text(encoding='utf-8', errors='replace')
        if not content.startswith('---'):
            return False, "No YAML frontmatter"
            
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return False, "Invalid frontmatter format"
            
        frontmatter = yaml.safe_load(match.group(1))
        
        if 'name' not in frontmatter:
            return False, "Missing 'name' in frontmatter"
        if 'description' not in frontmatter:
            return False, "Missing 'description' in frontmatter"
            
        return True, "SKILL.md frontmatter is valid"
    except yaml.YAMLError as e:
        return False, f"YAML parsing error: {e}"
    except (FileNotFoundError, PermissionError) as e:
        return False, f"Error reading SKILL.md: {e}"


def check_skill_name_consistency(skill_path):
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return True, "SKILL.md not found"
    
    try:
        content = skill_md.read_text(encoding='utf-8', errors='replace')
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return True, "No frontmatter found"
        
        frontmatter = yaml.safe_load(match.group(1))
        
        if 'name' not in frontmatter:
            return False, "Missing 'name' field"
        
        if frontmatter['name'] != skill_path.name:
            return False, f"Name mismatch: SKILL.md='{frontmatter['name']}' vs directory='{skill_path.name}'"
        
        return True, "Name matches directory"
    except (yaml.YAMLError, FileNotFoundError, PermissionError) as e:
        return True, f"Check skipped: {e}"


def check_directory_structure(skill_path):
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "SKILL.md not found at root"
    
    allowed_files = ["SKILL.md", "README.md", "LICENSE.txt", "LICENSE", ".gitignore", "CLAUDE.md", "requirements.txt"]
    ref_doc_patterns = [r'.*-tracing\.md$', r'.*-guide\.md$', r'.*-protocol\.md$', 
                       r'.*-reference\.md$', r'.*-workflow\.md$', r'.*-methodology\.md$']
    unexpected_files = []
    
    try:
        for item in skill_path.iterdir():
            if item.is_file():
                if item.name not in allowed_files:
                    is_ref_doc = any(re.match(pattern, item.name) for pattern in ref_doc_patterns)
                    if not is_ref_doc:
                        unexpected_files.append(item.name)
    except (FileNotFoundError, PermissionError):
        return False, "Error scanning directory"
    
    if unexpected_files:
        return False, [f"Unexpected files: {', '.join(unexpected_files)}"]
    return True, "Directory structure is valid"


def check_packaging_logic(skill_path):
    package_script = skill_path / 'scripts' / 'package_skill.py'
    if not package_script.exists():
        return True, "No package_skill.py found"
        
    try:
        content = package_script.read_text(encoding='utf-8', errors='replace')
        
        if 'relative_to(skill_path.parent)' in content:
            return False, "Uses 'skill_path.parent' (creates nested zip)"
        
        if 'relative_to(skill_path)' not in content and 'arcname = file_path.name' not in content:
            return False, "Does not use correct flat structure logic"
            
        if '__pycache__' not in content and '.pyc' not in content:
            return False, "Does not filter __pycache__ or .pyc files"
            
        return True, "Packaging logic is correct"
    except (FileNotFoundError, PermissionError):
        return False, "Error reading package_skill.py"


def check_i18n_support(skill_path):
    issues = []
    
    skill_md = skill_path / 'SKILL.md'
    if skill_md.exists():
        try:
            content = skill_md.read_text(encoding='utf-8', errors='replace')
            
            emoji_pattern = re.compile(
                "["
                "\U0001F600-\U0001F64F"
                "\U0001F300-\U0001F5FF"
                "\U0001F680-\U0001F6FF"
                "\U0001F1E0-\U0001F1FF"
                "\U00002702-\U000027B0"
                "\U0001F900-\U0001F9FF"
                "\U0001FA00-\U0001FA6F"
                "\U0001FA70-\U0001FAFF"
                "]+", flags=re.UNICODE)
            
            emojis = emoji_pattern.findall(content)
            if emojis:
                issues.append(f"Emoji found in SKILL.md: {emojis[:3]}...")
            
            has_en = bool(re.search(r'[a-zA-Z]{3,}', content))
            has_zh = bool(re.search(r'[\u4e00-\u9fff]', content))
            
            if not (has_en and has_zh):
                issues.append("SKILL.md should include both English and Chinese")
                
        except (FileNotFoundError, PermissionError):
            issues.append("Could not read SKILL.md")
    
    return (False, issues) if issues else (True, "i18n support looks good")


def check_absolute_references(skill_path):
    issues = []
    absolute_patterns = [
        (r'[A-Z]:\\', 'Windows absolute path'),
        (r'/home/', 'Linux home path'),
        (r'/Users/', 'macOS user path'),
        (r'/etc/', 'Linux etc path'),
        (r'/var/', 'Linux var path'),
    ]
    
    for file_path in skill_path.glob('**/*'):
        if not file_path.is_file():
            continue
        if file_path.suffix not in ['.md', '.py', '.txt', '.json', '.yaml', '.yml']:
            continue
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='replace')
            for pattern, desc in absolute_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    rel_path = file_path.relative_to(skill_path)
                    issues.append(f"{rel_path}: Contains {desc}: {matches[0]}...")
        except (FileNotFoundError, PermissionError):
            pass
    
    return (False, issues) if issues else (True, "No hardcoded absolute paths found")


def check_registry_consistency(skill_path, skills_dir):
    if not skills_dir:
        return True, "Skills directory not provided"
    
    skills_json = Path(skills_dir) / 'skills.json'
    if not skills_json.exists():
        return True, "skills.json not found"
    
    try:
        content = skills_json.read_text(encoding='utf-8', errors='replace')
        data = json.loads(content)
        skill_name = skill_path.name
        
        if skill_name not in data.get('skills', {}):
            return False, f"Skill '{skill_name}' not found in skills.json"
        
        return True, "Registered in skills.json"
    except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
        return True, f"Could not verify: {e}"


def check_skill_map_consistency(skill_path, skills_dir):
    if not skills_dir:
        return True, "Skills directory not provided"
    
    skill_map_json = Path(skills_dir) / 'skill_map.json'
    if not skill_map_json.exists():
        return True, "skill_map.json not found"
    
    try:
        content = skill_map_json.read_text(encoding='utf-8', errors='replace')
        data = json.loads(content)
        skill_name = skill_path.name
        
        skills_dict = data.get("skills", data)
        for skill_key, skill_info in skills_dict.items():
            if isinstance(skill_info, dict) and skill_info.get('name') == skill_name:
                return True, "Mapped in skill_map.json"
        
        return False, f"Skill '{skill_name}' not found in skill_map.json"
    except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
        return True, f"Could not verify: {e}"


def run_audit(skill_path: Path, skills_dir: Path = None, check_level: str = "standard") -> AuditCollector:
    """Run all audit checks and return collected results."""
    collector = AuditCollector(skill_path, check_level)
    
    run_i18n = check_level in ["strict", "standard"]
    run_packaging = check_level in ["strict", "standard"]
    run_security = check_level in ["strict", "standard"]
    run_quality = check_level in ["strict", "standard"]
    run_output_quality = check_level in ["strict", "standard"]
    run_registry = check_level in ["strict", "standard"]
    run_absolute = check_level in ["strict", "standard"]
    
    collector.add_issues_from_check(validate_frontmatter(skill_path), SEVERITY_HIGH, "frontmatter")
    collector.add_issues_from_check(check_skill_name_consistency(skill_path), SEVERITY_HIGH, "name_consistency")
    collector.add_issues_from_check(check_directory_structure(skill_path), SEVERITY_HIGH, "directory_structure")
    collector.add_issues_from_check(check_dependencies(skill_path), SEVERITY_MEDIUM, "dependencies")
    collector.add_issues_from_check(check_encoding_parameter(skill_path), SEVERITY_HIGH, "encoding")
    collector.add_issues_from_check(check_errors_replace(skill_path), SEVERITY_HIGH, "errors_replace")
    
    if run_packaging:
        collector.add_issues_from_check(check_packaging_logic(skill_path), SEVERITY_MEDIUM, "packaging")
    
    if run_i18n:
        collector.add_issues_from_check(check_i18n_support(skill_path), SEVERITY_LOW, "i18n")
    
    if run_absolute:
        collector.add_issues_from_check(check_absolute_references(skill_path), SEVERITY_HIGH, "absolute_refs")
    
    if run_registry:
        collector.add_issues_from_check(check_registry_consistency(skill_path, skills_dir), SEVERITY_LOW, "registry")
        collector.add_issues_from_check(check_skill_map_consistency(skill_path, skills_dir), SEVERITY_LOW, "skill_map")
    
    if run_security:
        security_checks = [
            (check_malicious_script_injection, SEVERITY_CRITICAL),
            (check_permission_abuse, SEVERITY_HIGH),
            (check_prompt_injection, SEVERITY_CRITICAL),
            (check_code_execution_safety, SEVERITY_CRITICAL),
            (check_filesystem_security, SEVERITY_HIGH),
            (check_network_security, SEVERITY_HIGH),
        ]
        for check_func, severity in security_checks:
            collector.add_issues_from_check(check_func(skill_path), severity, check_func.__name__)
    
    if run_quality:
        quality_checks = [
            (check_technical_standards, SEVERITY_MEDIUM),
            (check_error_handling_patterns, SEVERITY_HIGH),
            (check_exception_handling, SEVERITY_HIGH),
            (check_logging_practices, SEVERITY_LOW),
            (check_input_validation, SEVERITY_HIGH),
            (check_output_sanitization, SEVERITY_MEDIUM),
        ]
        for check_func, severity in quality_checks:
            collector.add_issues_from_check(check_func(skill_path), severity, check_func.__name__)
    
    if run_output_quality:
        output_checks = [
            (check_data_masking, SEVERITY_CRITICAL),
            (check_token_optimization, SEVERITY_LOW),
            (check_ai_execution_effectiveness, SEVERITY_MEDIUM),
            (check_verbose_output, SEVERITY_LOW),
            (check_redundant_code, SEVERITY_LOW),
        ]
        for check_func, severity in output_checks:
            collector.add_issues_from_check(check_func(skill_path), severity, check_func.__name__)
    
    return collector


def audit_skill(skill_path, skills_dir=None, verbose=False, json_output=False, check_level="standard", report_file=None):
    """
    Audit a skill for compliance and best practices.
    Always outputs standardized audit report format.
    """
    skill_path = Path(skill_path).resolve()
    if skills_dir is None:
        skills_dir = skill_path.parent
    
    collector = run_audit(skill_path, skills_dir, check_level)
    audit_data = collector.to_audit_data()
    generator = AuditReportGenerator(audit_data, lang=get_lang())
    report = generator.generate()
    
    if json_output:
        output = {
            "skill_name": audit_data.skill_name,
            "audit_level": audit_data.audit_level,
            "audit_date": audit_data.audit_date,
            "total_issues": audit_data.total_issues,
            "critical": audit_data.critical_count,
            "high": audit_data.high_count,
            "medium": audit_data.medium_count,
            "low": audit_data.low_count,
            "assessment": audit_data.overall_assessment,
            "issues": [
                {"file": i.file, "line": i.line, "severity": i.severity, "description": i.description}
                for i in audit_data.issues
            ]
        }
        print(json.dumps(output, indent=2))
    else:
        print(report)
    
    if report_file:
        report_path = Path(report_file)
        if generator.save(report_path):
            print(f"\n[INFO] Report saved to: {report_path}")
    
    if collector.has_errors:
        print(f"\n{Fore.RED}[FAIL] Audit completed with errors{Style.RESET_ALL}")
        return False
    elif collector.has_warnings:
        print(f"\n{Fore.YELLOW}[WARN] Audit completed with warnings{Style.RESET_ALL}")
        return True
    else:
        print(f"\n{Fore.GREEN}[PASS] Audit completed successfully{Style.RESET_ALL}")
        return True


def main():
    parser = argparse.ArgumentParser(description='Audit a Trae skill for compliance and best practices')
    parser.add_argument('skill_path', help='Path to the skill directory to audit')
    parser.add_argument('skills_dir', nargs='?', help='Optional path to skills root directory')
    parser.add_argument('--level', choices=['strict', 'standard', 'relaxed'], default='standard',
                       help='Check strictness level (default: standard)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    parser.add_argument('--lang', choices=get_available_languages(), help='Language for output messages')
    parser.add_argument('--report', '-r', type=str, metavar='FILE', help='Save report to FILE')
    
    args = parser.parse_args()
    
    if args.lang:
        set_lang(args.lang)
    
    skill_path = Path(args.skill_path)
    if not skill_path.exists():
        print(f"Error: Skill path does not exist: {skill_path}")
        sys.exit(1)
    
    skills_dir = Path(args.skills_dir) if args.skills_dir else None
    
    success = audit_skill(
        skill_path, 
        skills_dir=skills_dir,
        verbose=args.verbose,
        json_output=args.json,
        check_level=args.level,
        report_file=args.report
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
