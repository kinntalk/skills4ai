---
name: proxy-manager
description: 代理配置管理工具，用于配置和管理代理设置，解决访问 GitHub 等远程仓库时的网络连接问题
keywords: [proxy, network, github, git, configuration]
aliases: [proxy-config, network-config]
dependencies: []
version: 1.0.0
author: Trae AI
license: MIT
---

# Proxy Manager

代理配置管理工具，用于配置和管理代理设置，解决访问 GitHub 等远程仓库时的网络连接问题。

## 功能特性

### 1. 自动代理配置
- 自动检测和应用代理配置
- 支持多种代理协议（HTTP、SOCKS5）
- 支持临时和永久代理配置

### 2. 代理配置管理
- 保存代理配置到 `.trae/proxy_config.json`
- 加载和应用已保存的代理配置
- 查看当前代理配置状态

### 3. Git 代理支持
- 自动配置 Git HTTP/HTTPS 代理
- 支持临时和永久 Git 代理配置
- 清除 Git 代理配置

### 4. 环境变量管理
- 自动设置 HTTP_PROXY、HTTPS_PROXY 环境变量
- 支持 NO_PROXY 白名单配置
- 为子进程提供代理环境

## 使用场景

### 场景 1：配置代理
当您需要访问 GitHub 但遇到网络连接问题时：

```bash
# 使用默认配置（HTTP 代理，端口 10808）
python .trae/skills/proxy-manager/scripts/setup_proxy.py http 127.0.0.1 10808

# 使用 SOCKS5 代理
python .trae/skills/proxy-manager/scripts/setup_proxy.py socks5 127.0.0.1 10808

# 带用户名和密码的代理
python .trae/skills/proxy-manager/scripts/setup_proxy.py http proxy.example.com 8080 username password
```

### 场景 2：应用代理到当前会话
在执行需要访问 GitHub 的操作前：

```bash
# 应用代理配置
python .trae/skills/proxy-manager/scripts/apply_proxy.py

# 然后执行需要代理的操作
python .trae/skills/skill-installer/scripts/install_skill.py wshobson/agents/plugins/python-development/skills/python-testing-patterns
```

### 场景 3：使用 Git 代理
执行 Git 操作时自动使用代理：

```bash
# 临时使用代理（不修改全局配置）
python .trae/skills/proxy-manager/scripts/git_with_proxy.py clone https://github.com/user/repo.git

# 永久配置代理
python .trae/skills/proxy-manager/scripts/git_with_proxy.py --permanent clone https://github.com/user/repo.git
```

### 场景 4：使用 Skill Installer
Skill Installer 会自动加载和应用代理配置：

```bash
# 直接使用，代理会自动应用
python .trae/skills/skill-installer/scripts/install_skill.py wshobson/agents/plugins/python-development/skills/python-testing-patterns --yes
```

## 代理配置文件

代理配置保存在 `.trae/proxy_config.json`：

```json
{
  "version": "1.0",
  "proxy": {
    "enabled": true,
    "type": "http",
    "host": "127.0.0.1",
    "port": 10808,
    "username": null,
    "password": null
  },
  "git": {
    "http_proxy": "http://127.0.0.1:10808",
    "https_proxy": "http://127.0.0.1:10808"
  },
  "environment": {
    "HTTP_PROXY": "http://127.0.0.1:10808",
    "HTTPS_PROXY": "http://127.0.0.1:10808",
    "NO_PROXY": "localhost,127.0.0.1"
  }
}
```

## 集成到其他 Skills

此代理配置系统会自动集成到以下 skills：

1. **skill-installer** - 自动加载代理配置并应用到 Git 操作
2. **using-git-worktrees** - 支持使用代理创建和管理 Git worktrees
3. **任何需要访问 GitHub 的 skill** - 通过环境变量自动应用代理

## 常见问题

### Q: 如何检查代理是否生效？
A: 运行 `python .trae/skills/proxy-manager/scripts/apply_proxy.py` 会显示代理配置状态。

### Q: 如何临时禁用代理？
A: 将 `.trae/proxy_config.json` 中的 `enabled` 设置为 `false`。

### Q: 支持哪些代理协议？
A: 支持 HTTP 和 SOCKS5 协议。

### Q: 如何配置 Git 全局代理？
A: 运行 `python .trae/skills/proxy-manager/scripts/git_with_proxy.py --permanent` 会配置 Git 全局代理。

## 最佳实践

1. **首次配置**：使用 `setup_proxy.py` 配置代理一次，后续操作自动使用
2. **验证配置**：使用 `apply_proxy.py` 验证代理配置是否正确
3. **临时使用**：使用 `git_with_proxy.py` 临时使用代理，不影响全局配置
4. **调试问题**：使用 `--verbose` 参数查看详细的代理应用日志

## 技术细节

### 代理检测优先级
1. 命令行参数（`--http-proxy`、`--https-proxy`）
2. 环境变量（`HTTP_PROXY`、`HTTPS_PROXY`）
3. 配置文件（`.trae/proxy_config.json`）

### Git 代理配置
- HTTP 代理：`git config --global http.proxy`
- HTTPS 代理：`git config --global https.proxy`
- 清除代理：`git config --global --unset http.proxy`

### 环境变量
- `HTTP_PROXY` / `http_proxy`：HTTP 请求代理
- `HTTPS_PROXY` / `https_proxy`：HTTPS 请求代理
- `NO_PROXY` / `no_proxy`：代理白名单

## 脚本说明

### setup_proxy.py
配置代理设置并保存到配置文件。

**用法：**
```bash
python .trae/skills/proxy-manager/scripts/setup_proxy.py <proxy_type> <host> <port> [username] [password]
```

**参数：**
- `proxy_type`: 代理类型（http、socks5）
- `host`: 代理服务器地址
- `port`: 代理服务器端口
- `username`: 代理用户名（可选）
- `password`: 代理密码（可选）

### apply_proxy.py
应用代理配置到当前会话。

**用法：**
```bash
python .trae/skills/proxy-manager/scripts/apply_proxy.py
```

**功能：**
- 读取 `.trae/proxy_config.json` 配置
- 设置环境变量
- 配置 Git 代理

### git_with_proxy.py
使用代理执行 Git 命令。

**用法：**
```bash
python .trae/skills/proxy-manager/scripts/git_with_proxy.py [--permanent] <git 命令>
```

**参数：**
- `--permanent`: 永久配置 Git 代理
- `git 命令`: 要执行的 Git 命令（如 clone、pull 等）

**示例：**
```bash
# 临时使用代理
python .trae/skills/proxy-manager/scripts/git_with_proxy.py clone https://github.com/user/repo.git

# 永久配置代理
python .trae/skills/proxy-manager/scripts/git_with_proxy.py --permanent clone https://github.com/user/repo.git
```
