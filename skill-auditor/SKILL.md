---
name: skill-auditor
description: A standard compliance checking tool for Trae skills. Use this skill when you need to verify if a skill follows best practices, specifically checking for dependency completeness, proper file encoding, path consistency, cross-platform compatibility, internationalization support, and correct packaging structure.
description_zh: Trae skills 标准合规性检查工具。当您需要验证 skill 是否遵循最佳实践时使用此 skill，专门检查依赖完整性、正确的文件编码、路径一致性、跨平台兼容性、国际化支持和正确的打包结构。
---

# Skill Auditor / Skill 审计工具

## Core Standards / 核心规范

### Mandatory Requirements (Must Comply) / 必须遵守的要求

1. **No Emoji in Code Output / 代码输出中严禁使用 Emoji**
   - Emoji characters are strictly prohibited in skill code output statements
   - 严禁在 skill 代码输出语句中使用 emoji 字符
   - Use text labels: `[PASS]`, `[FAIL]`, `[WARN]`, `[INFO]`

2. **No Hardcoded Absolute Paths / 不允许使用硬编码绝对路径**
   - Never use absolute paths like `C:\`, `/home/`, `/Users/` in code
   - 永远不要在代码中使用绝对路径如 `C:\`, `/home/`, `/Users/`
   - Use relative paths and `pathlib.Path()` / 使用相对路径和 `pathlib.Path()`

3. **Proper Encoding for File Operations / 文件操作使用正确的编码**
   - Use `encoding='utf-8'` for Chinese text files (recommended)
   - 中文文本文件使用 `encoding='utf-8'`（推荐）
   - Encoding should match actual file content / 编码应与实际文件内容匹配

4. **Cross-Platform Compatibility / 跨平台兼容性**
   - Use `pathlib.Path()` instead of `os.path` / 使用 `pathlib.Path()` 而非 `os.path`
   - Avoid platform-specific commands like `dir`, `ls` / 避免平台特定命令如 `dir`, `ls`

### Recommended Best Practices / 推荐最佳实践

1. **Multi-Language Support / 多语言支持**
   - Include both English and Chinese in SKILL.md (suggested)
   - 在 SKILL.md 中包含英文和中文（建议）

2. **Message Dictionary for i18n / 使用消息字典实现国际化**
   - Use message dictionaries for skills with extensive user-facing output
   - 对于有大量面向用户输出的 skill，使用消息字典

3. **Reference Documentation / 参考文档**
   - Provide documentation in `references/` directory
   - 在 `references/` 目录中提供文档

## Overview / 概述

The `skill-auditor` provides a comprehensive validation process for Trae skills. It automates detection of common pitfalls that can cause skills to fail in different environments (e.g., Windows encoding issues), lead to maintenance problems (e.g., incorrect directory structures, absolute paths, lack of i18n support), or introduce security vulnerabilities (e.g., code injection, permission abuse, prompt injection).

The auditor performs checks across multiple dimensions:
- **Basic Standards**: Structure, dependencies, encoding, and packaging
- **Security Analysis**: Malicious script injection, permission abuse, prompt injection, code execution safety, filesystem security, and network security
- **Quality Checks**: Technical standards including error handling, logging practices, input validation, output sanitization, and dependency security
- **Output Quality**: Data masking, infinite loops, token optimization, AI execution effectiveness, verbose output, and redundant code detection

## Standard Audit Process

This skill enforces a comprehensive 9-point standard check that every production-ready skill should pass.

### Section 1: Basic Structure

#### 1.1 Frontmatter Validation
- **Check:** Verifies `SKILL.md` frontmatter exists and contains required fields (`name`, `description`).
- **Why:** Ensures skill metadata is properly formatted for the skill loader.

#### 1.2 Name Consistency
- **Check:** Validates that the skill directory name matches the `name` field in `SKILL.md` frontmatter.
- **Why:** Prevents confusion and ensures proper skill registration.

#### 1.3 Directory Structure
- **Check:** Validates directory structure follows standard conventions (scripts/, references/, assets/).
- **Why:** Ensures skill is organized correctly and follows best practices.

### Section 2: Dependencies

#### 2.1 Dependency Integrity
- **Check:** Ensures that if a `scripts/` directory exists with Python files, a `requirements.txt` file is also present.
- **Why:** Prevents runtime `ModuleNotFoundError` when users try to run skill scripts.

### Section 3: Encoding & Path Safety

#### 3.1 Encoding Safety (Cross-Platform)
- **Check:** Scans Python scripts for file operations (`open`, `read_text`, `write_text`) that do not specify an encoding.
- **Why:** Python defaults to system locale (e.g., CP1252 or GBK on Windows), which can cause encoding issues. Use `encoding='utf-8'` for Chinese text files (recommended), but encoding should match actual file content.
- **Note:** `encoding='utf-8'` is recommended for Chinese text but not mandatory. Choose encoding based on actual file content.

#### 3.2 Path Consistency
- **Check:** Scans for references to deprecated or incorrect paths (e.g., `.trae/skills`).
- **Why:** Ensures all documentation and scripts point to the correct `.trae/skills` directory structure.

### Section 4: Packaging

#### 4.1 Packaging Structure
- **Check:** Verifies that packaging scripts create a "flat" zip structure (files at root) rather than nesting them inside a parent directory. Also checks for `__pycache__` exclusion.
- **Why:** Incorrect nesting prevents the skill loader from finding `SKILL.md`.

#### 4.2 Template Logic Validation
- **Check:** If `scripts/init_skill.py` exists, verifies that the generated `SKILL.md` template uses valid YAML string syntax for description (e.g., `description: "..."`) instead of invalid list syntax (e.g., `description: [...]`).
- **Why:** Prevents generated skills from failing validation immediately after creation due to YAML parsing errors.

### Section 5: Subprocess & Path Operations

#### 5.1 Subprocess Robustness
- **Check:** Validates subprocess calls use proper error handling (`errors='replace'`) for text output.
- **Why:** Prevents crashes when subprocess output contains non-UTF8 characters.

#### 5.2 Risky Path Operations
- **Check:** Detects risky file system operations like `os.system()` and hardcoded path separators.
- **Why:** Ensures code uses safe, cross-platform APIs.

### Section 6: Cross-Platform Compatibility

#### 6.1 Platform-Specific Commands
- **Check:** Detects platform-specific commands (`dir`, `del`, `ls`, `rm`).
- **Why:** Platform-specific commands fail on other operating systems. Use `pathlib` or `shutil` instead.

#### 6.2 Path Separator Usage
- **Check:** Detects hardcoded path separators (`/` or `\`) in string literals.
- **Why:** Hardcoded separators break cross-platform compatibility. Use `pathlib.Path()` for path operations.

#### 6.3 Absolute Path Patterns
- **Check:** Detects absolute path patterns (`C:\`, `/home/`, `/Users/`).
- **Why:** Absolute paths are not portable and break when skill is installed in different locations.

#### 6.4 os.path vs pathlib
- **Check:** Recommends using `pathlib.Path()` instead of `os.path.join()`.
- **Why:** `pathlib` provides better cross-platform support and more intuitive API.

### Section 7: Internationalization (i18n)

#### 7.1 Emoji Prohibition (REQUIRED)
- **Check:** Detects emoji characters in skill code output statements.
- **Why:** Emojis can cause encoding issues in some terminals and are not universally supported. Emoji characters are **strictly prohibited** in skill code output.
- **Note:** Unicode characters are allowed in code comments, but not in output statements.

#### 7.2 Multi-Language Support
- **Check:** Suggests including both English and Chinese keywords in `SKILL.md`.
- **Why:** Improves skill discoverability for users in different languages (suggestion, not requirement).

#### 7.3 Hardcoded Messages
- **Check:** Detects excessive hardcoded text in output messages.
- **Why:** Hardcoded messages make internationalization difficult. Consider using message dictionaries for better i18n support when applicable.

### Section 8: Absolute References

#### 8.1 Hardcoded Absolute Paths
- **Check:** Detects hardcoded absolute file paths in code and configuration files.
- **Why:** Absolute paths are not portable and break in different environments.

#### 8.2 Configuration File Paths
- **Check:** Validates configuration files don't contain absolute paths.
- **Why:** Configuration with absolute paths prevents skill from working in different locations.

### Section 9: Registry & Map Consistency

#### 9.1 Registry Consistency
- **Check:** Validates skill is properly registered in `skills.json` with correct metadata.
- **Why:** Ensures skill tracking and version management work correctly.

#### 9.2 Skill Map Consistency
- **Check:** Validates skill is properly mapped in `skill_map.json` with keywords.
- **Why:** Ensures skill can be automatically detected and invoked by user requests.

### Section 10: Security Analysis

#### 10.1 Malicious Script Injection
- **Check:** Detects patterns of malicious script injection including dynamic code execution (eval, exec, compile), unsafe subprocess calls with user input, arbitrary file system access patterns, and network requests to untrusted sources.
- **Why:** Dynamic code execution and unsafe subprocess calls are critical security vulnerabilities that can lead to code injection attacks.
- **Severity:** CRITICAL

#### 10.2 Permission Abuse
- **Check:** Identifies potential permission abuse risks including excessive file system access requests, network access without proper validation, system command execution without safeguards, and sensitive data access patterns.
- **Why:** Excessive permissions can lead to unauthorized access and data breaches.
- **Severity:** HIGH

#### 10.3 Prompt Injection
- **Check:** Detects potential prompt injection vectors including user-controlled prompt concatenation, unvalidated prompt modifications, instruction override patterns, and role manipulation attempts.
- **Why:** Prompt injection can bypass security controls and manipulate AI behavior.
- **Severity:** HIGH

#### 10.4 Code Execution Safety
- **Check:** Validates code execution safety including eval(), exec(), compile() usage, unsafe dynamic code patterns, and subprocess call safety.
- **Why:** Unsafe code execution is a critical security risk that can lead to arbitrary code execution.
- **Severity:** CRITICAL

#### 10.5 Filesystem Security
- **Check:** Validates filesystem security including path traversal vulnerabilities, unsafe file operations, and file permission handling.
- **Why:** Path traversal attacks can allow unauthorized file access.
- **Severity:** HIGH

#### 10.6 Network Security
- **Check:** Detects network security risks including untrusted URL patterns, missing validation, and potential data exfiltration.
- **Why:** Unvalidated network requests can lead to data leakage and security breaches.
- **Severity:** MEDIUM

### Section 11: Quality Checks

#### 11.1 Error Handling Patterns
- **Check:** Validates error handling patterns including missing try-except blocks in risky operations, bare except clauses, exception handling specificity, and proper error propagation.
- **Why:** Proper error handling prevents crashes and improves reliability.
- **Severity:** MEDIUM

#### 11.2 Logging Practices
- **Check:** Validates logging best practices including proper logging level usage, sensitive data in logs, log message formatting, and structured logging patterns.
- **Why:** Proper logging helps debugging while avoiding sensitive data exposure.
- **Severity:** LOW

#### 11.3 Input Validation
- **Check:** Validates input validation implementation including user input sanitization, type checking, and boundary validation.
- **Why:** Input validation prevents injection attacks and data corruption.
- **Severity:** HIGH

#### 11.4 Output Sanitization
- **Check:** Validates output sanitization including HTML/XML escaping, JSON serialization safety, and user output encoding.
- **Why:** Output sanitization prevents XSS and injection attacks.
- **Severity:** MEDIUM

#### 11.5 Dependency Security
- **Check:** Validates dependency security including known vulnerabilities, outdated packages, and insecure dependencies.
- **Why:** Vulnerable dependencies can introduce security risks.
- **Severity:** MEDIUM

#### 11.6 Technical Standards
- **Check:** Validates overall technical standards compliance across all quality dimensions.
- **Why:** Ensures code meets professional quality standards.
- **Severity:** MEDIUM

### Section 12: Output Quality

#### 12.1 Data Masking
- **Check:** Detects data masking issues and sensitive data exposure including sensitive data in logs, personal information in output, API keys or tokens in code, and credentials in error messages.
- **Why:** Sensitive data exposure can lead to security breaches and privacy violations.
- **Severity:** CRITICAL

#### 12.2 Infinite Loops
- **Check:** Detects potential infinite loops and unbounded recursion including while loops without proper exit conditions, recursive functions without base cases, unbounded iteration patterns, and potential infinite recursion.
- **Why:** Infinite loops can cause resource exhaustion and system hangs.
- **Severity:** HIGH

#### 12.3 Token Optimization
- **Check:** Analyzes code for token optimization opportunities including redundant code elimination, verbose output reduction, efficient algorithm alternatives, and token usage optimization tips.
- **Why:** Optimized code reduces token usage and improves efficiency.
- **Severity:** LOW

#### 12.4 AI Execution Effectiveness
- **Check:** Evaluates AI execution effectiveness including clarity of instructions in SKILL.md, conciseness of prompts, efficiency of workflows, and verbose outputs.
- **Why:** Clear and concise instructions improve AI understanding and execution.
- **Severity:** LOW

#### 12.5 Verbose Output
- **Check:** Detects verbose output patterns including excessive print statements, redundant logging, unnecessary debug output, and output consolidation opportunities.
- **Why:** Excessive output can overwhelm users and reduce readability.
- **Severity:** LOW

#### 12.6 Redundant Code
- **Check:** Identifies redundant code patterns including duplicate code blocks, unused imports, dead code, and code consolidation opportunities.
- **Why:** Redundant code increases maintenance burden and token usage.
- **Severity:** LOW

## Usage

### Running the Auditor

To audit a skill, run the `audit_skill.py` script against the target skill directory:

```bash
python scripts/audit_skill.py <path-to-target-skill> [path-to-skills-dir] [options]
```

**Arguments:**
- `<path-to-target-skill>`: Path to the skill directory to audit (required)
- `[path-to-skills-dir]`: Optional path to the skills root directory for registry checks

**Options:**
- `--level <level>`: Check strictness level (default: standard)
  - `strict`: All checks including security, quality, and output quality checks
  - `standard`: All checks with i18n issues as warnings (default)
  - `relaxed`: Only critical checks (basic structure, dependencies, encoding)
- `--verbose`: Enable verbose output with detailed information
- `--json`: Output results in JSON format for programmatic parsing

### Examples

```powershell
# Basic audit with standard checks
python scripts/audit_skill.py ../skill-creator

