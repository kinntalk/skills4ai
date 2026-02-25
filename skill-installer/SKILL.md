---
name: skill-installer
description: Install and manage skills from Git repositories into .trae/skills directory. Supports subdirectories, catalog browsing, dependency management, license verification, health checks, and version rollback.
---

# Skill Installer

## Overview

The `skill-installer` simplifies the process of adding new skills to your project. It fetches skills from Git repositories (like GitHub) and installs them into the standard `.trae/skills/` directory. It also automatically triggers `skill-auditor` to verify the quality of installed skills.

## Features

- **Git Integration**: Installs directly from Git URLs.
- **Subdirectory Support**: Can extract specific skills from monorepos (e.g., `user/repo/skill-name`).
- **Auto-Audit**: Automatically runs `skill-auditor` on the installed skill to ensure compliance.
- **Safe Install**: Uses temporary directories to prevent workspace pollution during download.
- **Skill Catalog**: Browse and install skills from a curated catalog.
- **Dependency Management**: Automatically detects and installs skill dependencies.
- **License Verification**: Automatically detects and validates license compatibility.
- **Health Checks**: Validate installed skills for proper structure and dependencies.
- **Version Rollback**: Rollback to previous versions using git history.

## Usage

### Install a Skill

#### By Git URL or User/Repo Format

```bash
python .trae/skills/skill-installer/scripts/install_skill.py <source>
```

**Examples:**
```bash
# Install from full GitHub URL
python scripts/install_skill.py https://github.com/user/my-skill-repo

# Install from user/repo format
python scripts/install_skill.py user/my-skill-repo

# Install specific skill from collection (e.g., vercel-labs/agent-skills)
python scripts/install_skill.py vercel-labs/agent-skills/skills/web-design-guidelines
```

#### By Skill Name

Install skills directly from the catalog using the skill name:

```bash
python .trae/skills/skill-installer/scripts/install_skill.py <skill-name>
```

**Examples:**
```bash
# Install by skill name
python scripts/install_skill.py brainstorming

# Install with category prefix
python scripts/install_skill.py curated/brainstorming

# Install by alias
python scripts/install_skill.py <alias>
```

#### Interactive Installation

Browse the catalog and select skills interactively:

```bash
python .trae/skills/skill-installer/scripts/install_skill.py --interactive
```

This will display:
1. List of available categories
2. Skills in the selected category
3. Skill details and confirmation prompt

#### Batch Installation

Install multiple skills at once:

```bash
python .trae/skills/skill-installer/scripts/install_skill.py skill1 skill2 skill3
```

**Example:**
```bash
python scripts/install_skill.py brainstorming planning-with-files systematic-debugging
```

#### Auto-Confirmation

Use the `--yes` or `-y` flag to automatically confirm all prompts:

```bash
python .trae/skills/skill-installer/scripts/install_skill.py --yes <source>
```

This will:
- Automatically overwrite existing skills
- Auto-install all dependencies without prompting
- Skip license confirmation prompts

#### Custom Destination

```bash
python scripts/install_skill.py user/repo --path ./custom/skills
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

**Uninstall a Skill:**
```bash
python .trae/skills/skill-installer/scripts/manage_skills.py uninstall <skill-name>
```

### Search Skills

Search for skills in the catalog by name, description, or aliases:

```bash
python .trae/skills/skill-installer/scripts/manage_skills.py search <query>
```

**Examples:**
```bash
# Search by name
python scripts/manage_skills.py search pdf

# Search by description keyword
python scripts/manage_skills.py search debugging

# Search by alias
python scripts/manage_skills.py search <alias>
```

### View Skill Information

Get detailed information about a skill:

```bash
python .trae/skills/skill-installer/scripts/manage_skills.py info <skill-name>
```

This displays:
- Skill name and category
- Description
- Source URL
- License type
- Aliases
- Dependencies (with installation status)
- Installation status and version

**Example:**
```bash
python scripts/manage_skills.py info brainstorming
```

### Browse Catalog

Browse all skills in the catalog, optionally filtered by category:

```bash
# Browse all categories and skills
python .trae/skills/skill-installer/scripts/manage_skills.py catalog

# Browse specific category
python .trae/skills/skill-installer/scripts/manage_skills.py catalog --category curated
```

### Health Check

Perform health checks on installed skills:

```bash
# Check all installed skills
python .trae/skills/skill-installer/scripts/manage_skills.py health

# Check specific skill
python .trae/skills/skill-installer/scripts/manage_skills.py health <skill-name>
```

The health check validates:
- Skill directory exists
- SKILL.md file exists
- YAML frontmatter is valid
- Required fields (name, description) are present
- Skill name matches directory name
- Dependencies are installed

### Version Rollback

Rollback a skill to a previous version:

```bash
# Show version history and select version
python .trae/skills/skill-installer/scripts/manage_skills.py rollback <skill-name>

