#!/usr/bin/env python3
"""
Internationalization (i18n) module for Skill Auditor.
Provides message dictionaries for multi-language support.
"""

import os
from typing import Dict, Any

DEFAULT_LANG = 'en'
CURRENT_LANG = os.environ.get('SKILL_LANG', 'en')

MESSAGES: Dict[str, Dict[str, Any]] = {
    'en': {
        'status': {
            'pass': '[PASS]',
            'fail': '[FAIL]',
            'warn': '[WARN]',
            'info': '[*]',
        },
        'audit': {
            'title': '[*] Auditing Skill: {name}',
            'path': '   Path: {path}',
            'level': '   Level: {level}',
            'skills_dir': '   Skills Dir: {dir}',
        },
        'sections': {
            'basic_structure': '=== Basic Structure ===',
            'dependencies': '=== Dependencies ===',
            'encoding_path_safety': '=== Encoding & Path Safety ===',
            'packaging': '=== Packaging ===',
            'subprocess_path': '=== Subprocess & Path Operations ===',
            'cross_platform': '=== Cross-Platform Compatibility ===',
            'i18n': '=== Internationalization (i18n) ===',
            'absolute_references': '=== Absolute References ===',
            'registry_map': '=== Registry & Map Consistency ===',
            'security': '=== Security Analysis ===',
            'quality': '=== Quality Checks ===',
            'output_quality': '=== Output Quality Checks ===',
        },
        'summary': {
            'title': 'Audit Summary:',
            'security_issues': '  Security Issues: {count}',
            'quality_issues': '  Quality Issues: {count}',
            'output_quality_issues': '  Output Quality Issues: {count}',
            'total_issues': '  Total Issues: {count}',
            'severity_breakdown': '\nSeverity Breakdown:',
            'critical': '  CRITICAL: {count}',
            'high': '  HIGH: {count}',
            'medium': '  MEDIUM: {count}',
            'low': '  LOW: {count}',
            'separator': '\n' + '=' * 40,
        },
        'results': {
            'errors': '[!] Audit completed with errors. Please fix issues above.',
            'warnings': '[!] Audit completed with warnings. Review issues above.',
            'passed': '[*] Skill passed all standard checks!',
        },
        'issues': {
            'dir_structure': 'Directory structure issues:',
            'encoding_issues': 'Found potential encoding issues:',
            'errors_replace': "Found file operations without errors='replace':",
            'encoding_param': 'Found file operations without encoding parameter:',
            'path_inconsistencies': 'Found path inconsistencies:',
            'subprocess_issues': 'Found potential subprocess robustness issues:',
            'risky_ops': 'Found high-risk operations:',
            'cross_platform': 'Found cross-platform compatibility issues:',
            'i18n_issues': 'Found i18n issues:',
            'absolute_refs': 'Found absolute references:',
            'registry_issues': 'Registry consistency issues:',
            'skill_map_issues': 'Skill map consistency issues:',
            'security_injection': 'Found malicious script injection patterns:',
            'permission_abuse': 'Found permission abuse patterns:',
            'prompt_injection': 'Found prompt injection vectors:',
            'code_exec_safety': 'Found code execution safety issues:',
            'filesystem_security': 'Found filesystem security issues:',
            'network_security': 'Found network security issues:',
            'tech_standards': 'Technical standards issues:',
            'error_handling': 'Error handling pattern issues:',
            'exception_specificity': 'Exception handling specificity issues:',
            'logging_practices': 'Logging practices issues:',
            'input_validation': 'Input validation issues:',
            'output_sanitization': 'Output sanitization issues:',
            'dependency_security': 'Dependency security issues:',
            'token_optimization': 'Token optimization suggestions:',
            'ai_execution': 'AI execution effectiveness issues:',
            'verbose_output': 'Verbose output patterns detected:',
            'redundant_code': 'Redundant code patterns detected:',
        },
        'warnings': {
            'file_not_found': 'Warning: File not found: {file}',
            'permission_denied': 'Warning: Permission denied: {file}',
            'decode_error': 'Warning: Could not decode {file}: {error}',
        },
        'verbose': {
            'checking': '  Checking: {file}',
        },
    },
    'zh': {
        'status': {
            'pass': '[通过]',
            'fail': '[失败]',
            'warn': '[警告]',
            'info': '[*]',
        },
        'audit': {
            'title': '[*] 审计技能: {name}',
            'path': '   路径: {path}',
            'level': '   级别: {level}',
            'skills_dir': '   技能目录: {dir}',
        },
        'sections': {
            'basic_structure': '=== 基础结构 ===',
            'dependencies': '=== 依赖项 ===',
            'encoding_path_safety': '=== 编码与路径安全 ===',
            'packaging': '=== 打包 ===',
            'subprocess_path': '=== 子进程与路径操作 ===',
            'cross_platform': '=== 跨平台兼容性 ===',
            'i18n': '=== 国际化 (i18n) ===',
            'absolute_references': '=== 绝对路径引用 ===',
            'registry_map': '=== 注册表与映射一致性 ===',
            'security': '=== 安全分析 ===',
            'quality': '=== 质量检查 ===',
            'output_quality': '=== 输出质量检查 ===',
        },
        'summary': {
            'title': '审计摘要:',
            'security_issues': '  安全问题: {count}',
            'quality_issues': '  质量问题: {count}',
            'output_quality_issues': '  输出质量问题: {count}',
            'total_issues': '  总问题数: {count}',
            'severity_breakdown': '\n严重程度分布:',
            'critical': '  严重: {count}',
            'high': '  高: {count}',
            'medium': '  中: {count}',
            'low': '  低: {count}',
            'separator': '\n' + '=' * 40,
        },
        'results': {
            'errors': '[!] 审计完成但存在错误。请修复上述问题。',
            'warnings': '[!] 审计完成但存在警告。请检查上述问题。',
            'passed': '[*] 技能通过所有标准检查!',
        },
        'issues': {
            'dir_structure': '目录结构问题:',
            'encoding_issues': '发现潜在编码问题:',
            'errors_replace': "发现文件操作缺少 errors='replace' 参数:",
            'encoding_param': '发现文件操作缺少编码参数:',
            'path_inconsistencies': '发现路径不一致问题:',
            'subprocess_issues': '发现子进程健壮性问题:',
            'risky_ops': '发现高风险操作:',
            'cross_platform': '发现跨平台兼容性问题:',
            'i18n_issues': '发现国际化问题:',
            'absolute_refs': '发现绝对路径引用:',
            'registry_issues': '注册表一致性问题:',
            'skill_map_issues': '技能映射一致性问题:',
            'security_injection': '发现恶意脚本注入模式:',
            'permission_abuse': '发现权限滥用模式:',
            'prompt_injection': '发现提示注入向量:',
            'code_exec_safety': '发现代码执行安全问题:',
            'filesystem_security': '发现文件系统安全问题:',
            'network_security': '发现网络安全问题:',
            'tech_standards': '技术标准问题:',
            'error_handling': '错误处理模式问题:',
            'exception_specificity': '异常处理特异性问题:',
            'logging_practices': '日志实践问题:',
            'input_validation': '输入验证问题:',
            'output_sanitization': '输出清理问题:',
            'dependency_security': '依赖安全问题:',
            'token_optimization': 'Token 优化建议:',
            'ai_execution': 'AI 执行效率问题:',
            'verbose_output': '检测到冗余输出模式:',
            'redundant_code': '检测到冗余代码模式:',
        },
        'warnings': {
            'file_not_found': '警告: 文件未找到: {file}',
            'permission_denied': '警告: 权限被拒绝: {file}',
            'decode_error': '警告: 无法解码 {file}: {error}',
        },
        'verbose': {
            'checking': '  检查中: {file}',
        },
    },
}


