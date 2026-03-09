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
import re
import yaml
from pathlib import Path

# Proxy configuration
proxy_config = {
    'http': None,
    'https': None,
    'no_proxy': None
}

def setup_proxy(http_proxy=None, https_proxy=None, no_proxy=None):
    """Setup proxy configuration for git operations"""
    global proxy_config
    
    # Auto-detect from environment if not explicitly provided
    proxy_config['http'] = http_proxy or os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
    proxy_config['https'] = https_proxy or os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    proxy_config['no_proxy'] = no_proxy or os.environ.get('NO_PROXY') or os.environ.get('no_proxy')
    
    if proxy_config['http'] or proxy_config['https']:
        print(f"{COLOR_CYAN}[PROXY] Using proxy configuration{COLOR_RESET}")
        if proxy_config['http']:
            print(f"{COLOR_CYAN}[PROXY] HTTP Proxy: {proxy_config['http']}{COLOR_RESET}")
        if proxy_config['https']:
            print(f"{COLOR_CYAN}[PROXY] HTTPS Proxy: {proxy_config['https']}{COLOR_RESET}")

def get_proxy_env():
    """Get proxy environment variables for subprocess"""
    env = os.environ.copy()
    if proxy_config['http']:
        env['HTTP_PROXY'] = proxy_config['http']
        env['http_proxy'] = proxy_config['http']
    if proxy_config['https']:
        env['HTTPS_PROXY'] = proxy_config['https']
        env['https_proxy'] = proxy_config['https']
    if proxy_config['no_proxy']:
        env['NO_PROXY'] = proxy_config['no_proxy']
        env['no_proxy'] = proxy_config['no_proxy']
    return env
try:
    from messages import *
except ImportError:
    # Fallback if messages.py not found in same dir (e.g. running from root)
    try:
        sys.path.append(str(Path(__file__).parent))
        from messages import *
    except ImportError:
        # Minimal fallback constants if all else fails
        COLOR_GREEN = "\033[92m"
        COLOR_RED = "\033[91m"
        COLOR_YELLOW = "\033[93m"
        COLOR_BLUE = "\033[94m"
        COLOR_CYAN = "\033[96m"
        COLOR_RESET = "\033[0m"
        MSG_COMMAND_FAILED = f"{COLOR_RED}Command failed: {{error}}{COLOR_RESET}"
        MSG_STDERR = f"Stderr: {{stderr}}{COLOR_RESET}"
        MSG_VERBOSE_ENABLED = f"{COLOR_CYAN}[INFO] Verbose mode enabled{COLOR_RESET}"
        MSG_VERBOSE_GIT_COMMAND = f"{COLOR_CYAN}[GIT] Running: {{cmd}}{COLOR_RESET}"
        MSG_VERBOSE_FILE_OP = f"{COLOR_CYAN}[FILE] {{op}}: {{path}}{COLOR_RESET}"

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



