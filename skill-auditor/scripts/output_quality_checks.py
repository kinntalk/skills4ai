#!/usr/bin/env python3
"""
Output Quality Checks for skill-auditor
Additional quality check functions for data masking, token optimization, etc.
"""

import sys
import re
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


def check_data_masking(skill_path):
    """
    Check for data masking issues and sensitive data exposure.

    Detects:
    1. Sensitive data exposure in logs
    2. Personal information in output
    3. API keys or tokens in code
    4. Credentials in error messages

    Args:
        skill_path: Path to the skill directory to scan.

    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    issues = []

    sensitive_patterns = [
        r'password\s*=\s*["\'][^"\']+["\']',
        r'api_key\s*=\s*["\'][^"\']+["\']',
        r'apikey\s*=\s*["\'][^"\']+["\']',
        r'secret\s*=\s*["\'][^"\']+["\']',
        r'token\s*=\s*["\'][^"\']+["\']',
        r'auth\s*=\s*["\'][^"\']+["\']',
        r'credential\s*=\s*["\'][^"\']+["\']',
        r'private_key\s*=\s*["\'][^"\']+["\']',
        r'ssh_key\s*=\s*["\'][^"\']+["\']',
        r'access_token\s*=\s*["\'][^"\']+["\']',
        r'refresh_token\s*=\s*["\'][^"\']+["\']',
        r'bearer\s+["\'][^"\']+["\']',
    ]

    pii_patterns = [
        r'email\s*=\s*["\'][^"\']+@[^"\']+["\']',
        r'phone\s*=\s*["\'][\d\s\-\(\)]+["\']',
        r'ssn\s*=\s*["\'][\d\s\-]+["\']',
        r'credit_card\s*=\s*["\'][\d\s\-]+["\']',
    ]

    class DataMaskingChecker(ast.NodeVisitor):
        def __init__(self, filename, source_lines):
            self.filename = filename
            self.source_lines = source_lines
            self.issues = []

        def visit_Call(self, node):
            if isinstance(node.func, ast.Name) and node.func.id in ['print', 'log', 'logger', 'logging']:
                for arg in node.args:
                    if isinstance(arg, ast.Name):
                        var_name = arg.id
                        if any(keyword in var_name.lower() for keyword in ['password', 'secret', 'token', 'key', 'credential', 'auth']):
                            self.issues.append(
                                f"{self.filename}:{node.lineno}: Potential sensitive data exposure: logging variable '{var_name}'"
                            )
            self.generic_visit(node)

    for py_file in skill_path.glob('**/*.py'):
        success, content = read_text_file(py_file)
        if not success:
            issues.append(f"Could not read {py_file.name}: {content}")
            continue
            
        source_lines = content.splitlines()

        try:
            tree = ast.parse(content, filename=str(py_file))
            checker = DataMaskingChecker(py_file.name, source_lines)
            checker.visit(tree)
            issues.extend(checker.issues)
        except SyntaxError:
            pass

        for i, line in enumerate(source_lines, 1):
            stripped = line.strip()
            if stripped.startswith('#'):
                continue

            if stripped.startswith('import') or stripped.startswith('from'):
                continue

            for pattern in sensitive_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        value = match.group(0)
                        if not any(placeholder in value.lower() for placeholder in ['todo', 'xxx', 'none', 'null', 'example', 'test']):
                            issues.append(f"{py_file.name}:{i}: Potential hardcoded sensitive data: {value[:50]}...")

            for pattern in pii_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        value = match.group(0)
                        if not any(placeholder in value.lower() for placeholder in ['todo', 'xxx', 'none', 'null', 'example', 'test']):
                            issues.append(f"{py_file.name}:{i}: Potential hardcoded PII: {value[:50]}...")

    if issues:
        return False, issues
    return True, "No data masking issues found"


def check_token_optimization(skill_path):
    """
    Analyze code for token optimization opportunities.

    Provides suggestions for:
    1. Redundant code elimination
    2. Verbose output reduction
    3. Efficient algorithm alternatives
    4. Token usage optimization tips

    Args:
        skill_path: Path to the skill directory to scan.

    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    suggestions = []

    class TokenOptimizationChecker(ast.NodeVisitor):
        def __init__(self, filename, source_lines):
            self.filename = filename
            self.source_lines = source_lines
            self.suggestions = []
            self.function_lines = {}

        def visit_FunctionDef(self, node):
            start_line = node.lineno
            end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line
            func_length = end_line - start_line + 1
            self.function_lines[node.name] = func_length

            if func_length > 50:
                self.suggestions.append(
                    f"{self.filename}:{start_line}: Function '{node.name}' is {func_length} lines long. Consider splitting into smaller functions for better token efficiency."
                )

            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node):
            start_line = node.lineno
            end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line
            func_length = end_line - start_line + 1
            self.function_lines[node.name] = func_length

            if func_length > 50:
                self.suggestions.append(
                    f"{self.filename}:{start_line}: Async function '{node.name}' is {func_length} lines long. Consider splitting into smaller functions for better token efficiency."
                )

            self.generic_visit(node)

        def visit_If(self, node):
            depth = self._get_nesting_depth(node)
            if depth > 4:
                self.suggestions.append(
                    f"{self.filename}:{node.lineno}: Deep nesting detected (depth {depth}). Consider refactoring to reduce complexity and token usage."
                )
            self.generic_visit(node)

        def _get_nesting_depth(self, node, current_depth=0):
            max_depth = current_depth
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.For, ast.While, ast.With)):
                    child_depth = self._get_nesting_depth(child, current_depth + 1)
                    max_depth = max(max_depth, child_depth)
            return max_depth

    for py_file in skill_path.glob('**/*.py'):
        success, content = read_text_file(py_file)
        if not success:
            suggestions.append(f"Could not read {py_file.name}: {content}")
            continue
            
        source_lines = content.splitlines()

        try:
            tree = ast.parse(content, filename=str(py_file))
            checker = TokenOptimizationChecker(py_file.name, source_lines)
            checker.visit(tree)
            suggestions.extend(checker.suggestions)
        except SyntaxError:
            pass

        for i, line in enumerate(source_lines, 1):
            stripped = line.strip()
            if stripped.startswith('#'):
                if len(stripped) > 200:
                    suggestions.append(
                        f"{py_file.name}:{i}: Very long comment ({len(stripped)} chars). Consider shortening or moving to documentation."
                    )

    skill_md = skill_path / 'SKILL.md'
    if skill_md.exists():
        success, content = read_text_file(skill_md)
        if success and len(content) > 10000:
            suggestions.append(
                f"SKILL.md is very long ({len(content)} chars). Consider condensing descriptions for better token efficiency."
            )

    if suggestions:
        return False, suggestions
    return True, "Code is well-optimized for token usage"


