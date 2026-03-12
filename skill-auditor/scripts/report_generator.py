#!/usr/bin/env python3
"""
Report Generator for skill-auditor
Generates standardized Markdown audit reports.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple


@dataclass
class AuditIssue:
    """Represents a single audit issue."""
    file: str
    line: int
    severity: str
    description: str
    suggestion: str = ""
    is_false_positive: bool = False
    false_positive_reason: str = ""


@dataclass
class AuditData:
    """Container for all audit data."""
    skill_name: str
    skill_path: Path
    audit_level: str
    audit_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    issues: List[AuditIssue] = field(default_factory=list)
    false_positives: List[AuditIssue] = field(default_factory=list)
    overall_assessment: str = ""
    key_findings: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)

    @property
    def total_issues(self) -> int:
        return len([i for i in self.issues if not i.is_false_positive])

    @property
    def critical_count(self) -> int:
        return len([i for i in self.issues if i.severity == "CRITICAL" and not i.is_false_positive])

    @property
    def high_count(self) -> int:
        return len([i for i in self.issues if i.severity == "HIGH" and not i.is_false_positive])

    @property
    def medium_count(self) -> int:
        return len([i for i in self.issues if i.severity == "MEDIUM" and not i.is_false_positive])

    @property
    def low_count(self) -> int:
        return len([i for i in self.issues if i.severity == "LOW" and not i.is_false_positive])


class AuditReportGenerator:
    """Generates standardized Markdown audit reports."""

    def __init__(self, data: AuditData, lang: str = "en"):
        self.data = data
        self.lang = lang
        self._messages = self._get_messages()

    def _get_messages(self) -> Dict:
        """Get message dictionary for current language."""
        messages = {
            "en": {
                "title": "# Skill Audit Report",
                "section_overview": "## 1. Audit Overview",
                "section_issues": "## 2. Issue Details",
                "section_critical": "### 2.1 CRITICAL Issues",
                "section_high": "### 2.2 HIGH Issues",
                "section_medium": "### 2.3 MEDIUM Issues",
                "section_low": "### 2.4 LOW Issues",
                "section_false_positive": "## 3. False Positive Analysis",
                "section_recommendations": "## 4. Fix Recommendations",
                "section_summary": "## 5. Summary",
                "label_skill_name": "Skill Name",
                "label_audit_level": "Audit Level",
                "label_audit_date": "Audit Date",
                "label_total_issues": "Total Issues",
                "label_severity": "Severity",
                "label_count": "Count",
                "label_item": "Item",
                "label_value": "Value",
                "label_file": "File",
                "label_line": "Line",
                "label_description": "Description",
                "label_fix_suggestion": "Fix Suggestion",
                "label_issue_type": "Issue Type",
                "label_reason": "Reason",
                "label_priority": "Priority",
                "label_action": "Action",
                "label_no_issues": "No {severity} issues found.",
                "label_no_false_positives": "No false positives detected.",
                "label_overall_assessment": "### Overall Assessment",
                "label_key_findings": "### Key Findings",
                "label_recommended_actions": "### Recommended Actions",
                "label_priority_order": "### Priority Order",
                "note_false_positive": "> [!INFO]\n> The following issues are false positives and do not require fixing.",
            },
            "zh": {
                "title": "# Skill Audit Report",
                "section_overview": "## 1. Audit Overview",
                "section_issues": "## 2. Issue Details",
                "section_critical": "### 2.1 CRITICAL Issues",
                "section_high": "### 2.2 HIGH Issues",
                "section_medium": "### 2.3 MEDIUM Issues",
                "section_low": "### 2.4 LOW Issues",
                "section_false_positive": "## 3. False Positive Analysis",
                "section_recommendations": "## 4. Fix Recommendations",
                "section_summary": "## 5. Summary",
                "label_skill_name": "Skill Name",
                "label_audit_level": "Audit Level",
                "label_audit_date": "Audit Date",
                "label_total_issues": "Total Issues",
                "label_severity": "Severity",
                "label_count": "Count",
                "label_item": "Item",
                "label_value": "Value",
                "label_file": "File",
                "label_line": "Line",
                "label_description": "Description",
                "label_fix_suggestion": "Fix Suggestion",
                "label_issue_type": "Issue Type",
                "label_reason": "Reason",
                "label_priority": "Priority",
                "label_action": "Action",
                "label_no_issues": "No {severity} issues found.",
                "label_no_false_positives": "No false positives detected.",
                "label_overall_assessment": "### Overall Assessment",
                "label_key_findings": "### Key Findings",
                "label_recommended_actions": "### Recommended Actions",
                "label_priority_order": "### Priority Order",
                "note_false_positive": "> [!INFO]\n> The following issues are false positives and do not require fixing.",
            }
        }
        return messages.get(self.lang, messages["en"])

    def _msg(self, key: str) -> str:
        """Get message by key."""
        return self._messages.get(key, key)

    def _make_file_link(self, file_path: str, line: int) -> str:
        """Create a clickable Markdown file link."""
        if not file_path:
            return "-"
        full_path = self.data.skill_path / file_path
        return f"[{file_path}](file:///{full_path.as_posix()}#L{line})"

    def _build_overview_section(self) -> str:
        """Build the audit overview section."""
        lines = [
            self._msg("section_overview"),
            "",
            f"| {self._msg('label_item')} | {self._msg('label_value')} |",
            "|------|-------|",
            f"| **{self._msg('label_skill_name')}** | {self.data.skill_name} |",
            f"| **{self._msg('label_audit_level')}** | {self.data.audit_level} |",
            f"| **{self._msg('label_audit_date')}** | {self.data.audit_date} |",
            f"| **{self._msg('label_total_issues')}** | {self.data.total_issues} |",
            "",
            f"### Issue Statistics",
            "",
            f"| {self._msg('label_severity')} | {self._msg('label_count')} |",
            "|----------|-------|",
            f"| CRITICAL | {self.data.critical_count} |",
            f"| HIGH | {self.data.high_count} |",
            f"| MEDIUM | {self.data.medium_count} |",
            f"| LOW | {self.data.low_count} |",
            "",
        ]
        return "\n".join(lines)

    def _build_issues_table(self, issues: List[AuditIssue]) -> str:
        """Build a table for a list of issues."""
        if not issues:
            return ""

        lines = [
            f"| # | {self._msg('label_file')} | {self._msg('label_line')} | {self._msg('label_description')} | {self._msg('label_fix_suggestion')} |",
            "|---|------|------|-------------|----------------|",
        ]

        for i, issue in enumerate(issues, 1):
            file_link = self._make_file_link(issue.file, issue.line)
            desc = issue.description[:80] + "..." if len(issue.description) > 80 else issue.description
            suggestion = issue.suggestion[:50] + "..." if len(issue.suggestion) > 50 else issue.suggestion
            lines.append(f"| {i} | {file_link} | {issue.line} | {desc} | {suggestion} |")

        lines.append("")
        return "\n".join(lines)

    def _build_issues_section(self) -> str:
        """Build the issue details section."""
        lines = [self._msg("section_issues"), ""]

        for severity, section_key in [
            ("CRITICAL", "section_critical"),
            ("HIGH", "section_high"),
            ("MEDIUM", "section_medium"),
            ("LOW", "section_low"),
        ]:
            lines.append(self._msg(section_key))
            lines.append("")
            issues = [i for i in self.data.issues if i.severity == severity and not i.is_false_positive]
            if issues:
                lines.append(self._build_issues_table(issues))
            else:
                lines.append(f"> [!NOTE]")
                lines.append(f"> {self._msg('label_no_issues').format(severity=severity)}")
                lines.append("")

        return "\n".join(lines)

    def _build_false_positive_section(self) -> str:
        """Build the false positive analysis section."""
        false_positives = [i for i in self.data.issues if i.is_false_positive]
        if not false_positives:
            return ""

        lines = [
            self._msg("section_false_positive"),
            "",
            self._msg("note_false_positive"),
            "",
            f"| # | {self._msg('label_file')} | {self._msg('label_line')} | {self._msg('label_issue_type')} | {self._msg('label_reason')} |",
            "|---|------|------|------------|--------|",
        ]

        for i, issue in enumerate(false_positives, 1):
            file_link = self._make_file_link(issue.file, issue.line)
            lines.append(f"| {i} | {file_link} | {issue.line} | {issue.severity} | {issue.false_positive_reason} |")

        lines.append("")
        return "\n".join(lines)

    def _build_recommendations_section(self) -> str:
        """Build the fix recommendations section."""
        lines = [
            self._msg("section_recommendations"),
            "",
            self._msg("label_priority_order"),
            "",
            f"| {self._msg('label_priority')} | {self._msg('label_issue_type')} | {self._msg('label_file')} | {self._msg('label_action')} |",
            "|----------|------------|------|--------|",
        ]

        priority_order = {"HIGH": 1, "MEDIUM": 2, "LOW": 3}
        sorted_issues = sorted(
            [i for i in self.data.issues if not i.is_false_positive],
            key=lambda x: priority_order.get(x.severity, 4)
        )

        for issue in sorted_issues[:10]:
            file_link = self._make_file_link(issue.file, issue.line)
            action = issue.suggestion[:40] + "..." if len(issue.suggestion) > 40 else issue.suggestion
            lines.append(f"| {issue.severity} | {issue.severity} | {file_link} | {action} |")

        lines.append("")
        return "\n".join(lines)

    def _build_summary_section(self) -> str:
        """Build the summary section."""
        lines = [
            self._msg("section_summary"),
            "",
            self._msg("label_overall_assessment"),
            "",
            self.data.overall_assessment or "Audit completed.",
            "",
            self._msg("label_key_findings"),
            "",
        ]

        for finding in self.data.key_findings:
            lines.append(f"- {finding}")

        lines.append("")
        lines.append(self._msg("label_recommended_actions"))
        lines.append("")

        for i, action in enumerate(self.data.recommended_actions, 1):
            lines.append(f"{i}. {action}")

        lines.append("")
        return "\n".join(lines)

    def generate(self) -> str:
        """Generate the complete audit report."""
        sections = [
            self._msg("title"),
            "",
            self._build_overview_section(),
            self._build_issues_section(),
            self._build_false_positive_section(),
            self._build_recommendations_section(),
            self._build_summary_section(),
        ]
        return "\n".join(sections)

    def save(self, output_path: Path) -> bool:
        """Save the report to a file."""
        try:
            report = self.generate()
            output_path.write_text(report, encoding="utf-8", errors="replace")
            return True
        except (OSError, PermissionError) as e:
            print(f"[FAIL] Error saving report: {e}")
            return False


def create_audit_data(
    skill_name: str,
    skill_path: Path,
    audit_level: str,
    issues: List[Tuple[str, int, str, str, str]],
    false_positives: List[Tuple[str, int, str, str, str, str]] = None,
    overall_assessment: str = "",
    key_findings: List[str] = None,
    recommended_actions: List[str] = None,
) -> AuditData:
    """
    Create AuditData from raw issue data.

    Args:
        skill_name: Name of the skill being audited
        skill_path: Path to the skill directory
        audit_level: Audit level (strict/standard/relaxed)
        issues: List of (file, line, severity, description, suggestion) tuples
        false_positives: List of (file, line, severity, description, suggestion, reason) tuples
        overall_assessment: Overall assessment text
        key_findings: List of key findings
        recommended_actions: List of recommended actions

    Returns:
        AuditData object
    """
    data = AuditData(
        skill_name=skill_name,
        skill_path=skill_path,
        audit_level=audit_level,
        overall_assessment=overall_assessment,
        key_findings=key_findings or [],
        recommended_actions=recommended_actions or [],
    )

    for file, line, severity, description, suggestion in issues:
        data.issues.append(AuditIssue(
            file=file,
            line=line,
            severity=severity,
            description=description,
            suggestion=suggestion,
        ))

    if false_positives:
        for file, line, severity, description, suggestion, reason in false_positives:
            data.issues.append(AuditIssue(
                file=file,
                line=line,
                severity=severity,
                description=description,
                suggestion=suggestion,
                is_false_positive=True,
                false_positive_reason=reason,
            ))

    return data
