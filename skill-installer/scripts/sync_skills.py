#!/usr/bin/env python3
"""
Skills Sync - 自动扫描并同步 skills.json
自动扫描 .trae/skills/ 目录下的所有 skills 并更新 skills.json
"""

import sys
import os
import json
import datetime
import re
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from messages import *
except ImportError:
    try:
        sys.path.append(str(Path(__file__).parent))
        from messages import *
    except ImportError:
        GREEN = "\033[92m"
        RED = "\033[91m"
        YELLOW = "\033[93m"
        BLUE = "\033[94m"
        COLOR_YELLOW = "\033[93m"
        COLOR_RESET = "\033[0m"
        RESET = "\033[0m"
        MSG_SYNCED_SUCCESS = f"{GREEN}Synced {{count}} skills to registry{RESET}"
        MSG_REGISTRY_FILE = f"   Registry file: {{path}}"
        MSG_SKILLS_LIST = f"\nSkills List:"
        MSG_DRY_RUN = f"Dry run: Would sync {{count}} skills"
        MSG_VALIDATING_SKILLS = f"\nValidating skills..."
        MSG_SKILL_VALID = f"   [PASS] {{name}}: Valid"
        MSG_SKILL_INVALID = f"   [FAIL] {{name}}: Invalid - {{error}}"
        MSG_DEPENDENCY_MISSING = f"   [WARN] {{name}}: Missing dependencies: {{deps}}"
        MSG_HEALTH_SUMMARY = f"\n{'='*60}"
        MSG_HEALTH_SUMMARY_TITLE = f"Health Summary"
        MSG_HEALTH_TOTAL = f"   Total skills checked: {{count}}"
        MSG_HEALTH_HEALTHY = f"   Healthy: {{count}}"
        MSG_HEALTH_WARNINGS = f"   Warnings: {{count}}"
        MSG_HEALTH_ERRORS = f"   Errors: {{count}}"
        MSG_HEALTH_ISSUES_HEADER = f"\nSkills with issues:"
        MSG_HEALTH_RECOMMENDATIONS = f"\nRecommendations:"
        MSG_HEALTH_RECOMMENDATION_FIX_MD = f"   - Fix SKILL.md files for skills with validation errors"
        MSG_HEALTH_RECOMMENDATION_INSTALL_DEPS = f"   - Install missing dependencies to resolve dependency warnings"

try:
    from install_skill import update_skill_map
except ImportError:
    try:
        sys.path.append(str(Path(__file__).parent))
        from install_skill import update_skill_map
    except ImportError:
        def update_skill_map(*args, **kwargs):
            print(f"{YELLOW}Warning: Could not import update_skill_map. skill_map.json will not be updated.{RESET}")

SKILLS_DIR = Path(__file__).parent.parent.parent
REGISTRY_FILE = SKILLS_DIR / 'skills.json'
SKILL_MAP_FILE = SKILLS_DIR / 'skill_map.json'

def validate_skill_md(skill_path):
    """验证 SKILL.md 文件
    
    Args:
        skill_path: skill 目录的 Path 对象
        
    Returns:
        tuple: (is_valid, error_message)
    """
    skill_md_path = skill_path / 'SKILL.md'
    
    if not skill_md_path.exists():
        return False, "SKILL.md file not found"
    
    try:
        content = skill_md_path.read_text(encoding='utf-8')
    except UnicodeDecodeError as e:
        logger.error(f"Unicode decode error reading {skill_md_path}: {e}")
        try:
            content = skill_md_path.read_text(encoding='utf-8', errors='replace')
            logger.warning(f"Retrying with errors='replace' for {skill_md_path}")
        except Exception as e2:
            logger.error(f"Failed to read {skill_md_path} even with errors='replace': {e2}")
            return False, f"Failed to read SKILL.md: {e2}"
    except Exception as e:
        logger.error(f"Error reading {skill_md_path}: {e}")
        return False, f"Failed to read SKILL.md: {e}"
    
    if not content.strip():
        return False, "SKILL.md is empty"
    
    yaml_pattern = r'^---\s*\n(.*?)\n---'
    match = re.match(yaml_pattern, content, re.DOTALL)
    
    if not match:
        return False, "Invalid YAML frontmatter format"
    
    yaml_content = match.group(1)
    
    try:
        import yaml
        frontmatter = yaml.safe_load(yaml_content)
    except ImportError:
        return False, "PyYAML not installed, cannot validate YAML"
    except Exception as e:
        logger.error(f"YAML parsing error in {skill_md_path}: {e}")
        return False, f"Failed to parse YAML: {e}"
    
    if not isinstance(frontmatter, dict):
        return False, "YAML frontmatter is not a dictionary"
    
    if 'name' not in frontmatter:
        return False, "Missing required field: 'name'"
    
    if 'description' not in frontmatter:
        return False, "Missing required field: 'description'"
    
    return True, None

