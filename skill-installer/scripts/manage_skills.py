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

        # Handle GITHUB_URL override for checks
        check_url = repo_url
        if "github.com" in repo_url:
            github_base = os.environ.get("GITHUB_URL", "").rstrip("/")
            if github_base and "github.com" not in github_base:
                # Replace https://github.com with mirror base
                check_url = repo_url.replace("https://github.com", github_base)

        print(f"Checking {name}...", end='', flush=True)
        
        # Check remote HEAD using git ls-remote
        remote_head = run_command(['git', 'ls-remote', check_url, 'HEAD'], capture_output=True)
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
    # Simplified logic: Use the stored repo_url directly, or combine with subdir if needed.
    # install_skill.py handles full URLs and GITHUB_URL env var correctly.
    
    install_source = repo_url
    
    # If we have a subdir and the URL doesn't already point to it (simplistic check)
    # Actually, install_skill expects "url" and "subdir" separately logic OR "url/subdir" string
    # But parse_source in install_skill splits by space or tries to guess.
    # Best way is to reconstruct the "user/repo/subdir" format IF it was a github URL,
    # OR just pass the full URL and let install_skill handle it?
    # install_skill(source, ...) calls parse_source(source).
    
    # Let's try to be smart but robust.
    # If it's a standard GitHub URL, we can rely on install_skill's env var logic if we pass the full URL.
    # But install_skill's parse_source logic for full URLs is:
    # if source.startswith("https://"): return source, ""
    # Unless it has /tree/main/
    
    # So if we have a subdir, we MUST provide it in a way parse_source understands.
    # Option A: "https://github.com/user/repo/tree/main/subdir"
    # Option B: "user/repo/subdir"
    
    if subdir:
        if "github.com" in repo_url and not "tree" in repo_url:
             # Try to construct tree URL which install_skill parses correctly
             if repo_url.endswith(".git"):
                 install_source = f"{repo_url[:-4]}/tree/main/{subdir}"
             else:
                 install_source = f"{repo_url}/tree/main/{subdir}"
        else:
             # Fallback for non-github or already complex URLs
             # This might fail if install_skill doesn't support "URL/subdir" pattern for custom git
             # But install_skill only supports subdir for:
             # 1. /tree/main/ (GitHub specific)
             # 2. user/repo/subdir (GitHub specific short form)
             
             # If we are using a mirror, the short form "user/repo" logic in install_skill 
             # uses GITHUB_URL env var. So converting back to short form is actually SAFEST
             # if we want to respect the env var dynamically!
             
             if "github.com" in repo_url:
                 # Extract user/repo
                 # https://github.com/user/repo.git -> user/repo
                 try:
                     parts = repo_url.rstrip('/').split('/')
                     if parts[-1].endswith('.git'):
                         repo_name = parts[-1][:-4]
                     else:
                         repo_name = parts[-1]
                     user_name = parts[-2]
                     install_source = f"{user_name}/{repo_name}/{subdir}"
                 except:
                     # Fallback
                     install_source = f"{repo_url} --subdir {subdir}" # Hypothetical, but install_skill doesn't support flags in source string
                     # Actually, let's just use the tree format, it's safer for the parser
                     install_source = f"{repo_url}/tree/main/{subdir}"
    
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