# Audit with registry checks
python scripts/audit_skill.py ../skill-creator .trae/skills

# Strict mode audit (all security, quality, and output quality checks)
python scripts/audit_skill.py ../skill-creator .trae/skills --level strict

# Relaxed mode audit (only critical checks)
python scripts/audit_skill.py ../skill-creator --level relaxed

# Verbose output for debugging
python scripts/audit_skill.py ../skill-creator --verbose

# JSON output for CI/CD integration
python scripts/audit_skill.py ../skill-creator --json

# Audit from different directory
python .trae/skills/skill-auditor/scripts/audit_skill.py .trae/skills/skill-installer .trae/skills --level strict
```

### Check Levels Explained

**Strict Mode (`--level strict`)**
- Runs all checks including security analysis, quality checks, and output quality checks
- Treats i18n issues as errors (must fix)
- Recommended for production skills and security-critical applications
- Example use case: Auditing a skill before publishing to production

**Standard Mode (`--level standard`)**
- Runs all checks including security, quality, and output quality checks
- Treats i18n issues as warnings (recommended to fix but not blocking)
- Default mode for most development workflows
- Example use case: Regular development and testing

**Relaxed Mode (`--level relaxed`)**
- Only runs critical checks: basic structure, dependencies, and encoding
- Skips security, quality, and output quality checks
- Useful for quick validation during early development
- Example use case: Initial skill creation and prototyping

### Interpreting Output

- **[INFO]**: Section header or informational message
- **[PASS]**: The check passed successfully.
- **[FAIL]**: A critical issue was found that must be fixed.
- **[WARN]**: A potential issue was found that requires manual review (non-blocking).

### Audit Sections

The auditor performs checks in 12 sections:

1. **Basic Structure** - Frontmatter, name consistency, directory structure
2. **Dependencies** - Dependency integrity and requirements.txt validation
3. **Encoding & Path Safety** - File encoding and path reference checks
4. **Packaging** - Packaging structure and template validation
5. **Subprocess & Path Operations** - Subprocess robustness and risky operations
6. **Cross-Platform Compatibility** - Platform-specific commands and path handling
7. **Internationalization (i18n)** - Multi-language support and message handling
8. **Absolute References** - Hardcoded absolute paths detection
9. **Registry & Map Consistency** - skills.json and skill_map.json validation
10. **Security Analysis** - Malicious script injection, permission abuse, prompt injection, code execution safety, filesystem security, and network security
11. **Quality Checks** - Error handling, logging practices, input validation, output sanitization, dependency security, and technical standards
12. **Output Quality** - Data masking, infinite loops, token optimization, AI execution effectiveness, verbose output, and redundant code detection

### Severity Levels

The auditor uses four severity levels to classify issues:

- **CRITICAL**: Must fix immediately. These are security vulnerabilities that can lead to code injection, data breaches, or system compromise.
- **HIGH**: Should fix soon. These are significant issues that can lead to security risks, data exposure, or system instability.
- **MEDIUM**: Should fix. These are quality and reliability issues that can impact maintainability and user experience.
- **LOW**: Nice to fix. These are optimization and style improvements that enhance code quality and efficiency.

## Usage Examples

### Running Security Checks

```powershell
# Run strict mode to check all security issues
python scripts/audit_skill.py ../my-skill --level strict

