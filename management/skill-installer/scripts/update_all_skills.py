#!/usr/bin/env python3
"""
Update All Skills - 自动更新所有已安装的 Trae skills
检查更新、备份、下载新版本、运行审计、更新注册表
"""

import sys
import json
import datetime
import subprocess
from pathlib import Path

try:
    from messages import *
except ImportError:
    try:
        sys.path.append(str(Path(__file__).parent))
        from messages import *
    except ImportError:
        # Fallback to simple ANSI colors if messages.py not available
        GREEN = "\033[92m"
        RED = "\033[91m"
        YELLOW = "\033[93m"
        BLUE = "\033[94m"
        CYAN = "\033[96m"
        RESET = "\033[0m"
        
        # Define simple icons as fallback
        ICON_OK = "[OK]"
        ICON_ERROR = "[X]"
        ICON_UPDATE = "[UPDATE]"
        ICON_WARN = "[!]"
        
        MSG_START_UPDATE = f"{BLUE}Starting skills update process{RESET}"
        MSG_PHASE_CHECK = f"{CYAN}Phase 1: Checking for updates...{RESET}"
        MSG_PHASE_UPDATE = f"{CYAN}Phase 2: Updating skills...{RESET}"
        MSG_NO_UPDATES = f"\n{GREEN}No updates available.{RESET}"
        MSG_FOUND_UPDATES = f"\n{CYAN}Found {{count}} skill(s) with updates:{RESET}"
        MSG_FORCE_HINT = f"\n{YELLOW}Use --force to proceed with updates{RESET}"
        MSG_UPDATE_SUMMARY = f"{BLUE}Update Summary{RESET}"
        MSG_TOTAL_CHECKED = f"Total skills checked: {{count}}"
        MSG_UPDATES_AVAILABLE_COUNT = f"Updates available: {{count}}"
        MSG_SUCCESS_COUNT = f"{GREEN}Successfully updated: {{count}}{RESET}"
        MSG_FAILED_COUNT = f"{RED}Failed to update: {{count}}{RESET}"

SKILLS_DIR = Path(__file__).parent.parent.parent
REGISTRY_FILE = SKILLS_DIR / 'skills.json'
LOG_FILE = SKILLS_DIR / 'skills_update.log'
BACKUPS_DIR = SKILLS_DIR / 'backups'

