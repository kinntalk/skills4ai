#!/usr/bin/env python3
"""
Skill Installer - Install skills from remote git repositories.
Supports GitHub URLs and subdirectories (e.g., vercel-labs/agent-skills/skill-name).
"""

import sys
import os
import argparse
import subprocess
import shutil
import tempfile
import time
import json
import datetime
from pathlib import Path

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def run_command(cmd, cwd=None, capture_output=False):
    """Run a shell command and check for errors"""
    try:
        if capture_output:
            result = subprocess.run(cmd, check=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors='replace')
            return result.stdout.strip()
        else:
            subprocess.run(cmd, check=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
    except subprocess.CalledProcessError as e:
        if not capture_output:
            print(f"{RED}Command failed: {e}{RESET}")
            stderr = e.stderr.decode('utf-8', errors='replace') if hasattr(e.stderr, 'decode') else e.stderr
            print(f"Stderr: {stderr}")
        return False

def update_registry(dest_root, skill_name, repo_url, subdir, commit_hash):
    """Update the skills.json registry file"""
    registry_path = dest_root / 'skills.json'
    registry = {'skills': {}}
    
    if registry_path.exists():
        try:
            content = registry_path.read_text(encoding='utf-8')
            registry = json.loads(content)
        except Exception as e:
            print(f"{YELLOW}Warning: Could not read existing skills.json: {e}. Creating new one.{RESET}")

    registry['skills'][skill_name] = {
        'source': repo_url,
        'subdir': subdir,
        'version': commit_hash,
        'updated_at': datetime.datetime.now().isoformat()
    }
    
    try:
        registry_path.write_text(json.dumps(registry, indent=2), encoding='utf-8')
        print(f"📝 Updated skills registry at {registry_path}")
    except Exception as e:
        print(f"{RED}Error writing to skills.json: {e}{RESET}")

def parse_source(source):
    """
    Parse the source string into repo_url and subdir.
    Examples:
      - https://github.com/user/repo -> (url, "")
      - https://github.com/user/repo/tree/main/subdir -> (url, "subdir")
      - user/repo -> (https://github.com/user/repo.git, "")
      - user/repo/subdir -> (https://github.com/user/repo.git, "subdir")
    """
    subdir = ""
    
    if source.startswith("https://") or source.startswith("git@"):
        # Full URL
        parts = source.split('/tree/main/') # Simple heuristic for GitHub
        if len(parts) > 1:
            return parts[0], parts[1]
        return source, ""
        
    # Short format: user/repo or user/repo/subdir
    parts = source.split('/')
    if len(parts) >= 2:
        github_base = os.environ.get("GITHUB_URL", "https://github.com").rstrip("/")
        repo_url = f"{github_base}/{parts[0]}/{parts[1]}.git"
        if len(parts) > 2:
            subdir = "/".join(parts[2:])
        return repo_url, subdir
        
    return source, ""

def install_skill(source, dest_root, run_audit=True, force=False):
    dest_root = Path(dest_root)
    repo_url, subdir = parse_source(source)
    
    print(f"📦 Installing from: {repo_url}")
    if subdir:
        print(f"   Subdirectory: {subdir}")
    print(f"   To: {dest_root}")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Clone repo
        print(f"⬇️  Cloning repository...")
        max_retries = 3
        for attempt in range(max_retries):
            if run_command(['git', 'clone', '--depth', '1', repo_url, '.'], cwd=temp_path):
                break
            print(f"{YELLOW}Retry {attempt + 1}/{max_retries}...{RESET}")
            time.sleep(2 ** attempt)
        else:
            print(f"{RED}Failed to clone repository after {max_retries} attempts.{RESET}")
            return False
            
        # Get commit hash
        commit_hash = run_command(['git', 'rev-parse', 'HEAD'], cwd=temp_path, capture_output=True)
        if not commit_hash:
            commit_hash = "unknown"
        print(f"   Version: {commit_hash[:7]}")

        # Determine source path
        source_path = temp_path
        if subdir:
            source_path = temp_path / subdir
            
        if not source_path.exists():
            # Try to find subdir with common prefixes if not found
            common_prefixes = ['skills', 'packages', 'apps']
            found = False
            for prefix in common_prefixes:
                alt_path = temp_path / prefix / subdir.split('/')[-1]
                if alt_path.exists():
                    print(f"{YELLOW}Warning: Subdirectory '{subdir}' not found. Found at '{prefix}/{subdir.split('/')[-1]}' instead.{RESET}")
                    source_path = alt_path
                    subdir = f"{prefix}/{subdir.split('/')[-1]}"
                    found = True
                    break
            
            if not found and not source_path.exists():
                print(f"{RED}Error: Subdirectory '{subdir}' not found in repository.{RESET}")
                return False
            
        # Determine skill name (from subdir name or repo name)
        if subdir:
            skill_name = Path(subdir).name
        else:
            # Extract from repo URL: https://github.com/user/repo.git -> repo
            skill_name = repo_url.rstrip('/').split('/')[-1]
            if skill_name.endswith('.git'):
                skill_name = skill_name[:-4]

        dest_path = dest_root / skill_name
        
        if dest_path.exists():
            print(f"{YELLOW}Warning: Destination '{dest_path}' already exists.{RESET}")
            if force:
                print(f"{YELLOW}Force mode enabled. Overwriting...{RESET}")
                shutil.rmtree(dest_path)
            else:
                overwrite = input("Overwrite? (y/N): ").lower()
                if overwrite != 'y':
                    print("Installation aborted.")
                    return False
                shutil.rmtree(dest_path)
            
        # Move files
        shutil.copytree(source_path, dest_path)
        print(f"{GREEN}✅ Installed '{skill_name}' to {dest_path}{RESET}")
        
        # Update Registry
        update_registry(dest_root, skill_name, repo_url, subdir, commit_hash)

        # Run Audit
        if run_audit:
            audit_script = Path(__file__).parent.parent.parent / 'skill-auditor' / 'scripts' / 'audit_skill.py'
            if audit_script.exists():
                print(f"\n🔍 Running skill-auditor...")
                try:
                    subprocess.run([sys.executable, str(audit_script), str(dest_path)], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"{YELLOW}Warning: Audit failed: {e}{RESET}")
            else:
                print(f"{YELLOW}Warning: skill-auditor not found. Skipping audit.{RESET}")
                
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Install Trae skills from git repositories")
    parser.add_argument("source", help="Git URL or 'user/repo/subdir' string")
    parser.add_argument("--path", default=".trae/skills", help="Destination directory (default: .trae/skills)")
    parser.add_argument("--no-audit", action="store_true", help="Skip running skill-auditor after install")
    parser.add_argument("--force", action="store_true", help="Force overwrite without prompting")
    
    args = parser.parse_args()
    
    success = install_skill(args.source, args.path, not args.no_audit, args.force)
    sys.exit(0 if success else 1)