def check_ai_execution_effectiveness(skill_path):
    """
    Evaluate AI execution effectiveness in skill documentation and code.

    Assesses:
    1. Clarity of instructions in SKILL.md
    2. Conciseness of prompts
    3. Efficiency of workflows
    4. Verbose outputs

    Args:
        skill_path: Path to the skill directory to scan.

    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    issues = []

    skill_md = skill_path / 'SKILL.md'
    if skill_md.exists():
        success, content = read_text_file(skill_md)
        if success:
            lines = content.splitlines()

            current_paragraph = []
            for i, line in enumerate(lines, 1):
                if line.strip():
                    current_paragraph.append(line)
                else:
                    if current_paragraph:
                        paragraph_text = ' '.join(current_paragraph)
                        if len(paragraph_text) > 500:
                            issues.append(
                                f"SKILL.md: Very long paragraph detected (around line {i - len(current_paragraph)}). Consider breaking into shorter sections for better AI comprehension."
                            )
                    current_paragraph = []

            redundant_phrases = [
                'please note that',
                'it is important to',
                'keep in mind that',
                'it should be noted that',
                'it is worth mentioning that',
            ]

            for i, line in enumerate(lines, 1):
                for phrase in redundant_phrases:
                    if phrase in line.lower():
                        issues.append(
                            f"SKILL.md:{i}: Redundant phrase '{phrase}' detected. Remove for more concise instructions."
                        )

            vague_patterns = [
                r'\b(do it|make it|fix it|handle it)\b',
                r'\b(appropriate|suitable|proper|correct)\s+(way|manner|method)',
            ]

            for i, line in enumerate(lines, 1):
                for pattern in vague_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        issues.append(
                            f"SKILL.md:{i}: Vague instruction detected. Be more specific for better AI execution."
                        )

    for py_file in skill_path.glob('**/*.py'):
        success, content = read_text_file(py_file)
        if not success:
            continue
            
        source_lines = content.splitlines()

        print_count = 0
        for line in source_lines:
            stripped = line.strip()
            if stripped.startswith('print('):
                print_count += 1

        if print_count > 30:
            issues.append(
                f"{py_file.name}: High number of print statements ({print_count}). Consider reducing verbose output for better AI execution efficiency."
            )

    if issues:
        return False, issues
    return True, "AI execution effectiveness looks good"


def check_verbose_output(skill_path):
    """
    Detect verbose output patterns in skill code.

    Identifies:
    1. Excessive print statements
    2. Redundant logging
    3. Unnecessary debug output
    4. Output consolidation opportunities

    Args:
        skill_path: Path to the skill directory to scan.

    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    issues = []

    class VerboseOutputChecker(ast.NodeVisitor):
        def __init__(self, filename, source_lines):
            self.filename = filename
            self.source_lines = source_lines
            self.issues = []
            self.print_count = 0
            self.log_count = 0
            self.debug_prints = []

        def visit_Call(self, node):
            if isinstance(node.func, ast.Name) and node.func.id == 'print':
                self.print_count += 1

                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        if any(keyword in arg.value.lower() for keyword in ['debug', 'test', 'xxx', 'todo', 'fixme']):
                            self.debug_prints.append(
                                f"{self.filename}:{node.lineno}: Debug print statement detected: '{arg.value[:50]}...'"
                            )

            if isinstance(node.func, ast.Attribute):
                if node.func.attr in ['debug', 'info', 'warning', 'error', 'critical']:
                    self.log_count += 1

            self.generic_visit(node)

    for py_file in skill_path.glob('**/*.py'):
        success, content = read_text_file(py_file)
        if not success:
            issues.append(f"Could not read {py_file.name}: {content}")
            continue
            
        source_lines = content.splitlines()

        try:
            tree = ast.parse(content, filename=str(py_file))
            checker = VerboseOutputChecker(py_file.name, source_lines)
            checker.visit(tree)

            if checker.print_count > 20:
                issues.append(
                    f"{py_file.name}: Excessive print statements ({checker.print_count}). Consider consolidating output or using logging levels."
                )

            if checker.log_count > 30:
                issues.append(
                    f"{py_file.name}: Excessive logging statements ({checker.log_count}). Consider reducing log verbosity."
                )

            issues.extend(checker.debug_prints)

        except SyntaxError:
            pass

        consecutive_prints = 0
        for line in source_lines:
            stripped = line.strip()
            if stripped.startswith('print('):
                consecutive_prints += 1
                if consecutive_prints > 5:
                    issues.append(
                        f"{py_file.name}: Consecutive print statements detected. Consider consolidating into a single output."
                    )
                    break
            else:
                consecutive_prints = 0

    if issues:
        return False, issues
    return True, "Output verbosity is reasonable"