def log_message(message, end='\n', flush=False):
    """Log message to both console and log file"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Only prefix with timestamp for log file, keep console output clean
    log_entry = f"[{timestamp}] {message}"
    print(message, end=end, flush=flush)
    
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
    except Exception as e:
        print(f"{RED}Warning: Could not write to log file: {e}{RESET}")

def load_registry():
    if not REGISTRY_FILE.exists():
        return {}
    try:
        content = REGISTRY_FILE.read_text(encoding='utf-8')
        return json.loads(content).get('skills', {})
    except Exception as e:
        log_message(f"{RED}Error reading skills.json: {e}{RESET}")
        return {}

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
            stderr = e.stderr.decode('utf-8', errors='replace') if hasattr(e.stderr, 'decode') else e.stderr
            log_message(f"{RED}Command failed: {stderr}{RESET}")
        return False

def check_for_update(skill_name, info):
    """Check if a skill has an update available"""
    repo_url = info.get('source')
    current_version = info.get('version')
    
    if not repo_url or repo_url == 'local' or not current_version or current_version == 'unknown':
        return None, "Local skill or missing version info"
    
    log_message(f"Checking {skill_name}...", end='', flush=True)
    
    # Handle GITHUB_URL override for checks
    check_url = repo_url
    if "github.com" in repo_url:
        github_base = os.environ.get("GITHUB_URL", "").rstrip("/")
        if github_base and "github.com" not in github_base:
            check_url = repo_url.replace("https://github.com", github_base)

    # Check remote HEAD using git ls-remote
    remote_head = run_command(['git', 'ls-remote', check_url, 'HEAD'], capture_output=True)
    if remote_head:
        remote_hash = remote_head.split()[0]
        if remote_hash != current_version:
            log_message(f" {GREEN}Update available!{RESET} ({current_version[:7]} -> {remote_hash[:7]})")
            return remote_hash, None
        else:
            log_message(f" {GREEN}Up to date.{RESET}")
            return None, "Up to date"
    else:
        log_message(f" {RED}Failed to check remote.{RESET}")
        return None, "Failed to check remote"

def backup_skill(skill_name):
    """Backup a skill to backups directory"""
    skill_path = SKILLS_DIR / skill_name
    if not skill_path.exists():
        return None
    
    # Create backups directory if it doesn't exist
    BACKUPS_DIR.mkdir(exist_ok=True)
    
    # Create timestamped backup
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUPS_DIR / skill_name / timestamp
    
    try:
        import shutil
        shutil.copytree(skill_path, backup_path)
        log_message(f"{YELLOW}Backed up {skill_name} to {backup_path}{RESET}")
        return backup_path
    except Exception as e:
        log_message(f"{RED}Error backing up {skill_name}: {e}{RESET}")
        return None

def update_skill(skill_name, info, remote_hash, force=False):
    """Update a single skill"""
    repo_url = info.get('source')
    subdir = info.get('subdir', '')
    
    # Backup current version
    backup_path = backup_skill(skill_name)
    
    # Install new version
    log_message(f"{CYAN}Updating {skill_name}...{RESET}")
    
    # Import install_skill function
    current_dir = Path(__file__).parent
    sys.path.append(str(current_dir))
    try:
        from install_skill import install_skill
    except ImportError:
        log_message(f"{RED}Error: Could not import install_skill.py{RESET}")
        return False
    
    # Construct install source
    install_source = repo_url
    if subdir:
        if "github.com" in repo_url:
            clean_url = repo_url.rstrip('.git')
            if '/tree/' not in clean_url:
                clean_url = clean_url.replace("https://github.com/", "")
                install_source = f"{clean_url}/{subdir}"
        else:
            install_source = f"{repo_url}/{subdir}"
    
    # Install new version
    success = install_skill(install_source, SKILLS_DIR, run_audit=True, force=force)
    
    if success:
        log_message(f"{GREEN}{ICON_OK} Successfully updated {skill_name}{RESET}")
        return True
    else:
        log_message(f"{RED}{ICON_ERROR} Failed to update {skill_name}{RESET}")
        # Restore backup if available
        if backup_path and backup_path.exists():
            try:
                import shutil
                skill_path = SKILLS_DIR / skill_name
                if skill_path.exists():
                    shutil.rmtree(skill_path)
                shutil.copytree(backup_path, skill_path)
                log_message(f"{GREEN}{ICON_OK} Restored backup for {skill_name}{RESET}")
            except Exception as e:
                log_message(f"{RED}{ICON_ERROR} Error restoring backup: {e}{RESET}")
        return False

def cleanup_old_backups(skill_name, keep=5):
    """Clean up old backups, keeping only the most recent N versions"""
    backup_dir = BACKUPS_DIR / skill_name
    if not backup_dir.exists():
        return
    
    try:
        backups = sorted(backup_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
        old_backups = backups[keep:]
        
        for old_backup in old_backups:
            try:
                import shutil
                shutil.rmtree(old_backup)
                log_message(f"{YELLOW}Removed old backup: {old_backup}{RESET}")
            except Exception as e:
                log_message(f"{RED}Error removing old backup {old_backup}: {e}{RESET}")
    except Exception as e:
        log_message(f"{RED}Error cleaning up backups: {e}{RESET}")

def update_all_skills(force=False):
    """Update all skills that have updates available"""
    log_message(f"{BLUE}{'='*60}{RESET}")
    log_message(MSG_START_UPDATE)
    log_message(f"{BLUE}{'='*60}{RESET}\n")
    
    skills = load_registry()
    if not skills:
        log_message("No skills found in registry.")
        return
    
    # Check for updates
    log_message(MSG_PHASE_CHECK)
    log_message(f"{'-'*60}")
    
    updates = []
    for skill_name, info in skills.items():
        remote_hash, error = check_for_update(skill_name, info)
        if remote_hash:
            updates.append((skill_name, info, remote_hash))
    
    if not updates:
        log_message(MSG_NO_UPDATES)
        return
    
    log_message(MSG_FOUND_UPDATES.format(count=len(updates)))
    for skill_name, info, remote_hash in updates:
        log_message(f"  - {skill_name}: {info.get('version', 'unknown')[:7]} -> {remote_hash[:7]}")
    
    if not force:
        log_message(MSG_FORCE_HINT)
        return
    
    # Update skills
    log_message(MSG_PHASE_UPDATE)
    log_message(f"{'-'*60}")
    
    success_count = 0
    failed_count = 0
    
    for skill_name, info, remote_hash in updates:
        if update_skill(skill_name, info, remote_hash, force=force):
            success_count += 1
            # Clean up old backups
            cleanup_old_backups(skill_name, keep=5)
        else:
            failed_count += 1
    
    # Summary
    log_message(f"\n{BLUE}{'='*60}{RESET}")
    log_message(MSG_UPDATE_SUMMARY)
    log_message(f"{BLUE}{'='*60}{RESET}")
    log_message(MSG_TOTAL_CHECKED.format(count=len(skills)))
    log_message(MSG_UPDATES_AVAILABLE_COUNT.format(count=len(updates)))
    log_message(MSG_SUCCESS_COUNT.format(count=success_count))
    if failed_count > 0:
        log_message(MSG_FAILED_COUNT.format(count=failed_count))
    log_message(f"Log file: {LOG_FILE}")
    log_message(f"Backups directory: {BACKUPS_DIR}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Update all Trae skills")
    parser.add_argument('--force', '-f', action='store_true', help='Force update without confirmation')
    parser.add_argument('--check-only', '-c', action='store_true', help='Only check for updates, do not update')
    
    args = parser.parse_args()
    
    if args.check_only:
        # Only check for updates
        log_message(f"{BLUE}{'='*60}{RESET}")
        log_message(f"{BLUE}Checking for skills updates...{RESET}")
        log_message(f"{BLUE}{'='*60}{RESET}\n")
        
        skills = load_registry()
        if not skills:
            log_message("No skills found in registry.")
            return
        
        updates = []
        for skill_name, info in skills.items():
            remote_hash, error = check_for_update(skill_name, info)
            if remote_hash:
                updates.append((skill_name, info, remote_hash))
        
        if not updates:
            log_message(MSG_NO_UPDATES)
        else:
            log_message(MSG_FOUND_UPDATES.format(count=len(updates)))
            for skill_name, info, remote_hash in updates:
                log_message(f"  - {skill_name}: {info.get('version', 'unknown')[:7]} -> {remote_hash[:7]}")
            log_message(MSG_FORCE_HINT)
    else:
        # Update all skills
        update_all_skills(force=args.force)

if __name__ == "__main__":
    main()
