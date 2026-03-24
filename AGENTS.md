# AGENTS.md - Skills Registry

**Version:** 1.0.0  
**Last Updated:** 2026-03-24  
**Total Skills:** 44

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
| Obsidian Skills | 4 | obsidian-bases, obsidian-cli, obsidian-markdown, url-to-obsidian |
| Other Skills | 26 | agent-browser, agentskills, baoyu-post-to-wechat, brainstorming, cli-anything-drawio, dispatching-parallel-agents, email-and-password-best-practices, executing-plans, find-skills, finishing-a-development-branch, good-mp-post, receiving-code-review, requesting-code-review, self-improving-agent, subagent-driven-development, test-driven-development, theme-factory, using-git-worktrees, using-superpowers, web-design-guidelines, x-app-manager, x-file-manager, x-login-pw, x-mail-sender, x-wechat-publisher, xhs-search |
| **Total** | **44** | |

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

**Description:** 代理配置管理工具，用于配置和管理代理设置，解决访问 GitHub 等远程仓库时的网络连接问题。当用户遇到网络连接问题、需要配置代理、访问 GitHub 失败、Git 操作超时、或需要设置 HTTP/SOCKS5 代理时，必须使用此技能。即使没有明确提到"代理"，只要涉及网络连接问题、远程仓库访问、或 Git 操作失败，都应该触发此技能。

**Path:** `proxy-manager/`

---

## Tool Skills

### skill-auditor

**Description:** Standard compliance checker for Agent skills. Verifies dependency completeness, file encoding, path consistency, cross-platform compatibility, i18n support, and packaging structure. Use when auditing skills before publishing or verifying compliance.

**Path:** `skill-auditor/`

---

### skill-creator

**Description:** Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy.

**Path:** `skill-creator/`

---

### skill-installer

**Description:** Install and manage skills from Git repositories into .trae/skills directory. Use this skill whenever the user wants to install, uninstall, update, or manage skills. Triggers on phrases like 'install skill', '安装 skill', '从 GitHub 安装', 'uninstall skill', '卸载 skill', 'update skills', 'list skills', '列出已安装的 skills'. Also handles encoding detection and conversion for skill files. Note: Registry synchronization is handled by skills-registry-sync skill.

**Path:** `skill-installer/`

---

### skills-registry-sync

**Description:** Sync skills registry after skill operations. Triggers on: 'install skill success', '安装 skill 成功', 'uninstall skill success', '卸载 skill 成功', 'delete skill success', '删除 skill 成功', 'create skill success', '创建 skill 成功', 'update skill success', '更新 skill 成功', 'skill installed', 'skill uninstalled', 'skill created', 'skill updated'. Updates skills.json, skill_map.json, and AGENTS.md to maintain registry consistency.

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

### baoyu-post-to-wechat

**Description:** Posts content to WeChat Official Account (微信公众号) via API or Chrome CDP. Supports article posting (文章) with HTML, markdown, or plain text input, and image-text posting (贴图, formerly 图文) with multiple images. Markdown article workflows default to converting ordinary external links into bottom citations for WeChat-friendly output. Use when user mentions "发布公众号", "post to wechat", "微信公众号", or "贴图/图文/文章".

**Path:** `baoyu-post-to-wechat/`

---

### brainstorming

**Description:** You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements and design before implementation.

**Path:** `brainstorming/`

---

### cli-anything-drawio

**Description:** No description available

**Path:** `cli-anything-drawio/`

---

### dispatching-parallel-agents

**Description:** Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies

**Path:** `dispatching-parallel-agents/`

---

### email-and-password-best-practices

**Description:** Configure email verification, implement password reset flows, set password policies, and customise hashing algorithms for Better Auth email/password authentication. Use when users need to set up login, sign-in, sign-up, credential authentication, or password security with Better Auth.

**Path:** `email-and-password-best-practices/`

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

### good-mp-post

**Description:** 微信公众号文章发布完整流程管理，包括AI辅助创作、图片生成、排版和发布。

**Path:** `good-mp-post/`

---

### receiving-code-review

**Description:** Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or technically questionable - requires technical rigor and verification, not performative agreement or blind implementation

