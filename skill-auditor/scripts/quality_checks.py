#!/usr/bin/env python3
"""
Quality Checks for skill-auditor
Consolidated quality analysis checks including:
- Error handling patterns
- Exception handling specificity
- Logging practices
- Input validation
- Output sanitization
- Technical standards
"""

import ast
import logging
from pathlib import Path
from typing import List, Tuple

try:
    from base_checker import BaseASTChecker
    from audit_config import RISKY_FUNCS_EXCEPTION_MAP
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from base_checker import BaseASTChecker
    from audit_config import RISKY_FUNCS_EXCEPTION_MAP

logger = logging.getLogger(__name__)


class ErrorHandlingChecker(BaseASTChecker):
    """Check for error handling patterns in risky operations."""
    
    def __init__(self, filename: str, source_lines: List[str]):
        super().__init__(filename, source_lines)
        self.risky_operations: List[Tuple[int, str, str]] = []
        self.try_blocks: List[Tuple[int, int]] = []
    
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id in RISKY_FUNCS_EXCEPTION_MAP:
                self.risky_operations.append((node.lineno, node.func.id, RISKY_FUNCS_EXCEPTION_MAP[node.func.id]))
        
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                func_name = f"{node.func.value.id}.{node.func.attr}"
                if func_name in RISKY_FUNCS_EXCEPTION_MAP:
                    self.risky_operations.append((node.lineno, func_name, RISKY_FUNCS_EXCEPTION_MAP[func_name]))
        
        self.generic_visit(node)
    
    def visit_Try(self, node):
        start_line = node.lineno
        end_line = getattr(node, 'end_lineno', start_line) or start_line
        self.try_blocks.append((start_line, end_line))
        self.generic_visit(node)
    
    def check_unprotected_operations(self) -> List[str]:
        """Check if risky operations are protected by try-except blocks."""
        issues = []
        for op_line, func_name, suggested_exceptions in self.risky_operations:
            is_protected = any(
                try_start <= op_line <= try_end
                for try_start, try_end in self.try_blocks
            )
            if not is_protected:
                issues.append(
                    f"{self.filename}:{op_line}: {func_name}() without try-except protection. "
                    f"Consider wrapping in try-except for: {suggested_exceptions}")
        return issues


class ExceptionSpecificityChecker(BaseASTChecker):
    """Check for specific exception types instead of generic Exception."""
    
    def visit_Try(self, node):
        for handler in node.handlers:
            lineno = handler.lineno if hasattr(handler, 'lineno') else node.lineno
            
            if handler.type is None:
                self.add_issue(lineno,
                    "Bare except clause detected. "
                    "Use specific exception types (e.g., except FileNotFoundError).")
            elif isinstance(handler.type, ast.Name) and handler.type.id == 'Exception':
                self.add_issue(lineno,
                    "Generic Exception handler detected. "
                    "Use more specific exception types for better error handling.")
            elif isinstance(handler.type, ast.Name) and handler.type.id in ['BaseException']:
                self.add_issue(lineno,
                    "BaseException handler detected. "
                    "This catches system-exiting exceptions. Use specific exception types instead.")
        
        self.generic_visit(node)


class LoggingPracticesChecker(BaseASTChecker):
    """Check for logging best practices."""
    
    def __init__(self, filename: str, source_lines: List[str]):
        super().__init__(filename, source_lines)
        self.log_count = 0
    
    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ['debug', 'info', 'warning', 'error', 'critical']:
                self.log_count += 1
                
                for arg in node.args:
                    if isinstance(arg, ast.Name):
                        var_name = arg.id.lower()
                        if any(kw in var_name for kw in ['password', 'secret', 'token', 'key', 'credential']):
                            self.add_issue(node.lineno,
                                f"Potential sensitive data in log: variable '{arg.id}'")
        
        self.generic_visit(node)


