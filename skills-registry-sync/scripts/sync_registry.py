#!/usr/bin/env python3
"""
Skills Registry Sync - Synchronize all skills registry files

This script synchronizes:
- skills.json: Tracks installed skills with metadata
- skill_map.json: Maps skill names for detection
- AGENTS.md: Human-readable skill documentation
"""

import sys
import os
import json
import datetime
import re
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

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
        'SYNC': BLUE
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

def validate_skill_md(skill_path):
    """Validate SKILL.md file"""
    skill_md_path = skill_path / 'SKILL.md'
    
    if not skill_md_path.exists():
        return False, "SKILL.md file not found", {}
    
    try:
        content = skill_md_path.read_text(encoding='utf-8')
    except UnicodeDecodeError as e:
        try:
            content = skill_md_path.read_text(encoding='utf-8', errors='replace')
        except Exception:
            return False, f"Failed to read SKILL.md", {}
    except Exception as e:
        return False, f"Failed to read SKILL.md: {e}", {}
    
    if not content.strip():
        return False, "SKILL.md is empty", {}
    
    yaml_pattern = r'^---\s*\n(.*?)\n---'
    match = re.match(yaml_pattern, content, re.DOTALL)
    
    if not match:
        return False, "Invalid YAML frontmatter format", {}
    
    yaml_content = match.group(1)
    
    try:
        import yaml
        frontmatter = yaml.safe_load(yaml_content)
    except ImportError:
        return False, "PyYAML not installed", {}
    except Exception as e:
        return False, f"Failed to parse YAML: {e}", {}
    
    if not isinstance(frontmatter, dict):
        return False, "YAML frontmatter is not a dictionary", {}
    
    if 'name' not in frontmatter:
        return False, "Missing required field: 'name'", frontmatter
    
    if 'description' not in frontmatter:
        return False, "Missing required field: 'description'", frontmatter
    
    return True, None, frontmatter

def validate_source_url(source):
    """Validate and normalize source URL format"""
    if source == "local":
        return True, source
    
    if not source.startswith(('http://', 'https://')):
        return False, f"Invalid source URL format: {source}"
    
    if source.endswith('.git'):
        return True, source
    
    return False, f"Source URL missing .git suffix: {source}"

def normalize_source_url(source):
    """Normalize source URL to ensure consistency"""
    if source == "local":
        return source
    
    if not source.endswith('.git'):
        return source + '.git'
    
    return source

def scan_skills():
    """Scan all installed skills - only includes skills with existing directories"""
    skills = {}
    
    existing_registry = {}
    try:
        if REGISTRY_FILE.exists():
            content = REGISTRY_FILE.read_text(encoding='utf-8')
            existing_registry = json.loads(content).get('skills', {})
    except Exception:
        pass
    
    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir() or skill_dir.name.startswith('.'):
            continue
        
        skill_name = skill_dir.name
        version = "unknown"
        source = "local"
        subdir = ""
        
        if skill_name in existing_registry:
            existing_info = existing_registry[skill_name]
            source = existing_info.get('source', source)
            source = normalize_source_url(source)
            subdir = existing_info.get('subdir', subdir)
            version = existing_info.get('version', version)
        
        try:
            git_dir = skill_dir / '.git'
            if git_dir.exists():
                import subprocess
                result = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=skill_dir, 
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                       text=True, errors='replace')
                if result.returncode == 0:
                    version = result.stdout.strip()
        except Exception:
            pass
        
        is_valid, validation_error, frontmatter = validate_skill_md(skill_dir)
        
        if not is_valid and is_skill_collection(skill_dir):
            is_valid = True
            validation_error = None
            frontmatter = {
                "name": skill_name,
                "description": f"Skill collection containing multiple sub-skills"
            }
            skills_subdir = skill_dir / 'skills'
            sub_skills = []
            for sub_skill in skills_subdir.iterdir():
                if sub_skill.is_dir() and (sub_skill / 'SKILL.md').exists():
                    sub_valid, _, sub_fm = validate_skill_md(sub_skill)
                    if sub_valid:
                        sub_skills.append(sub_skill.name)
            frontmatter["sub_skills"] = sub_skills
        
        skills[skill_name] = {
            "source": source,
            "subdir": subdir,
            "version": version,
            "last_update_time": datetime.datetime.now().isoformat(),
            "frontmatter": frontmatter if is_valid else {}
        }
    
    return skills

