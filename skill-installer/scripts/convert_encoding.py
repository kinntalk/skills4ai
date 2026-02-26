#!/usr/bin/env python3
"""
Encoding Conversion Tool - Convert files from one encoding to another.
Supports single file conversion and batch conversion for directories.
Uses chardet to auto-detect source encoding if not specified.
"""

import sys
import os
import argparse
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import chardet
except ImportError:
    print("Error: chardet library is required. Install it with: pip install chardet")
    sys.exit(1)


def detect_encoding(file_path: Path, sample_size: int = 10240) -> Optional[str]:
    """
    Detect the encoding of a file.
    
    Args:
        file_path: Path to the file
        sample_size: Number of bytes to read for detection
    
    Returns:
        Detected encoding name or None if detection failed
    """
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read(sample_size)
        
        if not raw_data:
            return None
        
        detection = chardet.detect(raw_data)
        encoding = detection.get('encoding')
        confidence = detection.get('confidence', 0.0)
        
        if confidence < 0.7:
            print(f"Warning: Low confidence ({confidence:.2f}) for {file_path}")
        
        return encoding
    except Exception as e:
        print(f"Error detecting encoding for {file_path}: {e}")
        return None


def convert_file_encoding(
    file_path: Path,
    source_encoding: Optional[str],
    target_encoding: str,
    backup: bool = True,
    overwrite: bool = False,
    errors: str = 'strict'
) -> Dict[str, Optional[str]]:
    """
    Convert a file from source encoding to target encoding.
    
    Args:
        file_path: Path to the file to convert
        source_encoding: Source encoding (None to auto-detect)
        target_encoding: Target encoding (e.g., 'utf-8')
        backup: Whether to create a backup of the original file
        overwrite: Whether to overwrite the original file
        errors: Error handling strategy ('strict', 'ignore', 'replace', 'surrogateescape')
    
    Returns:
        Dictionary containing conversion result:
        - file: File path
        - source_encoding: Detected or specified source encoding
        - target_encoding: Target encoding
        - success: Whether conversion succeeded
        - error: Error message if conversion failed
        - backup_path: Path to backup file if created
    """
    result = {
        'file': str(file_path),
        'source_encoding': source_encoding,
        'target_encoding': target_encoding,
        'success': False,
        'error': None,
        'backup_path': None
    }
    
    if not file_path.exists():
        result['error'] = f"File not found: {file_path}"
        return result
    
    if not file_path.is_file():
        result['error'] = f"Not a file: {file_path}"
        return result
    
    try:
        if source_encoding is None:
            source_encoding = detect_encoding(file_path)
            result['source_encoding'] = source_encoding
            
            if source_encoding is None:
                result['error'] = "Failed to detect source encoding"
                return result
            
            print(f"Detected encoding: {source_encoding}")
        
        if source_encoding.lower() == target_encoding.lower():
            result['success'] = True
            result['error'] = "File already in target encoding"
            return result
        
        backup_path = None
        if backup:
            backup_path = file_path.with_suffix(file_path.suffix + '.bak')
            if backup_path.exists():
                counter = 1
                while backup_path.exists():
                    backup_path = file_path.with_suffix(f"{file_path.suffix}.bak.{counter}")
                    counter += 1
            
            shutil.copy2(file_path, backup_path)
            result['backup_path'] = str(backup_path)
            print(f"Backup created: {backup_path}")
        
        with open(file_path, 'r', encoding=source_encoding, errors=errors) as f:
            content = f.read()
        
        if overwrite:
            with open(file_path, 'w', encoding=target_encoding, errors=errors) as f:
                f.write(content)
            print(f"Converted: {file_path}")
        else:
            output_path = file_path.with_suffix(f"{file_path.suffix}.{target_encoding}")
            with open(output_path, 'w', encoding=target_encoding, errors=errors) as f:
                f.write(content)
            print(f"Converted to: {output_path}")
        
        result['success'] = True
        
    except UnicodeDecodeError as e:
        result['error'] = f"Unicode decode error: {e}"
        print(f"Error decoding {file_path}: {e}")
        print(f"Try using a different source encoding or error handling strategy")
    except UnicodeEncodeError as e:
        result['error'] = f"Unicode encode error: {e}"
        print(f"Error encoding {file_path}: {e}")
        print(f"Try using a different target encoding or error handling strategy")
    except PermissionError:
        result['error'] = f"Permission denied: {file_path}"
        print(f"Error: Permission denied for {file_path}")
    except OSError as e:
        result['error'] = f"OS error: {e}"
        print(f"OS error for {file_path}: {e}")
    except Exception as e:
        result['error'] = f"Unexpected error: {e}"
        print(f"Unexpected error for {file_path}: {e}")
    
    return result


