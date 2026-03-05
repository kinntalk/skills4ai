# AGENTS.md - Skills Registry

**Version:** 1.0.0  
**Last Updated:** 2026-03-05  
**Total Skills:** 20

---

## Overview

This document provides a comprehensive registry of all available skills in the `.trae/skills` directory.

---

## Quick Reference

| Category | Count | Skills |
|-----------|--------|---------|
| Core Skills | 5 | image-generation, pdf-generation, planning-with-files, powershell-windows, proxy-manager |
| Tool Skills | 4 | skill-auditor, skill-creator, skill-installer, skills-registry-sync |
| Python Skills | 5 | async-python-patterns, python-design-patterns, python-packaging, python-performance-optimization, python-testing-patterns |
| Obsidian Skills | 1 | url-to-obsidian |
| Other Skills | 5 | agent-browser, agentskills, brainstorming, find-skills, web-design-guidelines |
| **Total** | **20** | |

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
| Core Skills | 5 | 25.0% |
| Tool Skills | 4 | 20.0% |
| Python Skills | 5 | 25.0% |
| Obsidian Skills | 1 | 5.0% |
| Other Skills | 5 | 25.0% |
| **Total** | **20** | **100%** |

---

*This registry is auto-generated by skills-registry-sync skill.*
