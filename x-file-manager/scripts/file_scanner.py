#!/usr/bin/env python3
"""
Local File Scanner - A comprehensive file scanning and analysis tool for AI Agents.

Features:
- File name search (fuzzy and regex)
- File type filtering
- File size filtering
- Hash calculation (MD5, SHA1, SHA256)
- Duplicate file detection
- Large file scanning
- Empty directory detection
- Safety mechanisms (timeout, limits, loop detection)
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any

try:
    from functools import lru_cache
except ImportError:
    lru_cache = lambda maxsize=128: lambda func: func


@dataclass
class FileInfo:
    path: str
    size: int
    modified_time: float
    created_time: float
    extension: str
    hash_md5: Optional[str] = None
    hash_sha256: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'path': self.path,
            'size': self.size,
            'size_human': self._human_readable_size(self.size),
            'modified_time': datetime.fromtimestamp(self.modified_time).isoformat() if self.modified_time else None,
            'created_time': datetime.fromtimestamp(self.created_time).isoformat() if self.created_time else None,
            'extension': self.extension,
            'hash_md5': self.hash_md5,
            'hash_sha256': self.hash_sha256
        }
    
    @staticmethod
    def _human_readable_size(size: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} PB"


@dataclass
class DuplicateGroup:
    hash_value: str
    size: int
    files: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'hash': self.hash_value,
            'size': self.size,
            'size_human': FileInfo._human_readable_size(self.size),
            'file_count': len(self.files),
            'wasted_space': self.size * (len(self.files) - 1),
            'wasted_space_human': FileInfo._human_readable_size(self.size * (len(self.files) - 1)),
            'files': self.files
        }


class SafetyConfig:
    MAX_FILES = 100000
    MAX_DEPTH = 50
    MAX_EXECUTION_TIME = 300
    MAX_FILE_SIZE_FOR_HASH = 1024 * 1024 * 1024
    HASH_CHUNK_SIZE = 8192
    MAX_RESULTS = 10000


class SafetyGuard:
    def __init__(self, config: SafetyConfig = None):
        self.config = config or SafetyConfig()
        self.start_time = time.time()
        self.file_count = 0
        self.visited_paths: Set[str] = set()
        self._timeout_exceeded = False
        self._limit_exceeded = False
    
    def check_timeout(self) -> bool:
        if time.time() - self.start_time > self.config.MAX_EXECUTION_TIME:
            self._timeout_exceeded = True
            return True
        return False
    
    def check_file_limit(self) -> bool:
        self.file_count += 1
        if self.file_count > self.config.MAX_FILES:
            self._limit_exceeded = True
            return True
        return False
    
    def check_loop(self, path: str) -> bool:
        resolved = os.path.realpath(path)
        if resolved in self.visited_paths:
            return True
        self.visited_paths.add(resolved)
        return False
    
    def is_safe(self) -> bool:
        return not (self._timeout_exceeded or self._limit_exceeded)
    
    def get_status(self) -> Dict[str, Any]:
        return {
            'elapsed_time': time.time() - self.start_time,
            'files_processed': self.file_count,
            'timeout_exceeded': self._timeout_exceeded,
            'limit_exceeded': self._limit_exceeded
        }


class FileScanner:
    def __init__(self, config: SafetyConfig = None):
        self.config = config or SafetyConfig()
        self.safety = SafetyGuard(self.config)
    
    def scan_directory(
        self,
        root_path: str,
        pattern: str = None,
        extensions: List[str] = None,
        min_size: int = None,
        max_size: int = None,
        max_depth: int = None
    ) -> List[FileInfo]:
        root = Path(root_path).resolve()
        if not root.exists():
            raise FileNotFoundError(f"Path not found: {root_path}")
        
        if not root.is_dir():
            raise NotADirectoryError(f"Not a directory: {root_path}")
        
        max_depth = max_depth or self.config.MAX_DEPTH
        results = []
        regex = None
        if pattern:
            try:
                regex = re.compile(pattern, re.IGNORECASE)
            except re.error:
                regex = re.compile(re.escape(pattern), re.IGNORECASE)
        
        extensions_set = None
        if extensions:
            extensions_set = {ext.lower().lstrip('.') for ext in extensions}
        
        for item in self._walk_safe(root, max_depth):
            if self.safety.check_timeout():
                break
            
            if not item.is_file():
                continue
            
            if self.safety.check_file_limit():
                break
            
            try:
                stat = item.stat()
                size = stat.st_size
                
                if min_size is not None and size < min_size:
                    continue
                if max_size is not None and size > max_size:
                    continue
                
                ext = item.suffix.lower().lstrip('.')
                if extensions_set and ext not in extensions_set:
                    continue
                
                if regex and not regex.search(item.name) and not regex.search(str(item)):
                    continue
                
                file_info = FileInfo(
                    path=str(item),
                    size=size,
                    modified_time=stat.st_mtime,
                    created_time=stat.st_ctime,
                    extension=ext
                )
                results.append(file_info)
                
                if len(results) >= self.config.MAX_RESULTS:
                    break
                    
            except (PermissionError, OSError) as e:
                continue
        
        return results
    
    def _walk_safe(self, root: Path, max_depth: int, current_depth: int = 0):
        if current_depth > max_depth:
            return
        
        if self.safety.check_timeout():
            return
        
        if self.safety.check_loop(str(root)):
            return
        
        try:
            for item in root.iterdir():
                if self.safety.check_timeout():
                    return
                
                if item.is_symlink():
                    continue
                
                yield item
                
                if item.is_dir():
                    yield from self._walk_safe(item, max_depth, current_depth + 1)
                    
        except (PermissionError, OSError):
            return
    
    def calculate_hash(
        self,
        file_path: str,
        algorithms: List[str] = None
    ) -> Dict[str, str]:
        algorithms = algorithms or ['md5', 'sha256']
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not path.is_file():
            raise ValueError(f"Not a file: {file_path}")
        
        size = path.stat().st_size
        if size > self.config.MAX_FILE_SIZE_FOR_HASH:
            raise ValueError(f"File too large for hashing: {size} bytes")
        
        hashers = {}
        for algo in algorithms:
            try:
                hashers[algo] = hashlib.new(algo)
            except ValueError:
                raise ValueError(f"Unsupported hash algorithm: {algo}")
        
        try:
            with open(path, 'rb') as f:
                while True:
                    if self.safety.check_timeout():
                        raise TimeoutError("Hash calculation timeout")
                    
                    chunk = f.read(self.config.HASH_CHUNK_SIZE)
                    if not chunk:
                        break
                    
                    for hasher in hashers.values():
                        hasher.update(chunk)
        except PermissionError:
            raise PermissionError(f"Cannot read file: {file_path}")
        
        return {algo: hasher.hexdigest() for algo, hasher in hashers.items()}
    
    def find_duplicates(
        self,
        root_path: str,
        extensions: List[str] = None,
        min_size: int = 0,
        max_size: int = None,
        use_hash: bool = True
    ) -> List[DuplicateGroup]:
        files = self.scan_directory(
            root_path,
            extensions=extensions,
            min_size=min_size or 1,
            max_size=max_size
        )
        
        size_groups: Dict[int, List[FileInfo]] = defaultdict(list)
        for f in files:
            size_groups[f.size].append(f)
        
        potential_duplicates = {
            size: file_list 
            for size, file_list in size_groups.items() 
            if len(file_list) > 1
        }
        
        if not use_hash:
            return [
                DuplicateGroup(
                    hash_value=f"size_{size}",
                    size=size,
                    files=[f.path for f in file_list]
                )
                for size, file_list in potential_duplicates.items()
            ]
        
        hash_groups: Dict[str, List[str]] = defaultdict(list)
        hash_size_map: Dict[str, int] = {}
        
        for size, file_list in potential_duplicates.items():
            for file_info in file_list:
                if self.safety.check_timeout():
                    break
                
                try:
                    hashes = self.calculate_hash(file_info.path, ['md5'])
                    hash_value = hashes['md5']
                    hash_groups[hash_value].append(file_info.path)
                    hash_size_map[hash_value] = size
                except (PermissionError, ValueError, TimeoutError):
                    continue
        
        return [
            DuplicateGroup(
                hash_value=hash_value,
                size=hash_size_map[hash_value],
                files=files
            )
            for hash_value, files in hash_groups.items()
            if len(files) > 1
        ]
    
    def find_large_files(
        self,
        root_path: str,
        top_n: int = 20,
        extensions: List[str] = None
    ) -> List[FileInfo]:
        files = self.scan_directory(
            root_path,
            extensions=extensions
        )
        
        sorted_files = sorted(files, key=lambda x: x.size, reverse=True)
        return sorted_files[:top_n]
    
    def find_empty_directories(self, root_path: str) -> List[str]:
        root = Path(root_path).resolve()
        if not root.exists():
            raise FileNotFoundError(f"Path not found: {root_path}")
        
        empty_dirs = []
        
        for item in self._walk_safe(root, self.config.MAX_DEPTH):
            if self.safety.check_timeout():
                break
            
            if item.is_dir():
                try:
                    if not any(item.iterdir()):
                        empty_dirs.append(str(item))
                except (PermissionError, OSError):
                    continue
        
        return empty_dirs
    
    def search_by_name(
        self,
        root_path: str,
        name_pattern: str,
        fuzzy: bool = True,
        case_sensitive: bool = False
    ) -> List[FileInfo]:
        if fuzzy:
            pattern = re.escape(name_pattern)
            if not case_sensitive:
                flags = re.IGNORECASE
            else:
                flags = 0
            regex = re.compile(pattern, flags)
        else:
            if case_sensitive:
                regex = re.compile(f"^{re.escape(name_pattern)}$")
            else:
                regex = re.compile(f"^{re.escape(name_pattern)}$", re.IGNORECASE)
        
        return self.scan_directory(root_path, pattern=regex.pattern)


def format_output(data: Any, format_type: str = 'json') -> str:
    if format_type == 'json':
        if isinstance(data, list):
            if data and isinstance(data[0], FileInfo):
                return json.dumps([f.to_dict() for f in data], indent=2, ensure_ascii=False)
            elif data and isinstance(data[0], DuplicateGroup):
                return json.dumps([d.to_dict() for d in data], indent=2, ensure_ascii=False)
            else:
                return json.dumps(data, indent=2, ensure_ascii=False)
        return json.dumps(data, indent=2, ensure_ascii=False)
    return str(data)


def parse_size(size_str: str) -> int:
    size_str = size_str.strip().upper()
    multipliers = {
        'B': 1,
        'KB': 1024,
        'MB': 1024 ** 2,
        'GB': 1024 ** 3,
        'TB': 1024 ** 4
    }
    
    match = re.match(r'^(\d+(?:\.\d+)?)\s*([KMGT]?B)?$', size_str)
    if not match:
        raise ValueError(f"Invalid size format: {size_str}")
    
    value = float(match.group(1))
    unit = match.group(2) or 'B'
    
    return int(value * multipliers.get(unit, 1))


def main():
    parser = argparse.ArgumentParser(
        description='Local File Scanner - Comprehensive file scanning and analysis tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s search /path/to/search -n "report" --ext pdf
  %(prog)s large /path/to/search --top 10
  %(prog)s duplicates /path/to/search --min-size 1MB
  %(prog)s hash /path/to/file --algo md5 sha256
  %(prog)s empty-dirs /path/to/search
"""
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    search_parser = subparsers.add_parser('search', help='Search files by name pattern')
    search_parser.add_argument('path', help='Root directory to search')
    search_parser.add_argument('-n', '--name', required=True, help='File name pattern')
    search_parser.add_argument('--ext', nargs='+', help='File extensions to include')
    search_parser.add_argument('--min-size', help='Minimum file size (e.g., 100MB)')
    search_parser.add_argument('--max-size', help='Maximum file size')
    search_parser.add_argument('--fuzzy', action='store_true', default=True, help='Fuzzy matching')
    search_parser.add_argument('--case-sensitive', action='store_true', help='Case sensitive search')
    search_parser.add_argument('--max-depth', type=int, help='Maximum search depth')
    search_parser.add_argument('--format', choices=['json', 'text'], default='json', help='Output format')
    
    large_parser = subparsers.add_parser('large', help='Find largest files')
    large_parser.add_argument('path', help='Root directory to scan')
    large_parser.add_argument('--top', type=int, default=20, help='Number of files to return')
    large_parser.add_argument('--ext', nargs='+', help='File extensions to include')
    large_parser.add_argument('--format', choices=['json', 'text'], default='json', help='Output format')
    
    dup_parser = subparsers.add_parser('duplicates', help='Find duplicate files')
    dup_parser.add_argument('path', help='Root directory to scan')
    dup_parser.add_argument('--ext', nargs='+', help='File extensions to include')
    dup_parser.add_argument('--min-size', help='Minimum file size')
    dup_parser.add_argument('--max-size', help='Maximum file size')
    dup_parser.add_argument('--no-hash', action='store_true', help='Compare by size only')
    dup_parser.add_argument('--format', choices=['json', 'text'], default='json', help='Output format')
    
    hash_parser = subparsers.add_parser('hash', help='Calculate file hash')
    hash_parser.add_argument('file', help='File path')
    hash_parser.add_argument('--algo', nargs='+', default=['md5', 'sha256'], help='Hash algorithms')
    hash_parser.add_argument('--format', choices=['json', 'text'], default='json', help='Output format')
    
    empty_parser = subparsers.add_parser('empty-dirs', help='Find empty directories')
    empty_parser.add_argument('path', help='Root directory to scan')
    empty_parser.add_argument('--format', choices=['json', 'text'], default='json', help='Output format')
    
    scan_parser = subparsers.add_parser('scan', help='General file scan')
    scan_parser.add_argument('path', help='Root directory to scan')
    scan_parser.add_argument('--ext', nargs='+', help='File extensions to include')
    scan_parser.add_argument('--min-size', help='Minimum file size')
    scan_parser.add_argument('--max-size', help='Maximum file size')
    scan_parser.add_argument('--max-depth', type=int, help='Maximum scan depth')
    scan_parser.add_argument('--format', choices=['json', 'text'], default='json', help='Output format')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    scanner = FileScanner()
    
    try:
        if args.command == 'search':
            min_size = parse_size(args.min_size) if args.min_size else None
            max_size = parse_size(args.max_size) if args.max_size else None
            results = scanner.search_by_name(
                args.path,
                args.name,
                fuzzy=args.fuzzy,
                case_sensitive=args.case_sensitive
            )
            if args.ext:
                results = [f for f in results if f.extension in [e.lower().lstrip('.') for e in args.ext]]
            if min_size:
                results = [f for f in results if f.size >= min_size]
            if max_size:
                results = [f for f in results if f.size <= max_size]
            print(format_output(results, args.format))
        
        elif args.command == 'large':
            results = scanner.find_large_files(
                args.path,
                top_n=args.top,
                extensions=args.ext
            )
            print(format_output(results, args.format))
        
        elif args.command == 'duplicates':
            min_size = parse_size(args.min_size) if args.min_size else 0
            max_size = parse_size(args.max_size) if args.max_size else None
            results = scanner.find_duplicates(
                args.path,
                extensions=args.ext,
                min_size=min_size,
                max_size=max_size,
                use_hash=not args.no_hash
            )
            print(format_output(results, args.format))
        
        elif args.command == 'hash':
            results = scanner.calculate_hash(args.file, args.algo)
            print(format_output(results, args.format))
        
        elif args.command == 'empty-dirs':
            results = scanner.find_empty_directories(args.path)
            print(format_output(results, args.format))
        
        elif args.command == 'scan':
            min_size = parse_size(args.min_size) if args.min_size else None
            max_size = parse_size(args.max_size) if args.max_size else None
            results = scanner.scan_directory(
                args.path,
                extensions=args.ext,
                min_size=min_size,
                max_size=max_size,
                max_depth=args.max_depth
            )
            print(format_output(results, args.format))
        
        safety_status = scanner.safety.get_status()
        if safety_status['timeout_exceeded']:
            print(f"\nWarning: Operation timed out after {safety_status['elapsed_time']:.1f}s", file=sys.stderr)
        if safety_status['limit_exceeded']:
            print(f"\nWarning: File limit ({SafetyConfig.MAX_FILES}) exceeded", file=sys.stderr)
    
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except PermissionError as e:
        print(f"Permission denied: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Invalid argument: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
