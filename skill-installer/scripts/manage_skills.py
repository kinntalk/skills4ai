#!/usr/bin/env python3
"""
Skill Manager - Manage installed Trae skills
Supports listing, checking for updates, and updating skills.
"""

import sys
import os
import argparse
import json
import subprocess
import tempfile
from pathlib import Path

# Import install_skill to reuse installation logic
# Assuming manage_skills.py is in the same directory as install_skill.py
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))
try:
    from install_skill import install_skill, run_command
except ImportError:
    print("Error: Could not import install_skill.py. Make sure it is in the same directory.")
    sys.exit(1)

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

SKILLS_DIR = Path(__file__).parent.parent.parent
REGISTRY_FILE = SKILLS_DIR / 'skills.json'

def load_registry():
    if not REGISTRY_FILE.exists():
        return {}
    try:
        content = REGISTRY_FILE.read_text(encoding='utf-8')
        return json.loads(content).get('skills', {})
    except Exception as e:
        print(f"{RED}Error reading skills.json: {e}{RESET}")
        return {}

def list_skills():
    skills = load_registry()
    if not skills:
        print("No skills found in registry (skills.json).")
        return

    print(f"\n{BLUE}Installed Skills:{RESET}")
    print(f"{'Name':<25} {'Version':<10} {'Source'}")
    print("-" * 60)
    for name, info in skills.items():
        version = info.get('version', 'unknown')[:7]
        source = info.get('source', 'unknown')
        print(f"{name:<25} {version:<10} {source}")
    print()

def check_updates():
    skills = load_registry()
    if not skills:
        print("No skills found in registry.")
        return

    print(f"\n{BLUE}Checking for updates...{RESET}")
    updates_available = []

    for name, info in skills.items():
        repo_url = info.get('source')
        current_version = info.get('version')
        
        if not repo_url or not current_version or current_version == 'unknown':
            print(f"{YELLOW}Skipping {name}: Missing source or version info.{RESET}")
            continue

        print(f"Checking {name}...", end='', flush=True)
        
        # Check remote HEAD using git ls-remote
        remote_head = run_command(['git', 'ls-remote', repo_url, 'HEAD'], capture_output=True, errors='replace')
        if remote_head:
            remote_hash = remote_head.split()[0]
            if remote_hash != current_version:
                print(f" {GREEN}Update available!{RESET} ({current_version[:7]} -> {remote_hash[:7]})")
                updates_available.append(name)
            else:
                print(f" {GREEN}Up to date.{RESET}")
        else:
            print(f" {RED}Failed to check remote.{RESET}")

    if updates_available:
        print(f"\n{YELLOW}Updates available for: {', '.join(updates_available)}{RESET}")
        print(f"Run 'python manage_skills.py update <name>' to update.")
    else:
        print(f"\n{GREEN}All skills are up to date.{RESET}")

import shutil
import time

def safe_rmtree(path, retries=5, delay=0.5):
    """
    Safely remove a directory tree with retries for Windows file locking issues.
    """
    path = Path(path)
    if not path.exists():
        return True
        
    for i in range(retries):
        try:
            shutil.rmtree(path)
            return True
        except PermissionError:
            if i < retries - 1:
                time.sleep(delay)
            else:
                print(f"{RED}Error: Could not delete {path}. Is it in use?{RESET}")
                return False
        except Exception as e:
            print(f"{RED}Error deleting {path}: {e}{RESET}")
            return False
    return False

def update_skill(name, force=False):
    skills = load_registry()
    if name not in skills:
        print(f"{RED}Error: Skill '{name}' not found in registry.{RESET}")
        return

    info = skills[name]
    repo_url = info.get('source')
    subdir = info.get('subdir', '')
    
    if not repo_url or repo_url == 'local':
        print(f"{YELLOW}Skipping {name}: Local skill or no source URL.{RESET}")
        return
    
    # Construct install source string
    # Handle different URL formats:
    # 1. Full GitHub URL: https://github.com/user/repo.git
    # 2. Full GitHub URL without .git: https://github.com/user/repo
    # 3. Short format: user/repo
    # 4. With subdir: user/repo/subdir or https://github.com/user/repo/tree/main/subdir
    install_source = repo_url
    
    if subdir:
        # If we have a subdir, construct the appropriate source string
        if "github.com" in repo_url:
            # Remove .git suffix if present
            clean_url = repo_url.rstrip('.git')
            # Check if it's already a tree URL
            if '/tree/' in clean_url:
                install_source = clean_url
            else:
                # Construct: user/repo/subdir format for install_skill
                clean_url = clean_url.replace("https://github.com/", "")
                install_source = f"{clean_url}/{subdir}"
        else:
            # Non-GitHub URL with subdir
            install_source = f"{repo_url}/{subdir}"
    
    print(f"Updating {name} from: {install_source}")
    
    # Backup existing skill before update
    backup_path = SKILLS_DIR / f"{name}-backup"
    skill_path = SKILLS_DIR / name
    
    if skill_path.exists():
        if backup_path.exists():
            safe_rmtree(backup_path)
        
        try:
            skill_path.rename(backup_path)
            print(f"{YELLOW}Backed up existing skill to {backup_path}{RESET}")
        except Exception as e:
            print(f"{RED}Error backing up skill: {e}{RESET}")
            return
    
    # Install the updated skill
    # Pass force parameter to avoid interactive prompts
    success = install_skill(install_source, SKILLS_DIR, run_audit=True, force=force)
    
    if success:
        print(f"{GREEN}Successfully updated {name}.{RESET}")
        # Clean up backup
        if backup_path.exists():
            safe_rmtree(backup_path)
            print(f"{GREEN}Removed backup.{RESET}")
    else:
        print(f"{RED}Failed to update {name}. Restoring backup...{RESET}")
        if backup_path.exists():
            if skill_path.exists():
                safe_rmtree(skill_path)
            
            try:
                backup_path.rename(skill_path)
                print(f"{GREEN}Restored previous version.{RESET}")
            except Exception as e:
                print(f"{RED}Critical Error: Failed to restore backup! Manual intervention required at {backup_path}{RESET}")

def main():
    parser = argparse.ArgumentParser(description="Manage Trae skills")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    subparsers.add_parser('list', help='List installed skills')
    subparsers.add_parser('check', help='Check for updates')
    
    update_parser = subparsers.add_parser('update', help='Update a skill')
    update_parser.add_argument('name', help='Name of the skill to update')
    update_parser.add_argument('--force', '-f', action='store_true', help='Force update without confirmation')
    
    subparsers.add_parser('update-all', help='Update all skills')

    args = parser.parse_args()

    if args.command == 'list':
        list_skills()
    elif args.command == 'check':
        check_updates()
    elif args.command == 'update':
        force = getattr(args, 'force', False)
        update_skill(args.name, force=force)
    elif args.command == 'update-all':
        skills = load_registry()
        for name in skills:
            update_skill(name, force=False)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
