#!/usr/bin/env python3
"""
Output Quality Checks for skill-auditor
Additional quality check functions for token optimization, verbose output, etc.

Uses shared checker classes from shared_checkers.py to avoid code duplication.
"""

import ast
import re
import logging
from pathlib import Path
from typing import List, Tuple

try:
    from base_checker import BaseASTChecker
    from audit_config import (
        PRINT_COUNT_THRESHOLD, CONSECUTIVE_PRINT_THRESHOLD,
        SKILL_MD_LENGTH_THRESHOLD, PARAGRAPH_LENGTH_THRESHOLD,
        REDUNDANT_PHRASES, VAGUE_PATTERNS
    )
    from shared_checkers import (
        TokenOptimizationChecker, VerboseOutputChecker, RedundantCodeChecker
    )
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from base_checker import BaseASTChecker
    from audit_config import (
        PRINT_COUNT_THRESHOLD, CONSECUTIVE_PRINT_THRESHOLD,
        SKILL_MD_LENGTH_THRESHOLD, PARAGRAPH_LENGTH_THRESHOLD,
        REDUNDANT_PHRASES, VAGUE_PATTERNS
    )
    from shared_checkers import (
        TokenOptimizationChecker, VerboseOutputChecker, RedundantCodeChecker
    )

logger = logging.getLogger(__name__)


def check_token_optimization(skill_path: Path) -> Tuple[bool, str | List[str]]:
    """Analyze code for token optimization opportunities."""
    issues = []
    
    for py_file, content, file_issues in BaseASTChecker.scan_python_files(skill_path, {'output_quality_checks.py'}):
        issues.extend(file_issues)
        if not content:
            continue
        
        source_lines = content.splitlines()
        try:
            tree = ast.parse(content, filename=str(py_file))
            checker = TokenOptimizationChecker(py_file.name, source_lines)
            checker.collect_docstring_lines(tree)
            checker.visit(tree)
            issues.extend(checker.suggestions)
            issues.extend(checker.check_comments(source_lines))
        except SyntaxError as e:
            issues.append(f"{py_file.name}: Syntax error - {e}")
    
    skill_md = skill_path / 'SKILL.md'
    if skill_md.exists():
        try:
            content = skill_md.read_text(encoding='utf-8', errors='replace')
            if len(content) > SKILL_MD_LENGTH_THRESHOLD:
                issues.append(
                    f"SKILL.md is very long ({len(content)} chars). "
                    f"Consider condensing (threshold: {SKILL_MD_LENGTH_THRESHOLD}).")
        except (FileNotFoundError, PermissionError):
            pass
    
    if issues:
        return False, issues
    return True, "Code is well-optimized for token usage"


def check_ai_execution_effectiveness(skill_path: Path) -> Tuple[bool, str | List[str]]:
    """Evaluate AI execution effectiveness in skill documentation and code."""
    issues = []
    
    skill_md = skill_path / 'SKILL.md'
    if skill_md.exists():
        try:
            content = skill_md.read_text(encoding='utf-8', errors='replace')
            lines = content.splitlines()
            
            current_paragraph = []
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                is_table_row = stripped.startswith('|') and stripped.endswith('|')
                if stripped and not is_table_row:
                    current_paragraph.append(line)
                elif not stripped:
                    if current_paragraph:
                        paragraph_text = ' '.join(current_paragraph)
                        if len(paragraph_text) > PARAGRAPH_LENGTH_THRESHOLD:
                            issues.append(
                                f"SKILL.md: Very long paragraph (around line {i - len(current_paragraph)}). "
                                f"Consider breaking into shorter sections (threshold: {PARAGRAPH_LENGTH_THRESHOLD}).")
                    current_paragraph = []
            
            for i, line in enumerate(lines, 1):
                for phrase in REDUNDANT_PHRASES:
                    if phrase in line.lower():
                        issues.append(f"SKILL.md:{i}: Redundant phrase '{phrase}' detected.")
                
                for pattern in VAGUE_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        issues.append(f"SKILL.md:{i}: Vague instruction detected. Be more specific.")
        
        except (FileNotFoundError, PermissionError):
            issues.append("SKILL.md not found or permission denied")
    
    for py_file, content, file_issues in BaseASTChecker.scan_python_files(skill_path, {'output_quality_checks.py'}):
        issues.extend(file_issues)
        if not content:
            continue
        
        source_lines = content.splitlines()
        print_count = sum(1 for line in source_lines if line.strip().startswith('print('))
        
        if print_count > PRINT_COUNT_THRESHOLD:
            issues.append(
                f"{py_file.name}: High number of print statements ({print_count}). "
                f"Consider reducing verbose output (threshold: {PRINT_COUNT_THRESHOLD}).")
    
    if issues:
        return False, issues
    return True, "AI execution effectiveness looks good"


def check_verbose_output(skill_path: Path) -> Tuple[bool, str | List[str]]:
    """Detect verbose output patterns in skill code."""
    issues = []
    
    for py_file, content, file_issues in BaseASTChecker.scan_python_files(skill_path, {'output_quality_checks.py'}):
        issues.extend(file_issues)
        if not content:
            continue
        
        source_lines = content.splitlines()
        try:
            tree = ast.parse(content, filename=str(py_file))
            checker = VerboseOutputChecker(py_file.name, source_lines)
            checker.collect_docstring_lines(tree)
            checker.visit(tree)
            issues.extend(checker.get_verbose_issues())
        except SyntaxError as e:
            issues.append(f"{py_file.name}: Syntax error - {e}")
        
        consecutive_prints = 0
        for line in source_lines:
            stripped = line.strip()
            if stripped.startswith('print('):
                consecutive_prints += 1
                if consecutive_prints > CONSECUTIVE_PRINT_THRESHOLD:
                    issues.append(
                        f"{py_file.name}: Consecutive print statements detected. "
                        "Consider consolidating into a single output.")
                    break
            else:
                consecutive_prints = 0
    
    if issues:
        return False, issues
    return True, "Output verbosity is reasonable"


def check_redundant_code(skill_path: Path) -> Tuple[bool, str | List[str]]:
    """Identify redundant code patterns in skill code."""
    issues = []
    
    for py_file, content, file_issues in BaseASTChecker.scan_python_files(skill_path, {'output_quality_checks.py'}):
        issues.extend(file_issues)
        if not content:
            continue
        
        source_lines = content.splitlines()
        try:
            tree = ast.parse(content, filename=str(py_file))
            checker = RedundantCodeChecker(py_file.name, source_lines)
            checker.collect_docstring_lines(tree)
            checker.visit(tree)
            issues.extend(checker.issues)
            issues.extend(checker.check_unused_imports())
            issues.extend(checker.check_duplicate_blocks(source_lines))
        except SyntaxError as e:
            issues.append(f"{py_file.name}: Syntax error - {e}")
    
    if issues:
        return False, issues
    return True, "No redundant code patterns detected"
