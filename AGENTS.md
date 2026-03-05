# AGENTS.md - Skills Registry

**Version:** 1.0.0  
**Last Updated:** 2026-03-05  
**Total Skills:** 36

---

## Overview

This document provides a comprehensive registry of all available skills in the `.trae/skills` directory.

---

## Quick Reference

| Category | Count | Skills |
|-----------|--------|---------|
| Core Skills | 5 | image-generation, pdf-generation, planning-with-files, powershell-windows, proxy-manager |
| Tool Skills | 4 | skill-auditor, skill-creator, skill-installer, skills-registry-sync |
| Superpowers | 13 | sp-dispatching-parallel-agents, sp-executing-plans, sp-finishing-a-development-branch, sp-receiving-code-review, sp-requesting-code-review, sp-subagent-driven-development, sp-systematic-debugging, sp-test-driven-development, sp-using-git-worktrees, sp-using-superpowers, sp-verification-before-completion, sp-writing-plans, sp-writing-skills |
| Python Skills | 5 | async-python-patterns, python-design-patterns, python-packaging, python-performance-optimization, python-testing-patterns |
| Obsidian Skills | 2 | obsidian-skills, url-to-obsidian |
| Other Skills | 7 | agent-browser, agentskills, bak-skill-creator, brainstorming, browser-use, find-skills, web-design-guidelines |
| **Total** | **36** | |

---

## Core Skills

### image-generation

**Description:** Converts Markdown documents to high-quality images (PNG/JPG) using Python and headless browser rendering. Ideal for creating social media posts, documentation screenshots, and sharing rich text content as images.

**Path:** `image-generation/`

---

### pdf-generation

**Description:** Professional PDF generation from markdown using Pandoc with Eisvogel template and EB Garamond fonts. Use when converting markdown to PDF, creating white papers, research documents, marketing materials, or technical documentation. Supports English, Russian, and Chinese documents with professional typography and color-coded themes. Mobile-optimized layout (6x9) by default for Telegram bot context, desktop/print layout (A4) for other contexts.

**Path:** `pdf-generation/`

---

### planning-with-files

**Description:** Implements Manus-style file-based planning to organize and track progress on complex tasks. Creates task_plan.md, findings.md, and progress.md. Use when asked to plan out, break down, or organize a multi-step project, research task, or any work requiring >5 tool calls. Supports automatic session recovery after /clear.

**Path:** `planning-with-files/`

---

### powershell-windows

**Description:** PowerShell Windows patterns. Critical pitfalls, operator syntax, error handling.

**Path:** `powershell-windows/`

---

### proxy-manager

**Description:** 代理配置管理工具，用于配置和管理代理设置，解决访问 GitHub 等远程仓库时的网络连接问题

**Path:** `proxy-manager/`

---

## Tool Skills

### skill-auditor

**Description:** Standard compliance checker for Trae skills. Verifies dependency completeness, file encoding, path consistency, cross-platform compatibility, i18n support, and packaging structure. Use when auditing skills before publishing or verifying compliance.

**Path:** `skill-auditor/`

---

### skill-creator

**Description:** Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, update or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy.

**Path:** `skill-creator/`

---

### skill-installer

**Description:** No description available

**Path:** `skill-installer/`

---

### skills-registry-sync

**Description:** Automatically check, update, and maintain consistency of skills registry files (skills.json, skill_map.json, AGENTS.md). Use when skills are installed/uninstalled, when registry files need synchronization, or for periodic maintenance to ensure all registration information is accurate and up-to-date.

**Path:** `skills-registry-sync/`

---

## Superpowers

### sp-dispatching-parallel-agents

**Description:** Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies

**Path:** `sp-dispatching-parallel-agents/`

---

### sp-executing-plans

**Description:** Use when you have a written implementation plan to execute in a separate session with review checkpoints

**Path:** `sp-executing-plans/`

---

### sp-finishing-a-development-branch

**Description:** Use when implementation is complete, all tests pass, and you need to decide how to integrate the work - guides completion of development work by presenting structured options for merge, PR, or cleanup

**Path:** `sp-finishing-a-development-branch/`

---

### sp-receiving-code-review

**Description:** Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or technically questionable - requires technical rigor and verification, not performative agreement or blind implementation

**Path:** `sp-receiving-code-review/`

---

### sp-requesting-code-review

**Description:** Use when completing tasks, implementing major features, or before merging to verify work meets requirements

**Path:** `sp-requesting-code-review/`

---

### sp-subagent-driven-development

**Description:** Use when executing implementation plans with independent tasks in the current session

**Path:** `sp-subagent-driven-development/`

---