def update_skills_json(skills):
    """Update skills.json"""
    CORE_SKILLS = ['skill-creator', 'skill-installer', 'skill-auditor', 'skills-registry-sync']
    
    def sort_key(item):
        name = item[0]
        if name in CORE_SKILLS:
            return (0, CORE_SKILLS.index(name) if name in CORE_SKILLS else len(CORE_SKILLS))
        return (1, name)
    
    sorted_skills = {}
    for name, info in sorted(skills.items(), key=sort_key):
        normalized_source = normalize_source_url(info["source"])
        sorted_skills[name] = {
            "source": normalized_source,
            "subdir": info["subdir"],
            "version": info["version"],
            "last_update_time": info["last_update_time"]
        }
    
    try:
        REGISTRY_FILE.write_text(json.dumps({"skills": sorted_skills}, indent=2, ensure_ascii=False), 
                                 encoding='utf-8')
        print_status('SYNC', f"Updated skills.json with {len(skills)} skills")
        return True
    except Exception as e:
        print_status('FAIL', f"Failed to update skills.json: {e}")
        return False

def generate_keywords(name, description):
    """Generate keywords from skill name and description"""
    keywords = [name]
    
    words = re.findall(r'\b[a-zA-Z]{4,}\b', description.lower())
    stop_words = {'that', 'this', 'with', 'from', 'when', 'have', 'will', 'been', 'were', 'they', 
                  'their', 'would', 'could', 'should', 'being', 'about', 'which', 'where', 'what'}
    keywords.extend([w for w in words[:5] if w not in stop_words])
    
    return keywords[:6]

def update_skill_map(skills):
    """Update skill_map.json"""
    skill_map = {"skills": {}, "detection_rules": {"priority_order": [], "exact_match": {}, "partial_match": {}}}
    
    if SKILL_MAP_FILE.exists():
        try:
            content = SKILL_MAP_FILE.read_text(encoding='utf-8')
            skill_map = json.loads(content)
            if 'detection_rules' not in skill_map:
                skill_map['detection_rules'] = {"priority_order": [], "exact_match": {}, "partial_match": {}}
        except Exception:
            pass
    
    existing_skills = set(skill_map.get('skills', {}).keys())
    new_skills = set(skills.keys())
    
    removed = existing_skills - new_skills
    added = new_skills - existing_skills
    
    for name in removed:
        if name in skill_map['skills']:
            del skill_map['skills'][name]
            print_status('SYNC', f"Removed '{name}' from skill_map.json")
    
    for name, info in skills.items():
        frontmatter = info.get('frontmatter', {})
        description = frontmatter.get('description', '')
        
        if name not in skill_map['skills']:
            print_status('SYNC', f"Added '{name}' to skill_map.json")
        
        skill_map['skills'][name] = {
            "name": name,
            "description": description,
            "keywords": generate_keywords(name, description),
            "aliases": [name]
        }
    
    priority_order = [s for s in skill_map.get('detection_rules', {}).get('priority_order', []) 
                      if s in new_skills]
    for name in sorted(new_skills):
        if name not in priority_order:
            priority_order.append(name)
    skill_map['detection_rules']['priority_order'] = priority_order
    
    try:
        SKILL_MAP_FILE.write_text(json.dumps(skill_map, indent=2, ensure_ascii=False), 
                                  encoding='utf-8')
        print_status('SYNC', f"Updated skill_map.json ({len(added)} added, {len(removed)} removed)")
        return True
    except Exception as e:
        print_status('FAIL', f"Failed to update skill_map.json: {e}")
        return False

