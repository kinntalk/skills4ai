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
try:
    from messages import *
except ImportError:
    # Fallback if messages.py not found in same dir (e.g. running from root)
    try:
        sys.path.append(str(Path(__file__).parent))
        from messages import *
    except ImportError:
        # Minimal fallback constants if all else fails
        GREEN = "\033[92m"
        RED = "\033[91m"
        YELLOW = "\033[93m"
        RESET = "\033[0m"
        MSG_COMMAND_FAILED = f"{RED}Command failed: {{error}}{RESET}"
        MSG_STDERR = f"Stderr: {{stderr}}"

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
            print(MSG_COMMAND_FAILED.format(error=e))
            stderr = e.stderr.decode('utf-8', errors='replace') if hasattr(e.stderr, 'decode') else e.stderr
            print(MSG_STDERR.format(stderr=stderr))
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
            print(MSG_REGISTRY_READ_ERROR.format(error=e))

    registry['skills'][skill_name] = {
        'source': repo_url,
        'subdir': subdir,
        'version': commit_hash,
        'updated_at': datetime.datetime.now().isoformat()
    }
    
    try:
        registry_path.write_text(json.dumps(registry, indent=2), encoding='utf-8')
        print(MSG_REGISTRY_UPDATED.format(path=registry_path))
    except Exception as e:
        print(MSG_REGISTRY_WRITE_ERROR.format(error=e))

def update_skill_map(dest_root, skill_name, skill_path):
    """Update the skill_map.json file with skill metadata"""
    skill_map_path = dest_root / 'skill_map.json'
    skill_map = {'skills': {}, 'detection_rules': {'priority_order': [], 'exact_match': {}, 'partial_match': {}}}
    
    if skill_map_path.exists():
        try:
            content = skill_map_path.read_text(encoding='utf-8')
            skill_map = json.loads(content)
        except Exception as e:
            print(f"Warning: Could not read skill_map.json: {e}")
    
    # Extract metadata from SKILL.md
    skill_md = skill_path / 'SKILL.md'
    description = ""
    keywords = []
    aliases = []
    
    if skill_md.exists():
        try:
            content = skill_md.read_text(encoding='utf-8')
            match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if match:
                frontmatter = yaml.safe_load(match.group(1))
                description = frontmatter.get('description', '')
                keywords = frontmatter.get('keywords', [])
                aliases = frontmatter.get('aliases', [])
        except Exception as e:
            print(f"Warning: Could not parse SKILL.md: {e}")
    
    # Auto-generate keywords if not provided
    if not keywords:
        keywords = [skill_name.replace('-', ' ')]
        if description:
            words = re.findall(r'\b[a-zA-Z]{4,}\b', description.lower())
            keywords.extend(words[:5])
        keywords = list(set(keywords))
        print(f"Auto-generated keywords for '{skill_name}': {keywords}")
    
    # Auto-generate aliases if not provided
    if not aliases:
        aliases = [skill_name]
    
    # Add skill to skill_map
    skill_map['skills'][skill_name] = {
        'name': skill_name,
        'description': description,
        'keywords': keywords,
        'aliases': aliases
    }
    
    # Add to priority_order if not already present
    if skill_name not in skill_map['detection_rules']['priority_order']:
        skill_map['detection_rules']['priority_order'].append(skill_name)
    
    # Add exact matches based on skill name
    skill_name_lower = skill_name.lower().replace('-', ' ')
    skill_map['detection_rules']['exact_match'][skill_name_lower] = skill_name
    
    # Add partial matches based on keywords
    for keyword in keywords:
        keyword_lower = keyword.lower()
        if keyword_lower not in skill_map['detection_rules']['partial_match']:
            skill_map['detection_rules']['partial_match'][keyword_lower] = skill_name
        elif isinstance(skill_map['detection_rules']['partial_match'][keyword_lower], str):
            # Convert to list if multiple skills match
            existing = skill_map['detection_rules']['partial_match'][keyword_lower]
            skill_map['detection_rules']['partial_match'][keyword_lower] = [existing, skill_name]
        elif isinstance(skill_map['detection_rules']['partial_match'][keyword_lower], list):
            if skill_name not in skill_map['detection_rules']['partial_match'][keyword_lower]:
                skill_map['detection_rules']['partial_match'][keyword_lower].append(skill_name)
    
    try:
        skill_map_path.write_text(json.dumps(skill_map, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"Updated skill_map.json with '{skill_name}'")
    except Exception as e:
        print(f"Warning: Could not update skill_map.json: {e}")

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
            print(MSG_DEST_EXISTS.format(path=dest_path))
            if force:
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
        
        # Update Registry
        update_registry(dest_root, skill_name, repo_url, subdir, commit_hash)
        
        # Update Skill Map
        update_skill_map(dest_root, skill_name, dest_path)

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
