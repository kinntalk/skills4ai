#!/usr/bin/env python3
"""
Security Checks for skill-auditor
Consolidated security analysis checks including:
- Malicious script injection
- Permission abuse
- Prompt injection
- Code execution safety
- Filesystem security
- Network security
- Data masking
"""

import ast
import logging
from pathlib import Path
from typing import List, Tuple

try:
    from base_checker import BaseASTChecker, FileOperationTracker
    from audit_config import (
        FILE_OPS_THRESHOLD, NETWORK_OPS_THRESHOLD, SYSTEM_CMDS_THRESHOLD,
        OS_DANGEROUS_FUNCS, OS_PERMISSION_FUNCS, OS_LINK_FUNCS
    )
    from shared_checkers import DataMaskingChecker
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from base_checker import BaseASTChecker, FileOperationTracker
    from audit_config import (
        FILE_OPS_THRESHOLD, NETWORK_OPS_THRESHOLD, SYSTEM_CMDS_THRESHOLD,
        OS_DANGEROUS_FUNCS, OS_PERMISSION_FUNCS, OS_LINK_FUNCS
    )
    from shared_checkers import DataMaskingChecker

logger = logging.getLogger(__name__)


class DynamicCodeExecutionChecker(BaseASTChecker):
    """
    Check for dynamic code execution safety issues.
    
    Consolidates checks for:
    - eval/exec/compile usage
    - subprocess shell=True risks
    - User input validation in dynamic code contexts
    """
    
    DANGEROUS_FUNCS = {'eval', 'exec', 'compile'}
    SUBPROCESS_FUNCS = {'run', 'call', 'Popen', 'check_output'}
    
    def visit_Call(self, node):
        lineno = node.lineno
        if self.is_in_docstring(lineno):
            self.generic_visit(node)
            return
        
        if isinstance(node.func, ast.Name):
            if node.func.id in self.DANGEROUS_FUNCS:
                has_user_input = any(
                    self.is_user_input_var(arg) for arg in node.args
                )
                if has_user_input:
                    self.add_issue(lineno,
                        f"{node.func.id}() with potential user input. "
                        "This is a CRITICAL security vulnerability.")
                else:
                    self.add_issue(lineno,
                        f"{node.func.id}() detected. "
                        "Dynamic code execution is a critical security risk. Remove or add strict validation.")
        
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                if node.func.value.id == 'subprocess' and node.func.attr in self.SUBPROCESS_FUNCS:
                    self._check_subprocess_call(node, lineno)
        
        self.generic_visit(node)
    
    def _check_subprocess_call(self, node, lineno: int) -> None:
        """Check subprocess call for security issues."""
        has_shell_true = False
        has_check_true = False
        has_user_input = any(self.is_user_input_var(arg) for arg in node.args)
        
        for kw in node.keywords:
            if kw.arg == 'shell' and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                has_shell_true = True
            if kw.arg == 'check' and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                has_check_true = True
        
        if has_shell_true and has_user_input:
            self.add_issue(lineno,
                f"subprocess.{node.func.attr}() with shell=True and user input. "
                "This is a CRITICAL command injection vulnerability.")
        elif has_shell_true and not has_check_true:
            self.add_issue(lineno,
                f"subprocess.{node.func.attr}() with shell=True and no check=True. "
                "Avoid shell=True or add check=True for safer execution.")
        elif has_shell_true:
            self.add_issue(lineno,
                f"subprocess.{node.func.attr}() with shell=True. "
                "Avoid shell=True to prevent command injection.")
        elif has_user_input:
            self.add_issue(lineno,
                f"subprocess.{node.func.attr}() with potential user input. "
                "Validate and sanitize user input before subprocess calls.")


