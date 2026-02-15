---
name: skill-auditor
description: A standard compliance checking tool for Trae skills. Use this skill when you need to verify if a skill follows best practices, specifically checking for dependency completeness, proper file encoding, path consistency, cross-platform compatibility, internationalization support, and correct packaging structure. Part of the quality monitoring ecosystem with context-aware routing support.
description_zh: Trae skills 标准合规性检查工具。当您需要验证 skill 是否遵循最佳实践时使用此 skill，专门检查依赖完整性、正确的文件编码、路径一致性、跨平台兼容性、国际化支持和正确的打包结构。作为质量监控生态系统的一部分，支持上下文感知路由。
keywords:
  - audit
  - check
  - validate
  - test
  - compliance
  - best-practices
  - quality
  - verify
  - 审计
  - 检查
  - 验证
  - 测试
  - 合规
  - 最佳实践
  - 质量
aliases:
  - skill-check
  - skill-validator
  - skill-tester
  - skill-linter
  - skill-audit
---

# Skill Auditor / Skill 审计工具

## Overview / 概述

The `skill-auditor` provides a standardized validation process for Trae skills. It automates detection of common pitfalls that can cause skills to fail in different environments (e.g., Windows encoding issues) or lead to maintenance problems (e.g., incorrect directory structures, absolute paths, lack of i18n support).

## When to Use This Skill / 何时使用此技能

Use this skill when:
- You need to validate a newly created skill
- You need to verify a skill meets quality standards
- You need to check if a skill follows best practices
- You need to audit a skill before installation
- You need to ensure a skill is compatible with the intelligent routing system

## Skill Context and Routing / 技能上下文和路由

This skill is part of the **management** skills category and is automatically routed by the intelligent routing system based on:

- **Trigger Phase**: `management`
- **Required For**: `skill-validation`, `compliance-check`
- **Priority**: 5

The routing system uses the `skill_map.json` context field to automatically detect when this skill should be invoked based on keywords like "audit", "check", "validate", "test", "compliance", "best-practices", "quality", "verify".

## Skills Directory Structure / 技能目录结构

Skills are organized in the `.trae/skills/` directory with the following structure:

```
.trae/skills/
├── workflow/           # Workflow-based skills (brainstorming, planning, etc.)
│   ├── AGENTS.md       # Workflow skills persona and boundaries
│   ├── brainstorming/
│   ├── writing-plans/
│   ├── executing-plans/
│   └── ...
├── management/         # Management skills (find-skills, skill-creator, etc.)
│   ├── AGENTS.md       # Management skills persona and boundaries
│   ├── find-skills/
│   ├── skill-creator/
│   ├── skill-installer/
│   ├── skill-auditor/
│   └── ...
├── domain/            # Domain-specific skills (ui-ux, claude-skills, etc.)
│   ├── AGENTS.md       # Domain skills persona and boundaries
│   ├── behavioral-product-design/
│   ├── ui-ux-pro-max-skill/
│   ├── claude-skills/
│   └── ...
├── [other skills]     # Other standalone skills
├── SKILL_ROUTING.md   # Intelligent routing system documentation
├── SKILL_QUALITY_MONITOR.md  # Quality monitoring system
├── skill_map.json     # Skill mapping and routing configuration
└── skills.json        # Skills registry and version tracking
```

Each skill category has its own AGENTS.md file that defines:
- **Persona**: Role and purpose of skills in that category
- **Workflow**: How skills interact with each other
- **Boundaries**: Rules and constraints for skill usage

## Integration with Management Workflow / 与管理工作流集成

This skill is part of the management skills workflow defined in [AGENTS.md](AGENTS.md):

1. **find-skills**: Discover available skills
2. **skill-installer**: Install from Git repositories
3. **skill-auditor**: Validate skill compliance (this skill)
4. **skill-creator**: Create new skills

**Management Boundaries:**
- **ALWAYS** audit skills after installation
- **NEVER** install skills without updating `skills.json`
- **USE** skill-creator for new skill scaffolding

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

## Usage

### Running the Auditor

To audit a skill, run the `audit_skill.py` script against the target skill directory:

```bash
python .trae/skills/management/skill-auditor/scripts/audit_skill.py <path-to-target-skill> [path-to-skills-dir]
```

**Arguments:**
- `<path-to-target-skill>`: Path to the skill directory to audit (required)
- `[path-to-skills-dir]`: Optional path to the skills root directory for registry checks

### Examples

```powershell
# Audit the skill-creator skill
python .trae/skills/management/skill-auditor/scripts/audit_skill.py ../skill-creator

# Audit with registry checks
python .trae/skills/management/skill-auditor/scripts/audit_skill.py ../skill-creator .trae/skills

# Audit from different directory
python .trae/skills/management/skill-auditor/scripts/audit_skill.py .trae/skills/management/skill-installer .trae/skills
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

## Integration with Intelligent Routing System / 与智能路由系统集成

The intelligent routing system (see [SKILL_ROUTING.md](../../SKILL_ROUTING.md)) automatically detects when users need to audit skills and routes to this skill based on:

- **Keyword matching**: "audit", "check", "validate", "test", "compliance", "best-practices", "quality", "verify"
- **Context awareness**: Management phase triggers
- **Priority**: 5 (medium priority)

After using this skill, the routing system may recommend:
- **skill-creator**: If the skill needs to be fixed or recreated
- **skill-installer**: If the skill needs to be reinstalled
- **find-skills**: If the user wants to find alternative skills

## Quality Monitoring / 质量监控

This skill is monitored by the quality monitoring system (see [SKILL_QUALITY_MONITOR.md](../../SKILL_QUALITY_MONITOR.md)):

- **Target Success Rate**: > 90%
- **Target Usage Frequency**: Low (< 5/day)
- **Priority**: High

Usage statistics are tracked in `skill_usage_stats.json` to optimize routing and identify improvement opportunities.

### Quality Metrics / 质量指标

The auditor tracks the following quality metrics:

| Metric | Description | Target |
|---------|-------------|---------|
| Pass Rate | Percentage of skills that pass all checks | > 95% |
| Critical Issues | Number of critical issues found | 0 |
| Warning Issues | Number of warning issues found | < 5% of total checks |
| Audit Time | Average time to complete audit | < 30 seconds |

### Continuous Improvement / 持续改进

The quality monitoring system implements:

1. **Weekly Reviews**: Review audit results and identify common issues
2. **Monthly Audits**: Comprehensive audit of all skills
3. **Error Pattern Tracking**: Track and analyze recurring issues
4. **Best Practices Updates**: Update standards based on audit findings
5. **Routing Optimization**: Use audit results to improve skill routing accuracy

## Resources

### scripts/
- `audit_skill.py`: The main executable script that performs all checks.
- `requirements.txt`: Dependencies for the audit script (requires `PyYAML`).
