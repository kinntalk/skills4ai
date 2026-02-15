---
name: find-skills
description: Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending capabilities. This skill should be used when the user is looking for functionality that might exist as an installable skill. Part of the management skills ecosystem with context-aware routing support.
keywords:
  - find
  - discover
  - search
  - install
  - skills
  - agent
  - capability
  - 查找
  - 发现
  - 搜索
  - 安装
  - 技能
  - 代理
  - 能力
aliases:
  - find-skills
  - skill-discovery
  - skill-search
  - skill-finder
---

# Find Skills

This skill helps you discover and install skills from the open agent skills ecosystem.

## When to Use This Skill

Use this skill when the user:

- Asks "how do I do X" where X might be a common task with an existing skill
- Says "find a skill for X" or "is there a skill for X"
- Asks "can you do X" where X is a specialized capability
- Expresses interest in extending agent capabilities
- Wants to search for tools, templates, or workflows
- Mentions they wish they had help with a specific domain (design, testing, deployment, etc.)

## Skill Context and Routing

This skill is part of the **management** skills category and is automatically routed by the intelligent routing system based on:

- **Trigger Phase**: `management`
- **Required For**: `skill-discovery`, `capability-search`
- **Priority**: 5

The routing system uses the `skill_map.json` context field to automatically detect when this skill should be invoked based on keywords like "find", "discover", "search", "install", "skills", "agent", "capability".

## What is Skills CLI?

The Skills CLI (`npx skills`) is a package manager for the open agent skills ecosystem. Skills are modular packages that extend agent capabilities with specialized knowledge, workflows, and tools.

**Key commands:**
- `npx skills find [query]` - Search for skills interactively or by keyword
- `npx skills add <package>` - Install a skill from GitHub or other sources
- `npx skills check` - Check for skill updates
- `npx skills update` - Update all installed skills

**Browse skills at:** https://skills.sh/

## Skills Directory Structure

Skills are organized in `.trae/skills/` directory with the following structure:
```
.trae/skills/
├── workflow/           # Workflow-based skills (brainstorming, planning, etc.)
├── management/         # Management skills (find-skills, skill-creator, etc.)
├── domain/            # Domain-specific skills (ui-ux, claude-skills, etc.)
└── [other skills]     # Other standalone skills
```

Each skill category has its own AGENTS.md file that defines:
- **Persona**: Role and purpose of skills in that category
- **Workflow**: How skills interact with each other
- **Boundaries**: Rules and constraints for skill usage

## Integration with Skills CLI

The find-skills skill integrates with the Skills CLI (`npx skills`) to provide better discovery and installation experience.

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

**For local skills**, always use the local management skills (find-skills, skill-installer) to ensure:
- Automatic quality checks
- Consistent routing priority
- Better integration with the project

**⚠️ Important**: Using `npx skills find` or `npx skills add` directly may bypass quality checks and routing priorities. Always prefer local management skills when available.

## Skills Directory Structure

Skills are organized in the `.trae/skills/` directory with the following structure:

```
.trae/skills/
├── workflow/           # Workflow-based skills (brainstorming, planning, etc.)
├── management/         # Management skills (find-skills, skill-creator, etc.)
├── domain/            # Domain-specific skills (ui-ux, claude-skills, etc.)
└── [other skills]     # Other standalone skills
```

Each skill category has its own AGENTS.md file that defines:
- **Persona**: Role and purpose of skills in that category
- **Workflow**: How skills interact with each other
- **Boundaries**: Rules and constraints for skill usage

## How to Help Users Find Skills

### Step 1: Understand What They Need

When a user asks for help with something, identify:

1. The domain (e.g., React, testing, design, deployment)
2. The specific task (e.g., writing tests, creating animations, reviewing PRs)
3. Whether this is a common enough task that a skill likely exists

### Step 2: Search for Skills

Run the find command with a relevant query:

```bash
npx skills find [query]
```

For example:

- User asks "how do I make my React app faster?" → `npx skills find react performance`
- User asks "can you help me with PR reviews?" → `npx skills find pr review`
- User asks "I need to create a changelog" → `npx skills find changelog`

The command will return results like:

```
Install with npx skills add <owner/repo@skill>

vercel-labs/agent-skills@vercel-react-best-practices
└ https://skills.sh/vercel-labs/agent-skills/vercel-react-best-practices
```