def run_command(cmd, cwd=None, capture_output=False):
    """Run a shell command and check for errors"""
    try:
        cmd_str = ' '.join(cmd) if isinstance(cmd, list) else cmd
        verbose_print('git', cmd=cmd_str)
        
        # Get proxy environment
        env = get_proxy_env()
        
        if capture_output:
            result = subprocess.run(cmd, check=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors='replace', env=env)
            verbose_print('git', output=result.stdout.strip())
            return result.stdout.strip()
        else:
            subprocess.run(cmd, check=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
            return True
    except subprocess.CalledProcessError as e:
        if not capture_output:
            print(MSG_COMMAND_FAILED.format(error=e))
            stderr = e.stderr.decode('utf-8', errors='replace') if hasattr(e.stderr, 'decode') else e.stderr
            print(MSG_STDERR.format(stderr=stderr))
            
            # Provide more specific error messages based on error type
            if 'Could not resolve' in str(e) or 'Could not connect' in str(e):
                print(MSG_ERROR_NETWORK.format(url=cmd[2] if len(cmd) > 2 else 'unknown'))
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

def parse_skill_dependencies(skill_path):
    """
    Parse dependencies from SKILL.md file.
    
    Args:
        skill_path: Path to the skill directory
    
    Returns:
        List of dependency skill names (empty list if no dependencies)
    """
    skill_md = skill_path / 'SKILL.md'
    
    if not skill_md.exists():
        return []
    
    try:
        content = skill_md.read_text(encoding='utf-8')
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if match:
            frontmatter = yaml.safe_load(match.group(1))
            dependencies = frontmatter.get('dependencies', [])
            
            if isinstance(dependencies, str):
                return [dependencies]
            elif isinstance(dependencies, list):
                return dependencies
    except Exception as e:
        print(f"Warning: Could not parse dependencies from SKILL.md: {e}")
    
    return []

def check_dependencies_installed(dependencies, dest_root):
    """
    Check which dependencies are already installed.
    
    Args:
        dependencies: List of dependency skill names
        dest_root: Path to the skills directory
    
    Returns:
        Tuple of (missing_dependencies, installed_dependencies)
    """
    registry_path = Path(dest_root) / 'skills.json'
    installed_skills = set()
    
    if registry_path.exists():
        try:
            content = registry_path.read_text(encoding='utf-8')
            registry = json.loads(content)
            installed_skills = set(registry.get('skills', {}).keys())
        except Exception as e:
            print(f"Warning: Could not read skills.json: {e}")
    
    missing = []
    installed = []
    
    for dep in dependencies:
        if dep in installed_skills:
            installed.append(dep)
        else:
            missing.append(dep)
    
    return missing, installed

def resolve_install_order(skill_name, dependencies, dest_root):
    """
    Resolve the correct installation order using topological sort.
    Handles circular dependency detection.
    
    Args:
        skill_name: Name of the main skill to install
        dependencies: List of dependency skill names
        dest_root: Path to the skills directory
    
    Returns:
        Ordered list of skills to install (dependencies first, then main skill)
        Returns None if circular dependency is detected
    """
    registry_path = Path(dest_root) / 'skills.json'
    
    def get_dependencies_for_skill(skill):
        """Get dependencies for a specific skill"""
        skill_path = Path(dest_root) / skill
        if skill_path.exists():
            return parse_skill_dependencies(skill_path)
        return []
    
    def build_dependency_graph():
        """Build the dependency graph"""
        graph = {}
        all_skills = [skill_name] + dependencies
        
        for skill in all_skills:
            if skill not in graph:
                graph[skill] = set()
            
            deps = get_dependencies_for_skill(skill)
            for dep in deps:
                if dep in all_skills:
                    graph[skill].add(dep)
        
        return graph
    
    graph = build_dependency_graph()
    
    def topological_sort():
        """Kahn's algorithm for topological sort"""
        in_degree = {node: 0 for node in graph}
        
        for node in graph:
            for neighbor in graph[node]:
                in_degree[neighbor] = in_degree.get(neighbor, 0) + 1
        
        queue = [node for node in in_degree if in_degree[node] == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        if len(result) != len(graph):
            return None
        
        return result
    
    def detect_cycle():
        """Detect circular dependencies using DFS"""
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {node: WHITE for node in graph}
        cycle = []
        
        def dfs(node, path):
            color[node] = GRAY
            path.append(node)
            
            for neighbor in graph[node]:
                if color[neighbor] == GRAY:
                    idx = path.index(neighbor)
                    return path[idx:]
                elif color[neighbor] == WHITE:
                    result = dfs(neighbor, path)
                    if result:
                        return result
            
            color[node] = BLACK
            path.pop()
            return None
        
        for node in graph:
            if color[node] == WHITE:
                result = dfs(node, [])
                if result:
                    return result
        
        return None
    
    cycle = detect_cycle()
    if cycle:
        print(MSG_CIRCULAR_DEPENDENCY.format(cycle=' -> '.join(cycle)))
        return None
    
    order = topological_sort()
    if order is None:
        print(MSG_DEPENDENCY_RESOLUTION_FAILED)
        return None
    
    return order

def detect_license(skill_path):
    """
    Detect the license type from a skill directory.
    
    Args:
        skill_path: Path to the skill directory
    
    Returns:
        License type string (e.g., "MIT", "Apache-2.0", "GPL-3.0") or None if not found
    """
    skill_path = Path(skill_path)
    
    # Common license file names
    license_files = ['LICENSE', 'LICENSE.txt', 'LICENSE.md', 'LICENSE.rst', 'COPYING', 'COPYING.txt']
    
    for license_file in license_files:
        license_path = skill_path / license_file
        if license_path.exists():
            try:
                content = license_path.read_text(encoding='utf-8', errors='ignore')
                
                # Common license patterns
                license_patterns = [
                    (r'MIT License', 'MIT'),
                    (r'MIT\s', 'MIT'),
                    (r'Apache License.*?2\.0', 'Apache-2.0'),
                    (r'Apache-2\.0', 'Apache-2.0'),
                    (r'GNU General Public License.*?version 3', 'GPL-3.0'),
                    (r'GPL-3\.0', 'GPL-3.0'),
                    (r'GNU General Public License.*?version 2', 'GPL-2.0'),
                    (r'GPL-2\.0', 'GPL-2.0'),
                    (r'GNU General Public License', 'GPL'),
                    (r'BSD.*?2-Clause', 'BSD-2-Clause'),
                    (r'BSD.*?3-Clause', 'BSD-3-Clause'),
                    (r'BSD.*?4-Clause', 'BSD-4-Clause'),
                    (r'BSD\s', 'BSD'),
                    (r'Mozilla Public License.*?2\.0', 'MPL-2.0'),
                    (r'MPL-2\.0', 'MPL-2.0'),
                    (r'GNU Lesser General Public License.*?version 3', 'LGPL-3.0'),
                    (r'LGPL-3\.0', 'LGPL-3.0'),
                    (r'GNU Lesser General Public License.*?version 2', 'LGPL-2.1'),
                    (r'LGPL-2\.1', 'LGPL-2.1'),
                    (r'ISC License', 'ISC'),
                    (r'ISC\s', 'ISC'),
                    (r'Public Domain', 'Public Domain'),
                    (r'CC0', 'CC0'),
                    (r'Unlicense', 'Unlicense'),
                ]
                
                # Try to match license patterns
                for pattern, license_type in license_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        return license_type
                
                # If no pattern matched but license file exists, return "Custom"
                return 'Custom'
                
            except Exception as e:
                print(f"Warning: Could not read license file {license_file}: {e}")
                continue
    
    return None

def check_license_compatibility(license_type):
    """
    Check if a license is compatible with the project.
    
    Args:
        license_type: License type string (e.g., "MIT", "Apache-2.0", "GPL-3.0")
    
    Returns:
        Tuple of (status, message):
        - status: "compatible", "warning", or "incompatible"
        - message: Warning or error message if applicable, None otherwise
    """
    if license_type is None:
        return "warning", "No license file found. License terms are unknown."
    
    # Compatible licenses (permissive licenses)
    compatible_licenses = [
        'MIT', 'Apache-2.0', 'BSD', 'BSD-2-Clause', 'BSD-3-Clause', 'BSD-4-Clause',
        'ISC', 'Public Domain', 'CC0', 'Unlicense'
    ]
    
    # Warning licenses (copyleft but less restrictive)
    warning_licenses = [
        'LGPL-2.1', 'LGPL-3.0', 'MPL-2.0'
    ]
    
    # Incompatible licenses (strong copyleft)
    incompatible_licenses = [
        'GPL', 'GPL-2.0', 'GPL-3.0', 'AGPL'
    ]
    
    license_type_lower = license_type.lower()
    
    for license in compatible_licenses:
        if license.lower() in license_type_lower:
            return "compatible", None
    
    for license in warning_licenses:
        if license.lower() in license_type_lower:
            warning_msg = f"{license_type} is a copyleft license. It may require sharing modifications."
            return "warning", warning_msg
    
    for license in incompatible_licenses:
        if license.lower() in license_type_lower:
            error_msg = f"{license_type} is a strong copyleft license. Using it in a commercial project may require releasing your code under the same license."
            return "incompatible", error_msg
    
    # Unknown license
    return "warning", f"License '{license_type}' is not a recognized standard license. Please review the license terms carefully."

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

def resolve_source(source):
    """
    Resolve a skill name, alias, or category prefix to actual source URL and subdir.
    Falls back to parse_source for traditional URL and user/repo formats.
    
    Examples:
      - skill-name -> Resolved from catalog to (url, subdir)
      - category/skill-name -> Resolved from catalog to (url, subdir)
      - alias -> Resolved from catalog to (url, subdir)
      - https://github.com/user/repo -> (url, "") via parse_source
      - user/repo/subdir -> (url, "subdir") via parse_source
      - user/repo -> (url, "") via parse_source
    
    Args:
        source: Skill name, alias, category/name, or traditional source format
    
    Returns:
        Tuple of (repo_url, subdir) or (None, None) if resolution fails
    """
    # Check if this is a traditional format (URL or user/repo)
    if source.startswith("https://") or source.startswith("git@"):
        # Full URL - use parse_source directly
        return parse_source(source)
    
    # Check if it looks like a user/repo format with subdir (3+ parts)
    parts = source.split('/')
    if len(parts) >= 3:
        # user/repo/subdir format - use parse_source directly
        return parse_source(source)
    
    # For 2-part format, treat as user/repo format
    return parse_source(source)

def interactive_menu():
    """
    Display available skills and allow user to select one.
    
    Returns:
        Selected skill source or None if user exits
    """
    print(f"{COLOR_CYAN}Interactive Skill Installation{COLOR_RESET}")
    print("This mode is not available without skill_catalog.")
    print("Please use a direct Git URL or user/repo format.")
    return None

def select_skill_from_category(category):
    """
    Display all skills in a category and allow user to select one.
    
    Args:
        category: Category name to display skills from
    
    Returns:
        Selected skill dictionary or None if user exits
    """
    print(f"{COLOR_CYAN}Interactive Skill Selection{COLOR_RESET}")
    print("This mode is not available without skill_catalog.")
    print("Please use a direct Git URL or user/repo format.")
    return None

def preview_skill(skill_info):
    """
    Display detailed information about a skill and ask for confirmation.
    
    Args:
        skill_info: Skill dictionary containing skill information
    
    Returns:
        True if user confirms installation, False otherwise
    """
    print(MSG_INTERACTIVE_PREVIEW_HEADER)
    print(MSG_INTERACTIVE_PREVIEW_TITLE)
    print(MSG_INTERACTIVE_PREVIEW_NAME.format(name=skill_info['name']))
    print(MSG_INTERACTIVE_PREVIEW_DESC.format(description=skill_info['description']))
    print(MSG_INTERACTIVE_PREVIEW_SOURCE.format(source=skill_info['source']))
    print(MSG_INTERACTIVE_PREVIEW_LICENSE.format(license=skill_info['license']))
    
    if skill_info.get('dependencies'):
        print(MSG_INTERACTIVE_PREVIEW_DEPS.format(dependencies=', '.join(skill_info['dependencies'])))
    else:
        print(MSG_INTERACTIVE_PREVIEW_NO_DEPS)
    
    print(MSG_INTERACTIVE_PREVIEW_FOOTER)
    
    choice = input(MSG_INTERACTIVE_CONFIRM_INSTALL).strip().lower()
    return choice == 'y'

def interactive_install(dest_root, run_audit=True, force=False, auto_install_deps=False):
    """
    Run interactive installation mode.
    
    Args:
        dest_root: Destination directory for skills
        run_audit: Whether to run skill-auditor after install
        force: Whether to force overwrite without prompting
        auto_install_deps: Whether to auto-install dependencies without prompting
    """
    print(MSG_INTERACTIVE_WELCOME)
    
    while True:
        category = interactive_menu()
        if category is None:
            print(MSG_INTERACTIVE_EXIT)
            return
        
        while True:
            skill_info = select_skill_from_category(category)
            if skill_info is None:
                break
            
            if preview_skill(skill_info):
                skill_name = skill_info['name']
                success = install_skill(skill_name, dest_root, run_audit, force, auto_install_deps)
                
                if success:
                    print(MSG_INTERACTIVE_SKILL_INSTALLED.format(name=skill_name))
                else:
                    print(MSG_INTERACTIVE_SKILL_INSTALL_FAILED.format(name=skill_name))
                
                another = input(MSG_INTERACTIVE_INSTALL_ANOTHER).strip().lower()
                if another != 'y':
                    print(MSG_INTERACTIVE_EXIT)
                    return

def batch_install(sources, dest_root, run_audit=True, force=False, auto_install_deps=False):
    """
    Install multiple skills in batch mode.
    
    Args:
        sources: List of skill sources (URLs, user/repo, skill names, etc.)
        dest_root: Destination directory for skills
        run_audit: Whether to run skill-auditor after install
        force: Whether to force overwrite without prompting
        auto_install_deps: Whether to auto-install dependencies without prompting
    
    Returns:
        True if all installations succeeded, False otherwise
    """
    total = len(sources)
    successful = []
    failed = []
    
    print(MSG_BATCH_INSTALL_START)
    print(MSG_BATCH_INSTALL_TITLE.format(count=total))
    print(MSG_BATCH_INSTALL_START)
    
    for idx, source in enumerate(sources, 1):
        # Progress indicator
        percent = int((idx - 1) / total * 100)
        print(MSG_PROGRESS_INSTALLING.format(current=idx, total=total))
        verbose_print('state', description=f"Installing {source} ({idx}/{total})")
        
        try:
            success = install_skill(source, dest_root, run_audit, force, auto_install_deps)
            
            if success:
                print(MSG_BATCH_INSTALL_SUCCESS.format(source=source))
                successful.append(source)
            else:
                print(MSG_BATCH_INSTALL_FAILED.format(source=source))
                failed.append(source)
        except Exception as e:
            print(MSG_BATCH_INSTALL_FAILED.format(source=source))
            print(MSG_BATCH_INSTALL_ERROR.format(error=str(e)))
            failed.append(source)
        
        print()
    
    print(MSG_BATCH_INSTALL_SUMMARY)
    print(MSG_BATCH_INSTALL_SUMMARY_TITLE)
    print(MSG_BATCH_INSTALL_TOTAL.format(total=total))
    print(MSG_BATCH_INSTALL_SUCCESS_COUNT.format(count=len(successful)))
    print(MSG_BATCH_INSTALL_FAILED_COUNT.format(count=len(failed)))
    
    if failed:
        print(MSG_BATCH_INSTALL_FAILED_LIST.format(skills=', '.join(failed)))
        if len(successful) == 0:
            print(MSG_BATCH_INSTALL_ALL_FAILED)
        else:
            print(MSG_BATCH_INSTALL_SOME_FAILED)
    else:
        print(MSG_BATCH_INSTALL_ALL_SUCCESS)
    
    print(MSG_BATCH_INSTALL_SUMMARY)
    
    return len(failed) == 0

def install_skill(source, dest_root, run_audit=True, force=False, auto_install_deps=False):
    dest_root = Path(dest_root)
    repo_url, subdir = resolve_source(source)
    
    # Check if resolution failed
    if repo_url is None:
        return False
    
    print(MSG_INSTALLING.format(url=repo_url))
    if subdir:
        print(MSG_SUBDIR.format(subdir=subdir))
    print(MSG_DESTINATION.format(path=dest_root))

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Clone repo
        print(MSG_CLONING)
        max_retries = 3
        for attempt in range(max_retries):
            if run_command(['git', 'clone', '--depth', '1', repo_url, '.'], cwd=temp_path):
                break
            print(MSG_RETRY.format(attempt=attempt + 1, max_retries=max_retries))
            time.sleep(2 ** attempt)
        else:
            print(MSG_CLONE_FAILED.format(max_retries=max_retries))
            return False
            
        # Get commit hash
        commit_hash = run_command(['git', 'rev-parse', 'HEAD'], cwd=temp_path, capture_output=True)
        if not commit_hash:
            commit_hash = "unknown"
        print(MSG_VERSION.format(version=commit_hash[:7]))

        # Determine source path
        source_path = temp_path
        if subdir:
            # Try skills/ prefix first (common pattern for monorepos)
            skills_path = temp_path / 'skills' / subdir.split('/')[-1]
            if skills_path.exists():
                print(MSG_SUBDIR_FOUND_ALT.format(subdir=subdir, alt_path=f"skills/{subdir.split('/')[-1]}"))
                source_path = skills_path
                subdir = f"skills/{subdir.split('/')[-1]}"
            else:
                # Try exact path
                source_path = temp_path / subdir
            
            if not source_path.exists():
                # Try other common prefixes if still not found
                common_prefixes = ['packages', 'apps']
                found = False
                for prefix in common_prefixes:
                    alt_path = temp_path / prefix / subdir.split('/')[-1]
                    if alt_path.exists():
                        print(MSG_SUBDIR_FOUND_ALT.format(subdir=subdir, alt_path=f"{prefix}/{subdir.split('/')[-1]}"))
                        source_path = alt_path
                        subdir = f"{prefix}/{subdir.split('/')[-1]}"
                        found = True
                        break
                
                if not found:
                    print(MSG_SUBDIR_NOT_FOUND.format(subdir=subdir))
                    return False

        # Smart detection of skill name and source path
        detected_name = None
        detected_source_path = None

        # 1. Check for .claude/skills/<name> pattern
        claude_skills_dir = source_path / '.claude' / 'skills'
        if claude_skills_dir.exists() and claude_skills_dir.is_dir():
            subdirs = [d for d in claude_skills_dir.iterdir() if d.is_dir()]
            if len(subdirs) == 1:
                detected_name = subdirs[0].name
                detected_source_path = subdirs[0]
                print(f"Detected nested skill in .claude/skills/{detected_name}")

        # 2. Check for SKILL.md in root or detected path
        check_path = detected_source_path if detected_source_path else source_path
        skill_md = check_path / 'SKILL.md'
        if skill_md.exists():
            try:
                content = skill_md.read_text(encoding='utf-8')
                match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
                if match:
                    name_in_md = match.group(1).strip()
                    # Only use if we haven't found a name yet, or if it matches the detected dir name
                    if not detected_name:
                         detected_name = name_in_md
                         print(f"Detected skill name from SKILL.md: {detected_name}")
            except Exception:
                pass

        # Apply detection results
        if detected_name:
            skill_name = detected_name
        else:
            skill_name = None # Clear if not detected
        
        if detected_source_path:
            source_path = detected_source_path
            # Adjust subdir to reflect the internal path for registry
            extra_path = detected_source_path.relative_to(temp_path)
            if subdir:
                 subdir = f"{subdir}/{extra_path}"
            else:
                 subdir = str(extra_path).replace('\\', '/')
            
        # Determine skill name (from subdir name or repo name)
        if not skill_name:
            if subdir:
                skill_name = Path(subdir).name
            else:
                # Extract from repo URL: https://github.com/user/repo.git -> repo
                skill_name = repo_url.rstrip('/').split('/')[-1]
                if skill_name.endswith('.git'):
                    skill_name = skill_name[:-4]

        dest_path = dest_root / skill_name
        
        if dest_path.exists():
            print(MSG_DEST_EXISTS.format(path=dest_path))
            if force or auto_install_deps:
                print(MSG_FORCE_OVERWRITE)
                shutil.rmtree(dest_path)
            else:
                overwrite = input(MSG_OVERWRITE_PROMPT).lower()
                if overwrite != 'y':
                    print(MSG_INSTALL_ABORTED)
                    return False
                shutil.rmtree(dest_path)
            
        # Move files
        shutil.copytree(source_path, dest_path)
        print(MSG_INSTALLED_SUCCESS.format(name=skill_name, path=dest_path))
        
        # Check License (skip for local skills or if --yes flag is used)
        is_local_skill = repo_url.startswith('file://') or not repo_url.startswith(('http://', 'https://', 'git@'))
        if not is_local_skill and not auto_install_deps:
            print(MSG_LICENSE_CHECKING)
            license_type = detect_license(dest_path)
            
            if license_type:
                print(MSG_LICENSE_DETECTED.format(license_type=license_type))
            else:
                print(MSG_LICENSE_NOT_FOUND)
                license_type = None
            
            # Check license compatibility
            status, message = check_license_compatibility(license_type)
            
            # Display license information
            print(MSG_LICENSE_INFO_HEADER)
            print(MSG_LICENSE_INFO_TYPE.format(license_type=license_type if license_type else "Unknown"))
            
            if status == "compatible":
                print(MSG_LICENSE_COMPATIBLE)
            elif status == "warning":
                status_text = f"{COLOR_YELLOW}Warning{COLOR_RESET}"
                print(MSG_LICENSE_INFO_STATUS.format(status=status_text))
                print(MSG_LICENSE_WARNING.format(message=message))
            elif status == "incompatible":
                status_text = f"{COLOR_RED}Incompatible{COLOR_RESET}"
                print(MSG_LICENSE_INFO_STATUS.format(status=status_text))
                print(MSG_LICENSE_INCOMPATIBLE)
                print(f"   {message}")
                
                # Ask user to confirm if license is incompatible (skip if --yes flag is used)
                if not auto_install_deps:
                    confirm = input(MSG_LICENSE_CONFIRM_INCOMPATIBLE).lower()
                    if confirm != 'y':
                        print(MSG_INSTALL_ABORTED)
                        # Clean up the installed skill
                        shutil.rmtree(dest_path)
                        return False
        
        print(MSG_REGISTRY_SYNC_REQUIRED)

        # Handle Dependencies
        dependencies = parse_skill_dependencies(dest_path)
        
        if dependencies:
            print(MSG_CHECKING_DEPENDENCIES.format(skill_name=skill_name))
            
            count = len(dependencies)
            word = "y" if count == 1 else "ies"
            print(MSG_DEPENDENCIES_FOUND.format(count=count, deps=', '.join(dependencies)))
            
            missing, installed = check_dependencies_installed(dependencies, dest_root)
            
            for dep in installed:
                print(MSG_DEPENDENCY_INSTALLED.format(dep=dep))
            
            for dep in missing:
                print(MSG_DEPENDENCY_MISSING.format(dep=dep))
            
            if missing:
                print(MSG_MISSING_DEPENDENCIES.format(deps=', '.join(missing)))
                
                install_deps = False
                if auto_install_deps:
                    print(MSG_AUTO_INSTALLING_DEPS.format(deps=f": {', '.join(missing)}"))
                    install_deps = True
                else:
                    response = input(MSG_INSTALL_DEPENDENCIES_PROMPT).lower()
                    install_deps = (response == 'y')
                
                if install_deps:
                    # Resolve installation order
                    install_order = resolve_install_order(skill_name, dependencies, dest_root)
                    
                    if install_order is None:
                        print(f"{COLOR_YELLOW}Warning: Could not resolve dependency order. Installing in original order.{COLOR_RESET}")
                        install_order = missing
                    else:
                        # Filter out the main skill and already installed skills
                        install_order = [s for s in install_order if s in missing]
                        print(MSG_INSTALL_ORDER.format(order=' -> '.join(install_order)))
                    
                    # Install dependencies
                    for dep in install_order:
                        print(MSG_INSTALLING_DEPENDENCY.format(dep=dep))
                        success = install_skill(dep, dest_root, run_audit=False, force=False, auto_install_deps=auto_install_deps)
                        if not success:
                            print(MSG_DEPENDENCY_INSTALL_FAILED.format(dep=dep))
                            return False
                    
                    print(MSG_ALL_DEPENDENCIES_INSTALLED)
        else:
            print(MSG_NO_DEPENDENCIES)

        # Run Audit
        if run_audit:
            audit_script = Path(__file__).parent.parent.parent / 'skill-auditor' / 'scripts' / 'audit_skill.py'
            if audit_script.exists():
                print(MSG_AUDIT_RUNNING)
                try:
                    subprocess.run([sys.executable, str(audit_script), str(dest_path)], check=True)
                except subprocess.CalledProcessError as e:
                    print(MSG_AUDIT_FAILED.format(error=e))
            else:
                print(MSG_AUDIT_SKIPPED)
        
        # Trigger Post-Operation Analysis
        try:
            analysis_script = Path(__file__).parent / 'post_op_analysis.py'
            if analysis_script.exists():
                subprocess.run([sys.executable, str(analysis_script), 'install', skill_name, str(dest_path)], check=False)
        except Exception as e:
            print(f"Warning: Post-operation analysis failed: {e}")
                
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Install Trae skills from git repositories or catalog",
        epilog="Examples:\n"
               "  python install_skill.py https://github.com/user/repo\n"
               "  python install_skill.py user/repo/subdir\n"
               "  python install_skill.py skill-name\n"
               "  python install_skill.py category/skill-name\n"
               "  python install_skill.py alias\n"
               "  python install_skill.py --interactive\n"
               "  python install_skill.py skill1 skill2 skill3  # Batch install",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("source", nargs='*', help="Git URL, 'user/repo/subdir', skill name, category/skill-name, or alias (not required with --interactive). Multiple sources can be provided for batch installation.")
    parser.add_argument("--path", default=".trae/skills", help="Destination directory (default: .trae/skills)")
    parser.add_argument("--no-audit", action="store_true", help="Skip running skill-auditor after install")
    parser.add_argument("--force", action="store_true", help="Force overwrite without prompting")
    parser.add_argument("--yes", action="store_true", help="Auto-install all dependencies without prompting")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode to browse and install skills from catalog")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose mode for detailed debug output")
    parser.add_argument("--http-proxy", help="HTTP proxy URL (e.g., http://proxy.example.com:8080)")
    parser.add_argument("--https-proxy", help="HTTPS proxy URL (e.g., https://proxy.example.com:8080)")
    parser.add_argument("--no-proxy", help="Comma-separated list of hosts to bypass proxy")
    
    args = parser.parse_args()
    
    # Set verbose mode
    set_verbose(args.verbose)
    
    # Setup proxy configuration
    setup_proxy(args.http_proxy, args.https_proxy, args.no_proxy)
    
    if args.interactive:
        print(f"{COLOR_RED}Error: Interactive mode is not available without skill_catalog.{COLOR_RESET}")
        print("Please use a direct Git URL or user/repo format.")
        sys.exit(1)
    
    if not args.source:
        parser.print_help()
        sys.exit(1)
    
    if len(args.source) == 1:
        success = install_skill(args.source[0], args.path, not args.no_audit, args.force, args.yes)
        sys.exit(0 if success else 1)
    else:
        success = batch_install(args.source, args.path, not args.no_audit, args.force, args.yes)
        sys.exit(0 if success else 1)
