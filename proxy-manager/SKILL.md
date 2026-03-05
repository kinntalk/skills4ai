---
name: proxy-manager
description: 代理配置管理工具，用于配置和管理代理设置，解决访问 GitHub 等远程仓库时的网络连接问题
keywords: [proxy, network, github, git, configuration, smart-proxy]
aliases: [proxy-config, network-config]
dependencies: []
version: 2.0.0
author: Trae AI
license: MIT
---

# Proxy Manager

代理配置管理工具，用于配置和管理代理设置，解决访问 GitHub 等远程仓库时的网络连接问题。

## 功能特性

### 1. 智能代理检测（v2.0 新增）
- **自动判断是否需要代理**：通过直连测试自动检测目标地址可达性
- **本地地址自动排除**：自动识别本地网络地址（localhost、192.168.x.x、10.x.x.x 等）
- **NO_PROXY 自动生成**：根据本机网络配置自动生成代理白名单

### 2. 自动代理配置
- 自动检测和应用代理配置
- 支持多种代理协议（HTTP、SOCKS5）
- 支持临时和永久代理配置

### 3. 代理配置管理
- 保存代理配置到 `.trae/proxy_config.json`
- 加载和应用已保存的代理配置
- 查看当前代理配置状态

### 4. Git 智能代理支持
- **自动代理切换**：根据目标地址自动选择是否使用代理
- 支持临时和永久 Git 代理配置
- 清除 Git 代理配置

### 5. 环境变量管理
- 自动设置 HTTP_PROXY、HTTPS_PROXY 环境变量
- **智能 NO_PROXY 白名单**：自动包含本地网络地址
- 为子进程提供代理环境

## 使用场景

### 场景 1：配置代理（智能模式）
当您需要访问 GitHub 但遇到网络连接问题时：

```bash
# 使用智能模式配置代理（自动生成 NO_PROXY）
python .trae/skills/proxy-manager/scripts/setup_proxy.py http 127.0.0.1 10808

# 使用 SOCKS5 代理
python .trae/skills/proxy-manager/scripts/setup_proxy.py socks5 127.0.0.1 10808

# 带用户名和密码的代理
python .trae/skills/proxy-manager/scripts/setup_proxy.py http proxy.example.com 8080 username password

# 禁用自动 NO_PROXY 生成
python .trae/skills/proxy-manager/scripts/setup_proxy.py http 127.0.0.1 10808 --no-auto-no-proxy
```

### 场景 2：应用代理到当前会话（智能模式）
在执行需要访问 GitHub 的操作前：

```bash
# 应用代理配置（智能模式，自动扩展 NO_PROXY）
python .trae/skills/proxy-manager/scripts/apply_proxy.py

# 应用代理配置并测试连接
python .trae/skills/proxy-manager/scripts/apply_proxy.py --test

# 简单模式（不使用智能检测）
python .trae/skills/proxy-manager/scripts/apply_proxy.py --simple

# 不配置 Git 代理
python .trae/skills/proxy-manager/scripts/apply_proxy.py --no-git
```

### 场景 3：智能 Git 代理（自动切换）
执行 Git 操作时自动判断是否需要代理：

```bash
# 智能模式：自动判断是否需要代理
python .trae/skills/proxy-manager/scripts/git_with_proxy.py clone https://github.com/user/repo.git

# 强制使用代理
python .trae/skills/proxy-manager/scripts/git_with_proxy.py --force-proxy clone https://github.com/user/repo.git

# 强制直连
python .trae/skills/proxy-manager/scripts/git_with_proxy.py --force-direct clone https://github.com/user/repo.git

# 永久配置代理
python .trae/skills/proxy-manager/scripts/git_with_proxy.py --permanent clone https://github.com/user/repo.git
```

### 场景 4：测试代理工具模块
验证智能代理功能是否正常：

```bash
# 测试代理工具模块
python .trae/skills/proxy-manager/scripts/proxy_utils.py
```

## 代理配置文件

代理配置保存在 `.trae/proxy_config.json`（v2.0 格式）：

```json
{
  "version": "2.0",
  "proxy": {
    "enabled": true,
    "type": "http",
    "host": "127.0.0.1",
    "port": 10808,
    "username": null,
    "password": null,
    "auto_detect": true,
    "no_proxy": "localhost,127.0.0.1,::1,localaddress,*.local,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,..."
  },
  "git": {
    "http_proxy": "http://127.0.0.1:10808",
    "https_proxy": "http://127.0.0.1:10808"
  },
  "environment": {
    "HTTP_PROXY": "http://127.0.0.1:10808",
    "HTTPS_PROXY": "http://127.0.0.1:10808",
    "NO_PROXY": "localhost,127.0.0.1,..."
  }
}
```

## 智能代理行为

### 直连地址（不走代理）
以下地址自动直连，无需代理：
- `localhost`、`127.0.0.1`、`::1`
- 本地网络地址：`192.168.x.x`、`10.x.x.x`、`172.16-31.x.x`
- 本地主机名
- 可直连的公网地址（通过连通性测试）

