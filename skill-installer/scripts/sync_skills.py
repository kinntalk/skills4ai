#!/usr/bin/env python3
"""
Skills Sync - 自动扫描并同步 skills.json
自动扫描 .trae/skills/ 目录下的所有 skills 并更新 skills.json
"""

import sys
import os
import json
import datetime
from pathlib import Path

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
        RESET = "\033[0m"
        MSG_SYNCED_SUCCESS = f"{GREEN}Synced {{count}} skills to registry{RESET}"
        MSG_REGISTRY_FILE = f"   Registry file: {{path}}"
        MSG_SKILLS_LIST = f"\nSkills List:"
        MSG_DRY_RUN = f"Dry run: Would sync {{count}} skills"

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
        SKILL_MAP_FILE.write_text(json.dumps(skill_map, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"Updated skill_map.json (removed {len(skills_to_remove)} entries)")
            
    except Exception as e:
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
        except Exception:
            pass
            
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
        except:
            pass
        
        skills[skill_name] = {
            "source": source,
            "subdir": subdir,
            "version": version,
            "updated_at": datetime.datetime.now().isoformat()
        }
    
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
    except Exception as e:
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
