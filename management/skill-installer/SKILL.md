---
name: skill-installer
description: Install and manage Trae skills from Git repositories. Supports subdirectories for monorepo skill collections. Automatically triggers skill-auditor to verify quality. Part of the management skills ecosystem with context-aware routing support.
keywords:
  - install
  - update
  - uninstall
  - manage
  - git
  - repository
  - 安装
  - 更新
  - 卸载
  - 管理
  - git仓库
  - 安装skill
  - 更新skill
  - 卸载skill
aliases:
  - skill-manager
  - skill-updater
  - install-skill
  - update-skill
---

# Skill Installer

## Overview

The `skill-installer` simplifies the process of adding new skills to your project. It fetches skills from Git repositories (like GitHub) and installs them into the standard `.trae/skills/` directory. It also automatically triggers `skill-auditor` to verify the quality of installed skills.

## When to Use This Skill

Use this skill when:
- User wants to install a skill from a Git repository
- User wants to update an existing skill
- User wants to manage installed skills (list, check updates)
- User mentions installing/updating/uninstalling skills

## Skill Context and Routing

This skill is part of the **management** skills category and is automatically routed by the intelligent routing system based on:

- **Trigger Phase**: `management`
- **Required For**: `skill-installation`, `skill-updates`
- **Priority**: 5

The routing system uses the `skill_map.json` context field to automatically detect when this skill should be invoked based on keywords like "install", "update", "uninstall", "manage", "git", "repository".

## Features

- **Git Integration**: Installs directly from Git URLs.
- **Subdirectory Support**: Can extract specific skills from monorepos (e.g., `user/repo/skill-name`).
- **Auto-Audit**: Automatically runs `skill-auditor` on the installed skill to ensure compliance.
- **Safe Install**: Uses temporary directories to prevent workspace pollution during download.
- **Registry Updates**: Automatically updates `skills.json` with installed skill information.

## Skills Directory Structure

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

## Usage

### Install a Skill

```bash
python .trae/skills/management/skill-installer/scripts/install_skill.py <source>
```

### Manage Skills

The `manage_skills.py` script provides a convenient way to list installed skills, check for updates, and upgrade them.

**List Installed Skills:**
```bash
python .trae/skills/management/skill-installer/scripts/manage_skills.py list
```

**Check for Updates:**
```bash
python .trae/skills/management/skill-installer/scripts/manage_skills.py check
```

**Update a Skill:**
```bash
python .trae/skills/management/skill-installer/scripts/manage_skills.py update <skill-name>
```

**Update All Skills:**
```bash
python .trae/skills/management/skill-installer/scripts/manage_skills.py update-all
```

### Examples

**Install a full repo as a skill:**
```bash
python .trae/skills/management/skill-installer/scripts/install_skill.py user/my-skill-repo
```

**Install a specific skill from a collection (e.g., vercel-labs/agent-skills):**
```bash
# syntax: user/repo/path/to/skill
python .trae/skills/management/skill-installer/scripts/install_skill.py vercel-labs/agent-skills/skills/web-design-guidelines
```

**Install from official anthropics/skills monorepo:**
The official Anthropic skills repository is a monorepo with skills in the `skills/` subdirectory:
```bash
# Install template-skill (minimal template)
python .trae/skills/management/skill-installer/scripts/install_skill.py anthropics/skills/template

# Install skill-creator (full scaffolding)
python .trae/skills/management/skill-installer/scripts/install_skill.py anthropics/skills/skills/skill-creator

# Install pdf skill (with scripts and references)
python .trae/skills/management/skill-installer/scripts/install_skill.py anthropics/skills/skills/pdf
```

**Custom Destination:**
```bash
python .trae/skills/management/skill-installer/scripts/install_skill.py user/repo --path ./custom/skills
```

## Integration with Management Workflow

This skill is part of the management skills workflow defined in [AGENTS.md](../AGENTS.md).

### Integration with Skills CLI

The skill-installer skill integrates with the Skills CLI (`npx skills`) to provide better installation and management experience.

### Recommended Workflow

**Step 1: Search for skills using find-skills**
```bash
# Use find-skills to search
python .trae/skills/management/find-skills/scripts/find_skills.py "planning"
```

**Step 2: Install found skills using skill-installer**
```bash
# Use skill-installer to install
python .trae/skills/management/skill-installer/scripts/install_skill.py <source>
```