def convert_directory_encoding(
    dir_path: Path,
    source_encoding: Optional[str],
    target_encoding: str,
    extensions: Optional[List[str]] = None,
    recursive: bool = False,
    backup: bool = True,
    overwrite: bool = False,
    errors: str = 'strict'
) -> List[Dict[str, Optional[str]]]:
    """
    Convert encoding for all files in a directory.
    
    Args:
        dir_path: Path to the directory
        source_encoding: Source encoding (None to auto-detect)
        target_encoding: Target encoding
        extensions: List of file extensions to convert
        recursive: Whether to search recursively
        backup: Whether to create backups
        overwrite: Whether to overwrite original files
        errors: Error handling strategy
    
    Returns:
        List of conversion results
    """
    if not dir_path.exists():
        print(f"Error: Directory not found: {dir_path}")
        return []
    
    if not dir_path.is_dir():
        print(f"Error: Not a directory: {dir_path}")
        return []
    
    results = []
    
    if recursive:
        file_pattern = '**/*'
    else:
        file_pattern = '*'
    
    files = dir_path.glob(file_pattern)
    
    for file_path in files:
        if not file_path.is_file():
            continue
        
        if extensions:
            if file_path.suffix.lower() not in extensions:
                continue
        
        result = convert_file_encoding(
            file_path,
            source_encoding,
            target_encoding,
            backup,
            overwrite,
            errors
        )
        results.append(result)
    
    return results


def print_summary(results: List[Dict[str, Optional[str]]]) -> None:
    """
    Print a summary of conversion results.
    
    Args:
        results: List of conversion results
    """
    total = len(results)
    successful = sum(1 for r in results if r['success'])
    failed = total - successful
    
    source_encoding_counts = {}
    for result in results:
        if result['source_encoding']:
            encoding = result['source_encoding'].lower()
            source_encoding_counts[encoding] = source_encoding_counts.get(encoding, 0) + 1
    
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Total files: {total}")
    print(f"  Successfully converted: {successful}")
    print(f"  Failed: {failed}")
    
    if source_encoding_counts:
        print("\nSource encoding distribution:")
        for encoding, count in sorted(source_encoding_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {encoding}: {count}")
    
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Convert files from one encoding to another",
        epilog="Examples:\n"
               "  python convert_encoding.py file.txt --target utf-8\n"
               "  python convert_encoding.py file.txt --source gbk --target utf-8\n"
               "  python convert_encoding.py directory/ --target utf-8 --recursive\n"
               "  python convert_encoding.py directory/ --target utf-8 --extensions .py .txt\n"
               "  python convert_encoding.py file.txt --target utf-8 --no-backup --overwrite\n"
               "  python convert_encoding.py file.txt --target utf-8 --errors replace",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "path",
        help="File or directory path to convert"
    )
    parser.add_argument(
        "--source", "-s",
        help="Source encoding (auto-detect if not specified)"
    )
    parser.add_argument(
        "--target", "-t",
        required=True,
        help="Target encoding (e.g., utf-8, gbk, gb2312)"
    )
    parser.add_argument(
        "--recursive", "-r",
        action="store_true",
        help="Search recursively in subdirectories (only for directories)"
    )
    parser.add_argument(
        "--extensions", "-e",
        nargs='+',
        help="File extensions to convert (e.g., .py .txt .md)"
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Do not create backup files"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite original files (default: create new file with encoding suffix)"
    )
    parser.add_argument(
        "--errors",
        choices=['strict', 'ignore', 'replace', 'surrogateescape'],
        default='strict',
        help="Error handling strategy (default: strict)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be converted without actually converting"
    )
    
    args = parser.parse_args()
    
    path = Path(args.path)
    target_encoding = args.target
    source_encoding = args.source
    backup = not args.no_backup
    overwrite = args.overwrite
    
    if args.dry_run:
        print("Dry run mode - no files will be modified")
        print(f"Target encoding: {target_encoding}")
        if source_encoding:
            print(f"Source encoding: {source_encoding}")
        else:
            print("Source encoding: auto-detect")
        print()
    
    if path.is_file():
        if args.dry_run:
            detected = detect_encoding(path) if not source_encoding else source_encoding
            print(f"Would convert: {path}")
            print(f"  Source: {detected}")
            print(f"  Target: {target_encoding}")
            print(f"  Backup: {'Yes' if backup else 'No'}")
            print(f"  Overwrite: {'Yes' if overwrite else 'No'}")
        else:
            result = convert_file_encoding(
                path,
                source_encoding,
                target_encoding,
                backup,
                overwrite,
                args.errors
            )
            
            if not result['success']:
                print(f"Failed: {result['error']}")
                sys.exit(1)
    elif path.is_dir():
        extensions = [ext.lower() for ext in args.extensions] if args.extensions else None
        
        if args.dry_run:
            if extensions:
                print(f"File extensions: {', '.join(extensions)}")
            print(f"Recursive: {'Yes' if args.recursive else 'No'}")
            print()
            
            file_pattern = '**/*' if args.recursive else '*'
            files = list(path.glob(file_pattern))
            files = [f for f in files if f.is_file()]
            
            if extensions:
                files = [f for f in files if f.suffix.lower() in extensions]
            
            print(f"Would convert {len(files)} file(s):")
            for file_path in files:
                detected = detect_encoding(file_path) if not source_encoding else source_encoding
                print(f"  {file_path}")
                print(f"    Source: {detected}")
                print(f"    Target: {target_encoding}")
        else:
            results = convert_directory_encoding(
                path,
                source_encoding,
                target_encoding,
                extensions,
                args.recursive,
                backup,
                overwrite,
                args.errors
            )
            
            if not results:
                print("No files to process.")
                sys.exit(0)
            
            print_summary(results)
            
            failed = sum(1 for r in results if not r['success'])
            if failed > 0:
                sys.exit(1)
    else:
        print(f"Error: Path not found: {path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
