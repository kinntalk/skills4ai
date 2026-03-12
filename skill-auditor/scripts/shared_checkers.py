#!/usr/bin/env python3
"""
Shared Checkers for skill-auditor
Common checker classes used by multiple modules.

This module eliminates code duplication between:
- quality_checks.py
- output_quality_checks.py
- security_checks.py
"""

import ast
import re
from typing import List, Set, Dict

try:
    from base_checker import BaseASTChecker
    from audit_config import (
        PRINT_COUNT_THRESHOLD, LOG_COUNT_THRESHOLD,
        FUNCTION_LENGTH_THRESHOLD, COMMENT_LENGTH_THRESHOLD,
        SENSITIVE_DATA_PATTERNS, PII_PATTERNS, PLACEHOLDER_KEYWORDS
    )
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from base_checker import BaseASTChecker
    from audit_config import (
        PRINT_COUNT_THRESHOLD, LOG_COUNT_THRESHOLD,
        FUNCTION_LENGTH_THRESHOLD, COMMENT_LENGTH_THRESHOLD,
        SENSITIVE_DATA_PATTERNS, PII_PATTERNS, PLACEHOLDER_KEYWORDS
    )


class TokenOptimizationChecker(BaseASTChecker):
    """Check for token optimization opportunities."""
    
    def __init__(self, filename: str, source_lines: List[str]):
        super().__init__(filename, source_lines)
        self.suggestions: List[str] = []
        self.function_lines: Dict[str, int] = {}
    
    def visit_FunctionDef(self, node):
        start_line = node.lineno
        end_line = getattr(node, 'end_lineno', start_line) or start_line
        func_length = end_line - start_line + 1
        self.function_lines[node.name] = func_length
        
        if func_length > FUNCTION_LENGTH_THRESHOLD:
            self.suggestions.append(
                f"{self.filename}:{start_line}: Function '{node.name}' is {func_length} lines long. "
                f"Consider splitting into smaller functions (threshold: {FUNCTION_LENGTH_THRESHOLD}).")
        
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        start_line = node.lineno
        end_line = getattr(node, 'end_lineno', start_line) or start_line
        func_length = end_line - start_line + 1
        self.function_lines[node.name] = func_length
        
        if func_length > FUNCTION_LENGTH_THRESHOLD:
            self.suggestions.append(
                f"{self.filename}:{start_line}: Async function '{node.name}' is {func_length} lines long. "
                f"Consider splitting into smaller functions (threshold: {FUNCTION_LENGTH_THRESHOLD}).")
        
        self.generic_visit(node)
    
    def visit_If(self, node):
        depth = self._get_nesting_depth(node)
        if depth > 4:
            self.suggestions.append(
                f"{self.filename}:{node.lineno}: Deep nesting detected (depth {depth}). "
                "Consider refactoring to reduce complexity.")
        self.generic_visit(node)
    
    def _get_nesting_depth(self, node, current_depth=0) -> int:
        max_depth = current_depth
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With)):
                child_depth = self._get_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
        return max_depth
    
    def check_comments(self, source_lines: List[str]) -> List[str]:
        """Check for overly long comments."""
        issues = []
        for i, line in enumerate(source_lines, 1):
            stripped = line.strip()
            if stripped.startswith('#') and len(stripped) > COMMENT_LENGTH_THRESHOLD:
                issues.append(
                    f"{self.filename}:{i}: Very long comment ({len(stripped)} chars). "
                    f"Consider shortening (threshold: {COMMENT_LENGTH_THRESHOLD}).")
        return issues


class VerboseOutputChecker(BaseASTChecker):
    """Check for verbose output patterns."""
    
    def __init__(self, filename: str, source_lines: List[str]):
        super().__init__(filename, source_lines)
        self.print_count = 0
        self.log_count = 0
        self.debug_prints: List[str] = []
    
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == 'print':
            self.print_count += 1
            
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    if any(kw in arg.value.lower() for kw in ['debug', 'test', 'xxx', 'todo', 'fixme']):
                        self.debug_prints.append(
                            f"{self.filename}:{node.lineno}: Debug print statement: '{arg.value[:50]}...'")
        
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ['debug', 'info', 'warning', 'error', 'critical']:
                self.log_count += 1
        
        self.generic_visit(node)
    
    def get_verbose_issues(self) -> List[str]:
        """Get issues related to verbose output."""
        issues = []
        
        if self.print_count > PRINT_COUNT_THRESHOLD:
            issues.append(
                f"{self.filename}: Excessive print statements ({self.print_count}). "
                f"Threshold: {PRINT_COUNT_THRESHOLD}. Consider consolidating output.")
        
        if self.log_count > LOG_COUNT_THRESHOLD:
            issues.append(
                f"{self.filename}: Excessive logging statements ({self.log_count}). "
                f"Threshold: {LOG_COUNT_THRESHOLD}. Consider reducing log verbosity.")
        
        issues.extend(self.debug_prints)
        return issues


