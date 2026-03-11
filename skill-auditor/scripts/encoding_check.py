#!/usr/bin/env python3
"""
Encoding Check for skill-auditor
Specialized checker for encoding parameter in file operations.
"""

import ast
from pathlib import Path
import logging

try:
    from file_utils import read_text_file
except ImportError:
    from pathlib import Path
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from file_utils import read_text_file

logger = logging.getLogger(__name__)


def check_encoding_parameter(skill_path):
    """
    Check for encoding parameter in file operations.

    Detects file operations that should specify encoding parameter:
    1. open() calls in text mode without encoding parameter
    2. read_text() calls without encoding parameter
    3. write_text() calls without encoding parameter
    4. subprocess text operations without encoding parameter

    Args:
        skill_path: Path to the skill directory to scan.

    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    issues = []

    class EncodingParameterChecker(ast.NodeVisitor):
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
                    has_encoding = False
                    has_binary_mode = False
                    encoding_value = None

                    for kw in node.keywords:
                        if kw.arg == 'encoding':
                            has_encoding = True
                            if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                                encoding_value = kw.value.value

                    for arg in node.args:
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                            if 'b' in arg.value:
                                has_binary_mode = True

                    if not has_binary_mode:
                        if not has_encoding:
                            self.issues.append(
                                f"{self.filename}:{lineno}: open() in text mode without encoding parameter. "
                                "Add encoding='utf-8' for cross-platform compatibility (recommended for Chinese text)."
                            )
                        elif encoding_value and encoding_value.lower() not in ['utf-8', 'utf8', 'utf_8']:
                            self.issues.append(
                                f"{self.filename}:{lineno}: open() with encoding='{encoding_value}'. "
                                "Consider using encoding='utf-8' for better cross-platform compatibility."
                            )

            if isinstance(node.func, ast.Attribute):
                if node.func.attr in ['read_text', 'write_text']:
                    has_encoding = False
                    encoding_value = None

                    for kw in node.keywords:
                        if kw.arg == 'encoding':
                            has_encoding = True
                            if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                                encoding_value = kw.value.value

                    if not has_encoding:
                        self.issues.append(
                            f"{self.filename}:{lineno}: {node.func.attr}() without encoding parameter. "
                            "Add encoding='utf-8' for cross-platform compatibility (recommended for Chinese text)."
                        )
                    elif encoding_value and encoding_value.lower() not in ['utf-8', 'utf8', 'utf_8']:
                        self.issues.append(
                            f"{self.filename}:{lineno}: {node.func.attr}() with encoding='{encoding_value}'. "
                            "Consider using encoding='utf-8' for better cross-platform compatibility."
                        )

                if node.func.attr == 'run' and isinstance(node.func.value, ast.Name) and node.func.value.id == 'subprocess':
                    has_encoding = False
                    has_text_mode = False

                    for kw in node.keywords:
                        if kw.arg == 'encoding':
                            has_encoding = True
                        if kw.arg == 'text' or kw.arg == 'universal_newlines':
                            has_text_mode = True

                    if has_text_mode and not has_encoding:
                        self.issues.append(
                            f"{self.filename}:{lineno}: subprocess.run() with text mode but no encoding parameter. "
                            "Add encoding='utf-8' for consistent behavior across platforms."
                        )

                if node.func.attr == 'check_output' and isinstance(node.func.value, ast.Name) and node.func.value.id == 'subprocess':
                    has_encoding = False
                    has_text_mode = False

                    for kw in node.keywords:
                        if kw.arg == 'encoding':
                            has_encoding = True
                        if kw.arg == 'text' or kw.arg == 'universal_newlines':
                            has_text_mode = True

                    if has_text_mode and not has_encoding:
                        self.issues.append(
                            f"{self.filename}:{lineno}: subprocess.check_output() with text mode but no encoding parameter. "
                            "Add encoding='utf-8' for consistent behavior across platforms."
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
                            has_encoding = False
                            has_binary_mode = False
                            encoding_value = None

                            for kw in item.context_expr.keywords:
                                if kw.arg == 'encoding':
                                    has_encoding = True
                                    if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                                        encoding_value = kw.value.value

                            for arg in item.context_expr.args:
                                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                                    if 'b' in arg.value:
                                        has_binary_mode = True

                            if not has_binary_mode:
                                if not has_encoding:
                                    self.issues.append(
                                        f"{self.filename}:{lineno}: open() in with statement (text mode) without encoding parameter. "
                                        "Add encoding='utf-8' for cross-platform compatibility."
                                    )
                                elif encoding_value and encoding_value.lower() not in ['utf-8', 'utf8', 'utf_8']:
                                    self.issues.append(
                                        f"{self.filename}:{lineno}: open() in with statement with encoding='{encoding_value}'. "
                                        "Consider using encoding='utf-8' for better cross-platform compatibility."
                                    )

            self.generic_visit(node)

    for py_file in skill_path.glob('**/*.py'):
        if py_file.name == 'encoding_check.py':
            continue
        success, content = read_text_file(py_file)
        if not success:
            issues.append(f"Could not read {py_file.name}: {content}")
            continue
            
        source_lines = content.splitlines()

        try:
            tree = ast.parse(content, filename=str(py_file))
            checker = EncodingParameterChecker(py_file.name, source_lines)
            checker._collect_docstring_lines(tree)
            checker.visit(tree)
            issues.extend(checker.issues)
        except SyntaxError as e:
            issues.append(f"{py_file.name}: Syntax error - {e}")

    if issues:
        return False, issues
    return True, "All file operations use appropriate encoding parameter"
