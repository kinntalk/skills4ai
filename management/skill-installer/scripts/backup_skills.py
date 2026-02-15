#!/usr/bin/env python3
"""
Backup Skills - 备份所有已安装的 Trae skills
创建时间戳备份，压缩为 zip 文件，存储在 .trae/skills/backups/
"""

import sys
import json
import datetime
import zipfile
import shutil
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
        MSG_BACKING_UP = f"{CYAN}Backing up {{name}}...{RESET}"
        MSG_BACKING_UP_ALL = f"{CYAN}Backing up all skills...{RESET}"
        MSG_BACKUP_SUCCESS = f"{GREEN}Backed up {{name}} to {{path}}{RESET}"
        MSG_BACKUP_ALL_SUCCESS = f"{GREEN}Backed up all skills to {{path}}{RESET}"
        MSG_BACKUP_SIZE = f"Backup size: {{size:.2f}} MB"
        MSG_NO_BACKUPS = "No backups found."
        MSG_AVAILABLE_BACKUPS = f"\n{BLUE}Available Backups:{RESET}"
        MSG_RESTORING = f"{CYAN}Restoring from {{name}}...{RESET}"
        MSG_RESTORE_CANCELLED = "Restore cancelled."
        MSG_RESTORE_CONFIRM = "This will overwrite existing skills. Continue? (y/N): "
        MSG_RESTORE_SKILL_EXISTS = f"Skill '{{name}}' already exists. Overwrite? (y/N): "
        MSG_RESTORED_SINGLE = f"{GREEN}Restored {{name}}{RESET}"
        MSG_RESTORED_ALL = f"{GREEN}Restored all skills{RESET}"
        MSG_CLEANING_BACKUPS = f"{CYAN}Cleaning up old backups (keeping {{keep}} most recent)...{RESET}"
        MSG_REMOVED_BACKUP = f"{GREEN}Removed: {{name}}{RESET}"

SKILLS_DIR = Path(__file__).parent.parent.parent
REGISTRY_FILE = SKILLS_DIR / 'skills.json'
BACKUPS_DIR = SKILLS_DIR / 'backups'

def load_registry():
    if not REGISTRY_FILE.exists():
        return {}
    try:
        content = REGISTRY_FILE.read_text(encoding='utf-8')
        return json.loads(content).get('skills', {})
    except Exception as e:
        print(f"{RED}Error reading skills.json: {e}{RESET}")
        return {}

def create_backup(skill_name=None, output_dir=None):
    """
    Create a backup of skills.
    
    Args:
        skill_name: Name of specific skill to backup, or None to backup all skills
        output_dir: Custom output directory, or None to use default BACKUPS_DIR
    
    Returns:
        Path to backup file, or None if failed
    """
    # Determine backup directory
    if output_dir:
        backup_dir = Path(output_dir)
    else:
        backup_dir = BACKUPS_DIR
    
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Create timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if skill_name:
        # Backup single skill
        skill_path = SKILLS_DIR / skill_name
        if not skill_path.exists():
            print(f"{RED}Error: Skill '{skill_name}' not found.{RESET}")
            return None
        
        backup_filename = f"{skill_name}_{timestamp}.zip"
        backup_path = backup_dir / backup_filename
        
        print(MSG_BACKING_UP.format(name=skill_name))
        
        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in skill_path.rglob('*'):
                    if '__pycache__' in file_path.parts or file_path.suffix == '.pyc':
                        continue
                    
                    if file_path.is_file():
                        arcname = file_path.relative_to(skill_path)
                        zipf.write(file_path, arcname)
            
            print(MSG_BACKUP_SUCCESS.format(name=skill_name, path=backup_path))
            return backup_path
        except Exception as e:
            print(f"{RED}Error backing up {skill_name}: {e}{RESET}")
            return None
    else:
        # Backup all skills
        skills = load_registry()
        if not skills:
            print("No skills found in registry.")
            return None
        
        backup_filename = f"all_skills_{timestamp}.zip"
        backup_path = backup_dir / backup_filename
        
        print(MSG_BACKING_UP_ALL)
        print(f"Total skills: {len(skills)}")
        
        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for skill_name in skills.keys():
                    skill_path = SKILLS_DIR / skill_name
                    if not skill_path.exists():
                        print(f"{YELLOW}Warning: {skill_name} not found, skipping.{RESET}")
                        continue
                    
                    for file_path in skill_path.rglob('*'):
                        if '__pycache__' in file_path.parts or file_path.suffix == '.pyc':
                            continue
                        
                        if file_path.is_file():
                            arcname = Path(skill_name) / file_path.relative_to(skill_path)
                            zipf.write(file_path, arcname)
                            # print(f"  Added: {arcname}")
            
            print(MSG_BACKUP_ALL_SUCCESS.format(path=backup_path))
            size_mb = backup_path.stat().st_size / 1024 / 1024
            print(MSG_BACKUP_SIZE.format(size=size_mb))
            return backup_path
        except Exception as e:
            print(f"{RED}Error backing up skills: {e}{RESET}")
            return None