# Run with verbose output to see detailed security findings
python scripts/audit_skill.py ../my-skill --level strict --verbose

# Example output for security issues:
# [FAIL] Security Analysis: Malicious Script Injection
#   scripts/handler.py:45: eval() with potential user input. This is a critical security vulnerability.
# [FAIL] Security Analysis: Code Execution Safety
#   scripts/utils.py:23: exec() detected. Dynamic code execution is a critical security risk.
```

### Running Quality Checks

```powershell
# Run standard mode to check quality issues
python scripts/audit_skill.py ../my-skill --level standard

# Example output for quality issues:
# [WARN] Quality Checks: Error Handling Patterns
#   scripts/main.py:67: Bare except clause detected. Use specific exception types.
# [WARN] Quality Checks: Logging Practices
#   scripts/handler.py:34: Potential sensitive data in log message: 'password'.
```

### Interpreting Severity Levels

```powershell
# Example audit output with severity indicators
# CRITICAL issues (must fix):
# [FAIL] Security Analysis: Data Masking
#   scripts/config.py:12: Potential hardcoded sensitive data: api_key = "sk-12345..."

# HIGH issues (should fix soon):
# [WARN] Security Analysis: Filesystem Security
#   scripts/utils.py:56: open() with potential user input. Path traversal vulnerability.

