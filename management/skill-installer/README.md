# Skill Installer

## Overview

The `skill-installer` simplifies the process of adding new skills to your project. It fetches skills from Git repositories (like GitHub) and installs them into the standard `.trae/skills/` directory. It also automatically triggers `skill-auditor` to verify the quality of installed skills.

## Features

- **Git Integration**: Installs directly from Git URLs.
- **Subdirectory Support**: Can extract specific skills from monorepos (e.g., `user/repo/skill-name`) and automatically detect common prefixes (e.g., `skills/`).
- **Robust Network Handling**: Automatically retries Git operations on network failure.
- **Safe Updates**: Implements automatic backup and rollback mechanisms during updates.
- **Auto-Audit**: Automatically runs `skill-auditor` on the installed skill to ensure compliance.

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

## Troubleshooting

### Common Issues

1. **Network Errors (`Failed to connect`, `Connection reset`)**
   - The installer automatically retries up to 3 times.
   - If persistent, check your internet connection or proxy settings.
   - Use `manage_skills.py update` which now safely backs up your existing skill before attempting an update, so you won't lose functionality if the network fails.

2. **Subdirectory Not Found**
   - The installer now attempts to auto-detect the correct path by checking common prefixes like `skills/`, `packages/`, or `apps/`.
   - If it still fails, verify the repository structure on GitHub and provide the full path (e.g., `user/repo/custom/path/to/skill`).

3. **Permission Denied**
   - Ensure you have write permissions to the `.trae/skills` directory.
   - On Windows, ensure no other process (like an open terminal or editor) is locking the files.

## Interaction Rules

> **Important Rule for AI Assistants:**
> If the user requests to install a skill but **does not explicitly mention** using `skill-installer`, you **MUST** ask for confirmation first.
