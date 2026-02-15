---
name: skill-creator
description: Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Claude's capabilities with specialized knowledge, workflows, or tool integrations. Part of the management skills ecosystem with context-aware routing support.
keywords:
  - create
  - new
  - skill
  - template
  - init
  - package
  - workflow
  - guide
  - documentation
  - scaffolding
  - boilerplate
  - structure
  - setup
  - initialization
  - template-generator
  - skill-development
  - skill-creation
  - skill-management
  - skill-packaging
  - 创建
  - 新建
  - 技能
  - 模板
  - 初始化
  - 打包
  - 工作流
  - 指南
  - 文档
  - 脚手架
  - 结构
  - 设置
aliases:
  - skill-creator
  - create-skill
  - init-skill
  - skill-scaffolding
  - skill-template
  - skill-generator
license: Complete terms in LICENSE.txt
---

# Skill Creator

This skill provides guidance for creating effective skills.

## Overview

Skills are modular, self-contained packages that extend Claude's capabilities with specialized knowledge, workflows, and tool integrations. This skill helps you create new skills or update existing ones.

## When to Use This Skill

Use this skill when:
- User wants to create a new skill
- User wants to add a custom skill to the workspace
- User asks to set up a skill template
- User asks "how to create a skill"
- User mentions creating/adding/making any skill

## Skill Context and Routing

This skill is part of the **management** skills category and is automatically routed by the intelligent routing system based on:

- **Trigger Phase**: `management`
- **Required For**: `skill-development`, `skill-packaging`
- **Priority**: 5

The routing system uses `skill_map.json` context field to automatically detect when this skill should be invoked based on keywords like "create", "new", "skill", "template", "init", "package", "workflow", "guide", "documentation", "scaffolding", "boilerplate", "structure", "setup", "initialization".

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

## Skill Structure

A valid skill requires:

1. **Directory**: `.trae/skills/<category>/<skill-name>/` (where category is workflow/, management/, or domain/)
2. **File**: `SKILL.md` inside the directory
3. **Optional Resources**: `scripts/`, `references/`, `assets/` subdirectories

## Creating a New Skill

### Option A: Use the Built-in Template (Recommended)

The `init_skill.py` script creates a complete skill structure with example files:

```bash
python .trae/skills/management/skill-creator/scripts/init_skill.py <skill-name> --path .trae/skills/
```

This creates:
- `SKILL.md` with comprehensive template
- `scripts/example.py` - Example executable script
- `scripts/requirements.txt` - Python dependencies
- `references/api_reference.md` - Reference documentation
- `assets/example_asset.txt` - Example asset file

### Option B: Use Official Minimal Template

For a minimal starting point, copy the official template-skill:

```bash
python .trae/skills/management/skill-installer/scripts/install_skill.py anthropics/skills/template
```

This creates a minimal `SKILL.md` with just the YAML frontmatter.

### Option C: Manual Creation

Create the directory and file manually:

```bash
mkdir .trae/skills/management/my-skill
```

Create `SKILL.md` with:

```yaml
---
name: my-skill
description: Brief description of what this skill does and when to use it.
keywords:
  - keyword1
  - keyword2
aliases:
  - alias1
  - alias2
---

# My Skill

Add your instructions here...
```

## SKILL.md Format

### Required Frontmatter

```yaml
---
name: skill-name
description: Concise description (under 200 characters) covering:
  1. What the skill does
  2. When Claude should use it
keywords:
  - keyword1
  - keyword2
aliases:
  - alias1
  - alias2
---
```

### Optional Fields

```yaml
license: path/to/LICENSE.txt
```

### Content Structure

After the frontmatter, add Markdown sections that guide Claude:

```markdown
## Overview

Brief explanation of what this skill enables.

## When to Use

Specific scenarios when this skill should be invoked.

## Usage

Step-by-step instructions or examples.

## Resources

Information about bundled resources (scripts, references, assets).
```

## Integration with Intelligent Routing System

To ensure your skill is properly routed by the intelligent routing system, you must:

1. **Add keywords**: Include relevant keywords in the frontmatter
2. **Add aliases**: Provide alternative names for the skill
3. **Update skill_map.json**: Add your skill to the mapping configuration

### skill_map.json Structure

```json
{
  "skills": {
    "your-skill-name": {
      "name": "your-skill-name",
      "path": "management/your-skill-name",
      "description": "Brief description",
      "context": {
        "trigger_phase": "management",
        "required_for": ["your-use-case"],
        "priority": 5
      },
      "keywords": ["keyword1", "keyword2"],
      "aliases": ["alias1", "alias2"]
    }
  },
  "detection_rules": {
    "exact_match": {
      "your-keyword": "your-skill-name"
    },
    "partial_match": {
      "your-keyword": "your-skill-name"
    },
    "context_aware": {
      "management": ["your-skill-name"]
    }
  }
}
```

### Context Field Explanation