**Path:** `receiving-code-review/`

---

### requesting-code-review

**Description:** Use when completing tasks, implementing major features, or before merging to verify work meets requirements

**Path:** `requesting-code-review/`

---

### self-improving-agent

**Description:** A universal self-improving agent that learns from ALL skill experiences. Uses multi-memory architecture (semantic + episodic + working) to continuously evolve the codebase. Auto-triggers on skill completion/error with hooks-based self-correction.

**Path:** `self-improving-agent/`

---

### subagent-driven-development

**Description:** Use when executing implementation plans with independent tasks in the current session

**Path:** `subagent-driven-development/`

---

### test-driven-development

**Description:** Use when implementing any feature or bugfix, before writing implementation code

**Path:** `test-driven-development/`

---

### theme-factory

**Description:** Toolkit for styling artifacts with a theme. These artifacts can be slides, docs, reportings, HTML landing pages, etc. There are 10 pre-set themes with colors/fonts that you can apply to any artifact that has been creating, or can generate a new theme on-the-fly.

**Path:** `theme-factory/`

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

### x-app-manager

**Description:** Windows application lifecycle management. Use when user requests to START or STOP desktop applications like WeChat, Feishu, DingTalk, Chrome, etc. Handles application launch and termination only. For login/authentication issues, use `x-login-pw` skill. / Windows 应用程序生命周期管理。当用户请求启动或关闭桌面应用（微信、飞书、钉钉、Chrome 等）时使用。仅处理应用启动和关闭。登录验证问题请使用 `x-login-pw` skill。

**Path:** `x-app-manager/`

---

### x-file-manager

**Description:** Local file perception and retrieval tool for AI Agents. Use when user wants to search files by name, type, size, hash, find duplicates, scan large files, or analyze local file system. Supports both Chinese and English queries like "查找大文件" or "find large files".

**Path:** `x-file-manager/`

---

### x-login-pw

**Description:** Desktop application login authentication handler. Use AFTER application is started (by `windows-app-manager`) and user needs login assistance. Handles QR code capture, SMS verification, and other authentication tasks. **Prerequisite: Target application MUST be running.** / 桌面应用登录验证处理器。在应用程序启动后（由 `windows-app-manager` 启动）且用户需要登录协助时使用。处理二维码捕获、短信验证等认证任务。**前置条件：目标应用必须已运行。**

**Path:** `x-login-pw/`

---

### x-mail-sender

**Description:** Local email sender via SMTP protocol supporting multiple providers (126, 163, QQ, Gmail, Outlook) with attachment capabilities. Use this skill whenever the user needs to send emails, send reports to email addresses, or mentions "send email", "发邮件", "email", "mail", "邮件". Trigger even when the user doesn't explicitly say "send email" but clearly intends to send content or files to an email address.

**Path:** `x-mail-sender/`

---

### x-wechat-publisher

**Description:** WeChat Official Account publishing workflow with AI-powered content creation, Markdown-to-WeChat HTML rendering, and hybrid-drive synchronization. Use this skill whenever the user mentions "发布公众号", "微信公众号", "同步微信", "公众号草稿", "WeChat Official Account", "post to WeChat", or wants to create, format, or sync articles to WeChat Official Account, even if they don't explicitly ask for a 'publisher' or 'WeChat'.

**Path:** `x-wechat-publisher/`

---

### xhs-search

**Description:** Search Xiaohongshu (小红书) notes and comments, save results to Obsidian vault. Use when user wants to search xiaohongshu.com, extract notes, get comments, or save xiaohongshu content to Obsidian. Supports both Chinese and English keywords like "搜索 英语学习" or "search Learning English".

**Path:** `xhs-search/`

---


## Statistics

### Category Distribution

| Category | Count | Percentage |
|----------|--------|------------|
| Core Skills | 5 | 11.4% |
| Tool Skills | 4 | 9.1% |
| Python Skills | 5 | 11.4% |
| Obsidian Skills | 4 | 9.1% |
| Other Skills | 26 | 59.1% |
| **Total** | **44** | **100%** |

---

*This registry is auto-generated by skills-registry-sync skill.*