def check_skill_dependencies(skill_path, installed_skills):
    """检查 skill 的依赖项
    
    Args:
        skill_path: skill 目录的 Path 对象
        installed_skills: 已安装的 skill 名称集合
        
    Returns:
        tuple: (missing_deps, satisfied_deps)
    """
    skill_md_path = skill_path / 'SKILL.md'
    
    if not skill_md_path.exists():
        return [], []
    
    try:
        content = skill_md_path.read_text(encoding='utf-8')
    except UnicodeDecodeError as e:
        logger.error(f"Unicode decode error reading {skill_md_path}: {e}")
        try:
            content = skill_md_path.read_text(encoding='utf-8', errors='replace')
            logger.warning(f"Retrying with errors='replace' for {skill_md_path}")
        except Exception as e2:
            logger.error(f"Failed to read {skill_md_path} even with errors='replace': {e2}")
            return [], []
    except (PermissionError, OSError) as e:
        logger.error(f"Error reading {skill_md_path}: {e}")
        return [], []
    
    yaml_pattern = r'^---\s*\n(.*?)\n---'
    match = re.match(yaml_pattern, content, re.DOTALL)
    
    if not match:
        return [], []
    
    yaml_content = match.group(1)
    
    try:
        import yaml
        frontmatter = yaml.safe_load(yaml_content)
    except Exception as e:
        logger.error(f"YAML parsing error in {skill_md_path}: {e}")
        return [], []
    
    if not isinstance(frontmatter, dict):
        return [], []
    
    dependencies = frontmatter.get('dependencies', [])
    
    if not dependencies:
        return [], []
    
    if isinstance(dependencies, str):
        dependencies = [dependencies]
    
    missing_deps = []
    satisfied_deps = []
    
    for dep in dependencies:
        if dep in installed_skills:
            satisfied_deps.append(dep)
        else:
            missing_deps.append(dep)
    
    return missing_deps, satisfied_deps

def prune_skill_map(installed_skills):
    """移除 skill_map.json 中已不存在的 skills"""
    if not SKILL_MAP_FILE.exists():
        return
        
    try:
        content = SKILL_MAP_FILE.read_text(encoding='utf-8')
        skill_map = json.loads(content)
        
        if 'skills' not in skill_map:
            return
            
        # Identify skills to remove
        skills_to_remove = []
        for name in skill_map['skills']:
            if name not in installed_skills:
                skills_to_remove.append(name)
        
        if not skills_to_remove:
            return

        # Remove from 'skills'
        for name in skills_to_remove:
            del skill_map['skills'][name]
            print(f"Pruned '{name}' from skill_map.json")
            
        # Remove from 'detection_rules.priority_order'
        if 'detection_rules' in skill_map and 'priority_order' in skill_map['detection_rules']:
            original_order = skill_map['detection_rules']['priority_order']
            new_order = [s for s in original_order if s not in skills_to_remove]
            skill_map['detection_rules']['priority_order'] = new_order
            
        # Write back to file
        try:
            SKILL_MAP_FILE.write_text(json.dumps(skill_map, indent=2, ensure_ascii=False), encoding='utf-8', errors='strict')
            print(f"Updated skill_map.json (removed {len(skills_to_remove)} entries)")
        except UnicodeEncodeError as e:
            logger.error(f"Unicode encode error writing to {SKILL_MAP_FILE}: {e}")
            print(f"{RED}Error writing to skill_map.json due to encoding error: {e}{RESET}")
            
    except UnicodeDecodeError as e:
        logger.error(f"Unicode decode error reading {SKILL_MAP_FILE}: {e}")
        try:
            content = SKILL_MAP_FILE.read_text(encoding='utf-8', errors='replace')
            logger.warning(f"Retrying with errors='replace' for {SKILL_MAP_FILE}")
            skill_map = json.loads(content)
            # Continue with the prune logic...
            if 'skills' not in skill_map:
                return
            skills_to_remove = []
            for name in skill_map['skills']:
                if name not in installed_skills:
                    skills_to_remove.append(name)
            if not skills_to_remove:
                return
            for name in skills_to_remove:
                del skill_map['skills'][name]
                print(f"Pruned '{name}' from skill_map.json")
            if 'detection_rules' in skill_map and 'priority_order' in skill_map['detection_rules']:
                original_order = skill_map['detection_rules']['priority_order']
                new_order = [s for s in original_order if s not in skills_to_remove]
                skill_map['detection_rules']['priority_order'] = new_order
            try:
                SKILL_MAP_FILE.write_text(json.dumps(skill_map, indent=2, ensure_ascii=False), encoding='utf-8', errors='strict')
                print(f"Updated skill_map.json (removed {len(skills_to_remove)} entries)")
            except UnicodeEncodeError as e2:
                logger.error(f"Unicode encode error writing to {SKILL_MAP_FILE}: {e2}")
                print(f"{RED}Error writing to skill_map.json due to encoding error: {e2}{RESET}")
        except Exception as e2:
            logger.error(f"Failed to read {SKILL_MAP_FILE} even with errors='replace': {e2}")
            print(f"{RED}Error pruning skill_map.json: {e2}{RESET}")
    except Exception as e:
        logger.error(f"Error pruning skill_map.json: {e}")
        print(f"{RED}Error pruning skill_map.json: {e}{RESET}")

