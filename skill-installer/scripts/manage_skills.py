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
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

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
        MSG_VERBOSE_ENABLED = f"{CYAN}[INFO] Verbose mode enabled{RESET}"
        MSG_VERBOSE_GIT_COMMAND = f"{CYAN}[GIT] Running: {{cmd}}{RESET}"
        MSG_VERBOSE_FILE_OP = f"{CYAN}[FILE] {{op}}: {{path}}{RESET}"

# Global verbose flag
verbose_mode = False

def set_verbose(enabled):
    """Set verbose mode globally"""
    global verbose_mode
    verbose_mode = enabled
    if enabled:
        print(MSG_VERBOSE_ENABLED)

def verbose_print(msg_type, **kwargs):
    """Print verbose messages if verbose mode is enabled"""
    if verbose_mode:
        if msg_type == 'git':
            cmd = kwargs.get('cmd', '')
            output = kwargs.get('output', '')
            print(MSG_VERBOSE_GIT_COMMAND.format(cmd=cmd))
            if output:
                print(MSG_VERBOSE_GIT_OUTPUT.format(output=output))
        elif msg_type == 'file':
            operation = kwargs.get('operation', '')
            path = kwargs.get('path', '')
            print(MSG_VERBOSE_FILE_OP.format(operation=operation, path=path))
        elif msg_type == 'state':
            description = kwargs.get('description', '')
            print(MSG_VERBOSE_STATE_CHANGE.format(description=description))
        elif msg_type == 'dep':
            dep = kwargs.get('dep', '')
            print(MSG_VERBOSE_DEPENDENCY_CHECK.format(dep=dep))



SKILLS_DIR = Path(__file__).parent.parent.parent
REGISTRY_FILE = SKILLS_DIR / 'skills.json'