class PermissionAbuseChecker(BaseASTChecker):
    """Check for potential permission abuse patterns."""
    
    def __init__(self, filename: str, source_lines: List[str]):
        super().__init__(filename, source_lines)
        self.tracker = FileOperationTracker()
    
    def visit_Call(self, node):
        lineno = node.lineno
        if self.is_in_docstring(lineno):
            self.generic_visit(node)
            return
        
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                if node.func.value.id == 'os':
                    if node.func.attr in OS_DANGEROUS_FUNCS:
                        self.tracker.add_system_cmd(lineno)
                        self.add_issue(lineno,
                            f"os.{node.func.attr}() detected. "
                            "Prefer subprocess.run() for better control and security.")
                    
                    if node.func.attr in OS_PERMISSION_FUNCS:
                        self.tracker.add_system_cmd(lineno)
                        for arg in node.args:
                            if self.is_user_input_var(arg):
                                self.add_issue(lineno,
                                    f"os.{node.func.attr}() with potential user input. "
                                    "This is a permission escalation risk.")
                    
                    if node.func.attr in OS_LINK_FUNCS:
                        self.tracker.add_system_cmd(lineno)
                        for arg in node.args:
                            if self.is_user_input_var(arg):
                                self.add_issue(lineno,
                                    f"os.{node.func.attr}() with potential user input. "
                                    "Link operations can be security-sensitive.")
                
                if node.func.value.id == 'subprocess' and node.func.attr in ['run', 'call', 'Popen', 'check_output']:
                    has_shell = False
                    for kw in node.keywords:
                        if kw.arg == 'shell' and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                            has_shell = True
                    self.tracker.add_system_cmd(lineno)
                    if has_shell:
                        self.add_issue(lineno,
                            f"subprocess.{node.func.attr}() with shell=True detected. "
                            "This can lead to permission abuse and command injection.")
                
                if isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name):
                        if node.func.value.id in ['requests', 'urllib', 'http', 'socket']:
                            self.tracker.add_network_op(lineno)
                        elif node.func.value.id == 'urllib.request' and node.func.attr == 'urlopen':
                            self.tracker.add_network_op(lineno)
        
        if isinstance(node.func, ast.Name):
            if node.func.id in ['open', 'execfile', 'compile']:
                self.tracker.add_file_op(lineno)
        
        self.generic_visit(node)
    
    def get_threshold_issues(self, filename: str) -> List[str]:
        """Check if operation counts exceed thresholds."""
        issues = []
        file_ops, net_ops, sys_cmds = self.tracker.get_counts()
        
        if file_ops > FILE_OPS_THRESHOLD:
            issues.append(
                f"{filename}: Excessive file operations detected ({file_ops} operations). "
                f"Threshold is {FILE_OPS_THRESHOLD}. Review if all file access is necessary.")
        
        if net_ops > NETWORK_OPS_THRESHOLD:
            issues.append(
                f"{filename}: Multiple network operations detected ({net_ops} operations). "
                f"Threshold is {NETWORK_OPS_THRESHOLD}. Ensure proper validation and error handling.")
        
        if sys_cmds > SYSTEM_CMDS_THRESHOLD:
            issues.append(
                f"{filename}: Multiple system command executions detected ({sys_cmds} operations). "
                f"Threshold is {SYSTEM_CMDS_THRESHOLD}. Review necessity and add proper safeguards.")
        
        return issues


class PromptInjectionChecker(BaseASTChecker):
    """Check for potential prompt injection vectors."""
    
    def visit_Call(self, node):
        lineno = node.lineno
        if self.is_in_docstring(lineno):
            self.generic_visit(node)
            return
        
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                if node.func.attr in ['format', 'replace', 'join', 'split', 'strip', 'lower', 'upper']:
                    for arg in node.args:
                        if self.is_user_input_var(arg):
                            self.add_issue(lineno,
                                "String operation with potential user input. "
                                "Validate and sanitize user input before string manipulation.")
        
        if isinstance(node.func, ast.BinOp):
            if isinstance(node.func.op, ast.Add):
                has_user_input = any(
                    self.is_user_input_var(arg) for arg in [node.func.left, node.func.right]
                )
                if has_user_input:
                    self.add_issue(lineno,
                        "String concatenation with potential user input. "
                        "This could be a prompt injection vector. Use proper validation.")
        
        self.generic_visit(node)
    
    def visit_Constant(self, node):
        if isinstance(node.value, str) and not self.is_in_docstring(node.lineno):
            if self.has_prompt_injection_pattern(node.value):
                self.add_issue(node.lineno,
                    "Potential prompt injection pattern detected in string literal. "
                    "Review for hardcoded injection vectors.")
        self.generic_visit(node)


class FilesystemSecurityChecker(BaseASTChecker):
    """Check for filesystem security issues."""
    
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
                            "open() with potential user input. "
                            "This is a path traversal vulnerability. Validate and sanitize file paths.")
        
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                if node.func.attr in ['open', 'read_text', 'write_text', 'read_bytes', 'write_bytes', 'mkdir', 'rmdir', 'unlink', 'remove']:
                    for arg in node.args:
                        if self.is_user_input_var(arg):
                            self.add_issue(lineno,
                                f"{node.func.attr}() with potential user input. "
                                "Validate and sanitize file paths to prevent path traversal.")
        
        self.generic_visit(node)
    
    def visit_Constant(self, node):
        if isinstance(node.value, str) and not self.is_in_docstring(node.lineno):
            if self.has_path_traversal(node.value):
                self.add_issue(node.lineno,
                    f"Path traversal pattern detected in string literal: '{node.value[:50]}...'. "
                    "Review for hardcoded path traversal vectors.")
        self.generic_visit(node)


