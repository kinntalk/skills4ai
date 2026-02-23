"""
Test script with filesystem security issues
"""
import os
from pathlib import Path

def path_traversal_vulnerability(filename):
    """HIGH: Path traversal vulnerability"""
    with open(filename) as f:
        return f.read()

def unsafe_file_operations(user_id, content):
    """HIGH: Unsafe file operations"""
    filename = f"/data/{user_id}.txt"
    with open(filename, 'w') as f:
        f.write(content)

def no_permission_checks(filepath):
    """HIGH: No permission checks"""
    os.remove(filepath)

def unvalidated_path_join(base, user_path):
    """HIGH: Unvalidated path join"""
    full_path = os.path.join(base, user_path)
    with open(full_path) as f:
        return f.read()

def arbitrary_file_write(filename, content):
    """HIGH: Arbitrary file write"""
    with open(filename, 'w') as f:
        f.write(content)

def directory_traversal_read(user_path):
    """HIGH: Directory traversal read"""
    import os
    path = os.path.normpath(user_path)
    if path.startswith('..'):
        path = os.path.join('/safe', path)
    with open(path) as f:
        return f.read()
