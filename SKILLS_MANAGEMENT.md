# Skills Management Guide

## Overview

This guide explains how to manage Trae skills, including version control, updates, backups, and troubleshooting.

---

## File Structure

```
.trae/skills/
├── skills.json              # Skills registry (version tracking)
├── skills_update.log         # Update log
├── backups/                 # Backup directory
│   ├── skill-name/
│   │   └── 20260210_143022/
│   └── all_skills_20260210_143022.zip
├── skill-installer/
│   └── scripts/
│       ├── install_skill.py      # Install skills from Git
│       ├── manage_skills.py      # List, check, update skills
│       ├── sync_skills.py        # Sync skills.json
│       ├── update_all_skills.py  # Update all skills
│       └── backup_skills.py     # Backup and restore
├── skill-auditor/
│   └── scripts/
│       └── audit_skill.py       # Validate skills
├── skill-creator/
│   └── scripts/
│       ├── init_skill.py         # Create new skill
│       ├── package_skill.py      # Package skill
│       └── quick_validate.py    # Validate skill
└── [other skills...]
```

---

## Skills Registry (skills.json)

The `skills.json` file tracks all installed skills and their versions.

### Structure

```json
{
  "skills": {
    "skill-name": {
      "source": "https://github.com/user/repo.git",
      "subdir": "path/to/skill",
      "version": "abc1234def5678",
      "updated_at": "2026-02-10T14:30:00.000000"
    }
  }
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `source` | string | Git repository URL or "local" for local skills |
| `subdir` | string | Subdirectory path (if skill is in a subdirectory) |
| `version` | string | Git commit hash or "unknown" |
| `updated_at` | string | ISO 8601 timestamp |

---

## Common Commands

### 1. List Installed Skills

```bash
# Using manage_skills.py
python .trae/skills/skill-installer/scripts/manage_skills.py list

# Using sync_skills.py
python .trae/skills/skill-installer/scripts/sync_skills.py list
```

### 2. Check for Updates

```bash
# Check all skills
python .trae/skills/skill-installer/scripts/manage_skills.py check

# Check all skills (using update_all_skills.py)
python .trae/skills/skill-installer/scripts/update_all_skills.py --check-only
```

### 3. Update Skills

```bash
# Update a single skill
python .trae/skills/skill-installer/scripts/manage_skills.py update <skill-name>

# Update all skills
python .trae/skills/skill-installer/scripts/manage_skills.py update-all

# Update all skills (using update_all_skills.py)
python .trae/skills/skill-installer/scripts/update_all_skills.py --force
```

### 4. Install a New Skill

```bash
# Install from GitHub
python .trae/skills/skill-installer/scripts/install_skill.py user/repo

# Install from subdirectory
python .trae/skills/skill-installer/scripts/install_skill.py user/repo/skills/skill-name

# Install from full URL
python .trae/skills/skill-installer/scripts/install_skill.py https://github.com/user/repo.git

# Force overwrite
python .trae/skills/skill-installer/scripts/install_skill.py user/repo --force
```

### 5. Backup Skills

```bash
# Backup all skills
python .trae/skills/skill-installer/scripts/backup_skills.py backup

# Backup a specific skill
python .trae/skills/skill-installer/scripts/backup_skills.py backup --skill <skill-name>

# List backups
python .trae/skills/skill-installer/scripts/backup_skills.py list

# Restore from backup
python .trae/skills/skill-installer/scripts/backup_skills.py restore <backup-file>

# Restore specific skill
python .trae/skills/skill-installer/scripts/backup_skills.py restore <backup-file> --skill <skill-name>

# Clean up old backups (keep 5 most recent)
python .trae/skills/skill-installer/scripts/backup_skills.py cleanup --keep 5
```

### 6. Sync Skills Registry

```bash
# Sync skills.json with installed skills
python .trae/skills/skill-installer/scripts/sync_skills.py sync