def check_redundant_code(skill_path):
    """
    Identify redundant code patterns in skill code.

    Finds:
    1. Duplicate code blocks
    2. Unused imports
    3. Dead code
    4. Code consolidation opportunities

    Args:
        skill_path: Path to the skill directory to scan.

    Returns:
        tuple: (success: bool, message: str | list[str])
    """
    issues = []

    class RedundantCodeChecker(ast.NodeVisitor):
        def __init__(self, filename, source_lines):
            self.filename = filename
            self.source_lines = source_lines
            self.issues = []
            self.imports = set()
            self.used_names = set()
            self.function_defs = {}

        def visit_Import(self, node):
            for alias in node.names:
                self.imports.add(alias.name)
            self.generic_visit(node)

        def visit_ImportFrom(self, node):
            for alias in node.names:
                self.imports.add(alias.name)
            self.generic_visit(node)

        def visit_Name(self, node):
            self.used_names.add(node.id)
            self.generic_visit(node)

        def visit_FunctionDef(self, node):
            self.function_defs[node.name] = node.lineno

            if not node.body:
                issues.append(f"{self.filename}:{node.lineno}: Empty function '{node.name}' detected. Remove or implement.")
            elif len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                issues.append(f"{self.filename}:{node.lineno}: Function '{node.name}' only contains 'pass'. Remove or implement.")

            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node):
            self.function_defs[node.name] = node.lineno

            if not node.body:
                issues.append(f"{self.filename}:{node.lineno}: Empty async function '{node.name}' detected. Remove or implement.")
            elif len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                issues.append(f"{self.filename}:{node.lineno}: Async function '{node.name}' only contains 'pass'. Remove or implement.")

            self.generic_visit(node)

        def visit_ClassDef(self, node):
            if not node.body:
                issues.append(f"{self.filename}:{node.lineno}: Empty class '{node.name}' detected. Remove or implement.")
            elif len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                issues.append(f"{self.filename}:{node.lineno}: Class '{node.name}' only contains 'pass'. Remove or implement.")

            self.generic_visit(node)

    for py_file in skill_path.glob('**/*.py'):
        success, content = read_text_file(py_file)
        if not success:
            issues.append(f"Could not read {py_file.name}: {content}")
            continue
            
        source_lines = content.splitlines()

        try:
            tree = ast.parse(content, filename=str(py_file))
            checker = RedundantCodeChecker(py_file.name, source_lines)
            checker.visit(tree)

            for imp in checker.imports:
                if '.' in imp:
                    base_name = imp.split('.')[-1]
                else:
                    base_name = imp

                if base_name not in checker.used_names:
                    issues.append(
                        f"{py_file.name}: Unused import '{imp}' detected. Remove to reduce code size."
                    )

            code_blocks = {}
            for i in range(0, len(source_lines) - 2, 3):
                block = '\n'.join(source_lines[i:i+3])
                if len(block) > 50:
                    if block in code_blocks:
                        issues.append(
                            f"{py_file.name}: Potential duplicate code block detected around line {i+1} (similar to line {code_blocks[block]+1}). Consider consolidating."
                        )
                    else:
                        code_blocks[block] = i

        except SyntaxError:
            pass

    if issues:
        return False, issues
    return True, "No redundant code patterns detected"
