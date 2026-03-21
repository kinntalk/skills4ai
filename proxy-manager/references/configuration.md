# 配置说明

## 目录

- [配置文件位置](#配置文件位置)
- [配置文件格式](#配置文件格式)
- [配置字段说明](#配置字段说明)
- [使用场景](#使用场景)
- [配置示例](#配置示例)

## 配置文件位置

代理配置保存在项目根目录下的 `.trae/proxy_config.json` 文件中。

## 配置文件格式

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
    "force_proxy_domains": ["github.com", "*.github.com"],
    "no_proxy": "localhost,127.0.0.1,::1,localaddress,*.local,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
  },
  "git": {
    "http_proxy": "http://127.0.0.1:10808",
    "https_proxy": "http://127.0.0.1:10808"
  },
  "environment": {
    "HTTP_PROXY": "http://127.0.0.1:10808",
    "HTTPS_PROXY": "http://127.0.0.1:10808",
    "NO_PROXY": "localhost,127.0.0.1,::1,localaddress,*.local,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
  }
}
```

## 配置字段说明

### version
- **类型**: string
- **说明**: 配置文件版本，当前为 `2.1`
- **用途**: 用于配置文件版本管理和迁移

### proxy.enabled
- **类型**: boolean
- **说明**: 是否启用代理
- **默认值**: true
- **用途**: 全局开关，控制代理是否生效

### proxy.type
- **类型**: string
- **说明**: 代理类型
- **可选值**: `http`、`socks5`
- **默认值**: `http`
- **用途**: 指定代理协议类型

### proxy.host
- **类型**: string
- **说明**: 代理服务器地址
- **示例**: `127.0.0.1`、`proxy.example.com`
- **用途**: 指定代理服务器的 IP 地址或域名

### proxy.port
- **类型**: number
- **说明**: 代理服务器端口
- **示例**: `10808`、`8080`
- **用途**: 指定代理服务器的端口号

### proxy.username
- **类型**: string | null
- **说明**: 代理用户名（可选）
- **默认值**: null
- **用途**: 如果代理服务器需要认证，提供用户名

### proxy.password
- **类型**: string | null
- **说明**: 代理密码（可选）
- **默认值**: null
- **用途**: 如果代理服务器需要认证，提供密码

### proxy.auto_detect
- **类型**: boolean
- **说明**: 是否启用智能代理检测
- **默认值**: true
- **用途**: 控制是否自动检测目标地址是否需要代理

### proxy.force_proxy_domains
- **类型**: array
- **说明**: 强制代理域名列表
- **示例**: `["github.com", "*.github.com"]`
- **用途**: 指定哪些域名强制使用代理，不受直连测试影响
- **支持通配符**: 如 `*.github.com` 匹配所有 GitHub 子域名

### proxy.no_proxy
- **类型**: string
- **说明**: NO_PROXY 白名单，逗号分隔
- **示例**: `"localhost,127.0.0.1,::1,localaddress,*.local,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"`
- **用途**: 指定哪些地址不走代理

### git.http_proxy
- **类型**: string | null
- **说明**: Git HTTP 代理配置
- **示例**: `"http://127.0.0.1:10808"`
- **用途**: Git HTTP 请求使用的代理

### git.https_proxy
- **类型**: string | null
- **说明**: Git HTTPS 代理配置
- **示例**: `"http://127.0.0.1:10808"`
- **用途**: Git HTTPS 请求使用的代理

### environment.HTTP_PROXY
- **类型**: string
- **说明**: HTTP 代理环境变量
- **示例**: `"http://127.0.0.1:10808"`
- **用途**: HTTP 请求使用的代理

### environment.HTTPS_PROXY
- **类型**: string
- **说明**: HTTPS 代理环境变量
- **示例**: `"http://127.0.0.1:10808"`
- **用途**: HTTPS 请求使用的代理

### environment.NO_PROXY
- **类型**: string
- **说明**: NO_PROXY 环境变量
- **示例**: `"localhost,127.0.0.1,::1,localaddress,*.local,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"`
- **用途**: 指定哪些地址不走代理

## 使用场景

### 场景 1：配置 HTTP 代理

```bash
python .trae/skills/proxy-manager/scripts/setup_proxy.py http 127.0.0.1 10808
```

生成的配置文件：
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
    "force_proxy_domains": [],
    "no_proxy": "localhost,127.0.0.1,::1,localaddress,*.local,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
  }
}
```

### 场景 2：配置 SOCKS5 代理

```bash
python .trae/skills/proxy-manager/scripts/setup_proxy.py socks5 127.0.0.1 10808
```

生成的配置文件：
```json
{
  "version": "2.1",
  "proxy": {
    "enabled": true,
    "type": "socks5",
    "host": "127.0.0.1",
    "port": 10808,
    "username": null,
    "password": null,
    "auto_detect": true,
    "force_proxy_domains": [],
    "no_proxy": "localhost,127.0.0.1,::1,localaddress,*.local,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
  }
}
```

### 场景 3：配置带认证的代理

```bash
python .trae/skills/proxy-manager/scripts/setup_proxy.py http proxy.example.com 8080 username password
```

生成的配置文件：
```json
{
  "version": "2.1",
  "proxy": {
    "enabled": true,
    "type": "http",
    "host": "proxy.example.com",
    "port": 8080,
    "username": "username",
    "password": "password",
    "auto_detect": true,
    "force_proxy_domains": [],
    "no_proxy": "localhost,127.0.0.1,::1,localaddress,*.local,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
  }
}
```

### 场景 4：配置强制代理域名

编辑 `.trae/proxy_config.json`，添加 `force_proxy_domains` 字段：

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
    "force_proxy_domains": ["github.com", "*.github.com"],
    "no_proxy": "localhost,127.0.0.1,::1,localaddress,*.local,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
  }
}
```

**说明**：
- `github.com`：强制 `github.com` 域名使用代理
- `*.github.com`：强制所有 `github.com` 的子域名使用代理（如 `api.github.com`、`raw.githubusercontent.com`）

### 场景 5：禁用自动 NO_PROXY 生成

```bash
python .trae/skills/proxy-manager/scripts/setup_proxy.py http 127.0.0.1 10808 --no-auto-no-proxy
```

生成的配置文件：
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
    "auto_detect": false,
    "force_proxy_domains": [],
    "no_proxy": "localhost,127.0.0.1"
  }
}
```

## 配置示例

### 最小配置

```json
{
  "version": "2.1",
  "proxy": {
    "enabled": true,
    "type": "http",
    "host": "127.0.0.1",
    "port": 10808
  }
}
```

### 完整配置

```json
{
  "version": "2.1",
  "proxy": {
    "enabled": true,
    "type": "http",
    "host": "127.0.0.1",
    "port": 10808,
    "username": "user",
    "password": "pass",
    "auto_detect": true,
    "force_proxy_domains": ["github.com", "*.github.com", "gitlab.com"],
    "no_proxy": "localhost,127.0.0.1,::1,localaddress,*.local,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
  },
  "git": {
    "http_proxy": "http://127.0.0.1:10808",
    "https_proxy": "http://127.0.0.1:10808"
  },
  "environment": {
    "HTTP_PROXY": "http://127.0.0.1:10808",
    "HTTPS_PROXY": "http://127.0.0.1:10808",
    "NO_PROXY": "localhost,127.0.0.1,::1,localaddress,*.local,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
  }
}
```

### SOCKS5 代理配置

```json
{
  "version": "2.1",
  "proxy": {
    "enabled": true,
    "type": "socks5",
    "host": "127.0.0.1",
    "port": 10808,
    "username": null,
    "password": null,
    "auto_detect": true,
    "force_proxy_domains": [],
    "no_proxy": "localhost,127.0.0.1,::1,localaddress,*.local,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
  }
}
```

### 禁用代理

```json
{
  "version": "2.1",
  "proxy": {
    "enabled": false,
    "type": "http",
    "host": "127.0.0.1",
    "port": 10808,
    "username": null,
    "password": null,
    "auto_detect": true,
    "force_proxy_domains": [],
    "no_proxy": "localhost,127.0.0.1,::1,localaddress,*.local,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
  }
}
```