### sp-systematic-debugging

**Description:** Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes

**Path:** `sp-systematic-debugging/`

---

### sp-test-driven-development

**Description:** Use when implementing any feature or bugfix, before writing implementation code

**Path:** `sp-test-driven-development/`

---

### sp-using-git-worktrees

**Description:** Use when starting feature work that needs isolation from current workspace or before executing implementation plans - creates isolated git worktrees with smart directory selection and safety verification

**Path:** `sp-using-git-worktrees/`

---

### sp-using-superpowers

**Description:** Use when starting any conversation - establishes how to find and use skills, requiring Skill tool invocation before ANY response including clarifying questions

**Path:** `sp-using-superpowers/`

---

### sp-verification-before-completion

**Description:** Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always

**Path:** `sp-verification-before-completion/`

---

### sp-writing-plans

**Description:** Use when you have a spec or requirements for a multi-step task, before touching code

**Path:** `sp-writing-plans/`

---

### sp-writing-skills

**Description:** Use when creating new skills, editing existing skills, or verifying skills work before deployment

**Path:** `sp-writing-skills/`

---

## Python Skills

### async-python-patterns

**Description:** Master Python asyncio, concurrent programming, and async/await patterns for high-performance applications. Use when building async APIs, concurrent systems, or I/O-bound applications requiring non-blocking operations.

**Path:** `async-python-patterns/`

---

### python-design-patterns

**Description:** Python design patterns including KISS, Separation of Concerns, Single Responsibility, and composition over inheritance. Use when making architecture decisions, refactoring code structure, or evaluating when abstractions are appropriate.

**Path:** `python-design-patterns/`

---

### python-packaging

**Description:** Create distributable Python packages with proper project structure, setup.py/pyproject.toml, and publishing to PyPI. Use when packaging Python libraries, creating CLI tools, or distributing Python code.

**Path:** `python-packaging/`

---

### python-performance-optimization

**Description:** Profile and optimize Python code using cProfile, memory profilers, and performance best practices. Use when debugging slow Python code, optimizing bottlenecks, or improving application performance.

**Path:** `python-performance-optimization/`

---

### python-testing-patterns

**Description:** Implement comprehensive testing strategies with pytest, fixtures, mocking, and test-driven development. Use when writing Python tests, setting up test suites, or implementing testing best practices.

**Path:** `python-testing-patterns/`

---

## Obsidian Skills

### obsidian-skills

**Description:** Skill collection containing multiple sub-skills

**Path:** `obsidian-skills/`

---

### url-to-obsidian

**Description:** Convert web pages to Obsidian Flavored Markdown and save to your Obsidian vault. Supports login-required pages, automatic vault detection, and asset downloading.

**Path:** `url-to-obsidian/`

---

## Other Skills

### agent-browser

**Description:** Browser automation CLI for AI agents. Use when the user needs to interact with websites, including navigating pages, filling forms, clicking buttons, taking screenshots, extracting data, testing web apps, or automating any browser task. Triggers include requests to "open a website", "fill out a form", "click a button", "take a screenshot", "scrape data from a page", "test this web app", "login to a site", "automate browser actions", or any task requiring programmatic web interaction.

**Path:** `agent-browser/`

---

### agentskills

**Description:** No description available

**Path:** `agentskills/`

---

### bak-skill-creator

**Description:** Guide for creating effective skills that extend Claude's capabilities with specialized knowledge, workflows, or tool integrations. Use when creating new skills, updating existing skills, or asking about skill development best practices.

**Path:** `bak-skill-creator/`

---

### brainstorming

**Description:** You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements and design before implementation.

**Path:** `brainstorming/`

---

### browser-use

**Description:** Skill collection containing multiple sub-skills

**Path:** `browser-use/`

---

### find-skills

**Description:** Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending capabilities. This skill should be used when the user is looking for functionality that might exist as an installable skill.

**Path:** `find-skills/`

---

### web-design-guidelines

**Description:** Review UI code for Web Interface Guidelines compliance. Use when asked to "review my UI", "check accessibility", "audit design", "review UX", or "check my site against best practices".

**Path:** `web-design-guidelines/`

---


## Statistics

### Category Distribution

| Category | Count | Percentage |
|----------|--------|------------|
| Core Skills | 5 | 13.9% |
| Tool Skills | 4 | 11.1% |
| Superpowers | 13 | 36.1% |
| Python Skills | 5 | 13.9% |
| Obsidian Skills | 2 | 5.6% |
| Other Skills | 7 | 19.4% |
| **Total** | **36** | **100%** |

---

*This registry is auto-generated by skills-registry-sync skill.*
