#!/usr/bin/env python3
"""
Post-Operation Analysis Hook
Analyzes skill operations and triggers audits for core skills.
"""

import sys
import os
import subprocess
from pathlib import Path

# Import messages for consistent output
try:
    from messages import *
except ImportError:
    try:
        sys.path.append(str(Path(__file__).parent))
        from messages import *
    except ImportError:
        # Fallback if messages.py not found
        COLOR_GREEN = "\033[92m"
        COLOR_RED = "\033[91m"
        COLOR_YELLOW = "\033[93m"
        COLOR_RESET = "\033[0m"
        ICON_INFO = "[INFO]"
        ICON_WARN = "[WARN]"
        ICON_ERROR = "[FAIL]"
        ICON_SUCCESS = "[PASS]"
        ICON_SEARCH = "[SEARCH]"

# Define core skills that require strict auditing
CORE_SKILLS = ['find-skills', 'skill-creator', 'skill-installer', 'skill-auditor']

def run_audit(skill_path):
    """Run skill-auditor on a specific skill"""
    auditor_script = Path(__file__).parent.parent.parent / 'skill-auditor' / 'scripts' / 'audit_skill.py'
    if not auditor_script.exists():
        print(f"{COLOR_YELLOW}{ICON_WARN} Skill auditor not found at {auditor_script}{COLOR_RESET}")
        return False

    print(f"{ICON_INFO} Running post-operation audit on {skill_path.name}...")
    try:
        # Run with 'strict' level to catch emojis as errors
        subprocess.run([sys.executable, str(auditor_script), str(skill_path), '-l', 'strict'], check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"{COLOR_RED}{ICON_ERROR} Audit failed for {skill_path.name}{COLOR_RESET}")
        return False

def analyze_operation(operation_type, skill_name, skill_path):
    """
    Analyze the operation and trigger necessary actions.
    
    Args:
        operation_type: 'install', 'update', 'uninstall', 'create', 'package'
        skill_name: Name of the skill involved
        skill_path: Path to the skill directory (might not exist for uninstall)
    """
    print(f"\n{ICON_SEARCH} Post-operation analysis for {operation_type} on '{skill_name}'")
    
    # If a core skill was modified, run audit immediately
    if skill_name in CORE_SKILLS and operation_type in ['install', 'update', 'create']:
        if Path(skill_path).exists():
            print(f"{ICON_INFO} Core skill '{skill_name}' modified. Triggering strict audit.")
            if not run_audit(Path(skill_path)):
                print(f"{COLOR_YELLOW}{ICON_WARN} Core skill '{skill_name}' failed audit! Please review immediately.{COLOR_RESET}")
            else:
                print(f"{COLOR_GREEN}{ICON_SUCCESS} Core skill '{skill_name}' passed audit.{COLOR_RESET}")
    
    # Future: Add more sophisticated analysis logic here
    # e.g., Check for dependency conflicts, suggest updates, etc.

def main():
    if len(sys.argv) < 4:
        print("Usage: post_op_analysis.py <operation_type> <skill_name> <skill_path>")
        sys.exit(1)

    operation_type = sys.argv[1]
    skill_name = sys.argv[2]
    skill_path = sys.argv[3]

    analyze_operation(operation_type, skill_name, skill_path)

if __name__ == "__main__":
    main()