def run_command(cmd, cwd=None, capture_output=False):
    """Run a shell command and check for errors"""
    try:
        cmd_str = ' '.join(cmd) if isinstance(cmd, list) else cmd
        verbose_print('git', cmd=cmd_str)
        
        if capture_output:
            # Removed errors='replace' to avoid TypeError in older python versions if check is strict, 
            # but usually run_command in manage_skills was copy-pasted. 
            # Assuming standard subprocess usage.
            result = subprocess.run(cmd, check=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors='replace')
            verbose_print('git', output=result.stdout.strip())
            return result.stdout.strip()
        else:
            subprocess.run(cmd, check=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
    except subprocess.CalledProcessError as e:
        if not capture_output:
            print(MSG_COMMAND_FAILED.format(error=e))
            
            # Provide more specific error messages based on error type
            if 'Could not resolve' in str(e) or 'Could not connect' in str(e):
                url = cmd[2] if len(cmd) > 2 else 'unknown'
                print(MSG_ERROR_NETWORK.format(url=url))
                print(MSG_ERROR_NETWORK_SUGGESTION)
            elif 'Permission denied' in str(e):
                print(MSG_ERROR_PERMISSION_DENIED.format(path=cwd or 'unknown'))
                print(MSG_ERROR_PERMISSION_SUGGESTION)
            elif 'not found' in str(e).lower() and 'git' in str(e).lower():
                print(MSG_ERROR_GIT_NOT_INSTALLED)
                print(MSG_ERROR_GIT_NOT_INSTALLED_SUGGESTION)
        return False
    except FileNotFoundError:
        print(MSG_ERROR_GIT_NOT_INSTALLED)
        print(MSG_ERROR_GIT_NOT_INSTALLED_SUGGESTION)
        return False

def load_registry():
    if not REGISTRY_FILE.exists():
        return {}
    try:
        content = REGISTRY_FILE.read_text(encoding='utf-8')
        return json.loads(content).get('skills', {})
    except UnicodeDecodeError as e:
        logger.error(f"Unicode decode error reading {REGISTRY_FILE}: {e}")
        try:
            content = REGISTRY_FILE.read_text(encoding='utf-8', errors='replace')
            logger.warning(f"Retrying with errors='replace' for {REGISTRY_FILE}")
            return json.loads(content).get('skills', {})
        except Exception as e2:
            logger.error(f"Failed to read {REGISTRY_FILE} even with errors='replace': {e2}")
            print(f"{RED}Error reading skills.json: {e}{RESET}")
            return {}
    except Exception as e:
        logger.error(f"Error reading {REGISTRY_FILE}: {e}")
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
    total = len(skills)
    
    for idx, (name, info) in enumerate(skills.items(), 1):
        # Progress indicator
        print(MSG_PROGRESS_CHECKING.format(current=idx, total=total))
        verbose_print('state', description=f"Checking updates for {name} ({idx}/{total})")
        
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
import stat
import os

def safe_rmtree(path, retries=3, delay=0.5):
    """
    Safely remove a directory tree with retries and permission handling for Windows.
    
    Handles:
    - Windows file locking issues (retries with delay)
    - Read-only files (common in .git/objects/pack/)
    - Permission denied errors
    
    Args:
        path: Path to directory to remove
        retries: Number of retry attempts (default 3)
        delay: Delay between retries in seconds (default 0.5)
    
    Returns:
        True if successfully removed, False otherwise
    """
    path = Path(path)
    if not path.exists():
        return True
    
    def on_rm_error(func, p, exc_info):
        """Error handler for shutil.rmtree - fixes permissions and retries."""
        try:
            os.chmod(p, stat.S_IWRITE | stat.S_IREAD)
            func(p)
        except Exception:
            pass
    
    for attempt in range(retries):
        try:
            shutil.rmtree(path, onerror=on_rm_error)
            if not path.exists():
                return True
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                print(MSG_DELETE_LOCKED.format(path=path))
                logger.error(f"Failed to remove {path} after {retries} attempts: {e}")
                return False
    
    return not path.exists()

def uninstall_skill(name, auto_confirm=True):
    """Uninstall a skill by removing its directory.
    
    Note: This function only removes the skill directory.
    Registry synchronization (skills.json, skill_map.json, AGENTS.md) 
    should be handled by skills-registry-sync skill after uninstallation.
    
    Args:
        name: Name of the skill to uninstall
        auto_confirm: If True (default), skip confirmation prompt.
                     Set to False only for interactive CLI usage with --confirm flag.
    """
    skills = load_registry()
    if name not in skills:
        skill_path = SKILLS_DIR / name
        if not skill_path.exists():
            print(MSG_SKILL_NOT_FOUND.format(name=name))
            return
        print(f"Skill '{name}' not in registry but directory exists. Proceeding with removal...")
    
    skill_path = SKILLS_DIR / name
    
    print(f"Removing skill directory: {skill_path}")
    if safe_rmtree(skill_path):
        print(f"Successfully removed directory: {skill_path}")
        print(MSG_REGISTRY_SYNC_REQUIRED_UNINSTALL)
    else:
        print(f"Failed to remove skill directory: {skill_path}")

def search_skills_command(query):
    """
    Search for skills in skills.json by name or description.
    
    Args:
        query: Search query string
    """
    print(MSG_SEARCHING.format(query=query))
    
    try:
        skills = load_registry()
        results = []
        
        if skills:
            for skill_name, skill_info in skills.items():
                if query.lower() in skill_name.lower() or query.lower() in skill_info.get('description', '').lower():
                    results.append({
                        'name': skill_name,
                        'description': skill_info.get('description', ''),
                        'source': skill_info.get('source', 'unknown'),
                        'aliases': skill_info.get('aliases', []),
                        'category': 'installed'
                    })
        
        if not results:
            print(MSG_NO_SEARCH_RESULTS.format(query=query))
            return
        
        print(MSG_SEARCH_RESULTS_HEADER.format(query=query))
        
        for skill in results:
            print(MSG_SEARCH_RESULT_ITEM.format(name=skill['name']))
            
            # Truncate description if too long
            description = skill.get('description', '')
            if len(description) > 80:
                description = description[:77] + "..."
            print(MSG_SEARCH_RESULT_DESC.format(description=description))
            
            # Show aliases if any
            aliases = skill.get('aliases', [])
            if aliases:
                aliases_str = ', '.join(aliases)
                print(MSG_SEARCH_RESULT_ALIASES.format(aliases=aliases_str))
            
            # Show source type (local/remote)
            source = skill.get('source', 'unknown')
            source_type = 'local' if source == 'local' else 'remote'
            print(MSG_SEARCH_RESULT_SOURCE.format(source=source_type))
            
            print()
        
        print(f"Found {len(results)} result(s) matching '{query}'")
        
    except Exception as e:
        print(f"{RED}Error searching skills: {e}{RESET}")

def info_command(skill_name):
    """
    Show detailed information about a skill.
    
    Args:
        skill_name: Name of skill to show info for
    """
    try:
        skills = load_registry()
        
        if skill_name not in skills:
            print(MSG_SKILL_NOT_FOUND.format(name=skill_name))
            return
        
        skill_info = skills[skill_name]
        
        print(MSG_INFO_HEADER)
        print(MSG_INFO_TITLE)
        
        name = skill_name
        description = skill_info.get('description', '')
        source = skill_info.get('source', 'unknown')
        aliases = skill_info.get('aliases', [])
        
        print(MSG_INFO_NAME.format(name=name))
        print(MSG_INFO_DESCRIPTION.format(description=description))
        print(MSG_INFO_SOURCE.format(source=source))
        
        if aliases:
            aliases_str = ', '.join(aliases)
            print(MSG_INFO_ALIASES.format(aliases=aliases_str))
        
        print(MSG_INFO_STATUS_INSTALLED)
        version = skill_info.get('version', 'unknown')
        if version != 'unknown':
            version = version[:7]
        print(MSG_INFO_VERSION.format(version=version))
        
        updated = skill_info.get('last_update_time')
        if updated:
            print(MSG_INFO_UPDATED.format(updated=updated))
        
        print(MSG_INFO_FOOTER)
        
    except Exception as e:
        print(f"{RED}Error getting skill info: {e}{RESET}")


def health_check_command(skill_name=None):
    """
    Perform health check on skills.
    
    Args:
        skill_name: Optional name of a specific skill to check. If None, checks all installed skills.
    """
    import re
    import yaml
    
    print(MSG_HEALTH_CHECK_START)
    
    skills = load_registry()
    
    if skill_name:
        if skill_name not in skills:
            print(MSG_SKILL_NOT_FOUND.format(name=skill_name))
            return
        skills_to_check = {skill_name: skills[skill_name]}
    else:
        skills_to_check = skills
    
    if not skills_to_check:
        print(MSG_NO_SKILLS_REGISTRY)
        return
    
    overall_issues = []
    overall_recommendations = []
    
    for name, info in skills_to_check.items():
        print(MSG_HEALTH_CHECK_SKILL.format(skill_name=name))
        
        skill_path = SKILLS_DIR / name
        issues = []
        recommendations = []
        
        if not skill_path.exists():
            issues.append(f"Skill directory not found at {skill_path}")
            recommendations.append(f"Reinstall skill '{name}'")
            print(MSG_HEALTH_STATUS_ERROR)
            issues_str = '\n      - '.join(issues)
            print(MSG_HEALTH_ISSUES_FOUND.format(issues='\n      - ' + issues_str))
            recommendations_str = '\n      - '.join(recommendations)
            print(MSG_HEALTH_RECOMMENDATIONS.format(recommendations='\n      - ' + recommendations_str))
            overall_issues.extend([f"{name}: {issue}" for issue in issues])
            overall_recommendations.extend([f"{name}: {rec}" for rec in recommendations])
            continue
        
        skill_md_path = skill_path / 'SKILL.md'
        
        if not skill_md_path.exists():
            issues.append("SKILL.md file not found")
            recommendations.append("Create SKILL.md with proper YAML frontmatter")
            print(MSG_HEALTH_CHECK_SKILL_MD_MISSING)
            print(MSG_HEALTH_STATUS_ERROR)
            issues_str = '\n      - '.join(issues)
            print(MSG_HEALTH_ISSUES_FOUND.format(issues='\n      - ' + issues_str))
            recommendations_str = '\n      - '.join(recommendations)
            print(MSG_HEALTH_RECOMMENDATIONS.format(recommendations='\n      - ' + recommendations_str))
            overall_issues.extend([f"{name}: {issue}" for issue in issues])
            overall_recommendations.extend([f"{name}: {rec}" for rec in recommendations])
            continue
        
        try:
            content = skill_md_path.read_text(encoding='utf-8')
            
            if not content.startswith('---'):
                issues.append("SKILL.md missing YAML frontmatter")
                recommendations.append("Add YAML frontmatter with '---' delimiters")
                print(MSG_HEALTH_CHECK_SKILL_MD_INVALID.format(error="Missing YAML frontmatter"))
            else:
                frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
                if not frontmatter_match:
                    issues.append("SKILL.md has invalid YAML frontmatter format")
                    recommendations.append("Fix YAML frontmatter format (must start and end with '---')")
                    print(MSG_HEALTH_CHECK_SKILL_MD_INVALID.format(error="Invalid frontmatter format"))
                else:
                    frontmatter_str = frontmatter_match.group(1)
                    try:
                        frontmatter = yaml.safe_load(frontmatter_str)
                        
                        if not isinstance(frontmatter, dict):
                            issues.append("YAML frontmatter is not a dictionary")
                            recommendations.append("Fix YAML frontmatter to be a valid dictionary")
                        else:
                            if 'name' not in frontmatter:
                                issues.append("Missing required field 'name' in YAML frontmatter")
                                recommendations.append("Add 'name' field to YAML frontmatter")
                            
                            if 'description' not in frontmatter:
                                issues.append("Missing required field 'description' in YAML frontmatter")
                                recommendations.append("Add 'description' field to YAML frontmatter")
                            
                            if 'name' in frontmatter and frontmatter['name'] != name:
                                issues.append(f"Skill name mismatch: directory name '{name}' vs frontmatter name '{frontmatter['name']}'")
                                recommendations.append("Ensure directory name matches frontmatter name")
                            
                            if 'description' in frontmatter and len(frontmatter['description']) < 10:
                                issues.append("Description is too short (should be at least 10 characters)")
                                recommendations.append("Provide a more detailed description")
                    except yaml.YAMLError as e:
                        issues.append(f"YAML parsing error: {e}")
                        recommendations.append("Fix YAML syntax in frontmatter")
                        print(MSG_HEALTH_CHECK_SKILL_MD_INVALID.format(error=f"YAML error: {e}"))
        except UnicodeDecodeError as e:
            logger.error(f"Unicode decode error reading {skill_md_path}: {e}")
            try:
                content = skill_md_path.read_text(encoding='utf-8', errors='replace')
                logger.warning(f"Retrying with errors='replace' for {skill_md_path}")
                issues.append(f"Encoding issues in SKILL.md: {e}")
                recommendations.append("Fix encoding issues in SKILL.md")
                print(MSG_HEALTH_CHECK_SKILL_MD_INVALID.format(error=f"Encoding error: {e}"))
            except Exception as e2:
                logger.error(f"Failed to read {skill_md_path} even with errors='replace': {e2}")
                issues.append(f"Error reading SKILL.md: {e2}")
                recommendations.append("Ensure SKILL.md is readable and properly formatted")
                print(MSG_HEALTH_CHECK_SKILL_MD_INVALID.format(error=str(e2)))
        except Exception as e:
            logger.error(f"Error reading {skill_md_path}: {e}")
            issues.append(f"Error reading SKILL.md: {e}")
            recommendations.append("Ensure SKILL.md is readable and properly formatted")
            print(MSG_HEALTH_CHECK_SKILL_MD_INVALID.format(error=str(e)))
        
        try:
            # Check dependencies from SKILL.md frontmatter
            skill_md_path = skill_path / 'SKILL.md'
            if skill_md_path.exists():
                import re
                import yaml
                content = skill_md_path.read_text(encoding='utf-8')
                frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
                if frontmatter_match:
                    frontmatter_str = frontmatter_match.group(1)
                    frontmatter = yaml.safe_load(frontmatter_str)
                    if isinstance(frontmatter, dict):
                        dependencies = frontmatter.get('dependencies', [])
                        if dependencies:
                            missing_deps = []
                            for dep in dependencies:
                                if dep not in skills:
                                    missing_deps.append(dep)
                                    print(MSG_HEALTH_CHECK_DEPENDENCY_MISSING.format(dep=dep))
                            
                            if missing_deps:
                                issues.append(f"Missing dependencies: {', '.join(missing_deps)}")
                                recommendations.append(f"Install missing dependencies: {', '.join(missing_deps)}")
        except Exception:
            pass
        
        if issues:
            print(MSG_HEALTH_STATUS_ERROR)
            issues_str = '\n      - '.join(issues)
            print(MSG_HEALTH_ISSUES_FOUND.format(issues='\n      - ' + issues_str))
            recommendations_str = '\n      - '.join(recommendations)
            print(MSG_HEALTH_RECOMMENDATIONS.format(recommendations='\n      - ' + recommendations_str))
            overall_issues.extend([f"{name}: {issue}" for issue in issues])
            overall_recommendations.extend([f"{name}: {rec}" for rec in recommendations])
        else:
            print(MSG_HEALTH_STATUS_HEALTHY)
            print(MSG_HEALTH_NO_ISSUES)
        
        print()
    
    if skill_name:
        print(f"Health check complete for skill: {skill_name}")
    else:
        print(f"Health check complete for {len(skills_to_check)} skill(s)")
    
    if overall_issues:
        print(f"\n{COLOR_YELLOW}Overall Status: Issues Found{COLOR_RESET}")
        print(f"Total issues: {len(overall_issues)}")
    else:
        print(f"\n{COLOR_GREEN}Overall Status: All Skills Healthy{COLOR_RESET}")

def get_version_history(skill_path):
    """
    Get version history for a skill using git log.

    Args:
        skill_path: Path to the skill directory

    Returns:
        List of (commit_hash, date, message) tuples, or empty list if not a git repo
    """
    git_dir = skill_path / '.git'
    if not git_dir.exists():
        return []

    try:
        result = run_command(['git', 'log', '--oneline', '--date=short', '--format=%H|%ad|%s'], cwd=skill_path, capture_output=True)
        if not result:
            return []

        history = []
        for line in result.split('\n'):
            if line:
                parts = line.split('|', 2)
                if len(parts) == 3:
                    commit_hash, date, message = parts
                    history.append((commit_hash, date, message))

        return history
    except Exception:
        return []

def rollback_skill(skill_name, version=None, auto_confirm=False):
    """
    Rollback a skill to a previous version.

    Args:
        skill_name: Name of the skill to rollback
        version: Optional specific commit hash to rollback to
        auto_confirm: If True, skip interactive prompts (requires version to be specified)
    """
    skills = load_registry()
    if skill_name not in skills:
        print(MSG_SKILL_NOT_FOUND.format(name=skill_name))
        return

    skill_path = SKILLS_DIR / skill_name

    print(MSG_ROLLBACK_START.format(name=skill_name))

    version_history = get_version_history(skill_path)
    if not version_history:
        print(MSG_ROLLBACK_NOT_GIT_REPO.format(name=skill_name))
        return

    if not version:
        if auto_confirm:
            print(f"{COLOR_RED}Error: --yes flag requires --version to be specified for rollback.{COLOR_RESET}")
            print("Use --version <commit-hash> to specify the version to rollback to.")
            return
        
        print(MSG_ROLLBACK_VERSION_HISTORY)
        for idx, (commit_hash, date, message) in enumerate(version_history, 1):
            short_hash = commit_hash[:7]
            print(f"  {idx}. {short_hash}  {date}  {message}")

        print(MSG_ROLLBACK_SELECT_VERSION, end='')
        user_input = input().strip()

        if user_input.lower() == 'q':
            print("Rollback cancelled.")
            return

        try:
            idx = int(user_input) - 1
            if idx < 0 or idx >= len(version_history):
                print(f"{COLOR_RED}Invalid selection. Rollback cancelled.{COLOR_RESET}")
                return
            version = version_history[idx][0]
        except ValueError:
            print(f"{COLOR_RED}Invalid input. Rollback cancelled.{COLOR_RESET}")
            return

    short_version = version[:7]
    print(MSG_ROLLBACK_TO_VERSION.format(version=short_version))

    backup_path = SKILLS_DIR / f"{skill_name}-rollback-backup"
    if skill_path.exists():
        if backup_path.exists():
            safe_rmtree(backup_path)

        try:
            skill_path.rename(backup_path)
            print(MSG_ROLLBACK_BACKUP_CREATED.format(path=backup_path))
        except Exception as e:
            print(MSG_BACKUP_ERROR.format(error=e))
            return

    try:
        result = run_command(['git', 'checkout', version], cwd=backup_path, capture_output=False)
        if result:
            backup_path.rename(skill_path)
            print(MSG_ROLLBACK_SUCCESS.format(name=skill_name, version=short_version))

            skills[skill_name]['version'] = version
            skills[skill_name]['updated'] = time.strftime('%Y-%m-%d %H:%M:%S')

            try:
                REGISTRY_FILE.write_text(json.dumps({'skills': skills}, indent=2), encoding='utf-8', errors='strict')
            except UnicodeEncodeError as e:
                logger.error(f"Unicode encode error writing to {REGISTRY_FILE}: {e}")
                print(f"{COLOR_YELLOW}Warning: Could not update skills.json due to encoding error: {e}{COLOR_RESET}")
            except Exception as e:
                logger.error(f"Error writing to {REGISTRY_FILE}: {e}")
                print(f"{COLOR_YELLOW}Warning: Could not update skills.json: {e}{COLOR_RESET}")
        else:
            raise Exception("Git checkout failed")
    except Exception as e:
        print(MSG_ROLLBACK_FAILED.format(name=skill_name))
        print(f"{COLOR_RED}Error: {e}{COLOR_RESET}")

        if backup_path.exists():
            if skill_path.exists():
                safe_rmtree(skill_path)

            try:
                backup_path.rename(skill_path)
                print(MSG_ROLLBACK_BACKUP_RESTORED)
            except Exception as restore_error:
                print(f"{COLOR_RED}Failed to restore backup: {restore_error}{COLOR_RESET}")

def update_skill(name, force=False, auto_confirm=False):
    skills = load_registry()
    if name not in skills:
        print(MSG_SKILL_NOT_FOUND.format(name=name))
        return

    info = skills[name]
    repo_url = info.get('source')
    subdir = info.get('subdir', '')
    
    verbose_print('state', description=f"Updating skill '{name}'")
    
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
                 except (IndexError, ValueError):
                     # Fallback
                     install_source = f"{repo_url} --subdir {subdir}" # Hypothetical, but install_skill doesn't support flags in source string
                     # Actually, let's just use the tree format, it's safer for the parser
                     install_source = f"{repo_url}/tree/main/{subdir}"
    
    print(MSG_UPDATING_FROM.format(name=name, source=install_source))
    
    # Backup existing skill before update
    backup_path = SKILLS_DIR / f"{name}-backup"
    skill_path = SKILLS_DIR / name
    
    verbose_print('file', operation='Creating backup', path=str(backup_path))
    
    if skill_path.exists():
        if backup_path.exists():
            safe_rmtree(backup_path)
        
        try:
            skill_path.rename(backup_path)
            print(MSG_BACKUP_CREATED.format(path=backup_path))
        except (PermissionError, OSError) as e:
            print(MSG_BACKUP_ERROR.format(error=e))
            return
    
    # Install the updated skill
    # Pass force and auto_confirm parameters to avoid interactive prompts
    verbose_print('state', description=f"Installing updated version of '{name}'")
    success = install_skill(install_source, SKILLS_DIR, run_audit=True, force=force, auto_install_deps=auto_confirm)
    
    if success:
        print(MSG_UPDATE_SUCCESS.format(name=name))
        # Clean up backup
        if backup_path.exists():
            verbose_print('file', operation='Removing backup', path=str(backup_path))
            safe_rmtree(backup_path)
            print(MSG_BACKUP_REMOVED)
            
        # Trigger Post-Operation Analysis
        try:
            analysis_script = Path(__file__).parent / 'post_op_analysis.py'
            if analysis_script.exists():
                verbose_print('file', operation='Running post-operation analysis', path=str(analysis_script))
                subprocess.run([sys.executable, str(analysis_script), 'update', name, str(skill_path)], check=False)
        except Exception as e:
            print(f"Warning: Post-operation analysis failed: {e}")
            
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
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose mode for detailed debug output")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    subparsers.add_parser('list', help='List installed skills')
    subparsers.add_parser('check', help='Check for updates')
    
    update_parser = subparsers.add_parser('update', help='Update a skill')
    update_parser.add_argument('name', help='Name of the skill to update')
    update_parser.add_argument('--force', '-f', action='store_true', help='Force update without confirmation')
    update_parser.add_argument('--yes', '-y', action='store_true', help='Auto-confirm all prompts')
    
    update_all_parser = subparsers.add_parser('update-all', help='Update all skills')
    update_all_parser.add_argument('--yes', '-y', action='store_true', help='Auto-confirm all prompts')

    uninstall_parser = subparsers.add_parser('uninstall', help='Uninstall a skill')
    uninstall_parser.add_argument('name', help='Name of the skill to uninstall')
    uninstall_parser.description = 'Uninstall a skill by removing its directory and updating registries. Auto-confirmed by default.'

    search_parser = subparsers.add_parser('search', help='Search for skills')
    search_parser.add_argument('query', help='Search query (matches name or description)')
    search_parser.description = 'Search for skills by name or description. ' \
                                'Supports fuzzy matching across installed skills.'

    info_parser = subparsers.add_parser('info', help='Show detailed information about a skill')
    info_parser.add_argument('name', help='Name of skill to show info for')

    health_parser = subparsers.add_parser('health', help='Check health of installed skills', aliases=['check-health'])
    health_parser.add_argument('name', nargs='?', help='Optional skill name to check (if not provided, checks all skills)')
    health_parser.description = 'Perform health check on skills. Validates SKILL.md format, directory structure, and dependencies.'

    rollback_parser = subparsers.add_parser('rollback', help='Rollback a skill to a previous version')
    rollback_parser.add_argument('name', help='Name of skill to rollback')
    rollback_parser.add_argument('--version', '-v', help='Specific commit hash to rollback to (if not provided, shows version history)')
    rollback_parser.add_argument('--yes', '-y', action='store_true', help='Auto-confirm rollback (requires --version to be specified)')
    rollback_parser.description = 'Rollback a skill to a previous version using git history. Shows available versions if no specific version is provided.'

    args = parser.parse_args()
    
    # Set verbose mode
    set_verbose(args.verbose)

    if args.command == 'list':
        list_skills()
    elif args.command == 'check':
        check_updates()
    elif args.command == 'update':
        force = getattr(args, 'force', False)
        yes = getattr(args, 'yes', False)
        update_skill(args.name, force=force, auto_confirm=yes)
    elif args.command == 'update-all':
        skills = load_registry()
        for name in skills:
            update_skill(name, force=False, auto_confirm=False)
    elif args.command == 'uninstall':
        uninstall_skill(args.name)
    elif args.command == 'search':
        search_skills_command(args.query)
    elif args.command == 'info':
        info_command(args.name)
    elif args.command == 'health' or args.command == 'check-health':
        skill_name = getattr(args, 'name', None)
        health_check_command(skill_name)
    elif args.command == 'rollback':
        version = getattr(args, 'version', None)
        yes = getattr(args, 'yes', False)
        rollback_skill(args.name, version, auto_confirm=yes)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