class NetworkSecurityChecker(BaseASTChecker):
    """Check for network security issues."""
    
    def visit_Call(self, node):
        lineno = node.lineno
        if self.is_in_docstring(lineno):
            self.generic_visit(node)
            return
        
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                if node.func.value.id in ['requests', 'urllib', 'http']:
                    for arg in node.args:
                        if self.is_user_input_var(arg):
                            self.add_issue(lineno,
                                "Network request with potential user input. "
                                "Validate and sanitize URLs and parameters to prevent SSRF and injection attacks.")
                elif node.func.value.id not in ['pyautogui', 'cv2', 'np', 'numpy', 'PIL', 'Image'] and \
                     node.func.attr in ['urlopen', 'get', 'post', 'put', 'delete', 'request', 'connect']:
                    for arg in node.args:
                        if self.is_user_input_var(arg):
                            self.add_issue(lineno,
                                "Network request with potential user input. "
                                "Validate and sanitize URLs and parameters to prevent SSRF and injection attacks.")
        
        self.generic_visit(node)
    
    def visit_Constant(self, node):
        if isinstance(node.value, str) and not self.is_in_docstring(node.lineno):
            if self.has_untrusted_url(node.value):
                self.add_issue(node.lineno,
                    f"Untrusted URL pattern detected: '{node.value}'. "
                    "Review for security risks and use trusted URLs only.")
        self.generic_visit(node)


def check_malicious_script_injection(skill_path: Path) -> Tuple[bool, str | List[str]]:
    """Detect patterns of malicious script injection and dynamic code execution."""
    return BaseASTChecker.run_checker(skill_path, DynamicCodeExecutionChecker, {'security_checks.py'})


def check_permission_abuse(skill_path: Path) -> Tuple[bool, str | List[str]]:
    """Identify potential permission abuse risks."""
    issues = []
    
    for py_file, content, file_issues in BaseASTChecker.scan_python_files(skill_path, {'security_checks.py'}):
        issues.extend(file_issues)
        if not content:
            continue
        
        source_lines = content.splitlines()
        try:
            tree = ast.parse(content, filename=str(py_file))
            checker = PermissionAbuseChecker(py_file.name, source_lines)
            checker.collect_docstring_lines(tree)
            checker.visit(tree)
            issues.extend(checker.issues)
            issues.extend(checker.get_threshold_issues(py_file.name))
        except SyntaxError as e:
            issues.append(f"{py_file.name}: Syntax error - {e}")
    
    if issues:
        return False, issues
    return True, "No permission abuse patterns detected"


def check_prompt_injection(skill_path: Path) -> Tuple[bool, str | List[str]]:
    """Detect potential prompt injection vectors."""
    return BaseASTChecker.run_checker(skill_path, PromptInjectionChecker, {'security_checks.py'})


def check_code_execution_safety(skill_path: Path) -> Tuple[bool, str | List[str]]:
    """Check for code execution safety issues (alias for malicious script injection)."""
    return BaseASTChecker.run_checker(skill_path, DynamicCodeExecutionChecker, {'security_checks.py'})


def check_filesystem_security(skill_path: Path) -> Tuple[bool, str | List[str]]:
    """Check for filesystem security issues."""
    return BaseASTChecker.run_checker(skill_path, FilesystemSecurityChecker, {'security_checks.py'})


def check_network_security(skill_path: Path) -> Tuple[bool, str | List[str]]:
    """Check for network security issues."""
    return BaseASTChecker.run_checker(skill_path, NetworkSecurityChecker, {'security_checks.py'})


def check_data_masking(skill_path: Path) -> Tuple[bool, str | List[str]]:
    """Check for data masking issues and sensitive data exposure."""
    issues = []
    
    for py_file, content, file_issues in BaseASTChecker.scan_python_files(skill_path, {'security_checks.py'}):
        issues.extend(file_issues)
        if not content:
            continue
        
        source_lines = content.splitlines()
        try:
            tree = ast.parse(content, filename=str(py_file))
            checker = DataMaskingChecker(py_file.name, source_lines)
            checker.collect_docstring_lines(tree)
            checker.visit(tree)
            issues.extend(checker.issues)
            issues.extend(checker.check_patterns(source_lines))
        except SyntaxError as e:
            issues.append(f"{py_file.name}: Syntax error - {e}")
    
    if issues:
        return False, issues
    return True, "No data masking issues found"
