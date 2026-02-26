#!/usr/bin/env python3
"""
Exception Handling Check for skill-auditor
Specialized checker for specific exception types instead of generic Exception.
"""

import ast
from pathlib import Path


def check_exception_handling(skill_path):
    """
    Check for specific exception types instead of generic Exception.

    Detects:
    1. Bare except clauses (except:)
    2. Generic Exception handlers (except Exception:)
    3. Suggests specific exception types based on context:
       - FileNotFoundError for file operations
       - PermissionError for permission issues
       - OSError for OS-related errors
       - ValueError for value conversion errors
       - TypeError for type errors
       - KeyError for dictionary key errors
       - AttributeError for attribute errors
       - JSONDecodeError for JSON parsing errors
       - yaml.YAMLError for YAML parsing errors

    Args:
        skill_path: Path to the skill directory to scan.

    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    issues = []

    class ExceptionHandlingChecker(ast.NodeVisitor):
        def __init__(self, filename, source_lines):
            self.filename = filename
            self.source_lines = source_lines
            self.issues = []
            self.risky_operations = []

        def visit_Call(self, node):
            risky_funcs = {
                'open': 'FileNotFoundError, PermissionError, OSError',
                'Path.open': 'FileNotFoundError, PermissionError, OSError',
                'read_text': 'FileNotFoundError, PermissionError, OSError',
                'write_text': 'FileNotFoundError, PermissionError, OSError',
                'json.load': 'FileNotFoundError, json.JSONDecodeError, ValueError',
                'json.loads': 'json.JSONDecodeError, ValueError',
                'json.dump': 'FileNotFoundError, PermissionError, TypeError, ValueError',
                'json.dumps': 'TypeError, ValueError',
                'yaml.safe_load': 'FileNotFoundError, yaml.YAMLError',
                'yaml.load': 'FileNotFoundError, yaml.YAMLError',
                'yaml.safe_dump': 'FileNotFoundError, PermissionError, yaml.YAMLError',
                'subprocess.run': 'subprocess.CalledProcessError, FileNotFoundError, PermissionError',
                'subprocess.check_output': 'subprocess.CalledProcessError, FileNotFoundError, PermissionError',
                'subprocess.Popen': 'FileNotFoundError, PermissionError, ValueError',
                'Path.unlink': 'FileNotFoundError, PermissionError, OSError',
                'Path.mkdir': 'FileExistsError, PermissionError, OSError',
                'Path.rmdir': 'FileNotFoundError, PermissionError, OSError',
                'Path.rename': 'FileNotFoundError, PermissionError, OSError',
                'Path.stat': 'FileNotFoundError, PermissionError, OSError',
            }

            if isinstance(node.func, ast.Name):
                if node.func.id in risky_funcs:
                    self.risky_operations.append((node.lineno, node.func.id, risky_funcs[node.func.id]))

            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    func_name = f"{node.func.value.id}.{node.func.attr}"
                    if func_name in risky_funcs:
                        self.risky_operations.append((node.lineno, func_name, risky_funcs[func_name]))

            self.generic_visit(node)

        def visit_Try(self, node):
            for handler in node.handlers:
                lineno = handler.lineno if hasattr(handler, 'lineno') else node.lineno

                if handler.type is None:
                    self.issues.append(
                        f"{self.filename}:{lineno}: Bare except clause detected. "
                        "Use specific exception types (e.g., except FileNotFoundError, except PermissionError)."
                    )
                elif isinstance(handler.type, ast.Name) and handler.type.id == 'Exception':
                    self.issues.append(
                        f"{self.filename}:{lineno}: Generic Exception handler detected. "
                        "Use more specific exception types for better error handling."
                    )
                elif isinstance(handler.type, ast.Name):
                    exc_name = handler.type.id
                    if exc_name in ['BaseException']:
                        self.issues.append(
                            f"{self.filename}:{lineno}: BaseException handler detected. "
                            "This catches system-exiting exceptions. Use specific exception types instead."
                        )

            self.generic_visit(node)

    for py_file in skill_path.glob('**/*.py'):
        if py_file.name == 'exception_handling_check.py':
            continue
        try:
            content = py_file.read_text(encoding='utf-8')
            source_lines = content.splitlines()

            try:
                tree = ast.parse(content, filename=str(py_file))
                checker = ExceptionHandlingChecker(py_file.name, source_lines)
                checker.visit(tree)
                issues.extend(checker.issues)
            except SyntaxError as e:
                issues.append(f"{py_file.name}: Syntax error - {e}")
        except Exception as e:
            issues.append(f"Could not read {py_file.name}: {e}")

    if issues:
        return False, issues
    return True, "Exception handling uses specific exception types"