class RedundantCodeChecker(BaseASTChecker):
    """Check for redundant code patterns."""
    
    def __init__(self, filename: str, source_lines: List[str]):
        super().__init__(filename, source_lines)
        self.imports: Set[str] = set()
        self.used_names: Set[str] = set()
        self.function_defs: Dict[str, int] = {}
    
    def visit_Import(self, node):
        for alias in node.names:
            if alias.asname:
                self.imports.add(alias.asname)
            else:
                self.imports.add(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        for alias in node.names:
            if alias.asname:
                self.imports.add(alias.asname)
            else:
                self.imports.add(alias.name)
        self.generic_visit(node)
    
    def visit_Name(self, node):
        self.used_names.add(node.id)
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        self.function_defs[node.name] = node.lineno
        
        if not node.body:
            self.add_issue(node.lineno, f"Empty function '{node.name}' detected. Remove or implement.")
        elif len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            self.add_issue(node.lineno, f"Function '{node.name}' only contains 'pass'. Remove or implement.")
        
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        self.function_defs[node.name] = node.lineno
        
        if not node.body:
            self.add_issue(node.lineno, f"Empty async function '{node.name}' detected. Remove or implement.")
        elif len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            self.add_issue(node.lineno, f"Async function '{node.name}' only contains 'pass'. Remove or implement.")
        
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        if not node.body:
            self.add_issue(node.lineno, f"Empty class '{node.name}' detected. Remove or implement.")
        elif len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            self.add_issue(node.lineno, f"Class '{node.name}' only contains 'pass'. Remove or implement.")
        
        self.generic_visit(node)
    
    def check_unused_imports(self) -> List[str]:
        """Check for unused imports."""
        issues = []
        for imp in self.imports:
            base_name = imp.split('.')[-1] if '.' in imp else imp
            if base_name not in self.used_names:
                issues.append(f"{self.filename}: Unused import '{imp}' detected. Remove to reduce code size.")
        return issues
    
    def check_duplicate_blocks(self, source_lines: List[str]) -> List[str]:
        """Check for duplicate code blocks."""
        issues = []
        code_blocks: Dict[str, int] = {}
        
        for i in range(0, len(source_lines) - 2, 3):
            block = '\n'.join(source_lines[i:i+3])
            if len(block) > 50:
                if block in code_blocks:
                    issues.append(
                        f"{self.filename}: Potential duplicate code block around line {i+1} "
                        f"(similar to line {code_blocks[block]+1}). Consider consolidating.")
                else:
                    code_blocks[block] = i
        
        return issues


class DataMaskingChecker(BaseASTChecker):
    """Check for data masking issues and sensitive data exposure."""
    
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id in ['print', 'log', 'logger', 'logging']:
            for arg in node.args:
                if isinstance(arg, ast.Name):
                    var_name = arg.id
                    if any(kw in var_name.lower() for kw in ['password', 'secret', 'token', 'key', 'credential', 'auth']):
                        self.add_issue(node.lineno,
                            f"Potential sensitive data exposure: logging variable '{var_name}'")
        self.generic_visit(node)
    
    def check_patterns(self, source_lines: List[str]) -> List[str]:
        """Check for sensitive data patterns in source lines."""
        issues = []
        for i, line in enumerate(source_lines, 1):
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('import') or stripped.startswith('from'):
                continue
            
            for pattern in SENSITIVE_DATA_PATTERNS:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    value = match.group(0)
                    if not any(ph in value.lower() for ph in PLACEHOLDER_KEYWORDS):
                        issues.append(f"{self.filename}:{i}: Potential hardcoded sensitive data: {value[:50]}...")
            
            for pattern in PII_PATTERNS:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    value = match.group(0)
                    if not any(ph in value.lower() for ph in PLACEHOLDER_KEYWORDS):
                        issues.append(f"{self.filename}:{i}: Potential hardcoded PII: {value[:50]}...")
        
        return issues