### 代理地址（走代理）
以下地址自动使用代理：
- 无法直连的公网地址（如 GitHub、Google 等）
- 连接超时的地址

### 本地服务（不受影响）
以下服务不受代理影响：
- Open Code IDE、Trae IDE 等本地服务
- 本地开发服务器（如 localhost:3000、localhost:8080）
- 本地数据库服务

## 集成到其他 Skills

此代理配置系统会自动集成到以下 skills：

1. **skill-installer** - 自动加载代理配置并应用到 Git 操作
2. **using-git-worktrees** - 支持使用代理创建和管理 Git worktrees
3. **任何需要访问 GitHub 的 skill** - 通过环境变量自动应用代理

## 常见问题

### Q: 如何检查代理是否生效？
A: 运行 `python .trae/skills/proxy-manager/scripts/apply_proxy.py --test` 会显示代理配置状态和连接测试结果。

### Q: 如何临时禁用代理？
A: 将 `.trae/proxy_config.json` 中的 `enabled` 设置为 `false`。

### Q: 支持哪些代理协议？
A: 支持 HTTP 和 SOCKS5 协议。

### Q: 如何配置 Git 全局代理？
A: 运行 `python .trae/skills/proxy-manager/scripts/git_with_proxy.py --permanent` 会配置 Git 全局代理。

### Q: 如何强制使用/不使用代理？
A: 使用 `--force-proxy` 或 `--force-direct` 选项。

### Q: 智能代理如何判断是否需要代理？
A: 系统会按以下顺序判断：
1. 检查目标地址是否为本地地址
2. 检查目标地址是否在 NO_PROXY 列表中
3. 尝试直连测试（2秒超时）
4. 直连失败则使用代理

## 最佳实践

1. **首次配置**：使用 `setup_proxy.py` 配置代理一次，后续操作自动使用
2. **验证配置**：使用 `apply_proxy.py --test` 验证代理配置是否正确
3. **智能使用**：使用 `git_with_proxy.py` 自动判断是否需要代理
4. **调试问题**：使用 `--force-proxy` 或 `--force-direct` 排查问题

## 技术细节

### 代理检测优先级
1. 命令行参数（`--force-proxy`、`--force-direct`）
2. 本地地址检测（自动直连）
3. NO_PROXY 列表匹配
4. 直连测试结果
5. 配置文件（`.trae/proxy_config.json`）

### Git 代理配置
- HTTP 代理：`git config --global http.proxy`
- HTTPS 代理：`git config --global https.proxy`
- 清除代理：`git config --global --unset http.proxy`

### 环境变量
- `HTTP_PROXY` / `http_proxy`：HTTP 请求代理
- `HTTPS_PROXY` / `https_proxy`：HTTPS 请求代理
- `NO_PROXY` / `no_proxy`：代理白名单（自动生成）

## 脚本说明

### proxy_utils.py（v2.0 新增）
智能代理工具模块，提供核心功能：
- `is_local_address(host)` - 检查是否为本地地址
- `can_direct_connect(url)` - 测试直连可达性
- `should_use_proxy(url, config)` - 智能判断是否需要代理
- `get_auto_no_proxy()` - 自动生成 NO_PROXY 列表
- `get_proxy_for_url(url, config)` - 获取目标 URL 的代理配置

### setup_proxy.py
配置代理设置并保存到配置文件。

**用法：**
```bash
python .trae/skills/proxy-manager/scripts/setup_proxy.py <proxy_type> <host> <port> [username] [password] [--no-auto-no-proxy]
```

**参数：**
- `proxy_type`: 代理类型（http、socks5）
- `host`: 代理服务器地址
- `port`: 代理服务器端口
- `username`: 代理用户名（可选）
- `password`: 代理密码（可选）
- `--no-auto-no-proxy`: 禁用自动 NO_PROXY 生成

### apply_proxy.py
应用代理配置到当前会话。

**用法：**
```bash
python .trae/skills/proxy-manager/scripts/apply_proxy.py [--simple] [--no-git] [--test]
```

**参数：**
- `--simple`: 简单模式，不使用智能检测
- `--no-git`: 不配置 Git 代理
- `--test`: 测试代理连接

### git_with_proxy.py
使用代理执行 Git 命令（智能模式）。

**用法：**
```bash
python .trae/skills/proxy-manager/scripts/git_with_proxy.py [选项] <git 命令>
```

**参数：**
- `--permanent`: 永久配置 Git 代理
- `--force-proxy`: 强制使用代理
- `--force-direct`: 强制直连
- `git 命令`: 要执行的 Git 命令（如 clone、pull 等）

**示例：**
```bash
# 智能模式（自动判断）
python .trae/skills/proxy-manager/scripts/git_with_proxy.py clone https://github.com/user/repo.git

# 强制代理
python .trae/skills/proxy-manager/scripts/git_with_proxy.py --force-proxy clone https://github.com/user/repo.git

# 强制直连
python .trae/skills/proxy-manager/scripts/git_with_proxy.py --force-direct clone https://github.com/user/repo.git
```