def get_message(key: str, lang: str = None, **kwargs) -> str:
    """
    Get a localized message by key.
    
    Args:
        key: Message key in format 'category.subkey' (e.g., 'status.pass')
        lang: Language code ('en', 'zh'). Defaults to CURRENT_LANG.
        **kwargs: Format arguments for the message.
    
    Returns:
        Formatted message string.
    """
    if lang is None:
        lang = CURRENT_LANG
    
    if lang not in MESSAGES:
        lang = DEFAULT_LANG
    
    keys = key.split('.')
    msg = MESSAGES.get(lang, MESSAGES[DEFAULT_LANG])
    
    for k in keys:
        if isinstance(msg, dict):
            msg = msg.get(k)
        if msg is None:
            return key
    
    if isinstance(msg, str) and kwargs:
        try:
            return msg.format(**kwargs)
        except KeyError:
            return msg
    
    return msg


def get_lang() -> str:
    """Get current language setting."""
    return CURRENT_LANG


def set_lang(lang: str) -> None:
    """Set current language."""
    global CURRENT_LANG
    if lang in MESSAGES:
        CURRENT_LANG = lang
    else:
        CURRENT_LANG = DEFAULT_LANG


def get_available_languages() -> list:
    """Get list of available languages."""
    return list(MESSAGES.keys())