# Rollback to specific version
python .trae/skills/skill-installer/scripts/manage_skills.py rollback <skill-name> --version <commit-hash>
```

## Skill Catalog Format

The skill catalog is stored in `skill_catalog.json` and follows this structure:

```json
{
  "version": "1.0",
  "categories": {
    "category-name": {
      "description": "Category description",
      "skills": [
        {
          "name": "skill-name",
          "description": "Skill description",
          "source": "user/repo or https://github.com/user/repo",
          "license": "MIT",
          "aliases": ["alias1", "alias2"],
          "dependencies": ["dep1", "dep2"]
        }
      ]
    }
  }
}
```

**Fields:**
- `version`: Catalog version (currently "1.0")
- `categories`: Dictionary of categories
  - `category-name`: Category identifier
    - `description`: Category description
    - `skills`: List of skills in this category
      - `name`: Unique skill name
      - `description`: Skill description
      - `source`: Git URL or user/repo format, or "local" for built-in skills
      - `license`: License type
      - `aliases`: Optional list of alternative names
      - `dependencies`: Optional list of required skills

## Dependency Format in SKILL.md

Skills declare dependencies in their SKILL.md file using YAML frontmatter:

```yaml
---
name: my-skill
description: A skill that does something useful
dependencies:
  - brainstorming
  - planning-with-files
---

# My Skill

Detailed documentation here...
```

**Fields:**
- `name`: Skill name (must match directory name)
- `description`: Skill description
- `dependencies`: List of required skill names (optional)

## Dependency Management

Skills can declare dependencies in their SKILL.md file. When installing a skill with dependencies:

1. The installer checks which dependencies are already installed
2. Missing dependencies are listed
3. You're prompted to install missing dependencies (or use `--yes` to auto-install)
4. Dependencies are installed in the correct order (topological sort)
5. Circular dependencies are detected and reported

**Example:**
```bash
# Auto-install dependencies
python scripts/install_skill.py --yes <skill-with-deps>
```

## License Verification

The installer automatically detects and validates license compatibility:

- **Compatible licenses**: MIT, Apache-2.0, BSD, ISC, Public Domain, CC0, Unlicense
- **Warning licenses**: LGPL-2.1, LGPL-3.0, MPL-2.0 (copyleft with restrictions)
- **Incompatible licenses**: GPL, GPL-2.0, GPL-3.0, AGPL (strong copyleft)

When a license is detected:
- License type is displayed
- Compatibility status is shown
- For incompatible licenses, you're prompted to confirm (unless using `--yes`)

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

4. **Skill Not Found in Catalog**
   - Use the `search` command to find the correct skill name or alias.
   - Check if the skill exists in the catalog using `catalog` command.
   - Verify you're using the correct category prefix if needed.

5. **Missing Dependencies**
   - Use `--yes` flag to auto-install dependencies.
   - Or manually install dependencies first, then install the main skill.
   - Use `health` command to check dependency status.

6. **Circular Dependencies**
   - The installer detects circular dependencies and reports them.
   - Review the dependencies in the affected skills and resolve the cycle.

7. **License Incompatible**
   - Review the license terms carefully.
   - Use `--yes` flag to skip license confirmation (not recommended).
   - Consider using an alternative skill with a compatible license.

8. **Health Check Failures**
   - Check that SKILL.md exists and has valid YAML frontmatter.
   - Ensure required fields (name, description) are present.
   - Verify the skill name matches the directory name.
   - Install missing dependencies.

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

**Install by skill name from catalog:**
```bash
python scripts/install_skill.py brainstorming
```

**Install multiple skills at once:**
```bash
python scripts/install_skill.py brainstorming planning-with-files systematic-debugging
```

**Interactive installation:**
```bash
python scripts/install_skill.py --interactive
```

**Search for skills:**
```bash
python scripts/manage_skills.py search pdf
```

**View skill information:**
```bash
python scripts/manage_skills.py info brainstorming
```

**Browse catalog:**
```bash
python scripts/manage_skills.py catalog
python scripts/manage_skills.py catalog --category curated
```

**Health check:**
```bash
python scripts/manage_skills.py health
python scripts/manage_skills.py health brainstorming
```

**Rollback to previous version:**
```bash
python scripts/manage_skills.py rollback brainstorming
python scripts/manage_skills.py rollback brainstorming --version abc1234
```

**Custom Destination:**
```bash
python scripts/install_skill.py user/repo --path ./custom/skills
```

**Auto-confirm all prompts:**
```bash
python scripts/install_skill.py --yes brainstorming
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
