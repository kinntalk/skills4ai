# AGENTS.md - Skills Registry

**Version:** 1.0.0  
**Last Updated:** 2026-03-10  
**Total Skills:** 34

---

## Overview

This document provides a comprehensive registry of all available skills in the `.trae/skills` directory.

---

## Quick Reference

| Category | Count | Skills |
|-----------|--------|---------|
| Core Skills | 6 | image-generation, x-file-manager, pdf-generation, planning-with-files, powershell-windows, proxy-manager |
| Tool Skills | 4 | skill-auditor, skill-creator, skill-installer, skills-registry-sync |
| Python Skills | 5 | async-python-patterns, python-design-patterns, python-packaging, python-performance-optimization, python-testing-patterns |
| Obsidian Skills | 4 | obsidian-bases, obsidian-cli, obsidian-markdown, url-to-obsidian |
| Other Skills | 15 | agent-browser, agentskills, brainstorming, dispatching-parallel-agents, executing-plans, find-skills, finishing-a-development-branch, receiving-code-review, requesting-code-review, subagent-driven-development, test-driven-development, using-git-worktrees, using-superpowers, web-design-guidelines, xhs-search |
| **Total** | **34** | |

---

## Core Skills

### image-generation

**Description:** Converts Markdown documents to high-quality images (PNG/JPG) using Python and headless browser rendering. Ideal for creating social media posts, documentation screenshots, and sharing rich text content as images.

**Path:** `image-generation/`

---

### x-file-manager

**Description:** Local file perception and retrieval tool for AI Agents. Use when user wants to search files by name, type, size, hash, find duplicates, scan large files, or analyze local file system. Supports both Chinese and English queries like "查找大文件" or "find large files".

**Path:** `x-file-manager/`

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

**Description:** Install and manage skills from Git repositories into .trae/skills directory. Supports subdirectories, catalog browsing, dependency management, license verification, health checks, version rollback, encoding detection, and encoding conversion. Note: Registry synchronization (skills.json, skill_map.json, AGENTS.md) is handled by skills-registry-sync skill.

**Path:** `skill-installer/`

---

### skills-registry-sync

**Description:** Automatically check, update, and maintain consistency of skills registry files (skills.json, skill_map.json, AGENTS.md). Use when skills are installed/uninstalled, when registry files need synchronization, or for periodic maintenance to ensure all registration information is accurate and up-to-date.

**Path:** `skills-registry-sync/`

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

### obsidian-bases

**Description:** Create and edit Obsidian Bases (.base files) with views, filters, formulas, and summaries. Use when working with .base files, creating database-like views of notes, or when the user mentions Bases, table views, card views, filters, or formulas in Obsidian.

**Path:** `obsidian-bases/`

---

### obsidian-cli

**Description:** Interact with Obsidian vaults using the Obsidian CLI to read, create, search, and manage notes, tasks, properties, and more. Also supports plugin and theme development with commands to reload plugins, run JavaScript, capture errors, take screenshots, and inspect the DOM. Use when the user asks to interact with their Obsidian vault, manage notes, search vault content, perform vault operations from the command line, or develop and debug Obsidian plugins and themes.

**Path:** `obsidian-cli/`

---

### obsidian-markdown

**Description:** Create and edit Obsidian Flavored Markdown with wikilinks, embeds, callouts, properties, and other Obsidian-specific syntax. Use when working with .md files in Obsidian, or when the user mentions wikilinks, callouts, frontmatter, tags, embeds, or Obsidian notes.

**Path:** `obsidian-markdown/`

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

### brainstorming

**Description:** You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements and design before implementation.

**Path:** `brainstorming/`

---

### dispatching-parallel-agents

**Description:** Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies

**Path:** `dispatching-parallel-agents/`

---

### executing-plans

**Description:** Use when you have a written implementation plan to execute in a separate session with review checkpoints

**Path:** `executing-plans/`

---

### find-skills

**Description:** Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending capabilities. This skill should be used when the user is looking for functionality that might exist as an installable skill.

**Path:** `find-skills/`

---

### finishing-a-development-branch

**Description:** Use when implementation is complete, all tests pass, and you need to decide how to integrate the work - guides completion of development work by presenting structured options for merge, PR, or cleanup

**Path:** `finishing-a-development-branch/`

---

### receiving-code-review

**Description:** Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or technically questionable - requires technical rigor and verification, not performative agreement or blind implementation

**Path:** `receiving-code-review/`

---

### requesting-code-review

**Description:** Use when completing tasks, implementing major features, or before merging to verify work meets requirements

**Path:** `requesting-code-review/`

---

### subagent-driven-development

**Description:** Use when executing implementation plans with independent tasks in the current session

**Path:** `subagent-driven-development/`

---

### test-driven-development

**Description:** Use when implementing any feature or bugfix, before writing implementation code

**Path:** `test-driven-development/`

---

### using-git-worktrees

**Description:** Use when starting feature work that needs isolation from current workspace or before executing implementation plans - creates isolated git worktrees with smart directory selection and safety verification

**Path:** `using-git-worktrees/`

---

### using-superpowers

**Description:** Use when starting any conversation - establishes how to find and use skills, requiring Skill tool invocation before ANY response including clarifying questions

**Path:** `using-superpowers/`

---

### web-design-guidelines

**Description:** Review UI code for Web Interface Guidelines compliance. Use when asked to "review my UI", "check accessibility", "audit design", "review UX", or "check my site against best practices".

**Path:** `web-design-guidelines/`

---

### xhs-search

**Description:** Search Xiaohongshu (小红书) notes and comments, save results to Obsidian vault. Use when user wants to search xiaohongshu.com, extract notes, get comments, or save xiaohongshu content to Obsidian. Supports both Chinese and English keywords like "搜索 英语学习" or "search Learning English".

**Path:** `xhs-search/`

---


## Statistics

### Category Distribution

| Category | Count | Percentage |
|----------|--------|------------|
| Core Skills | 6 | 17.6% |
| Tool Skills | 4 | 11.8% |
| Python Skills | 5 | 14.7% |
| Obsidian Skills | 4 | 11.8% |
| Other Skills | 15 | 44.1% |
| **Total** | **34** | **100%** |

---

*This registry is auto-generated by skills-registry-sync skill.*
