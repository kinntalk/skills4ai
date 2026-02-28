#!/usr/bin/env python3
"""
Skills Consistency Checker - Check consistency across registry files

This script checks:
- skills.json vs actual skill directories
- skill_map.json vs skills.json
- AGENTS.md vs actual skills
"""

import sys
import os
import json
import re
from pathlib import Path

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"

SKILLS_DIR = Path(__file__).parent.parent.parent
REGISTRY_FILE = SKILLS_DIR / 'skills.json'
SKILL_MAP_FILE = SKILLS_DIR / 'skill_map.json'
AGENTS_FILE = SKILLS_DIR / 'AGENTS.md'

def print_status(status, message):
    """Print status message with color"""
    colors = {
        'PASS': GREEN,
        'FAIL': RED,
        'WARN': YELLOW,
        'INFO': CYAN,
        'CHECK': BLUE
    }
    color = colors.get(status, '')
    print(f"{color}[{status}]{RESET} {message}")

def is_skill_collection(skill_dir):
    """Check if a directory is a skill collection (contains skills/ subdirectory with SKILL.md files)"""
    skills_subdir = skill_dir / 'skills'
    if skills_subdir.is_dir():
        for sub_skill in skills_subdir.iterdir():
            if sub_skill.is_dir() and (sub_skill / 'SKILL.md').exists():
                return True
    return False

def get_installed_skills():
    """Get set of installed skill directory names"""
    skills = set()
    for item in SKILLS_DIR.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            skill_md = item / 'SKILL.md'
            if skill_md.exists():
                skills.add(item.name)
            elif is_skill_collection(item):
                skills.add(item.name)
    return skills

def load_json_file(filepath):
    """Load JSON file safely"""
    if not filepath.exists():
        return None
    try:
        content = filepath.read_text(encoding='utf-8')
        return json.loads(content)
    except Exception as e:
        print_status('FAIL', f"Failed to load {filepath.name}: {e}")
        return None

def check_skills_json(installed_skills):
    """Check skills.json consistency"""
    print_status('CHECK', "Checking skills.json...")
    
    issues = []
    
    data = load_json_file(REGISTRY_FILE)
    if data is None:
        issues.append(("critical", "skills.json not found or invalid"))
        return issues
    
    registered = set(data.get('skills', {}).keys())
    
    missing_from_registry = installed_skills - registered
    extra_in_registry = registered - installed_skills
    
    if missing_from_registry:
        for skill in missing_from_registry:
            issues.append(("missing", f"'{skill}' installed but not in skills.json"))
    
    if extra_in_registry:
        for skill in extra_in_registry:
            issues.append(("orphan", f"'{skill}' in skills.json but not installed"))
    
    for name, info in data.get('skills', {}).items():
        health = info.get('health', {})
        if not health.get('is_valid', True):
            issues.append(("invalid", f"'{name}': {health.get('validation_error', 'Unknown error')}"))
    
    if not issues:
        print_status('PASS', "skills.json is consistent")
    else:
        for severity, msg in issues:
            status = 'FAIL' if severity in ('critical', 'missing') else 'WARN'
            print_status(status, msg)
    
    return issues

def check_skill_map(installed_skills):
    """Check skill_map.json consistency"""
    print_status('CHECK', "Checking skill_map.json...")
    
    issues = []
    
    data = load_json_file(SKILL_MAP_FILE)
    if data is None:
        issues.append(("critical", "skill_map.json not found or invalid"))
        return issues
    
    mapped = set(data.get('skills', {}).keys())
    
    missing_from_map = installed_skills - mapped
    extra_in_map = mapped - installed_skills
    
    if missing_from_map:
        for skill in missing_from_map:
            issues.append(("missing", f"'{skill}' installed but not in skill_map.json"))
    
    if extra_in_map:
        for skill in extra_in_map:
            issues.append(("orphan", f"'{skill}' in skill_map.json but not installed"))
    
    priority_order = data.get('detection_rules', {}).get('priority_order', [])
    for skill in priority_order:
        if skill not in installed_skills:
            issues.append(("orphan", f"'{skill}' in priority_order but not installed"))
    
    if not issues:
        print_status('PASS', "skill_map.json is consistent")
    else:
        for severity, msg in issues:
            status = 'FAIL' if severity in ('critical', 'missing') else 'WARN'
            print_status(status, msg)
    
    return issues

