---
name: skills-registry-sync
description: Synchronize skills registry files (skills.json, skill_map.json, AGENTS.md) after skill operations. **MUST invoke after completing** install/uninstall/create operations, or when explicitly requesting registry sync/consistency checks (e.g., "同步注册表", "sync registry", "check consistency").
---

# Skills Registry Sync

This skill maintains consistency across all skills registry files by synchronizing skills.json, skill_map.json, and AGENTS.md with the actual installed skills.

## Core Files

| File | Purpose |
|------|---------|
| `skills.json` | Tracks installed skills with source, version, health status |
| `skill_map.json` | Maps skill names to descriptions, keywords, aliases for detection |
| `AGENTS.md` | Human-readable registry with skill documentation |

## Decision Flow

First determine what the user needs:

1. **User just completed install/uninstall/create** → Run `sync_registry.py`
2. **User explicitly requests sync** → Run `sync_registry.py`
3. **User wants to check consistency** → Run `check_consistency.py`
4. **User mentions registry issues** → Run `check_consistency.py` first, then `sync_registry.py --fix` if needed

## Execution Steps

### Step 1: Sync All Registries

Invoke this when:
- User has just completed installing a skill
- User has just completed uninstalling a skill
- User has just completed creating a skill
- User explicitly asks to sync the registry

```bash
python .trae/skills/skills-registry-sync/scripts/sync_registry.py
```

The script will:
1. Scan `.trae/skills/` directory for all installed skills
2. Update `skills.json` with current skill information
3. Update `skill_map.json` with skill metadata
4. Update `AGENTS.md` with skill documentation
5. Report all changes made

**Why this matters:** Registry files must stay in sync to ensure accurate skill tracking, proper triggering, and consistent documentation across the system.

### Step 2: Check Consistency

Invoke this when:
- User wants to verify registry consistency
- User suspects registry issues
- User mentions inconsistencies

```bash
python .trae/skills/skills-registry-sync/scripts/check_consistency.py
```

The script will:
1. Compare `skills.json` with actual skill directories
2. Compare `skill_map.json` with `skills.json`
3. Compare `AGENTS.md` with actual skills
4. Generate a consistency report with specific issues

**Why this matters:** Inconsistencies can cause skills to be missing from detection, have incorrect metadata, or be documented incorrectly.

### Step 3: Fix Inconsistencies

If the consistency check reports issues, run:

```bash
python .trae/skills/skills-registry-sync/scripts/sync_registry.py --fix
```

This automatically fixes all detected inconsistencies.

## Output Format

Report sync results clearly:

```
[SYNC] Scanning skills directory...
[INFO] Found N installed skills
[SYNC] Updated skills.json with N skills
[SYNC] Updated skill_map.json (X added, Y removed)
[SYNC] Updated AGENTS.md with N skills
[PASS] All registry files synchronized successfully
```

For consistency checks:

```
[CHECK] Checking skills.json...
[PASS/FAIL] Status message
[CHECK] Checking skill_map.json...
[PASS/FAIL] Status message
[CHECK] Checking AGENTS.md...
[PASS/FAIL] Status message

CONSISTENCY REPORT
Total issues found: N
  Critical: X
  Missing entries: Y
  Orphan entries: Z
```

## Integration Rules

**When to invoke this skill:**

Invoke **AFTER** these operations complete successfully:
- Installing a skill (e.g., after "安装 find-skills", "install find-skills")
- Uninstalling a skill (e.g., after "卸载 find-skills", "uninstall find-skills")
- Creating a skill (e.g., after "创建 skill", "create skill")

**When NOT to invoke:**

- If the install/uninstall/create operation fails or is cancelled
- If the user is only searching or viewing skills (no changes made)
- For bare commands like "install skill" without context of completion

**Integration with other skills:**

- **skill-installer**: Automatically call this skill after successful install/uninstall
- **skill-creator**: Automatically call this skill after successful skill creation
- **skill-auditor**: Health check results are used for validation