The `context` field in skill_map.json defines:

- **trigger_phase**: When this skill should be triggered (e.g., "management", "workflow", "domain")
- **required_for**: What use cases this skill is required for
- **priority**: Skill priority (1-10, where 1 is highest priority)

## Resource Directories

### scripts/

Executable code (Python/Bash/etc.) that can be run directly.

**Examples:**
- PDF skill: `fill_fillable_fields.py`, `convert_pdf_to_images.py`
- DOCX skill: `document.py`, `utilities.py`

**Use for:** Automation, data processing, file conversion, API calls.

### references/

Documentation loaded into context to inform Claude's process.

**Examples:**
- Product management: `communication.md`, `context_building.md`
- BigQuery: API reference documentation
- Finance: Schema documentation, company policies

**Use for:** In-depth documentation, API references, workflow guides.

### assets/

Files used in Claude's output (not loaded into context).

**Examples:**
- Brand styling: PowerPoint templates, logo files
- Frontend builder: HTML/React boilerplate
- Typography: Font files (.ttf, .woff2)

**Use for:** Templates, boilerplate code, images, fonts, sample data.

## Best Practices

1. **Keep descriptions concise** - Under 200 characters for best display
2. **Use imperative language** - "To complete X, do Y" not "You should do X"
3. **Be specific about triggers** - When should Claude use this skill?
4. **Include examples** - Concrete user requests and expected outputs
5. **Organize by structure** - Choose workflow-based, task-based, or reference-based organization
6. **Test thoroughly** - Use `skill-auditor` to validate your skill
7. **Add to skill_map.json** - Ensure skill is properly mapped for routing
8. **Follow AGENTS.md** - Adhere to category-specific guidelines
9. **Support i18n** - Include both English and Chinese keywords when appropriate
10. **Avoid emojis** - Never use emojis in code output statements

## Validation

After creating a skill, validate it:

```bash
python .trae/skills/management/skill-auditor/scripts/audit_skill.py .trae/skills/management/my-skill
```

The auditor checks for:
- Proper frontmatter and structure
- Dependency integrity
- Encoding and path safety
- Cross-platform compatibility
- Internationalization support
- Compliance with quality standards

## Packaging

To package a skill for distribution:

```bash
python .trae/skills/management/skill-creator/scripts/package_skill.py .trae/skills/management/my-skill ./dist
```

## Common Skill Patterns

### Workflow-Based Skills
Best for sequential processes (e.g., DOCX editing, PDF operations)
Structure: Overview → Workflow Decision Tree → Step 1 → Step 2...

### Task-Based Skills
Best for tool collections (e.g., PDF manipulation, Excel analysis)
Structure: Overview → Quick Start → Task Category 1 → Task Category 2...

### Reference-Based Skills
Best for standards or specifications (e.g., brand guidelines, coding standards)
Structure: Overview → Guidelines → Specifications → Usage...

### Capabilities-Based Skills
Best for integrated systems (e.g., product management, UI/UX design)
Structure: Overview → Core Capabilities → ### 1. Feature → ### 2. Feature...

## Integration with Management Workflow

This skill is part of the management skills workflow defined in [AGENTS.md](AGENTS.md):

1. **find-skills**: Discover available skills
2. **skill-installer**: Install from Git repositories
3. **skill-auditor**: Validate skill compliance
4. **skill-creator**: Create new skills (this skill)

**Management Boundaries:**
- **ALWAYS** audit skills after installation
- **NEVER** install skills without updating `skills.json`
- **USE** skill-creator for new skill scaffolding

## Quality Monitoring

This skill is monitored by the quality monitoring system (see [SKILL_QUALITY_MONITOR.md](../../SKILL_QUALITY_MONITOR.md)):

- **Target Success Rate**: > 85%
- **Target Usage Frequency**: Low (< 5/day)
- **Priority**: Medium

Usage statistics are tracked in `skill_usage_stats.json` to optimize routing and identify improvement opportunities.

## Related Skills

After using this skill, the intelligent routing system may recommend:
- **skill-auditor**: To validate the created skill
- **skill-installer**: To install the skill in other projects
- **find-skills**: To check if similar skills already exist

## Troubleshooting

### Issue: Skill not detected by routing system

**Solution:**
1. Verify skill is in correct category directory (workflow/, management/, or domain/)
2. Check that skill_map.json contains proper mapping
3. Ensure keywords and aliases are defined in frontmatter
4. Verify context field is properly configured

### Issue: Skill fails audit

**Solution:**
1. Review audit output for specific issues
2. Check encoding and path safety
3. Ensure all dependencies are listed in requirements.txt
4. Verify no hardcoded absolute paths
5. Remove any emojis from code output statements

### Issue: Skill not found by find-skills

**Solution:**
1. Ensure skill is registered in skills.json
2. Verify skill description is clear and concise
3. Check that keywords are relevant and comprehensive
4. Consider adding more aliases for better discoverability