class InputValidationChecker(BaseASTChecker):
    """Check for input validation implementation."""
    
    def visit_Call(self, node):
        lineno = node.lineno
        if self.is_in_docstring(lineno):
            self.generic_visit(node)
            return
        
        if isinstance(node.func, ast.Name):
            if node.func.id == 'open':
                for arg in node.args:
                    if self.is_user_input_var(arg):
                        self.add_issue(lineno,
                            "open() with potential user input without validation. "
                            "Validate file paths to prevent path traversal.")
        
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ['read_text', 'write_text', 'mkdir', 'rmdir', 'unlink']:
                for arg in node.args:
                    if self.is_user_input_var(arg):
                        self.add_issue(lineno,
                            f"{node.func.attr}() with potential user input without validation. "
                            "Validate inputs to prevent security issues.")
        
        self.generic_visit(node)


class OutputSanitizationChecker(BaseASTChecker):
    """Check for output sanitization issues."""
    
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id in ['print', 'format']:
                for arg in node.args:
                    if isinstance(arg, ast.Name):
                        var_name = arg.id.lower()
                        if any(kw in var_name for kw in ['html', 'xml', 'json', 'response', 'output']):
                            self.add_issue(node.lineno,
                                f"Potential unsanitized output: variable '{arg.id}'. "
                                "Consider sanitizing output for the target format.")
        
        self.generic_visit(node)


def check_error_handling_patterns(skill_path: Path) -> Tuple[bool, str | List[str]]:
    """Check for error handling patterns."""
    issues = []
    
    for py_file, content, file_issues in BaseASTChecker.scan_python_files(skill_path, {'quality_checks.py'}):
        issues.extend(file_issues)
        if not content:
            continue
        
        source_lines = content.splitlines()
        try:
            tree = ast.parse(content, filename=str(py_file))
            checker = ErrorHandlingChecker(py_file.name, source_lines)
            checker.collect_docstring_lines(tree)
            checker.visit(tree)
            issues.extend(checker.issues)
            issues.extend(checker.check_unprotected_operations())
        except SyntaxError as e:
            issues.append(f"{py_file.name}: Syntax error - {e}")
    
    if issues:
        return False, issues
    return True, "Error handling patterns look good"


def check_exception_handling(skill_path: Path) -> Tuple[bool, str | List[str]]:
    """Check for specific exception types."""
    return BaseASTChecker.run_checker(skill_path, ExceptionSpecificityChecker, {'quality_checks.py'})


def check_logging_practices(skill_path: Path) -> Tuple[bool, str | List[str]]:
    """Check for logging best practices."""
    issues = []
    
    for py_file, content, file_issues in BaseASTChecker.scan_python_files(skill_path, {'quality_checks.py'}):
        issues.extend(file_issues)
        if not content:
            continue
        
        source_lines = content.splitlines()
        try:
            tree = ast.parse(content, filename=str(py_file))
            checker = LoggingPracticesChecker(py_file.name, source_lines)
            checker.collect_docstring_lines(tree)
            checker.visit(tree)
            issues.extend(checker.issues)
        except SyntaxError as e:
            issues.append(f"{py_file.name}: Syntax error - {e}")
    
    if issues:
        return False, issues
    return True, "Logging practices look good"


def check_input_validation(skill_path: Path) -> Tuple[bool, str | List[str]]:
    """Check for input validation implementation."""
    return BaseASTChecker.run_checker(skill_path, InputValidationChecker, {'quality_checks.py'})


def check_output_sanitization(skill_path: Path) -> Tuple[bool, str | List[str]]:
    """Check for output sanitization issues."""
    return BaseASTChecker.run_checker(skill_path, OutputSanitizationChecker, {'quality_checks.py'})


def check_technical_standards(skill_path: Path) -> Tuple[bool, str | List[str]]:
    """Check for overall technical standards compliance."""
    issues = []
    
    for py_file, content, file_issues in BaseASTChecker.scan_python_files(skill_path, {'quality_checks.py'}):
        issues.extend(file_issues)
        if not content:
            continue
        
        source_lines = content.splitlines()
        
        for i, line in enumerate(source_lines, 1):
            stripped = line.strip()
            
            if stripped == 'except:':
                issues.append(f"{py_file.name}:{i}: Bare except clause found.")
            
            if 'TODO' in line or 'FIXME' in line or 'XXX' in line:
                issues.append(f"{py_file.name}:{i}: Unresolved TODO/FIXME/XXX comment.")
    
    if issues:
        return False, issues
    return True, "Technical standards compliance looks good"