def check_agents_md(installed_skills):
    """Check AGENTS.md consistency"""
    print_status('CHECK', "Checking AGENTS.md...")
    
    issues = []
    
    if not AGENTS_FILE.exists():
        issues.append(("critical", "AGENTS.md not found"))
        return issues
    
    try:
        content = AGENTS_FILE.read_text(encoding='utf-8')
    except Exception as e:
        issues.append(("critical", f"Failed to read AGENTS.md: {e}"))
        return issues
    
    documented = set()
    for match in re.finditer(r'^### ([a-zA-Z0-9_-]+)$', content, re.MULTILINE):
        documented.add(match.group(1))
    
    missing_from_doc = installed_skills - documented
    extra_in_doc = documented - installed_skills
    
    if missing_from_doc:
        for skill in missing_from_doc:
            issues.append(("missing", f"'{skill}' installed but not documented in AGENTS.md"))
    
    if extra_in_doc:
        for skill in extra_in_doc:
            issues.append(("orphan", f"'{skill}' documented but not installed"))
    
    total_match = re.search(r'\*\*Total Skills:\*\*\s*(\d+)', content)
    if total_match:
        documented_total = int(total_match.group(1))
        if documented_total != len(installed_skills):
            issues.append(("mismatch", f"Total count ({documented_total}) != installed skills ({len(installed_skills)})"))
    
    if not issues:
        print_status('PASS', "AGENTS.md is consistent")
    else:
        for severity, msg in issues:
            status = 'FAIL' if severity in ('critical', 'missing') else 'WARN'
            print_status(status, msg)
    
    return issues

def check_cross_consistency():
    """Check cross-file consistency"""
    print_status('CHECK', "Checking cross-file consistency...")
    
    issues = []
    
    skills_data = load_json_file(REGISTRY_FILE)
    map_data = load_json_file(SKILL_MAP_FILE)
    
    if skills_data and map_data:
        skills_names = set(skills_data.get('skills', {}).keys())
        map_names = set(map_data.get('skills', {}).keys())
        
        if skills_names != map_names:
            only_in_skills = skills_names - map_names
            only_in_map = map_names - skills_names
            
            if only_in_skills:
                issues.append(("mismatch", f"Skills only in skills.json: {only_in_skills}"))
            if only_in_map:
                issues.append(("mismatch", f"Skills only in skill_map.json: {only_in_map}"))
    
    if not issues:
        print_status('PASS', "Cross-file consistency verified")
    else:
        for severity, msg in issues:
            print_status('WARN', msg)
    
    return issues

def generate_report(all_issues):
    """Generate summary report"""
    print()
    print("=" * 60)
    print("CONSISTENCY REPORT")
    print("=" * 60)
    
    total_issues = sum(len(issues) for issues in all_issues.values())
    critical_count = sum(1 for issues in all_issues.values() for s, _ in issues if s == 'critical')
    missing_count = sum(1 for issues in all_issues.values() for s, _ in issues if s == 'missing')
    orphan_count = sum(1 for issues in all_issues.values() for s, _ in issues if s == 'orphan')
    mismatch_count = sum(1 for issues in all_issues.values() for s, _ in issues if s == 'mismatch')
    
    print(f"\nTotal issues found: {total_issues}")
    
    if critical_count:
        print(f"  Critical: {critical_count}")
    if missing_count:
        print(f"  Missing entries: {missing_count}")
    if orphan_count:
        print(f"  Orphan entries: {orphan_count}")
    if mismatch_count:
        print(f"  Mismatches: {mismatch_count}")
    
    if total_issues == 0:
        print_status('PASS', "All registry files are consistent!")
    else:
        print()
        print_status('WARN', "Run sync_registry.py to fix these issues:")
        print("  python .trae/skills/skills-registry-sync/scripts/sync_registry.py --fix")
    
    return total_issues

def main():
    print_status('INFO', "Starting consistency check...")
    print()
    
    installed_skills = get_installed_skills()
    print_status('INFO', f"Found {len(installed_skills)} installed skills")
    print()
    
    all_issues = {}
    
    all_issues['skills.json'] = check_skills_json(installed_skills)
    print()
    
    all_issues['skill_map.json'] = check_skill_map(installed_skills)
    print()
    
    all_issues['AGENTS.md'] = check_agents_md(installed_skills)
    print()
    
    all_issues['cross'] = check_cross_consistency()
    print()
    
    total_issues = generate_report(all_issues)
    
    return 0 if total_issues == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