def scan_skills():
    """扫描所有已安装的 skills"""
    skills = {}
    
    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir() or skill_dir.name.startswith('.'):
            continue
        
        # Check for git repo to get version
        version = "unknown"
        source = "local"
        subdir = ""
        skill_name = skill_dir.name
        
        # 尝试从现有的 skills.json 获取信息（用于保留远程 skills 的版本信息）
        try:
            if REGISTRY_FILE.exists():
                content = REGISTRY_FILE.read_text(encoding='utf-8')
                existing = json.loads(content)
                if skill_name in existing.get('skills', {}):
                    existing_info = existing['skills'][skill_name]
                    source = existing_info.get('source', source)
                    subdir = existing_info.get('subdir', subdir)
                    version = existing_info.get('version', version)
        except UnicodeDecodeError as e:
            logger.error(f"Unicode decode error reading {REGISTRY_FILE}: {e}")
            try:
                content = REGISTRY_FILE.read_text(encoding='utf-8', errors='replace')
                logger.warning(f"Retrying with errors='replace' for {REGISTRY_FILE}")
                existing = json.loads(content)
                if skill_name in existing.get('skills', {}):
                    existing_info = existing['skills'][skill_name]
                    source = existing_info.get('source', source)
                    subdir = existing_info.get('subdir', subdir)
                    version = existing_info.get('version', version)
            except Exception as e2:
                logger.error(f"Failed to read {REGISTRY_FILE} even with errors='replace': {e2}")
        except Exception as e:
            logger.error(f"Error reading {REGISTRY_FILE}: {e}")
            
        # Try to update version from git if possible (and if it's a git repo)
        try:
            git_dir = skill_dir / '.git'
            if git_dir.exists():
                    # It's a git repo root
                    import subprocess
                    # Added errors='replace' for robustness against non-UTF8 output
                    result = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=skill_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors='replace')
                    if result.returncode == 0:
                        version = result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError, PermissionError, OSError):
            pass
        
        # Validate SKILL.md
        is_valid, validation_error = validate_skill_md(skill_dir)
        
        skills[skill_name] = {
            "source": source,
            "subdir": subdir,
            "version": version,
            "updated_at": datetime.datetime.now().isoformat(),
            "health": {
                "is_valid": is_valid,
                "validation_error": validation_error,
                "missing_deps": [],
                "satisfied_deps": []
            }
        }
    
    # Check dependencies after collecting all skill names
    installed_skills = set(skills.keys())
    for skill_name in skills:
        skill_path = SKILLS_DIR / skill_name
        missing_deps, satisfied_deps = check_skill_dependencies(skill_path, installed_skills)
        skills[skill_name]["health"]["missing_deps"] = missing_deps
        skills[skill_name]["health"]["satisfied_deps"] = satisfied_deps
    
    # 增加 Prune 逻辑：移除 skills.json 中存在但目录不存在的条目
    # 实际上，上面的循环只扫描了存在的目录，所以新的 skills 字典自然已经 pruned 了
    # 但如果 scan_skills 是为了 merge 而不是 overwrite，那就需要额外处理
    # 目前 sync_registry 直接用 scan_skills 的结果覆盖文件，所以 skills.json 也是自动 pruned 的
    
    return skills

