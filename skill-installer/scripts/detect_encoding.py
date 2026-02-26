#!/usr/bin/env python3
"""
Encoding Detection Tool - Detect file encoding using chardet library.
Supports single file detection and batch detection for directories.
"""

import sys
import os
import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import chardet
except ImportError:
    print("Error: chardet library is required. Install it with: pip install chardet")
    sys.exit(1)


def detect_file_encoding(file_path: Path, sample_size: int = 10240) -> Dict[str, Optional[str]]:
    """
    Detect the encoding of a single file.
    
    Args:
        file_path: Path to the file to detect
        sample_size: Number of bytes to read for detection (default: 10KB)
    
    Returns:
        Dictionary containing encoding information:
        - encoding: Detected encoding name (e.g., 'utf-8', 'gbk')
        - confidence: Detection confidence (0.0 to 1.0)
        - language: Detected language (optional)
        - error: Error message if detection failed
    """
    result = {
        'file': str(file_path),
        'encoding': None,
        'confidence': None,
        'language': None,
        'error': None
    }
    
    if not file_path.exists():
        result['error'] = f"File not found: {file_path}"
        return result
    
    if not file_path.is_file():
        result['error'] = f"Not a file: {file_path}"
        return result
    
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read(sample_size)
        
        if not raw_data:
            result['error'] = "File is empty"
            return result
        
        detection = chardet.detect(raw_data)
        result['encoding'] = detection.get('encoding')
        result['confidence'] = detection.get('confidence')
        result['language'] = detection.get('language')
        
    except PermissionError:
        result['error'] = f"Permission denied: {file_path}"
    except OSError as e:
        result['error'] = f"OS error reading file: {e}"
    except Exception as e:
        result['error'] = f"Unexpected error: {e}"
    
    return result


def detect_directory_encoding(
    dir_path: Path,
    extensions: Optional[List[str]] = None,
    recursive: bool = False,
    sample_size: int = 10240
) -> List[Dict[str, Optional[str]]]:
    """
    Detect encoding for all files in a directory.
    
    Args:
        dir_path: Path to the directory
        extensions: List of file extensions to check (e.g., ['.py', '.txt'])
        recursive: Whether to search recursively in subdirectories
        sample_size: Number of bytes to read for detection per file
    
    Returns:
        List of encoding detection results for each file
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
        
        result = detect_file_encoding(file_path, sample_size)
        results.append(result)
    
    return results


def format_result(result: Dict[str, Optional[str]], verbose: bool = False) -> str:
    """
    Format a detection result for display.
    
    Args:
        result: Detection result dictionary
        verbose: Whether to show detailed information
    
    Returns:
        Formatted string
    """
    if result['error']:
        return f"Error: {result['file']}\n  {result['error']}"
    
    encoding = result['encoding'] or 'Unknown'
    confidence = result['confidence'] or 0.0
    confidence_pct = f"{confidence * 100:.1f}%"
    
    output = f"{result['file']}: {encoding} ({confidence_pct})"
    
    if verbose and result['language']:
        output += f" [Language: {result['language']}]"
    
    return output


def print_summary(results: List[Dict[str, Optional[str]]]) -> None:
    """
    Print a summary of detection results.
    
    Args:
        results: List of detection results
    """
    total = len(results)
    successful = sum(1 for r in results if r['encoding'] is not None)
    failed = total - successful
    
    encoding_counts = {}
    for result in results:
        if result['encoding']:
            encoding = result['encoding'].lower()
            encoding_counts[encoding] = encoding_counts.get(encoding, 0) + 1
    
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Total files: {total}")
    print(f"  Successfully detected: {successful}")
    print(f"  Failed: {failed}")
    
    if encoding_counts:
        print("\nEncoding distribution:")
        for encoding, count in sorted(encoding_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {encoding}: {count}")
    
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Detect file encoding using chardet library",
        epilog="Examples:\n"
               "  python detect_encoding.py file.txt\n"
               "  python detect_encoding.py directory/ --recursive\n"
               "  python detect_encoding.py directory/ --extensions .py .txt\n"
               "  python detect_encoding.py file.txt --json\n"
               "  python detect_encoding.py directory/ --recursive --output results.json",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "path",
        help="File or directory path to detect encoding"
    )
    parser.add_argument(
        "--recursive", "-r",
        action="store_true",
        help="Search recursively in subdirectories (only for directories)"
    )
    parser.add_argument(
        "--extensions", "-e",
        nargs='+',
        help="File extensions to check (e.g., .py .txt .md)"
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=10240,
        help="Number of bytes to read for detection (default: 10240)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed information including language detection"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    parser.add_argument(
        "--output", "-o",
        help="Save results to a file (JSON format)"
    )
    
    args = parser.parse_args()
    
    path = Path(args.path)
    
    if path.is_file():
        results = [detect_file_encoding(path, args.sample_size)]
    elif path.is_dir():
        extensions = [ext.lower() for ext in args.extensions] if args.extensions else None
        results = detect_directory_encoding(path, extensions, args.recursive, args.sample_size)
    else:
        print(f"Error: Path not found: {path}")
        sys.exit(1)
    
    if not results:
        print("No files to process.")
        sys.exit(0)
    
    if args.json or args.output:
        output_data = {
            'path': str(path),
            'total_files': len(results),
            'successful': sum(1 for r in results if r['encoding'] is not None),
            'failed': sum(1 for r in results if r['encoding'] is None),
            'results': results
        }
        
        json_output = json.dumps(output_data, indent=2, ensure_ascii=False)
        
        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(json_output)
                print(f"Results saved to: {args.output}")
            except Exception as e:
                print(f"Error saving results: {e}")
                sys.exit(1)
        else:
            print(json_output)
    else:
        for result in results:
            print(format_result(result, args.verbose))
        
        if len(results) > 1:
            print_summary(results)


if __name__ == "__main__":
    main()