# MEDIUM issues (should fix):
# [WARN] Quality Checks: Input Validation
#   scripts/handler.py:89: No type checking for user input.

# LOW issues (nice to fix):
# [INFO] Output Quality: Token Optimization
#   scripts/main.py:123: Function is 65 lines long. Consider splitting.
```

### Fixing Common Issues

#### Example 1: Fixing Security Issue - Code Injection

**Before (vulnerable):**
```python
# scripts/handler.py
def process_user_code(user_input):
    result = eval(user_input)  # CRITICAL: Code injection
    return result
```

**After (secure):**
```python
# scripts/handler.py
import ast

def process_user_code(user_input):
    try:
        result = ast.literal_eval(user_input)  # Safe for literals only
        return result
    except (ValueError, SyntaxError):
        raise ValueError("Invalid input: only literals allowed")
```

#### Example 2: Fixing Quality Issue - Error Handling

**Before (poor error handling):**
```python
# scripts/utils.py
def read_config(filename):
    try:
        with open(filename) as f:
            return json.load(f)
    except:  # BAD: Bare except clause
        return None
```

**After (proper error handling):**
```python
# scripts/utils.py
def read_config(filename):
    try:
        with open(filename, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {filename}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file: {e}")
    except IOError as e:
        raise IOError(f"Error reading config file: {e}")
```

#### Example 3: Fixing Output Quality Issue - Verbose Output

**Before (excessive output):**
```python
# scripts/processor.py
def process_data(data):
    print("Starting processing...")
    print(f"Data length: {len(data)}")
    print("Processing item 1...")
    print("Processing item 2...")
    print("Processing item 3...")
    # ... many more print statements
    print("Done!")
    return result
```

**After (concise output):**
```python
# scripts/processor.py
import logging

logger = logging.getLogger(__name__)

def process_data(data):
    logger.info(f"Processing {len(data)} items")
    result = transform(data)
    logger.info("Processing complete")
    return result
```

### CI/CD Integration

```yaml
# .github/workflows/skill-audit.yml
name: Skill Audit
on: [push, pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install pyyaml
          
      - name: Run skill auditor (strict mode)
        run: |
          python .trae/skills/skill-auditor/scripts/audit_skill.py \
            . --level strict --json > audit-results.json
          
      - name: Upload audit results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: audit-results
          path: audit-results.json
```

## Resources

### scripts/
- `audit_skill.py`: The main executable script that performs all checks.
- `requirements.txt`: Dependencies for the audit script (requires `PyYAML`).