def list_backups():
    """List all available backups"""
    if not BACKUPS_DIR.exists():
        print(MSG_NO_BACKUPS)
        return
    
    backups = sorted(BACKUPS_DIR.glob('*.zip'), key=lambda p: p.stat().st_mtime, reverse=True)
    
    if not backups:
        print(MSG_NO_BACKUPS)
        return
    
    print(MSG_AVAILABLE_BACKUPS)
    print(f"{'Filename':<40} {'Size (MB)':<15} {'Date'}")
    print("-" * 80)
    
    for backup in backups:
        size_mb = backup.stat().st_size / 1024 / 1024
        date = datetime.datetime.fromtimestamp(backup.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        print(f"{backup.name:<40} {size_mb:<15.2f} {date}")
    
    print()

def restore_backup(backup_file, skill_name=None, force=False):
    """
    Restore skills from a backup.
    
    Args:
        backup_file: Path to backup zip file
        skill_name: Name of specific skill to restore, or None to restore all
        force: Force overwrite without confirmation
    """
    backup_path = Path(backup_file)
    
    if not backup_path.exists():
        print(f"{RED}Error: Backup file not found: {backup_path}{RESET}")
        return False
    
    print(MSG_RESTORING.format(name=backup_path.name))
    
    try:
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            # List contents
            if skill_name:
                # Restore single skill
                skill_path = SKILLS_DIR / skill_name
                
                if skill_path.exists():
                    if not force:
                        confirm = input(MSG_RESTORE_SKILL_EXISTS.format(name=skill_name)).lower()
                        if confirm != 'y':
                            print(MSG_RESTORE_CANCELLED)
                            return False
                    shutil.rmtree(skill_path)
                
                # Extract skill files
                skill_files = [f for f in zipf.namelist() if f.startswith(skill_name + '/') or f == skill_name]
                if not skill_files:
                    print(f"{RED}Error: Skill '{skill_name}' not found in backup.{RESET}")
                    return False
                
                for file in skill_files:
                    zipf.extract(file, SKILLS_DIR)
                
                print(MSG_RESTORED_SINGLE.format(name=skill_name))
            else:
                # Restore all skills
                if not force:
                    confirm = input(MSG_RESTORE_CONFIRM).lower()
                    if confirm != 'y':
                        print(MSG_RESTORE_CANCELLED)
                        return False
                
                zipf.extractall(SKILLS_DIR)
                print(MSG_RESTORED_ALL)
        
        return True
    except Exception as e:
        print(f"{RED}Error restoring backup: {e}{RESET}")
        return False

def cleanup_old_backups(keep=5):
    """Clean up old backups, keeping only most recent N versions"""
    if not BACKUPS_DIR.exists():
        return
    
    backups = sorted(BACKUPS_DIR.glob('*.zip'), key=lambda p: p.stat().st_mtime, reverse=True)
    old_backups = backups[keep:]
    
    if not old_backups:
        print("No old backups to clean up.")
        return
    
    print(MSG_CLEANING_BACKUPS.format(keep=keep))
    
    for old_backup in old_backups:
        try:
            old_backup.unlink()
            print(MSG_REMOVED_BACKUP.format(name=old_backup.name))
        except Exception as e:
            print(f"{RED}Error removing {old_backup.name}: {e}{RESET}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Backup and restore Trae skills")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create a backup')
    backup_parser.add_argument('--skill', '-s', help='Name of specific skill to backup')
    backup_parser.add_argument('--output', '-o', help='Custom output directory')
    
    # List command
    subparsers.add_parser('list', help='List available backups')
    
    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore from backup')
    restore_parser.add_argument('backup_file', help='Path to backup zip file')
    restore_parser.add_argument('--skill', '-s', help='Name of specific skill to restore')
    restore_parser.add_argument('--force', '-f', action='store_true', help='Force overwrite without confirmation')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old backups')
    cleanup_parser.add_argument('--keep', '-k', type=int, default=5, help='Number of backups to keep (default: 5)')
    
    args = parser.parse_args()
    
    if args.command == 'backup':
        create_backup(skill_name=args.skill, output_dir=args.output)
    elif args.command == 'list':
        list_backups()
    elif args.command == 'restore':
        restore_backup(args.backup_file, skill_name=args.skill, force=args.force)
    elif args.command == 'cleanup':
        cleanup_old_backups(keep=args.keep)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
