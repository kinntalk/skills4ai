---
name: proxy-manager
description: 代理配置管理工具，用于配置和管理代理设置，解决访问 GitHub 等远程仓库时的网络连接问题。当用户遇到网络连接问题、需要配置代理、访问 GitHub 失败、Git 操作超时、或需要设置 HTTP/SOCKS5 代理时，必须使用此技能。即使没有明确提到"代理"，只要涉及网络连接问题、远程仓库访问、或 Git 操作失败，都应该触发此技能。
---

# Proxy Manager

代理配置管理工具，用于配置和管理代理设置，解决访问 GitHub 等远程仓库时的网络连接问题。

## 核心功能

### 智能代理检测
- 自动判断是否需要代理，通过直连测试检测目标地址可达性
- 本地地址自动排除（localhost、192.168.x.x、10.x.x.x 等）
- 自动生成 NO_PROXY 白名单

### 强制代理域名
- 可配置特定域名强制使用代理，不受直连测试影响
- 支持通配符模式（如 `*.github.com`）
- 优先级最高，适用于需要确保连接稳定性的服务
- 默认包含：
  - GitHub 相关域名：`*.github.com`

### 自动代理配置
- 自动检测和应用代理配置
- 支持多种代理协议（HTTP、SOCKS5）
- 支持临时和永久代理配置

### Git 智能代理支持
- 根据目标地址自动选择是否使用代理
- 自动识别强制代理域名并应用代理
- 支持临时和永久 Git 代理配置

## 使用方法

### 配置代理
```bash
# 配置 HTTP 代理
python .trae/skills/proxy-manager/scripts/setup_proxy.py http 127.0.0.1 10808

# 配置 SOCKS5 代理
python .trae/skills/proxy-manager/scripts/setup_proxy.py socks5 127.0.0.1 10808
```

### 应用代理到当前会话
```bash
# 应用代理配置
python .trae/skills/proxy-manager/scripts/apply_proxy.py

# 应用代理配置并测试连接
python .trae/skills/proxy-manager/scripts/apply_proxy.py --test
```

### 使用 Git 代理
```bash
# 智能模式：自动判断是否需要代理
python .trae/skills/proxy-manager/scripts/git_with_proxy.py clone https://github.com/user/repo.git

# 强制使用代理
python .trae/skills/proxy-manager/scripts/git_with_proxy.py --force-proxy clone https://github.com/user/repo.git
```

### 使用 Git 代理

系统按以下顺序判断是否使用代理：

1. **强制代理域名**（优先级最高）
   - 检查目标域名是否在 `force_proxy_domains` 列表中
   - 支持通配符匹配，如 `*.github.com` 匹配 `api.github.com`
   - 如果匹配且代理服务器可用，强制使用代理

2. **命令行参数**
   - `--force-proxy`：强制使用代理
   - `--force-direct`：强制直连

3. **本地地址检测**
   - `localhost`、`127.0.0.1`、`::1`
   - 本地网络地址：`192.168.x.x`、`10.x.x.x`、`172.16-31.x.x`
   - 自动直连，无需代理

4. **NO_PROXY 白名单匹配**
   - 检查目标地址是否在 NO_PROXY 列表中
   - 支持通配符模式

5. **直连测试**
   - 尝试直连测试（2秒超时）
   - 直连成功则不使用代理
   - 直连失败则使用代理

6. **默认配置**
   - 以上条件都不满足时，根据配置文件决定

## 配置文件

代理配置保存在 `.trae/proxy_config.json`：

```json
{
  "version": "2.1",
  "proxy": {
    "enabled": true,
    "type": "http",
    "host": "127.0.0.1",
    "port": 10808,
    "username": null,
    "password": null,
    "auto_detect": true,
    "force_proxy_domains": ["*.github.com"],
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

## 详细文档

更多详细信息请参考：
- [配置说明](references/configuration.md) - 详细的配置字段说明和使用场景
- [常见问题](references/faq.md) - 常见问题和解答
- [技术细节](references/technical-details.md) - 技术实现细节和脚本说明
