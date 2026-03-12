#!/usr/bin/env python3
"""
Base AST Checker for skill-auditor
Provides common functionality for all AST-based checkers.
"""

import ast
import logging
from pathlib import Path
from typing import Set, List, Tuple, Optional, Generator

try:
    from file_utils import read_text_file
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from file_utils import read_text_file

logger = logging.getLogger(__name__)


USER_INPUT_VAR_NAMES = {
    'input', 'user_input', 'user_input_data', 'data', 'payload',
    'filename', 'filepath', 'path', 'file', 'arg', 'argument',
    'user_path', 'target', 'source', 'cmd', 'command',
    'user_message', 'user_query', 'query', 'message',
    'url', 'endpoint', 'host', 'address'
}

PATH_TRAVERSAL_PATTERNS = ['../', '..\\', '%2e%2e', '%2e%2e%2f', '%2e%2e%5c', '..%2f', '..%5c', '....']

UNTRUSTED_URL_PATTERNS = [
    'http://', 'localhost', '127.0.0.1', '0.0.0.0',
    '192.168.', '10.', '172.16.', 'file://', 'ftp://',
    'telnet://', 'gopher://'
]

PROMPT_INJECTION_PATTERNS = [
    'ignore previous', 'ignore all previous', 'disregard', 'forget',
    'new instruction', 'override', 'system:', 'assistant:', 'user:',
    'role:', 'jailbreak', 'developer mode', 'bypass'
]


class BaseASTChecker(ast.NodeVisitor):
    """
    Base class for AST-based code checkers.
    
    Provides:
    - Docstring line detection (to skip docstrings in checks)
    - File scanning utilities
    - Common helper methods for user input detection
    """
    
    def __init__(self, filename: str, source_lines: List[str]):
        self.filename = filename
        self.source_lines = source_lines
        self.issues: List[str] = []
        self.docstring_lines: Set[int] = set()
    
    def collect_docstring_lines(self, tree: ast.AST) -> None:
        """Collect all line numbers that contain docstrings."""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                self._add_docstring_lines_from_node(node)
            elif isinstance(node, ast.Module):
                self._add_docstring_lines_from_node(node)
    
    def _add_docstring_lines_from_node(self, node) -> None:
        """Add docstring lines from a node to the set."""
        if not (node.body and isinstance(node.body[0], ast.Expr)):
            return
        if not isinstance(node.body[0].value, ast.Constant):
            return
        if not isinstance(node.body[0].value.value, str):
            return
        
        start_line = node.body[0].lineno
        end_line = getattr(node.body[0], 'end_lineno', start_line) or start_line
        for line_num in range(start_line, end_line + 1):
            self.docstring_lines.add(line_num)
    
    def is_in_docstring(self, lineno: int) -> bool:
        """Check if a line number is within a docstring."""
        return lineno in self.docstring_lines
    
    def is_user_input_var(self, node: ast.AST, additional_names: Set[str] = None) -> bool:
        """Check if a node is a potentially dangerous user input variable."""
        if not isinstance(node, ast.Name):
            return False
        
        dangerous_names = USER_INPUT_VAR_NAMES.copy()
        if additional_names:
            dangerous_names.update(additional_names)
        
        return node.id in dangerous_names
    
    def has_path_traversal(self, value: str) -> bool:
        """Check if a string contains path traversal patterns."""
        for pattern in PATH_TRAVERSAL_PATTERNS:
            if pattern in value:
                return True
        return False
    
    def has_untrusted_url(self, url: str) -> bool:
        """Check if a URL is potentially untrusted."""
        url_lower = url.lower()
        for pattern in UNTRUSTED_URL_PATTERNS:
            if pattern in url_lower:
                return True
        return False
    
    def has_prompt_injection_pattern(self, value: str) -> bool:
        """Check if a string contains prompt injection patterns."""
        value_lower = value.lower()
        for pattern in PROMPT_INJECTION_PATTERNS:
            if pattern in value_lower:
                return True
        return False
    
    def add_issue(self, lineno: int, message: str) -> None:
        """Add an issue with filename and line number prefix."""
        self.issues.append(f"{self.filename}:{lineno}: {message}")
    
    @staticmethod
    def scan_python_files(
        skill_path: Path, 
        exclude_files: Set[str] = None
    ) -> Generator[Tuple[Path, str, List[str]], None, None]:
        """
        Scan all Python files in a skill directory.
        
        Args:
            skill_path: Path to the skill directory
            exclude_files: Set of filenames to exclude (e.g., {'audit_skill.py'})
        
        Yields:
            Tuple of (py_file, content, issues_list)
        """
        if exclude_files is None:
            exclude_files = set()
        
        for py_file in skill_path.glob('**/*.py'):
            if py_file.name in exclude_files:
                continue
            
            success, content = read_text_file(py_file)
            if not success:
                yield py_file, "", [f"Could not read {py_file.name}: {content}"]
                continue
            
            yield py_file, content, []
    
    @classmethod
    def run_checker(
        cls,
        skill_path: Path,
        checker_class: type,
        exclude_files: Set[str] = None
    ) -> Tuple[bool, str | List[str]]:
        """
        Run a checker class on all Python files in a skill directory.
        
        Args:
            skill_path: Path to the skill directory
            checker_class: The checker class to instantiate
            exclude_files: Set of filenames to exclude
        
        Returns:
            Tuple of (success, issues_list or success_message)
        """
        issues = []
        
        for py_file, content, file_issues in cls.scan_python_files(skill_path, exclude_files):
            issues.extend(file_issues)
            if not content:
                continue
                
            source_lines = content.splitlines()
            
            try:
                tree = ast.parse(content, filename=str(py_file))
                checker = checker_class(py_file.name, source_lines)
                checker.collect_docstring_lines(tree)
                checker.visit(tree)
                issues.extend(checker.issues)
            except SyntaxError as e:
                issues.append(f"{py_file.name}: Syntax error - {e}")
        
        if issues:
            return False, issues
        return True, "Check passed"


class FileOperationTracker:
    """Track file, network, and system operations for permission abuse detection."""
    
    def __init__(self):
        self.file_operations: List[int] = []
        self.network_operations: List[int] = []
        self.system_commands: List[int] = []
    
    def add_file_op(self, lineno: int) -> None:
        self.file_operations.append(lineno)
    
    def add_network_op(self, lineno: int) -> None:
        self.network_operations.append(lineno)
    
    def add_system_cmd(self, lineno: int) -> None:
        self.system_commands.append(lineno)
    
    def get_counts(self) -> Tuple[int, int, int]:
        return (
            len(self.file_operations),
            len(self.network_operations),
            len(self.system_commands)
        )