def sync_registry():
    """同步 skills.json"""
    skills = scan_skills()
    
    # Sort logic: core skills first (in defined order), then alphabetical
    def sort_key(item):
        name = item[0]
        CORE_SKILLS = ['find-skills', 'skill-creator', 'skill-installer', 'skill-auditor']
        if name in CORE_SKILLS:
            return (0, CORE_SKILLS.index(name))
        return (1, name)
        
    sorted_skills = dict(sorted(skills.items(), key=sort_key))
    
    # 写入更新后的 skills.json
    try:
        with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
            json.dump({"skills": sorted_skills}, f, indent=2, ensure_ascii=False)
        
        print(MSG_SYNCED_SUCCESS.format(count=len(skills)))
        print(MSG_REGISTRY_FILE.format(path=REGISTRY_FILE))
    except UnicodeEncodeError as e:
        logger.error(f"Unicode encode error writing to {REGISTRY_FILE}: {e}")
        print(f"{RED}Error writing registry due to encoding error: {e}{RESET}")
        return False
    except Exception as e:
        logger.error(f"Error writing registry: {e}")
        print(f"{RED}Error writing registry: {e}{RESET}")
        return False
    
    # 列出所有 skills
    print(MSG_SKILLS_LIST)
    print(f"{'Name':<30} {'Source':<40} {'Version':<12}")
    print("-" * 85)
    for name, info in sorted_skills.items():
        source = info.get('source', 'unknown')
        version = info.get('version', 'unknown')[:7] if info.get('version') != 'unknown' else 'unknown'
        print(f"{name:<30} {source:<40} {version:<12}")
        
        # Update skill_map.json for each skill
        skill_path = SKILLS_DIR / name
        if skill_path.exists():
            update_skill_map(SKILLS_DIR, name, skill_path)

    # Prune skill_map.json
    prune_skill_map(set(sorted_skills.keys()))
    
    # Health validation
    print(MSG_VALIDATING_SKILLS)
    healthy_count = 0
    warning_count = 0
    error_count = 0
    skills_with_issues = []
    
    for name, info in sorted_skills.items():
        health = info.get('health', {})
        is_valid = health.get('is_valid', True)
        validation_error = health.get('validation_error', None)
        missing_deps = health.get('missing_deps', [])
        
        if not is_valid:
            print(MSG_SKILL_INVALID.format(name=name, error=validation_error))
            error_count += 1
            skills_with_issues.append((name, 'validation_error', validation_error))
        elif missing_deps:
            deps_str = ', '.join(missing_deps)
            print(MSG_DEPENDENCY_MISSING.format(name=name, deps=deps_str))
            warning_count += 1
            skills_with_issues.append((name, 'missing_deps', missing_deps))
        else:
            print(MSG_SKILL_VALID.format(name=name))
            healthy_count += 1
    
    # Health summary
    print(MSG_HEALTH_SUMMARY)
    print(MSG_HEALTH_SUMMARY_TITLE)
    print(MSG_HEALTH_TOTAL.format(count=len(skills)))
    print(MSG_HEALTH_HEALTHY.format(count=healthy_count))
    if warning_count > 0:
        print(MSG_HEALTH_WARNINGS.format(count=warning_count))
    if error_count > 0:
        print(MSG_HEALTH_ERRORS.format(count=error_count))
    
    # Display skills with issues
    if skills_with_issues:
        print(MSG_HEALTH_ISSUES_HEADER)
        for name, issue_type, issue_detail in skills_with_issues:
            if issue_type == 'validation_error':
                print(f"   {COLOR_YELLOW}{name}{COLOR_RESET}: {issue_detail}")
            elif issue_type == 'missing_deps':
                deps_str = ', '.join(issue_detail)
                print(f"   {COLOR_YELLOW}{name}{COLOR_RESET}: Missing dependencies: {deps_str}")
        
        # Recommendations
        print(MSG_HEALTH_RECOMMENDATIONS)
        if error_count > 0:
            print(MSG_HEALTH_RECOMMENDATION_FIX_MD)
        if warning_count > 0:
            print(MSG_HEALTH_RECOMMENDATION_INSTALL_DEPS)
    
    return True

def list_skills():
    """列出所有已安装的 skills"""
    skills = scan_skills()
    
    print(MSG_SKILLS_LIST)
    print(f"{'Name':<30} {'Source':<40} {'Version':<12}")
    print("-" * 85)
    for name, info in sorted(skills.items()):
        source = info.get('source', 'unknown')
        version = info.get('version', 'unknown')[:7] if info.get('version') != 'unknown' else 'unknown'
        print(f"{name:<30} {source:<40} {version:<12}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sync skills registry")
    parser.add_argument('command', nargs='?', default='sync', choices=['sync', 'list'], help='Command to run (sync or list)')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without writing')
    
    args = parser.parse_args()
    
    if args.command == 'list':
        list_skills()
    elif args.command == 'sync':
        if args.dry_run:
            skills = scan_skills()
            print(MSG_DRY_RUN.format(count=len(skills)))
            for name, info in sorted(skills.items()):
                print(f"  - {name}: {info.get('source', 'unknown')}")
        else:
            sync_registry()

if __name__ == "__main__":
    main()
