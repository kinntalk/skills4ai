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

SKILLS_DIR = Path(__file__).parent.parent.parent
REGISTRY_FILE = SKILLS_DIR / 'skills.json'

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
    
    return skills

def sync_registry():
    """同步 skills.json"""
    skills = scan_skills()
    
    # 写入更新后的 skills.json
    try:
        with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
            json.dump({"skills": skills}, f, indent=2, ensure_ascii=False)
        
        print(MSG_SYNCED_SUCCESS.format(count=len(skills)))
        print(MSG_REGISTRY_FILE.format(path=REGISTRY_FILE))
    except Exception as e:
        print(f"{RED}Error writing registry: {e}{RESET}")
        return False
    
    # 列出所有 skills
    print(MSG_SKILLS_LIST)
    print(f"{'Name':<30} {'Source':<40} {'Version':<12}")
    print("-" * 85)
    for name, info in sorted(skills.items()):
        source = info.get('source', 'unknown')
        version = info.get('version', 'unknown')[:7] if info.get('version') != 'unknown' else 'unknown'
        print(f"{name:<30} {source:<40} {version:<12}")
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
