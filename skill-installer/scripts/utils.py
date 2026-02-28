"""
Shared utility functions for skill-installer.

This module contains common functions used across multiple scripts,
including path validation, input sanitization, and security utilities.
"""

import os
import re
from pathlib import Path
from urllib.parse import urlparse

# Import messages for verbose printing
try:
    from messages import (
        MSG_VERBOSE_ENABLED,
        MSG_VERBOSE_GIT_COMMAND,
        MSG_VERBOSE_GIT_OUTPUT,
        MSG_VERBOSE_FILE_OP,
        MSG_VERBOSE_STATE_CHANGE,
        MSG_VERBOSE_DEPENDENCY_CHECK,
    )
except ImportError:
    # Fallback if messages.py not found
    MSG_VERBOSE_ENABLED = "\033[96m[INFO] Verbose mode enabled\033[0m"
    MSG_VERBOSE_GIT_COMMAND = "\033[96m[GIT] Running: {cmd}\033[0m"
    MSG_VERBOSE_GIT_OUTPUT = "\033[96m[GIT] Output: {output}\033[0m"
    MSG_VERBOSE_FILE_OP = "\033[96m[FILE] {op}: {path}\033[0m"
    MSG_VERBOSE_STATE_CHANGE = "\033[96m[STATE] {description}\033[0m"
    MSG_VERBOSE_DEPENDENCY_CHECK = "\033[96m[DEP] Checking dependency: {dep}\033[0m"

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


def validate_and_sanitize_path(base_path: Path, user_path: str) -> Path:
    """
    Validate and sanitize a user-provided path to prevent path traversal attacks.
    
    Args:
        base_path: The base directory path (e.g., SKILLS_DIR)
        user_path: The user-provided path component (e.g., subdir, skill name)
    
    Returns:
        The validated and sanitized absolute path
    
    Raises:
        ValueError: If the path is invalid or contains path traversal attempts
    """
    if not user_path:
        return base_path
    
    # Remove any path traversal attempts
    sanitized = user_path.replace('..', '').replace('/', '').replace('\\', '')
    
    if not sanitized:
        raise ValueError(f"Invalid path: '{user_path}' contains only path traversal characters")
    
    # Build the final path
    final_path = base_path / sanitized
    
    # Resolve to absolute path
    resolved_path = final_path.resolve()
    base_resolved = base_path.resolve()
    
    # Ensure the resolved path is within the base path
    try:
        resolved_path.relative_to(base_resolved)
    except ValueError:
        raise ValueError(f"Path traversal detected: '{user_path}' resolves outside base directory")
    
    return resolved_path


def validate_url(url: str) -> bool:
    """
    Validate a URL to ensure it's properly formatted.
    
    Args:
        url: The URL to validate
    
    Returns:
        True if the URL is valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_skill_name(name: str) -> bool:
    """
    Validate a skill name to ensure it's properly formatted.
    
    Args:
        name: The skill name to validate
    
    Returns:
        True if the skill name is valid, False otherwise
    """
    if not name:
        return False
    
    # Check for invalid characters
    if re.search(r'[<>:"|?*]', name):
        return False
    
    # Check for path traversal
    if '..' in name or name.startswith('/') or name.startswith('\\'):
        return False
    
    # Check length
    if len(name) > 100:
        return False
    
    return True


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to remove potentially dangerous characters.
    
    Args:
        filename: The filename to sanitize
    
    Returns:
        The sanitized filename
    """
    # Remove path separators and special characters
    sanitized = re.sub(r'[<>:"|?*]', '', filename)
    sanitized = sanitized.replace('/', '').replace('\\', '').replace('..', '')
    
    return sanitized


def is_safe_path(path: Path, base_path: Path) -> bool:
    """
    Check if a path is safe (within the base path).
    
    Args:
        path: The path to check
        base_path: The base directory path
    
    Returns:
        True if the path is safe, False otherwise
    """
    try:
        path.resolve().relative_to(base_path.resolve())
        return True
    except ValueError:
        return False
