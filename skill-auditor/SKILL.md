---
name: skill-auditor
description: Standard compliance checker for Agent skills. Verifies dependency completeness, file encoding, path consistency, cross-platform compatibility, i18n support, and packaging structure. Use when auditing skills before publishing or verifying compliance.
description_zh: Agent skills 标准合规性检查工具。检查依赖完整性、文件编码、路径一致性、跨平台兼容性、国际化支持和打包结构。在发布前审计 skill 或验证合规性时使用。
---

# Skill Auditor

Comprehensive validation tool for Agent skills that detects common pitfalls causing skills to fail in different environments.

## Core Standards

| Requirement | Description |
|-------------|-------------|
| No Emoji | Use `[PASS]`, `[FAIL]`, `[WARN]`, `[INFO]` labels |
| No Absolute Paths | Use `pathlib.Path()` and relative paths |
| Encoding Parameter | Always specify `encoding='utf-8'` for text operations |
| Errors Parameter | Use `errors='replace'` for robust error handling |
| Cross-Platform | Avoid platform-specific commands (`dir`, `ls`, `rm`) |
| i18n Support | Use message dictionary with `en` and `zh` support |

## Audit Sections

| # | Section | Description |
|---|---------|-------------|
| 1 | Basic Structure | Frontmatter, name consistency, directory structure |
| 2 | Dependencies | requirements.txt completeness |
| 3 | Encoding & Path Safety | encoding parameter, errors='replace' |
| 4 | Packaging | Flat zip structure, __pycache__ exclusion |
| 5 | Cross-Platform | Platform-specific commands, path separators |
| 6 | i18n | Emoji prohibition, multi-language support |
| 7 | Absolute References | Hardcoded path detection |
| 8 | Registry Consistency | skills.json and skill_map.json validation |
| 9 | Security Analysis | Injection, permission abuse, code execution safety |
| 10 | Quality Checks | Error handling, exception specificity, input validation |
| 11 | Output Quality | Data masking, token optimization, redundant code |

## Usage

```powershell
python scripts/audit_skill.py <skill-path> [skills-dir] [options]
```

**Options:**
- `--level <strict|standard|relaxed>` - Check strictness (default: standard)
- `--verbose` - Enable verbose output
- `--json` - Output in JSON format
- `--report <file>` - Generate Markdown report

**Examples:**
```powershell
python scripts/audit_skill.py ../skill-creator
python scripts/audit_skill.py ../skill-creator .trae/skills --level strict --report audit.md
```

## Output Labels

| Label | Meaning |
|-------|---------|
| `[PASS]` | Check passed successfully |
| `[FAIL]` | Critical issue found - must fix |
| `[WARN]` | Potential issue - manual review needed |

## Severity Levels

| Level | Priority |
|-------|----------|
| CRITICAL | Fix immediately - security vulnerabilities |
| HIGH | Fix soon - significant issues |
| MEDIUM | Should fix - quality issues |
| LOW | Nice to fix - optimization |

## Resources

### scripts/

| File | Purpose |
|------|---------|
| `audit_skill.py` | Main entry point |
| `audit_config.py` | Configuration constants |
| `security_checks.py` | Security analysis checks |
| `quality_checks.py` | Quality analysis checks |
| `output_quality_checks.py` | Output quality checks |
| `file_param_checker.py` | Encoding/errors parameter checks |
| `file_utils.py` | Robust file reading utilities |
| `shared_checkers.py` | Shared checker classes |
| `report_generator.py` | Markdown report generator |
| `package_skill.py` | Skill packaging utility |
| `quick_validate.py` | Minimal validation |
| `requirements.txt` | Dependencies (PyYAML, charset_normalizer, colorama) |