**Benefits:**
- Better integration with local skills
- Automatic quality checks via skill-auditor
- Consistent routing priority
- Better error handling
- Unified skill management workflow

### When to Use Skills CLI Directly

Only use `npx skills` commands directly when:
- Installing skills from external repositories
- Updating skills from external repositories
- Managing skills from external repositories

**For local skills**, always use the local management workflow (find-skills → skill-installer) to ensure:
- Automatic quality checks
- Consistent routing priority
- Better integration with project

**⚠️ Important**: Using `npx skills find` or `npx skills add` directly may bypass quality checks and routing priorities. Always prefer the local management workflow when available.

1. **find-skills**: Discover available skills
2. **skill-installer**: Install from Git repositories (this skill)
3. **skill-auditor**: Validate skill compliance
4. **skill-creator**: Create new skills

**Management Boundaries:**
- **ALWAYS** audit skills after installation
- **NEVER** install skills without updating `skills.json`
- **USE** skill-creator for new skill scaffolding

## Automatic Quality Verification

After installing a skill, `skill-installer` automatically runs `skill-auditor` to verify:

- **Basic Structure**: Proper frontmatter, name consistency, directory structure
- **Dependencies**: Dependency integrity and requirements.txt validation
- **Encoding & Path Safety**: File encoding and path reference checks
- **Packaging**: Packaging structure and template validation
- **Subprocess & Path Operations**: Subprocess robustness and risky operations
- **Cross-Platform Compatibility**: Platform-specific commands and path handling
- **Internationalization (i18n)**: Multi-language support and message handling
- **Absolute References**: Hardcoded absolute paths detection
- **Registry & Map Consistency**: skills.json and skill_map.json validation

If the skill fails any critical checks, the installation will be aborted with a detailed error message.

## Interaction Rules

> **Important Rule for AI Assistants:**
> If the user requests to install a skill but **does not explicitly mention** using `skill-installer`, you **MUST** ask for confirmation first.
>
> **Example:**
> User: "Install the weather skill."
> AI: "Would you like me to use the `skill-installer` to fetch and install that skill?"

## Integration with Intelligent Routing System

The intelligent routing system (see [SKILL_ROUTING.md](../../SKILL_ROUTING.md)) automatically detects when users need to install skills and routes to this skill based on:

- **Keyword matching**: "install", "update", "uninstall", "manage", "git", "repository"
- **Context awareness**: Management phase triggers
- **Priority**: 5 (medium priority)

After using this skill, the routing system may recommend:
- **skill-auditor**: To verify the installed skill meets quality standards
- **skill-creator**: If the user wants to modify or extend the installed skill
- **find-skills**: If the user wants to discover more skills

## Quality Monitoring

This skill is monitored by the quality monitoring system (see [SKILL_QUALITY_MONITOR.md](../../SKILL_QUALITY_MONITOR.md)):

- **Target Success Rate**: > 90%
- **Target Usage Frequency**: Low (< 5/day)
- **Priority**: High

Usage statistics are tracked in `skill_usage_stats.json` to optimize routing and identify improvement opportunities.

## Requirements

- `git` must be installed and available in the system PATH.
- Python 3.7 or higher
- Dependencies listed in `scripts/requirements.txt`

## Troubleshooting

### Issue: Installation fails with "git not found"

**Solution:**
1. Verify git is installed: `git --version`
2. Ensure git is in system PATH
3. Restart terminal after installing git

### Issue: Skill fails audit after installation

**Solution:**
1. Review audit output for specific issues
2. Check if skill is compatible with current Trae version
3. Contact skill maintainer if issues persist
4. Consider using `skill-creator` to create a custom skill

### Issue: Cannot find installed skill

**Solution:**
1. Verify skill is in correct category directory (workflow/, management/, or domain/)
2. Check that skills.json contains the skill entry
3. Ensure skill_map.json has proper mapping
4. Run `manage_skills.py list` to see all installed skills

### Issue: Update fails

**Solution:**
1. Check network connectivity
2. Verify Git repository URL is correct
3. Ensure you have write permissions to the skills directory
4. Check if the skill has been removed or renamed in the repository

## Related Skills

- **find-skills**: Discover available skills before installing
- **skill-auditor**: Verify skill quality and compliance
- **skill-creator**: Create custom skills if needed
