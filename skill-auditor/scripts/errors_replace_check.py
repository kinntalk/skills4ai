#!/usr/bin/env python3
"""
Errors Replace Check for skill-auditor
Specialized checker for errors='replace' parameter in file operations.
"""

import ast
from pathlib import Path


def check_errors_replace(skill_path):
    """
    Check for errors='replace' parameter in file operations.

    Detects file operations that should use errors='replace' for robust error handling:
    1. open() calls in text mode without errors parameter
    2. read_text() calls without errors parameter
    3. write_text() calls without errors parameter
    4. subprocess text output handling without errors parameter

    Args:
        skill_path: Path to the skill directory to scan.

    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    issues = []

    class ErrorsReplaceChecker(ast.NodeVisitor):
        def __init__(self, filename, source_lines):
            self.filename = filename
            self.source_lines = source_lines
            self.issues = []
            self.docstring_lines = set()

        def _collect_docstring_lines(self, tree):
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    if node.body and isinstance(node.body[0], ast.Expr):
                        if isinstance(node.body[0].value, ast.Constant):
                            if isinstance(node.body[0].value.value, str):
                                start_line = node.body[0].lineno
                                end_line = node.body[0].end_lineno if hasattr(node.body[0], 'end_lineno') else start_line
                                for line_num in range(start_line, end_line + 1):
                                    self.docstring_lines.add(line_num)
                elif isinstance(node, ast.Module):
                    if node.body and isinstance(node.body[0], ast.Expr):
                        if isinstance(node.body[0].value, ast.Constant):
                            if isinstance(node.body[0].value.value, str):
                                start_line = node.body[0].lineno
                                end_line = node.body[0].end_lineno if hasattr(node.body[0], 'end_lineno') else start_line
                                for line_num in range(start_line, end_line + 1):
                                    self.docstring_lines.add(line_num)

        def _is_in_docstring(self, lineno):
            return lineno in self.docstring_lines

        def visit_Call(self, node):
            lineno = node.lineno
            if self._is_in_docstring(lineno):
                self.generic_visit(node)
                return

            if isinstance(node.func, ast.Name):
                if node.func.id == 'open':
                    has_errors = False
                    has_binary_mode = False
                    errors_value = None

                    for kw in node.keywords:
                        if kw.arg == 'errors':
                            has_errors = True
                            if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                                errors_value = kw.value.value

                    for arg in node.args:
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                            if 'b' in arg.value:
                                has_binary_mode = True

                    if not has_binary_mode:
                        if not has_errors:
                            self.issues.append(
                                f"{self.filename}:{lineno}: open() in text mode without errors parameter. "
                                "Add errors='replace' for robust error handling with non-UTF8 content."
                            )
                        elif errors_value not in ['replace', 'ignore', 'strict']:
                            self.issues.append(
                                f"{self.filename}:{lineno}: open() with errors='{errors_value}'. "
                                "Consider using errors='replace' for better error handling."
                            )

            if isinstance(node.func, ast.Attribute):
                if node.func.attr in ['read_text', 'write_text']:
                    has_errors = False
                    errors_value = None

                    for kw in node.keywords:
                        if kw.arg == 'errors':
                            has_errors = True
                            if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                                errors_value = kw.value.value

                    if not has_errors:
                        self.issues.append(
                            f"{self.filename}:{lineno}: {node.func.attr}() without errors parameter. "
                            "Add errors='replace' for robust error handling with non-UTF8 content."
                        )
                    elif errors_value not in ['replace', 'ignore', 'strict']:
                        self.issues.append(
                            f"{self.filename}:{lineno}: {node.func.attr}() with errors='{errors_value}'. "
                            "Consider using errors='replace' for better error handling."
                        )

                if node.func.attr == 'run' and isinstance(node.func.value, ast.Name) and node.func.value.id == 'subprocess':
                    has_errors = False
                    has_text_encoding = False

                    for kw in node.keywords:
                        if kw.arg == 'errors':
                            has_errors = True
                        if kw.arg == 'text' or kw.arg == 'encoding':
                            has_text_encoding = True

                    if has_text_encoding and not has_errors:
                        self.issues.append(
                            f"{self.filename}:{lineno}: subprocess.run() with text/encoding but no errors parameter. "
                            "Add errors='replace' to handle non-UTF8 output gracefully."
                        )

                if node.func.attr == 'check_output' and isinstance(node.func.value, ast.Name) and node.func.value.id == 'subprocess':
                    has_errors = False
                    has_text_encoding = False

                    for kw in node.keywords:
                        if kw.arg == 'errors':
                            has_errors = True
                        if kw.arg == 'text' or kw.arg == 'encoding':
                            has_text_encoding = True

                    if has_text_encoding and not has_errors:
                        self.issues.append(
                            f"{self.filename}:{lineno}: subprocess.check_output() with text/encoding but no errors parameter. "
                            "Add errors='replace' to handle non-UTF8 output gracefully."
                        )

            self.generic_visit(node)

        def visit_With(self, node):
            lineno = node.lineno
            if self._is_in_docstring(lineno):
                self.generic_visit(node)
                return

            for item in node.items:
                if isinstance(item.context_expr, ast.Call):
                    if isinstance(item.context_expr.func, ast.Name):
                        if item.context_expr.func.id == 'open':
                            has_errors = False
                            has_binary_mode = False
                            errors_value = None

                            for kw in item.context_expr.keywords:
                                if kw.arg == 'errors':
                                    has_errors = True
                                    if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                                        errors_value = kw.value.value

                            for arg in item.context_expr.args:
                                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                                    if 'b' in arg.value:
                                        has_binary_mode = True

                            if not has_binary_mode:
                                if not has_errors:
                                    self.issues.append(
                                        f"{self.filename}:{lineno}: open() in with statement (text mode) without errors parameter. "
                                        "Add errors='replace' for robust error handling."
                                    )
                                elif errors_value not in ['replace', 'ignore', 'strict']:
                                    self.issues.append(
                                        f"{self.filename}:{lineno}: open() in with statement with errors='{errors_value}'. "
                                        "Consider using errors='replace' for better error handling."
                                    )

            self.generic_visit(node)

    for py_file in skill_path.glob('**/*.py'):
        if py_file.name == 'errors_replace_check.py':
            continue
        try:
            content = py_file.read_text(encoding='utf-8')
            source_lines = content.splitlines()

            try:
                tree = ast.parse(content, filename=str(py_file))
                checker = ErrorsReplaceChecker(py_file.name, source_lines)
                checker._collect_docstring_lines(tree)
                checker.visit(tree)
                issues.extend(checker.issues)
            except SyntaxError as e:
                issues.append(f"{py_file.name}: Syntax error - {e}")
        except Exception as e:
            issues.append(f"Could not read {py_file.name}: {e}")

    if issues:
        return False, issues
    return True, "All file operations use appropriate errors parameter"