### Step 3: Present Options to the User

When you find relevant skills, present them to the user with:

1. The skill name and what it does
2. The install command they can run
3. A link to learn more at skills.sh

Example response:

```
I found a skill that might help! The "vercel-react-best-practices" skill provides
React and Next.js performance optimization guidelines from Vercel Engineering.

To install it:
npx skills add vercel-labs/agent-skills@vercel-react-best-practices

Learn more: https://skills.sh/vercel-labs/agent-skills/vercel-react-best-practices
```

### Step 4: Offer to Install

**Option A: Install with Skills CLI (Global)**
```bash
npx skills add <owner/repo@skill> -g -y
```
The `-g` flag installs globally (user-level) and `-y` skips confirmation prompts.

**Option B: Install with skill-installer (Local to Project)**
```bash
python .trae/skills/management/skill-installer/scripts/install_skill.py <owner/repo>
```

For monorepo skills (e.g., anthropics/skills), specify the subdirectory:
```bash
python .trae/skills/management/skill-installer/scripts/install_skill.py anthropics/skills/template
```

**Choosing Between Options:**
- Use **Skills CLI** (`npx skills`) for global installation across all projects
- Use **skill-installer** for project-specific installation to `.trae/skills/` directory
- Use **skill-installer** when installing from monorepo subdirectories (e.g., `anthropics/skills/template`)

### Step 5: Verify Installation

After installation, always run `skill-auditor` to verify the skill meets quality standards:

```bash
python .trae/skills/management/skill-auditor/scripts/audit_skill.py .trae/skills/<skill-name>
```

This ensures the skill:
- Has proper structure and frontmatter
- Follows best practices
- Is compatible with the intelligent routing system
- Meets quality standards defined in SKILL_QUALITY_MONITOR.md

## Common Skill Categories

When searching, consider these common categories:

| Category        | Example Queries                          |
| --------------- | ---------------------------------------- |
| Web Development | react, nextjs, typescript, css, tailwind |
| Testing         | testing, jest, playwright, e2e           |
| DevOps          | deploy, docker, kubernetes, ci-cd        |
| Documentation   | docs, readme, changelog, api-docs        |
| Code Quality    | review, lint, refactor, best-practices   |
| Design          | ui, ux, design-system, accessibility     |
| Productivity    | workflow, automation, git                |

## Tips for Effective Searches

1. **Use specific keywords**: "react testing" is better than just "testing"
2. **Try alternative terms**: If "deploy" doesn't work, try "deployment" or "ci-cd"
3. **Check popular sources**: Many skills come from `vercel-labs/agent-skills` or `ComposioHQ/awesome-claude-skills`
4. **Consider skill categories**: Skills are organized into workflow/, management/, and domain/ directories
5. **Check skill_map.json**: Review the context field to understand skill routing and dependencies

## When No Skills Are Found

If no relevant skills exist:

1. Acknowledge that no existing skill was found
2. Offer to help with the task directly using your general capabilities
3. Suggest the user could create their own skill with `skill-creator`

Example:

```
I searched for skills related to "xyz" but didn't find any matches.
I can still help you with this task directly! Would you like me to proceed?

If this is something you do often, you could create your own skill using skill-creator:
python .trae/skills/management/skill-creator/scripts/init_skill.py my-xyz-skill
```

## Integration with Intelligent Routing System

The intelligent routing system (see [SKILL_ROUTING.md](../../SKILL_ROUTING.md)) automatically detects when users need skill discovery and routes to this skill based on:

- **Keyword matching**: "find", "discover", "search", "install", "skills", "agent", "capability"
- **Context awareness**: Management phase triggers
- **Priority**: 5 (medium priority)

After using this skill, the routing system may recommend:
- **skill-installer**: If the user wants to install a found skill
- **skill-creator**: If the user wants to create a new skill
- **skill-auditor**: To verify installed skills meet quality standards

## Quality Monitoring

This skill is monitored by the quality monitoring system (see [SKILL_QUALITY_MONITOR.md](../../SKILL_QUALITY_MONITOR.md)):

- **Target Success Rate**: > 90%
- **Target Usage Frequency**: Low (< 5/day)
- **Priority**: Medium

Usage statistics are tracked in `skill_usage_stats.json` to optimize routing and identify improvement opportunities.
