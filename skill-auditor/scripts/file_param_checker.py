#!/usr/bin/env python3
"""
File Parameter Checker - Base class for file operation parameter checks.
Provides a unified framework for checking encoding, errors, and other parameters.
"""

import ast
from pathlib import Path
from typing import List, Tuple, Optional

try:
    from base_checker import BaseASTChecker
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from base_checker import BaseASTChecker


class FileParameterChecker(BaseASTChecker):
    """
    Base checker for file operation parameters.
    
    Subclasses should define:
    - PARAM_NAME: The parameter name to check (e.g., 'encoding', 'errors')
    - RECOMMENDED_VALUES: List of recommended values (e.g., ['utf-8', 'utf8'])
    - PARAM_DESCRIPTION: Description for error messages
    """
    
    PARAM_NAME: str = ''
    RECOMMENDED_VALUES: List[str] = []
    PARAM_DESCRIPTION: str = ''
    
    def _extract_param_value(self, node) -> Tuple[bool, Optional[str]]:
        """
        Extract parameter value from a call node.
        
        Returns:
            Tuple of (has_param, param_value)
        """
        has_param = False
        param_value = None
        
        for kw in node.keywords:
            if kw.arg == self.PARAM_NAME:
                has_param = True
                if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                    param_value = kw.value.value
        
        return has_param, param_value
    
    def _check_binary_mode(self, node) -> bool:
        """Check if the call is in binary mode."""
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                if 'b' in arg.value:
                    return True
        return False
    
    def _is_recommended_value(self, value: str) -> bool:
        """Check if the value is in recommended values."""
        return value.lower() in [v.lower() for v in self.RECOMMENDED_VALUES]
    
    def _check_open_param(self, node, lineno: int, context: str = '') -> None:
        """
        Check open() call for the parameter.
        
        Args:
            node: The AST Call node
            lineno: Line number
            context: Additional context for error message (e.g., 'in with statement')
        """
        has_param, param_value = self._extract_param_value(node)
        has_binary_mode = self._check_binary_mode(node)
        
        if not has_binary_mode:
            context_str = f" {context}" if context else ""
            if not has_param:
                self.add_issue(lineno,
                    f"open(){context_str} in text mode without {self.PARAM_NAME} parameter. "
                    f"Add {self.PARAM_NAME}='{self.RECOMMENDED_VALUES[0]}' for {self.PARAM_DESCRIPTION}.")
            elif param_value and not self._is_recommended_value(param_value):
                self.add_issue(lineno,
                    f"open(){context_str} with {self.PARAM_NAME}='{param_value}'. "
                    f"Consider using {self.PARAM_NAME}='{self.RECOMMENDED_VALUES[0]}' for better {self.PARAM_DESCRIPTION}.")
    
    def _check_pathlib_param(self, node, lineno: int) -> None:
        """Check pathlib read_text/write_text for the parameter."""
        has_param, param_value = self._extract_param_value(node)
        
        if not has_param:
            self.add_issue(lineno,
                f"{node.func.attr}() without {self.PARAM_NAME} parameter. "
                f"Add {self.PARAM_NAME}='{self.RECOMMENDED_VALUES[0]}' for {self.PARAM_DESCRIPTION}.")
        elif param_value and not self._is_recommended_value(param_value):
            self.add_issue(lineno,
                f"{node.func.attr}() with {self.PARAM_NAME}='{param_value}'. "
                f"Consider using {self.PARAM_NAME}='{self.RECOMMENDED_VALUES[0]}' for better {self.PARAM_DESCRIPTION}.")
    
    def _check_subprocess_param(self, node, lineno: int) -> None:
        """Check subprocess calls for the parameter."""
        pass  # Subclasses can override if needed
    
    def visit_Call(self, node):
        lineno = node.lineno
        if self.is_in_docstring(lineno):
            self.generic_visit(node)
            return
        
        if isinstance(node.func, ast.Name):
            if node.func.id == 'open':
                self._check_open_param(node, lineno)
        
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ['read_text', 'write_text']:
                self._check_pathlib_param(node, lineno)
            
            if node.func.attr in ['run', 'check_output']:
                if isinstance(node.func.value, ast.Name) and node.func.value.id == 'subprocess':
                    self._check_subprocess_param(node, lineno)
        
        self.generic_visit(node)
    
    def visit_With(self, node):
        lineno = node.lineno
        if self.is_in_docstring(lineno):
            self.generic_visit(node)
            return
        
        for item in node.items:
            if isinstance(item.context_expr, ast.Call):
                if isinstance(item.context_expr.func, ast.Name):
                    if item.context_expr.func.id == 'open':
                        self._check_open_param(item.context_expr, lineno, 'in with statement')
        
        self.generic_visit(node)


class EncodingParameterChecker(FileParameterChecker):
    """Check for encoding parameter in file operations."""
    
    PARAM_NAME = 'encoding'
    RECOMMENDED_VALUES = ['utf-8', 'utf8', 'utf_8']
    PARAM_DESCRIPTION = 'cross-platform compatibility'
    
    def _check_subprocess_param(self, node, lineno: int) -> None:
        """Check subprocess calls for encoding parameter when using text mode."""
        has_encoding = False
        has_text_mode = False
        
        for kw in node.keywords:
            if kw.arg == 'encoding':
                has_encoding = True
            if kw.arg in ['text', 'universal_newlines']:
                has_text_mode = True
        
        if has_text_mode and not has_encoding:
            self.add_issue(lineno,
                f"subprocess.{node.func.attr}() with text mode but no encoding parameter. "
                f"Add encoding='utf-8' for consistent behavior across platforms.")


class ErrorsReplaceChecker(FileParameterChecker):
    """Check for errors='replace' parameter in file operations."""
    
    PARAM_NAME = 'errors'
    RECOMMENDED_VALUES = ['replace', 'ignore', 'strict']
    PARAM_DESCRIPTION = 'robust error handling with non-UTF8 content'
    
    def _check_subprocess_param(self, node, lineno: int) -> None:
        """Check subprocess calls for errors parameter when using text/encoding."""
        has_errors = False
        has_text_encoding = False
        
        for kw in node.keywords:
            if kw.arg == 'errors':
                has_errors = True
            if kw.arg in ['text', 'encoding']:
                has_text_encoding = True
        
        if has_text_encoding and not has_errors:
            self.add_issue(lineno,
                f"subprocess.{node.func.attr}() with text/encoding but no errors parameter. "
                f"Add errors='replace' to handle non-UTF8 output gracefully.")


def check_encoding_parameter(skill_path: Path) -> Tuple[bool, str | List[str]]:
    """Check for encoding parameter in file operations."""
    return BaseASTChecker.run_checker(skill_path, EncodingParameterChecker, {'file_param_checker.py'})


def check_errors_replace(skill_path: Path) -> Tuple[bool, str | List[str]]:
    """Check for errors='replace' parameter in file operations."""
    return BaseASTChecker.run_checker(skill_path, ErrorsReplaceChecker, {'file_param_checker.py'})
