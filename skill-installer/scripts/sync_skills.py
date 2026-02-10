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

SKILLS_DIR = Path(__file__).parent.parent.parent
REGISTRY_FILE = SKILLS_DIR / 'skills.json'

def scan_skills():
    """扫描所有已安装的 skills"""
    skills = {}
    
    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir() or skill_dir.name.startswith('.'):
            continue
        
        skill_md = skill_dir / 'SKILL.md'
        if not skill_md.exists():
            continue
        
        skill_name = skill_dir.name
        
        # 从 SKILL.md 读取元数据
        source = "unknown"
        subdir = ""
        version = "unknown"
        
        try:
            content = skill_md.read_text(encoding='utf-8')
            # 尝试从 SKILL.md 提取 source 信息
            if 'source:' in content.lower():
                for line in content.split('\n'):
                    if 'source:' in line.lower():
                        source = line.split(':', 1)[1].strip()
                        break
        except Exception:
            pass
        
        # 检查是否是子目录 skill
        if skill_dir.name in ['find-skills', 'skill-creator', 'pdf-generation', 'image-generation', 'skill-auditor', 'skill-installer']:
            # 这些是远程安装的 skills，尝试从 skills.json 获取信息
            try:
                with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
                    if skill_name in existing.get('skills', {}):
                        existing_info = existing['skills'][skill_name]
                        source = existing_info.get('source', 'unknown')
                        subdir = existing_info.get('subdir', '')
                        version = existing_info.get('version', 'unknown')
            except Exception:
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
    
    # 读取现有的 skills.json 以保留远程 skills 的版本信息
    try:
        with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
            existing = json.load(f)
            existing_skills = existing.get('skills', {})
            
            # 保留远程 skills 的版本信息
            for skill_name in skills:
                if skill_name in existing_skills:
                    existing_info = existing_skills[skill_name]
                    if existing_info.get('source') != 'local':
                        # 保留远程 skill 的版本信息
                        skills[skill_name]['version'] = existing_info.get('version', 'unknown')
                        skills[skill_name]['source'] = existing_info.get('source', 'unknown')
                        skills[skill_name]['subdir'] = existing_info.get('subdir', '')
    except Exception as e:
        print(f"Warning: Could not read existing registry: {e}")
    
    # 写入更新后的 skills.json
    with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
        json.dump({"skills": skills}, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Synced {len(skills)} skills to registry")
    print(f"   Registry file: {REGISTRY_FILE}")
    
    # 列出所有 skills
    print(f"\n📋 Skills List:")
    print(f"{'Name':<30} {'Source':<40} {'Version':<12}")
    print("-" * 85)
    for name, info in sorted(skills.items()):
        source = info.get('source', 'unknown')
        version = info.get('version', 'unknown')[:7] if info.get('version') != 'unknown' else 'unknown'
        print(f"{name:<30} {source:<40} {version:<12}")

def list_skills():
    """列出所有已安装的 skills"""
    skills = scan_skills()
    
    print(f"\n📋 Installed Skills:")
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
            print(f"🔍 Dry run: Would sync {len(skills)} skills")
            for name, info in sorted(skills.items()):
                print(f"  - {name}: {info.get('source', 'unknown')}")
        else:
            sync_registry()

if __name__ == "__main__":
    main()