# Dry run (preview changes)
python .trae/skills/skill-installer/scripts/sync_skills.py sync --dry-run
```

### 7. Validate a Skill

```bash
# Run skill-auditor
python .trae/skills/skill-auditor/scripts/audit_skill.py <path-to-skill>
```

---

## Version Control Workflow

### Initial Setup

1. Install skills from Git repositories
2. Run `sync_skills.py` to update `skills.json`
3. Verify all skills are registered

### Regular Updates

1. Check for updates: `manage_skills.py check`
2. Review available updates
3. Update skills: `manage_skills.py update-all`
4. Verify updated skills work correctly

### Version Tracking

- Remote skills: Track using Git commit hash
- Local skills: Mark as "local" with version "unknown"
- Updated at: Timestamp of last update

---

## Backup Strategy

### Automatic Backups

The `update_all_skills.py` script automatically:
1. Creates timestamped backups before updates
2. Stores backups in `.trae/skills/backups/<skill-name>/`
3. Keeps only the 5 most recent versions

### Manual Backups

Use `backup_skills.py` to:
- Create full backups of all skills
- Create backups of specific skills
- Restore from previous versions
- Clean up old backups

### Backup Locations

```
.trae/skills/backups/
├── skill-name/
│   ├── 20260210_143022/    # Timestamped directory
│   ├── 20260210_150000/
│   └── 20260210_153000/
└── all_skills_20260210_143022.zip  # Full backup
```

---

## Troubleshooting

### Issue: skills.json is corrupted

**Symptoms:** `sync_skills.py` or `manage_skills.py` fails with JSON parsing errors

**Solution:**
1. Delete `skills.json`
2. Run `sync_skills.py` to regenerate it
3. Manually add version info for remote skills

```bash
rm .trae/skills/skills.json
python .trae/skills/skill-installer/scripts/sync_skills.py sync
```

### Issue: Skill not recognized

**Symptoms:** User requests a skill, but system doesn't recognize it

**Solution:**
1. Check if skill is in `skills.json`
2. Run `sync_skills.py` to refresh registry
3. Verify skill directory exists with `SKILL.md`

### Issue: Update fails

**Symptoms:** `manage_skills.py update` fails to install new version

**Solution:**
1. Check Git repository URL is correct
2. Verify network connectivity
3. Check if repository is private (requires authentication)
4. Restore from backup if needed

```bash
# Restore from backup
python .trae/skills/skill-installer/scripts/backup_skills.py restore <backup-file>
```

### Issue: Version information is inaccurate

**Symptoms:** `skills.json` version doesn't match actual version

**Solution:**
1. Run `git ls-remote` to get latest commit hash
2. Update `skills.json` manually
3. Run `sync_skills.py` to update timestamp

```bash
git ls-remote https://github.com/user/repo.git HEAD
```

### Issue: Local skill marked as remote

**Symptoms:** Local skill has a Git URL in `skills.json`

**Solution:**
1. Edit `skills.json`
2. Change `source` to "local"
3. Set `version` to "unknown"

```json
{
  "skills": {
    "my-local-skill": {
      "source": "local",
      "subdir": "",
      "version": "unknown",
      "updated_at": "2026-02-10T14:30:00.000000"
    }
  }
}
```

---

## Best Practices

### 1. Regular Updates

- Check for updates weekly
- Test updated skills before using in production
- Keep backup of working versions

### 2. Version Tracking

- Always update `skills.json` after installing new skills
- Use Git commit hashes for remote skills
- Keep `updated_at` timestamps accurate

### 3. Backup Strategy

- Create full backups before major updates
- Keep at least 3-5 recent versions
- Store backups in a separate location for disaster recovery

### 4. Skill Validation

- Run `skill-auditor` after installing new skills
- Check for encoding issues (especially on Windows)
- Verify dependencies are declared in `requirements.txt`

### 5. Registry Maintenance

- Run `sync_skills.py` regularly to keep registry accurate
- Remove entries for uninstalled skills
- Keep `skills.json` in version control

---

## Advanced Topics

### Custom Backup Locations

Specify a custom backup directory:

```bash
python .trae/skills/skill-installer/scripts/backup_skills.py backup --output /path/to/backups
```

### Force Updates

Skip confirmation prompts:

```bash
# Update single skill
python .trae/skills/skill-installer/scripts/manage_skills.py update <skill-name> --force

# Update all skills
python .trae/skills/skill-installer/scripts/update_all_skills.py --force
```

### Restore Specific Skill

Restore a single skill from a full backup:

```bash
python .trae/skills/skill-installer/scripts/backup_skills.py restore all_skills_20260210.zip --skill <skill-name>
```

---

## Related Files

| File | Description |
|------|-------------|
| `.trae/skills/skills.json` | Skills registry |
| `.trae/skills/skills_update.log` | Update log |
| `.trae/skills/skill_map.json` | Skill keyword mapping |
| `.trae/skills/SKILLS_REGISTRY.md` | Registry documentation |

---

## References

- [Trae Skills Documentation](https://github.com/anthropics/skills)
- [Skill Auditor](./skill-auditor/SKILL.md)
- [Skill Creator](./skill-creator/SKILL.md)
- [Skill Installer](./skill-installer/SKILL.md)
