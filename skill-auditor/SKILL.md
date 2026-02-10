---
name: skill-auditor
description: A standard compliance checking tool for Trae skills. Use this skill when you need to verify if a skill follows best practices, specifically checking for dependency completeness, proper file encoding, path consistency, and correct packaging structure.
---

# Skill Auditor

## Overview

The `skill-auditor` provides a standardized validation process for Trae skills. It automates the detection of common pitfalls that can cause skills to fail in different environments (e.g., Windows encoding issues) or lead to maintenance problems (e.g., incorrect directory structures).

## Standard Audit Process

This skill enforces a 6-point standard check that every production-ready skill should pass.

### 1. Dependency Integrity
- **Check:** Ensures that if a `scripts/` directory exists with Python files, a `requirements.txt` file is also present.
- **Why:** Prevents runtime `ModuleNotFoundError` when users try to run skill scripts.

### 2. Encoding Safety (Cross-Platform)
- **Check:** Scans Python scripts for file operations (`open`, `read_text`, `write_text`) that do not specify an encoding.
- **Why:** Python defaults to the system locale (e.g., CP1252 or GBK on Windows), which causes crashes when reading UTF-8 files. All file operations must explicitly use `encoding='utf-8'`.

### 3. Path Consistency
- **Check:** Scans for references to deprecated or incorrect paths (e.g., `.codebuddy/skills`).
- **Why:** Ensures all documentation and scripts point to the correct `.trae/skills` directory structure.

### 4. Packaging Structure
- **Check:** Verifies that packaging scripts create a "flat" zip structure (files at root) rather than nesting them inside a parent directory. Also checks for `__pycache__` exclusion.
- **Why:** Incorrect nesting prevents the skill loader from finding `SKILL.md`.

### 5. Metadata Validation
- **Check:** Verifies `SKILL.md` frontmatter exists and contains required fields (`name`, `description`).

### 6. Template Logic Validation
- **Check:** If `scripts/init_skill.py` exists, verifies that the generated `SKILL.md` template uses valid YAML string syntax for description (e.g., `description: "..."`) instead of invalid list syntax (e.g., `description: [...]`).
- **Why:** Prevents generated skills from failing validation immediately after creation due to YAML parsing errors.

## Usage

### Running the Auditor

To audit a skill, run the `audit_skill.py` script against the target skill directory:

```bash
python scripts/audit_skill.py <path-to-target-skill>
```

### Example

```powershell
# Audit the skill-creator skill
python scripts/audit_skill.py ../skill-creator
```

### Interpreting Output

- ✅ **PASS**: The check passed successfully.
- ❌ **FAIL**: A critical issue was found that must be fixed.
- ⚠️ **WARN**: A potential issue was found that requires manual review.

## Resources

### scripts/
- `audit_skill.py`: The main executable script that performs all checks.
- `requirements.txt`: Dependencies for the audit script (requires `PyYAML`).
