#!/usr/bin/env python3
"""
Validate and fix skill_map.json
"""
import json
import sys

def validate_json_file(file_path):
    """Validate JSON file and fix common issues"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check for common JSON issues
        issues = []
        
        # Check if file ends with a comma
        content = f.read()
        if content.strip().endswith(','):
            issues.append("File ends with a comma (invalid JSON)")
        
        # Validate JSON structure
        if 'skills' not in data:
            issues.append("Missing 'skills' key")
        
        if 'detection_rules' not in data:
            issues.append("Missing 'detection_rules' key")
        
        if 'context_aware' not in data:
            issues.append("Missing 'context_aware' key")
        
        # Check for local_vs_global in context_aware
        if 'context_aware' in data:
            if 'local_vs_global' not in data['context_aware']:
                issues.append("Missing 'local_vs_global' in context_aware")
        
        return issues
    except Exception as e:
        print(f"Error validating file: {e}")
        sys.exit(1)

if __name__ == '__main__':
    file_path = '.trae/skills/skill_map.json'
    issues = validate_json_file(file_path)
    
    if issues:
        print("Validation Issues Found:")
        for issue in issues:
            print(f"  - {issue}")
        sys.exit(1)
    else:
        print("✓ skill_map.json is valid!")
        sys.exit(0)
