---
name: skill-installer
description: "Install and manage skills from Git repositories into .trae/skills directory. Use this skill whenever the user wants to install, uninstall, update, or manage skills. Triggers on phrases like 'install skill', '安装 skill', '从 GitHub 安装', 'uninstall skill', '卸载 skill', 'update skills', 'list skills', '列出已安装的 skills'. Also handles encoding detection and conversion for skill files. Note: Registry synchronization is handled by skills-registry-sync skill."
---

# Skill Installer

Install, manage, and maintain Trae skills from Git repositories.

## When to Use This Skill

Use this skill immediately when the user:

**Installation requests:**
- Mentions installing a skill: "install xxx skill", "安装 xxx skill"
- Wants to add from GitHub: "从 GitHub 安装", "clone and install"
- Provides a Git URL or user/repo format

**Management requests:**
- Wants to uninstall: "uninstall xxx", "卸载 xxx", "删除 xxx skill"
- Wants to update: "update skills", "更新 skills"
- Wants to list installed: "list skills", "列出已安装的 skills"
- Wants skill info: "show info for xxx", "查看 xxx 信息"

**Encoding requests:**
- Detect encoding: "检测文件编码", "detect encoding"
- Convert encoding: "转换编码", "convert to UTF-8"

**Do NOT use for:**
- Finding/searching for skills → use `find-skills` skill instead

## Core Operations

### Install a Skill

```bash
python .trae/skills/skill-installer/scripts/install_skill.py <source>
```

**Source formats:**
- Full URL: `https://github.com/user/repo`
- Short format: `user/repo`
- With subdirectory: `user/repo/path/to/skill`
- Skill name from catalog: `brainstorming`

**Options:**
- `--yes` or `-y`: Auto-confirm all prompts (overwrite, dependencies, license)
- `--force`: Force overwrite existing installation
- `--no-audit`: Skip skill-auditor check
- `--path <dir>`: Custom destination directory

**Examples:**
```bash
# Install from GitHub URL
python scripts/install_skill.py https://github.com/user/my-skill

# Install with short format
python scripts/install_skill.py user/my-skill

# Install specific skill from monorepo
python scripts/install_skill.py vercel-labs/agent-skills/skills/web-design-guidelines

# Batch install multiple skills
python scripts/install_skill.py skill1 skill2 skill3

# Auto-confirm everything
python scripts/install_skill.py --yes brainstorming
```

### Manage Skills

```bash
python .trae/skills/skill-installer/scripts/manage_skills.py <command>
```

**Commands:**

| Command | Description |
|---------|-------------|
| `list` | List all installed skills |
| `check` | Check for available updates |
| `update <name>` | Update a specific skill |
| `update-all` | Update all skills |
| `uninstall <name>` | Remove a skill |
| `search <query>` | Search installed skills |
| `info <name>` | Show skill details |
| `health [name]` | Health check on skills |
| `rollback <name>` | Rollback to previous version |

**Examples:**
```bash
# List installed skills
python scripts/manage_skills.py list

# Check for updates
python scripts/manage_skills.py check

# Update a specific skill
python scripts/manage_skills.py update brainstorming

# Update with auto-confirm
python scripts/manage_skills.py update brainstorming --yes

# Uninstall a skill
python scripts/manage_skills.py uninstall old-skill

# Search for skills
python scripts/manage_skills.py search pdf

# Health check all skills
python scripts/manage_skills.py health

# Rollback to previous version
python scripts/manage_skills.py rollback brainstorming
```

### Encoding Operations

**Detect encoding:**
```bash
python .trae/skills/skill-installer/scripts/detect_encoding.py <path>

# Examples
python scripts/detect_encoding.py file.txt
python scripts/detect_encoding.py directory/ --recursive
python scripts/detect_encoding.py directory/ --extensions .py .txt
```

**Convert encoding:**
```bash
python .trae/skills/skill-installer/scripts/convert_encoding.py <path> --target <encoding>

# Examples
python scripts/convert_encoding.py file.txt --target utf-8
python scripts/convert_encoding.py directory/ --target utf-8 --recursive
python scripts/convert_encoding.py file.txt --source gbk --target utf-8 --overwrite
```

## How Installation Works

1. **Clone**: Downloads the repository to a temporary directory
2. **Detect**: Identifies skill name from SKILL.md or directory structure
3. **Validate**: Checks for SKILL.md with proper YAML frontmatter
4. **License**: Detects and validates license compatibility
5. **Dependencies**: Checks and installs missing dependencies
6. **Install**: Copies to `.trae/skills/<skill-name>/`
7. **Audit**: Runs skill-auditor for compliance check

## Dependency Management

Skills can declare dependencies in SKILL.md frontmatter:

```yaml
---
name: my-skill
description: A skill that depends on others
dependencies:
  - brainstorming
  - planning-with-files
---
```

When installing a skill with dependencies:
- Missing dependencies are detected automatically
- You're prompted to install them (or use `--yes` to auto-install)
- Installation order is resolved via topological sort
- Circular dependencies are detected and reported

## License Compatibility

| Status | Licenses |
|--------|----------|
| ✅ Compatible | MIT, Apache-2.0, BSD, ISC, Public Domain, CC0, Unlicense |
| ⚠️ Warning | LGPL-2.1, LGPL-3.0, MPL-2.0 |
| ❌ Incompatible | GPL, GPL-2.0, GPL-3.0, AGPL |

## Registry Synchronization

After installing or uninstalling skills, run the `skills-registry-sync` skill to update:
- `skills.json` - Source, version, health status
- `skill_map.json` - Skill metadata
- `AGENTS.md` - Skill documentation

```bash
python .trae/skills/skills-registry-sync/scripts/sync_registry.py
```

## Troubleshooting

**Network errors:**
- Installer retries up to 3 times automatically
- Check internet connection or proxy settings
- Use `manage_skills.py update` which backs up before updating

**Subdirectory not found:**
- Installer auto-detects common prefixes: `skills/`, `packages/`, `apps/`
- Verify repository structure on GitHub

**Permission denied:**
- Ensure write permissions to `.trae/skills`
- On Windows, close any programs locking the files

**Missing dependencies:**
- Use `--yes` flag to auto-install
- Or install dependencies first, then main skill

## Requirements

- `git` must be installed and in PATH
- `chardet` library for encoding features: `pip install chardet`
