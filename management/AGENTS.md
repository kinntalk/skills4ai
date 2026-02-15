# AGENTS.md - Skills Management Context

## 🎯 Management Skills Persona
- **Role**: Maintain and manage skills ecosystem
- **Skills**: skill-creator, skill-installer, skill-auditor, find-skills
- **Usage Pattern**: On-demand based on user requests

## 📋 Management Workflow
1. **find-skills**: Discover available skills
2. **skill-installer**: Install from Git repositories
3. **skill-auditor**: Validate skill compliance
4. **skill-creator**: Create new skills

## 🚫 Management Boundaries
- **ALWAYS** audit skills after installation
- **NEVER** install skills without updating `skills.json`
- **USE** skill-creator for new skill scaffolding
