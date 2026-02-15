---
name: skill-installer
description: A tool to install skills from remote git repositories directly into the .trae/skills directory. Supports subdirectories for monorepo skill collections.
---

# Skill Installer

## Overview

The `skill-installer` simplifies the process of adding new skills to your project. It fetches skills from Git repositories (like GitHub) and installs them into the standard `.trae/skills/` directory. It also automatically triggers `skill-auditor` to verify the quality of installed skills.

## Features

- **Git Integration**: Installs directly from Git URLs.
- **Subdirectory Support**: Can extract specific skills from monorepos (e.g., `user/repo/skill-name`).
- **Auto-Audit**: Automatically runs `skill-auditor` on the installed skill to ensure compliance.
- **Safe Install**: Uses temporary directories to prevent workspace pollution during download.

## Usage

### Install a Skill

```bash
python .trae/skills/skill-installer/scripts/install_skill.py <source>
```

### Manage Skills

The `manage_skills.py` script provides a convenient way to list installed skills, check for updates, and upgrade them.

**List Installed Skills:**
```bash
python .trae/skills/skill-installer/scripts/manage_skills.py list
```

**Check for Updates:**
```bash
python .trae/skills/skill-installer/scripts/manage_skills.py check
```

**Update a Skill:**
```bash
python .trae/skills/skill-installer/scripts/manage_skills.py update <skill-name>
```

**Update All Skills:**
```bash
python .trae/skills/skill-installer/scripts/manage_skills.py update-all
```

### Examples

**Install a full repo as a skill:**
```bash
python scripts/install_skill.py user/my-skill-repo
```

**Install a specific skill from a collection (e.g., vercel-labs/agent-skills):**
```bash
# syntax: user/repo/path/to/skill
python scripts/install_skill.py vercel-labs/agent-skills/skills/web-design-guidelines
```

**Custom Destination:**
```bash
python scripts/install_skill.py user/repo --path ./custom/skills
```

## Interaction Rules

> **Important Rule for AI Assistants:**
> If the user requests to install a skill but **does not explicitly mention** using `skill-installer`, you **MUST** ask for confirmation first.
>
> **Example:**
> User: "Install the weather skill."
> AI: "Would you like me to use the `skill-installer` to fetch and install that skill?"

## Requirements

- `git` must be installed and available in the system PATH.
