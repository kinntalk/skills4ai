---
name: skills-registry-sync
description: Automatically check, update, and maintain consistency of skills registry files (skills.json, skill_map.json, AGENTS.md). Use when skills are installed/uninstalled, when registry files need synchronization, or for periodic maintenance to ensure all registration information is accurate and up-to-date.
---

# Skills Registry Sync

This skill maintains consistency across all skills registry files, ensuring accurate tracking of installed skills.

## When to Use

- After installing or uninstalling skills
- When registry files (skills.json, skill_map.json, AGENTS.md) are out of sync
- For periodic maintenance to ensure consistency
- When detecting and fixing registry inconsistencies

## Core Files

| File | Purpose |
|------|---------|
| `skills.json` | Tracks installed skills with source, version, health status |
| `skill_map.json` | Maps skill names to descriptions, keywords, aliases for detection |
| `AGENTS.md` | Human-readable registry with skill documentation |

## Usage

### Sync All Registries

```bash
python .trae/skills/skills-registry-sync/scripts/sync_registry.py
```

This will:
1. Scan `.trae/skills/` directory for all installed skills
2. Update `skills.json` with current skill information
3. Update `skill_map.json` with skill metadata
4. Update `AGENTS.md` with skill documentation
5. Report all changes made

### Check Consistency

```bash
python .trae/skills/skills-registry-sync/scripts/check_consistency.py
```

This will:
1. Compare `skills.json` with actual skill directories
2. Compare `skill_map.json` with `skills.json`
3. Compare `AGENTS.md` with actual skills
4. Generate a consistency report

### Fix Inconsistencies

```bash
python .trae/skills/skills-registry-sync/scripts/sync_registry.py --fix
```

Automatically fixes detected inconsistencies.

## Output

The sync process reports:
- Skills added/removed from registries
- Metadata changes (version, source, description)
- Health status updates
- AGENTS.md section updates

## Interaction Rules

> **Important Rule for AI Assistants:**
>
> **When to Invoke skills-registry-sync:**
> - After successfully **installing** a skill (e.g., "安装 * skill", "install * skill")
> - After successfully **uninstalling** a skill (e.g., "卸载 * skill", "uninstall * skill")
> - After successfully **creating** a skill (e.g., "生成 * skill", "创建 * skill", "create * skill")
> - Always invoke **AFTER** the operation completes successfully, **NOT** before.
>
> **When NOT to Invoke skills-registry-sync:**
> - If the install/uninstall/create operation fails or is cancelled
> - If the user is only searching or viewing skills (no changes made)
>
> **Examples that REQUIRE skills-registry-sync (after completion):**
> - "安装 find-skills 这个 skill" → After installation completes, invoke skills-registry-sync
> - "安装 find-skills" → After installation completes, invoke skills-registry-sync
> - "install find-skills" → After installation completes, invoke skills-registry-sync
> - "卸载 find-skills" → After uninstallation completes, invoke skills-registry-sync
> - "uninstall find-skills" → After uninstallation completes, invoke skills-registry-sync
> - "创建一个新的 skill" → After creation completes, invoke skills-registry-sync
> - "create my-custom skill" → After creation completes, invoke skills-registry-sync

## Integration

This skill integrates with:
- **skill-installer**: Automatically called after install/uninstall
- **skill-auditor**: Uses health check results for validation
