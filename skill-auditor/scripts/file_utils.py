#!/usr/bin/env python3
"""
File reading utilities for skill-auditor.
Implements best practices for encoding, errors, and exception handling.
"""

import logging
from pathlib import Path

try:
    import charset_normalizer
except ImportError:
    charset_normalizer = None

logger = logging.getLogger(__name__)


def read_text_file(file_path: Path, encoding: str = None) -> tuple[bool, str]:
    """
    Read text file with robust encoding handling and exception management.
    
    Implements a progressive fallback strategy:
    1. Try specified encoding (or UTF-8) with strict mode
    2. If fails, try charset_normalizer for auto-detection
    3. Try fallback encodings (GB18030, GBK, latin-1)
    4. Finally use errors='replace' as last resort
    
    Args:
        file_path: Path to the file to read
        encoding: Optional encoding to try first (defaults to UTF-8)
    
    Returns:
        tuple: (success: bool, content_or_error: str)
    """
    target_encoding = encoding or 'utf-8'
    
    try:
        content = file_path.read_text(encoding=target_encoding, errors='strict')
        return True, content
        
    except FileNotFoundError:
        return False, f"File not found: {file_path}"
        
    except PermissionError:
        return False, f"Permission denied: {file_path}"
        
    except UnicodeDecodeError as e:
        logger.debug(f"UTF-8 decode failed for {file_path}: {e}")
        
        if charset_normalizer is not None and encoding is None:
            try:
                raw_data = file_path.read_bytes()
                detected = charset_normalizer.detect(raw_data)
                guessed_encoding = detected.get('encoding')
                
                if guessed_encoding and guessed_encoding.lower() not in ['utf-8', 'utf8', 'utf_8']:
                    try:
                        content = raw_data.decode(guessed_encoding, errors='strict')
                        logger.debug(f"Auto-detected encoding {guessed_encoding} for {file_path}")
                        return True, content
                    except (UnicodeDecodeError, LookupError):
                        pass
            except Exception as detect_e:
                logger.debug(f"Encoding detection failed: {detect_e}")
        
        fallback_encodings = ['gb18030', 'gbk', 'latin-1']
        for enc in fallback_encodings:
            if enc == target_encoding:
                continue
            try:
                content = file_path.read_text(encoding=enc, errors='strict')
                logger.debug(f"Used fallback encoding {enc} for {file_path}")
                return True, content
            except (UnicodeDecodeError, LookupError):
                continue
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='replace')
            return True, content
        except Exception as final_e:
            return False, f"Failed to read file {file_path}: {final_e}"
            
    except IsADirectoryError:
        return False, f"Path is a directory, not a file: {file_path}"
        
    except OSError as e:
        return False, f"OS error reading {file_path}: {e}"
        
    except Exception as e:
        logger.error(f"Unexpected error reading {file_path}: {e}", exc_info=True)
        return False, f"Unexpected error reading {file_path}: {type(e).__name__}: {e}"


def read_text_content_safe(file_path: Path, encoding: str = None) -> str:
    """
    Read text file content, always returning a string (never raises).
    
    This is a convenience wrapper for cases where you just want the content
    or an empty string on failure.
    
    Args:
        file_path: Path to the file to read
        encoding: Optional encoding to try first
    
    Returns:
        str: File content or empty string on failure
    """
    success, result = read_text_file(file_path, encoding)
    if success:
        return result
    logger.warning(f"Failed to read {file_path}: {result}")
    return ""


def safe_read_lines(file_path: Path, encoding: str = None) -> list[str]:
    """
    Read file and return lines, with robust error handling.
    
    Args:
        file_path: Path to the file to read
        encoding: Optional encoding to try first
    
    Returns:
        list[str]: List of lines (empty list on failure)
    """
    success, content = read_text_file(file_path, encoding)
    if success:
        return content.splitlines()
    return []
