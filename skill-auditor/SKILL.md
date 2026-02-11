---
name: skill-auditor
description: A standard compliance checking tool for Trae skills. Use this skill when you need to verify if a skill follows best practices, specifically checking for dependency completeness, proper file encoding, path consistency, cross-platform compatibility, internationalization support, and correct packaging structure.
---

# Skill Auditor

## Overview

The `skill-auditor` provides a standardized validation process for Trae skills. It automates detection of common pitfalls that can cause skills to fail in different environments (e.g., Windows encoding issues) or lead to maintenance problems (e.g., incorrect directory structures, absolute paths, lack of i18n support).

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
- **Why:** Python defaults to system locale (e.g., CP1252 or GBK on Windows), which causes crashes when reading UTF-8 files. All file operations must explicitly use `encoding='utf-8'`.

#### 3.2 Path Consistency
- **Check:** Scans for references to deprecated or incorrect paths (e.g., `.codebuddy/skills`).
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

#### 7.1 Multi-Language Support
- **Check:** Validates `SKILL.md` contains both English and Chinese keywords.
- **Why:** Ensures skill can be discovered and used by users in different languages.

#### 7.2 Hardcoded Messages
- **Check:** Detects excessive hardcoded text in output messages.
- **Why:** Hardcoded messages make internationalization difficult. Use message dictionaries.

#### 7.3 Unicode/Emoji Usage
- **Check:** Detects Unicode characters and emojis in output.
- **Why:** Unicode characters may cause encoding issues in some terminals. Consider message dictionaries for i18n.

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

## Usage

### Running the Auditor

To audit a skill, run the `audit_skill.py` script against the target skill directory:

```bash
python scripts/audit_skill.py <path-to-target-skill> [path-to-skills-dir]
```

**Arguments:**
- `<path-to-target-skill>`: Path to the skill directory to audit (required)
- `[path-to-skills-dir]`: Optional path to the skills root directory for registry checks

### Examples

```powershell
# Audit the skill-creator skill
python scripts/audit_skill.py ../skill-creator

# Audit with registry checks
python scripts/audit_skill.py ../skill-creator .trae/skills

# Audit from different directory
python .trae/skills/skill-auditor/scripts/audit_skill.py .trae/skills/skill-installer .trae/skills
```

### Interpreting Output

- **[INFO]**: Section header or informational message
- **[PASS]**: The check passed successfully.
- **[FAIL]**: A critical issue was found that must be fixed.
- **[WARN]**: A potential issue was found that requires manual review (non-blocking).

### Audit Sections

The auditor performs checks in 9 sections:

1. **Basic Structure** - Frontmatter, name consistency, directory structure
2. **Dependencies** - Dependency integrity and requirements.txt validation
3. **Encoding & Path Safety** - File encoding and path reference checks
4. **Packaging** - Packaging structure and template validation
5. **Subprocess & Path Operations** - Subprocess robustness and risky operations
6. **Cross-Platform Compatibility** - Platform-specific commands and path handling
7. **Internationalization (i18n)** - Multi-language support and message handling
8. **Absolute References** - Hardcoded absolute paths detection
9. **Registry & Map Consistency** - skills.json and skill_map.json validation

## Resources

### scripts/
- `audit_skill.py`: The main executable script that performs all checks.
- `requirements.txt`: Dependencies for the audit script (requires `PyYAML`).