def categorize_skill(name):
    """Categorize skill by name prefix"""
    if name.startswith('sp-'):
        return 'Superpowers'
    elif name in ['skill-creator', 'skill-installer', 'skill-auditor', 'skills-registry-sync']:
        return 'Tool Skills'
    elif name.startswith('python-') or name.startswith('async-'):
        return 'Python Skills'
    elif 'obsidian' in name.lower():
        return 'Obsidian Skills'
    elif name in ['image-generation', 'pdf-generation', 'planning-with-files', 'powershell-windows', 'proxy-manager']:
        return 'Core Skills'
    else:
        return 'Other Skills'

def update_agents_md(skills):
    """Update AGENTS.md"""
    categories = {}
    for name, info in skills.items():
        cat = categorize_skill(name)
        if cat not in categories:
            categories[cat] = []
        categories[cat].append((name, info))
    
    total = len(skills)
    
    category_order = ['Core Skills', 'Tool Skills', 'Superpowers', 'Python Skills', 'Obsidian Skills', 'Other Skills']
    
    content = f"""# AGENTS.md - Skills Registry

**Version:** 1.0.0  
**Last Updated:** {datetime.date.today()}  
**Total Skills:** {total}

---

## Overview

This document provides a comprehensive registry of all available skills in the `.trae/skills` directory.

---

## Quick Reference

| Category | Count | Skills |
|-----------|--------|---------|
"""
    
    for cat in category_order:
        if cat in categories:
            skill_names = ', '.join([s[0] for s in categories[cat]])
            content += f"| {cat} | {len(categories[cat])} | {skill_names} |\n"
    
    content += f"| **Total** | **{total}** | |\n\n---\n\n"
    
    for cat in category_order:
        if cat not in categories:
            continue
        
        content += f"## {cat}\n\n"
        
        for name, info in sorted(categories[cat], key=lambda x: x[0]):
            frontmatter = info.get('frontmatter', {})
            description = frontmatter.get('description', 'No description available')
            
            content += f"### {name}\n\n"
            content += f"**Description:** {description}\n\n"
            content += f"**Path:** `{name}/`\n\n"
            content += "---\n\n"
    
    content += f"""
## Statistics

### Category Distribution

| Category | Count | Percentage |
|----------|--------|------------|
"""
    
    for cat in category_order:
        if cat in categories:
            pct = round(len(categories[cat]) / total * 100, 1) if total > 0 else 0
            content += f"| {cat} | {len(categories[cat])} | {pct}% |\n"
    
    content += f"| **Total** | **{total}** | **100%** |\n\n"
    content += "---\n\n*This registry is auto-generated by skills-registry-sync skill.*\n"
    
    try:
        AGENTS_FILE.write_text(content, encoding='utf-8')
        print_status('SYNC', f"Updated AGENTS.md with {total} skills")
        return True
    except Exception as e:
        print_status('FAIL', f"Failed to update AGENTS.md: {e}")
        return False

def sync_all(fix=False):
    """Synchronize all registry files"""
    print_status('INFO', "Scanning skills directory...")
    
    skills = scan_skills()
    print_status('INFO', f"Found {len(skills)} installed skills")
    
    print()
    print_status('INFO', "Updating registry files...")
    
    results = []
    results.append(update_skills_json(skills))
    results.append(update_skill_map(skills))
    results.append(update_agents_md(skills))
    
    print()
    if all(results):
        print_status('PASS', "All registry files synchronized successfully")
    else:
        print_status('WARN', "Some registry files could not be updated")
    
    return all(results)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Sync skills registry files")
    parser.add_argument('--fix', action='store_true', help='Fix inconsistencies automatically')
    
    args = parser.parse_args()
    
    sync_all(fix=args.fix)

if __name__ == "__main__":
    main()
