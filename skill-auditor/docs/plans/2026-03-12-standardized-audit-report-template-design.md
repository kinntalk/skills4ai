# Standardized Audit Report Template Design

## Overview

This document defines the standardized report structure for skill-auditor output. The goal is to ensure consistent, readable, and actionable audit reports across all skill audits.

## Problem Statement

Currently, audit output presentation varies between sessions, making it difficult to:
- Compare audit results across different skills
- Track issues systematically
- Generate consistent documentation

## Solution

Implement a standardized Markdown report template with fixed sections and consistent formatting.

## Report Structure

### Section 1: Audit Overview

**Purpose**: Provide high-level summary of the audit.

**Content**:
- Skill name
- Audit level (strict/standard/relaxed)
- Audit date
- Total issue count
- Severity breakdown table

**Format**:
```markdown
## 1. Audit Overview

| Item | Value |
|------|-------|
| **Skill Name** | {skill_name} |
| **Audit Level** | {audit_level} |
| **Audit Date** | {audit_date} |
| **Total Issues** | {total_issues} |

### Issue Statistics

| Severity | Count |
|----------|-------|
| CRITICAL | {critical_count} |
| HIGH | {high_count} |
| MEDIUM | {medium_count} |
| LOW | {low_count} |
```

### Section 2: Issue Details

**Purpose**: List all issues organized by severity.

**Content**:
- Issue number
- File path (as clickable link)
- Line number
- Description
- Fix suggestion

**Format**:
```markdown
## 2. Issue Details

### 2.1 CRITICAL Issues

| # | File | Line | Description | Fix Suggestion |
|---|------|------|-------------|----------------|
| 1 | [file.py](file:///path/to/file.py#L10) | 10 | {description} | {suggestion} |

> [!NOTE]
> No CRITICAL issues found.

### 2.2 HIGH Issues

| # | File | Line | Description | Fix Suggestion |
|---|------|------|-------------|----------------|
| 1 | [file.py](file:///path/to/file.py#L20) | 20 | {description} | {suggestion} |

### 2.3 MEDIUM Issues

(Same format)

### 2.4 LOW Issues

(Same format)
```

### Section 3: False Positive Analysis

**Purpose**: Document issues that are false positives and explain why.

**Content**:
- Issue number
- File path
- Line number
- Issue type
- Reason for false positive

**Format**:
```markdown
## 3. False Positive Analysis

> [!INFO]
> The following issues are false positives and do not require fixing.

| # | File | Line | Issue Type | Reason |
|---|------|------|------------|--------|
| 1 | [base_checker.py](file:///path/to/base_checker.py#L30) | 30 | Path Traversal | Pattern definition, not actual traversal |
```

**Note**: This section is optional and only appears when false positives exist.

### Section 4: Fix Recommendations

**Purpose**: Provide prioritized action items.

**Content**:
- Priority level
- Issue type
- Affected file
- Recommended action

**Format**:
```markdown
## 4. Fix Recommendations

### Priority Order

| Priority | Issue Type | File | Action |
|----------|------------|------|--------|
| HIGH | Generic Exception | file_utils.py | Use specific exception types |
| MEDIUM | Long Paragraph | SKILL.md | Split into shorter sections |
| LOW | Unused Import | audit_skill.py | Remove unused imports |
```

### Section 5: Summary

**Purpose**: Provide overall assessment and next steps.

**Content**:
- Overall assessment (pass/fail/warnings)
- Key findings (bullet list)
- Recommended actions (numbered list)

**Format**:
```markdown
## 5. Summary

### Overall Assessment

{overall_assessment}

### Key Findings

- {finding_1}
- {finding_2}
- {finding_3}

### Recommended Actions

1. {action_1}
2. {action_2}
3. {action_3}
```

## Implementation Approach

### Option A: Template File

Create a Jinja2 template file that can be rendered with audit data.

**Pros**:
- Easy to modify template
- Separation of concerns
- Reusable

**Cons**:
- Additional dependency (Jinja2)
- Template file management

### Option B: Python String Formatting

Use Python f-strings or format() with embedded template.

**Pros**:
- No additional dependencies
- Simple implementation

**Cons**:
- Template embedded in code
- Harder to modify

### Option C: Markdown Builder Class

Create a class that constructs the report programmatically.

**Pros**:
- Flexible and extensible
- Type-safe
- Easy to test

**Cons**:
- More code to maintain

**Recommendation**: Option C (Markdown Builder Class) for flexibility and maintainability.

## File Links Format

All file references should use clickable Markdown links:

```markdown
[file.py](file:///absolute/path/to/file.py#L10)
```

This format:
- Works in most Markdown viewers
- Links to specific line numbers
- Uses absolute paths for reliability

## i18n Support

The template should support both English and Chinese output:

- Use message dictionary from `messages.py`
- Detect language from environment or CLI argument
- All section headers and labels should be translatable

## Output Options

The report generator should support:

1. **Console output**: Print to stdout (current behavior)
2. **File output**: Write to `.md` file
3. **JSON output**: Structured data for programmatic use (already supported via `--json`)

## Next Steps

1. Implement `report_generator.py` with Markdown builder class
2. Add `--report` CLI option to generate `.md` file
3. Update `messages.py` with report template strings
4. Add unit tests for report generation
