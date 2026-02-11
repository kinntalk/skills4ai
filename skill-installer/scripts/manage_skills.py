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
        CYAN = "\033[96m"
        RESET = "\033[0m"
        MSG_COMMAND_FAILED = f"{RED}Command failed: {{error}}{RESET}"
        MSG_NO_SKILLS_REGISTRY = "No skills found in registry."

SKILLS_DIR = Path(__file__).parent.parent.parent
REGISTRY_FILE = SKILLS_DIR / 'skills.json'

def run_command(cmd, cwd=None, capture_output=False):
    """Run a shell command and check for errors"""
    try:
        if capture_output:
            # Removed errors='replace' to avoid TypeError in older python versions if check is strict, 
            # but usually run_command in manage_skills was copy-pasted. 
            # Assuming standard subprocess usage.
            result = subprocess.run(cmd, check=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors='replace')
            return result.stdout.strip()
        else:
            subprocess.run(cmd, check=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
    except subprocess.CalledProcessError as e:
        if not capture_output:
            print(MSG_COMMAND_FAILED.format(error=e))
        return False

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
        print(MSG_NO_SKILLS_REGISTRY)
        return

    print(MSG_INSTALLED_HEADER)
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
        print(MSG_NO_SKILLS_REGISTRY)
        return

    print(MSG_CHECKING_UPDATES)
    updates_available = []
    
    for name, info in skills.items():
        repo_url = info.get('source')
        current_version = info.get('version')
        
        if not repo_url or not current_version or current_version == 'unknown':
            print(MSG_SKIPPING_SKILL.format(name=name))
            continue

        # Handle GITHUB_URL override for checks
        check_url = repo_url
        if "github.com" in repo_url:
            github_base = os.environ.get("GITHUB_URL", "").rstrip("/")
            if github_base and "github.com" not in github_base:
                # Replace https://github.com with mirror base
                check_url = repo_url.replace("https://github.com", github_base)

        print(MSG_CHECKING_SKILL.format(name=name), end='', flush=True)
        
        # Check remote HEAD using git ls-remote
        remote_head = run_command(['git', 'ls-remote', check_url, 'HEAD'], capture_output=True)
        if remote_head:
            remote_hash = remote_head.split()[0]
            if remote_hash != current_version:
                print(MSG_UPDATE_AVAILABLE.format(current=current_version[:7], remote=remote_hash[:7]))
                updates_available.append(name)
            else:
                print(MSG_UP_TO_DATE)
        else:
            print(MSG_CHECK_FAILED)
            
    if updates_available:
        skills_str = ", ".join(updates_available)
        print(MSG_UPDATES_FOUND.format(skills=skills_str))
        print(MSG_RUN_UPDATE_HINT)
    else:
        print(MSG_ALL_UP_TO_DATE)

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
                print(MSG_DELETE_LOCKED.format(path=path))
                return False
        except Exception as e:
            print(MSG_DELETE_ERROR.format(path=path, error=e))
            return False
    return False

def update_skill(name, force=False):
    skills = load_registry()
    if name not in skills:
        print(MSG_SKILL_NOT_FOUND.format(name=name))
        return

    info = skills[name]
    repo_url = info.get('source')
    subdir = info.get('subdir', '')
    
    if not repo_url or repo_url == 'local':
        print(MSG_SKILL_LOCAL.format(name=name))
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
    
    print(MSG_UPDATING_FROM.format(name=name, source=install_source))
    
    # Backup existing skill before update
    backup_path = SKILLS_DIR / f"{name}-backup"
    skill_path = SKILLS_DIR / name
    
    if skill_path.exists():
        if backup_path.exists():
            safe_rmtree(backup_path)
        
        try:
            skill_path.rename(backup_path)
            print(MSG_BACKUP_CREATED.format(path=backup_path))
        except Exception as e:
            print(MSG_BACKUP_ERROR.format(error=e))
            return
    
    # Install the updated skill
    # Pass force parameter to avoid interactive prompts
    success = install_skill(install_source, SKILLS_DIR, run_audit=True, force=force)
    
    if success:
        print(MSG_UPDATE_SUCCESS.format(name=name))
        # Clean up backup
        if backup_path.exists():
            safe_rmtree(backup_path)
            print(MSG_BACKUP_REMOVED)
    else:
        print(MSG_UPDATE_FAILED.format(name=name))
        if backup_path.exists():
            if skill_path.exists():
                safe_rmtree(skill_path)
            
            try:
                backup_path.rename(skill_path)
                print(MSG_RESTORE_SUCCESS)
            except Exception as e:
                print(MSG_RESTORE_FAILED.format(path=backup_path))

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
