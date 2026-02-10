# Skills Registry 管理文档

## 概述

本文档说明 Trae Skills 注册表 (`skills.json`) 的结构、管理方法和使用指南。

---

## 文件结构

### skills.json 位置
```
.trae/skills/skills.json
```

### skills.json 结构

```json
{
  "skills": {
    "<skill-name>": {
      "source": "<git-repo-url-or-local>",
      "subdir": "<subdirectory-path>",
      "version": "<commit-hash-or-unknown>",
      "updated_at": "<iso-timestamp>"
    }
  }
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|--------|------|
| `source` | string | 否 | Git 仓库 URL 或 "local"（本地 skill） |
| `subdir` | string | 否 | 子目录路径（如果 skill 在仓库的子目录中） |
| `version` | string | 否 | Git commit hash 或 "unknown" |
| `updated_at` | string | 否 | ISO 8601 格式的时间戳 |

---

## 已注册 Skills

### 远程 Skills

| Skill 名称 | Source | Subdir | Version |
|-----------|--------|--------|---------|
| find-skills | https://github.com/vercel-labs/skills.git | skills/find-skills | 556555c |
| skill-creator | https://github.com/anthropics/skills.git | skills/skill-creator | unknown |
| pdf-generation | https://github.com/glebis/claude-skills.git | pdf-generation | 89e7be8 |
| image-generation | https://github.com/glebis/claude-skills.git | image-generation | unknown |
| skill-auditor | https://github.com/glebis/claude-skills.git | skill-auditor | unknown |
| skill-installer | https://github.com/glebis/claude-skills.git | skill-installer | unknown |

### 本地 Skills

| Skill 名称 | Source | Subdir | Version |
|-----------|--------|--------|---------|
| demo-test-skill | local | | unknown |
| test-skill | local | | unknown |
| file-manager-skill | local | | unknown |
| dupeguru-tool | local | | unknown |

---

## 管理命令

### 1. 同步 Skills Registry

自动扫描 `.trae/skills/` 目录并更新 `skills.json`：

```bash
python .trae/skills/skill-installer/scripts/sync_skills.py sync
```

**功能**：
- 扫描所有已安装的 skills
- 保留远程 skills 的版本信息
- 更新 `updated_at` 时间戳
- 生成格式化的 skills 列表

### 2. 列出已安装 Skills

查看所有已注册的 skills：

```bash
python .trae/skills/skill-installer/scripts/sync_skills.py list
```

### 3. 干运行（Dry Run）

预览将要进行的更改，不实际写入文件：

```bash
python .trae/skills/skill-installer/scripts/sync_skills.py sync --dry-run
```

---

## Skill Map

`skill_map.json` 提供 skill 名称到关键词的映射，用于自动检测用户请求。

### 使用场景

当用户请求类似以下内容时，自动调用对应的 skill：
- "将 xxx.md 转换为 png" → image-generation
- "生成 pdf 文档" → pdf-generation
- "创建新 skill" → skill-creator
- "安装 skill" → skill-installer
- "审计 skill" → skill-auditor
- "查找 skill" → find-skills

### 关键词映射

| Skill | 关键词（中文） | 关键词（英文） |
|-------|------------------|------------------|
| image-generation | 图片、转换、截图、渲染、生成图片、生成png、生成jpg、markdown转图片、md转图片、文档转图片 | image, png, jpg, picture, photo, screenshot, markdown, render, convert |
| pdf-generation | 文档、报告、白皮书、pdf生成、生成pdf、markdown转pdf、md转pdf、文档转pdf | pdf, document, report, whitepaper, pandoc, latex |
| skill-creator | 创建、新建、初始化、模板、脚手架、创建skill、新建skill、初始化skill | create, new, init, template, skill, scaffold |
| skill-installer | 安装、更新、卸载、管理、git仓库、安装skill、更新skill、卸载skill | install, update, uninstall, manage, git, repository |
| skill-auditor | 审计、检查、验证、测试、合规、最佳实践、审计skill、检查skill、验证skill | audit, check, validate, test, compliance, best-practices |
| find-skills | 查找、搜索、发现、探索、浏览、查找skill、搜索skill、发现skill | find, search, discover, explore, browse |
| file-manager-skill | 文件、管理、重复、查找、搜索、文件管理、重复文件、查找文件 | file, manage, duplicate, finder, search |
| dupeguru-tool | 重复、文件、检测、重复文件、文件检测 | duplicate, dupeguru, file, detect |

---

## 最佳实践

### 1. 版本管理

- **定期更新版本信息**：每次 skill 更新后，更新 `version` 字段
- **使用 Git Commit Hash**：对于远程 skills，使用最新的 commit hash 作为版本号
- **本地 Skills**：使用 "local" 作为 source，version 设为 "unknown"

### 2. 注册表维护

- **自动同步**：使用 `sync_skills.py` 自动扫描和更新注册表
- **手动添加**：对于本地 skills，手动添加到 `skills.json`
- **版本跟踪**：记录每次更新的 `updated_at` 时间戳

### 3. Skill 发现

- **关键词映射**：使用 `skill_map.json` 自动检测用户意图
- **优先级顺序**：按照 `priority_order` 列表顺序匹配 skills
- **精确匹配**：优先使用 `exact_match` 中的关键词

### 4. 备份策略

- **定期备份**：每次更新 `skills.json` 前创建备份
- **保留历史**：保留最近 5 个版本的备份
- **备份位置**：`.trae/skills/backups/`

---

## 故障排查

### 问题：skills.json 格式错误

**症状**：`sync_skills.py` 报告 JSON 解析错误

**解决方案**：
1. 检查 JSON 格式是否正确
2. 确保所有字符串使用双引号
3. 验证逗号和括号匹配

### 问题：Skill 未被识别

**症状**：用户请求某个 skill，但系统未识别

**解决方案**：
1. 检查 `skill_map.json` 中是否包含该 skill 的关键词
2. 添加缺失的关键词到对应 skill 的 `keywords` 列表
3. 使用 skill 的完整名称直接调用

### 问题：版本信息不准确

**症状**：`skills.json` 中的 version 与实际不符

**解决方案**：
1. 运行 `git ls-remote` 获取最新 commit hash
2. 更新 `skills.json` 中的 `version` 字段
3. 更新 `updated_at` 时间戳

---

## 相关文件

| 文件 | 说明 |
|------|------|
| `.trae/skills/skills.json` | Skills 注册表 |
| `.trae/skills/skill_map.json` | Skill 关键词映射 |
| `.trae/skills/skill-installer/scripts/sync_skills.py` | 自动同步脚本 |
| `.trae/skills/skill-installer/scripts/manage_skills.py` | Skills 管理工具 |
| `.trae/skills/skill-installer/scripts/install_skill.py` | Skills 安装工具 |

---

## 更新日志

### 2026-02-10

- ✅ 完善 `skills.json`，添加所有已安装的 skills
- ✅ 创建 `sync_skills.py` 自动扫描脚本
- ✅ 创建 `skill_map.json` 关键词映射
- ✅ 创建 `SKILLS_REGISTRY.md` 管理文档
- ✅ 添加 image-generation 到 skills.json
- ✅ 添加 skill-auditor 到 skills.json
- ✅ 添加 skill-installer 到 skills.json
- ✅ 添加本地 skills（demo-test-skill, test-skill, file-manager-skill, dupeguru-tool）

---

## 参考资料

- [Trae Skills 文档](https://github.com/anthropics/skills)
- [Skills 管理最佳实践](https://github.com/anthropics/skills/blob/main/docs/best-practices.md)
