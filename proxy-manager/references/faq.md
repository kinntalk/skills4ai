# 常见问题

## 目录

- [代理配置](#代理配置)
- [代理使用](#代理使用)
- [Git 代理](#git-代理)
- [故障排查](#故障排查)
- [高级配置](#高级配置)

## 代理配置

### Q: 如何检查代理是否生效？

A: 运行以下命令会显示代理配置状态和连接测试结果：

```bash
python .trae/skills/proxy-manager/scripts/apply_proxy.py --test
```

测试输出示例：
```
测试代理连接...
  强制代理域名: github.com, *.github.com
  https://github.com: 使用代理 (Forced proxy for domain: github.com)
  https://api.github.com: 使用代理 (Forced proxy for domain: api.github.com)
```

### Q: 如何临时禁用代理？

A: 将 `.trae/proxy_config.json` 中的 `enabled` 设置为 `false`：

```json
{
  "proxy": {
    "enabled": false
  }
}
```

或者运行：

```bash
python .trae/skills/proxy-manager/scripts/clear_proxy.py
```

### Q: 支持哪些代理协议？

A: 支持 HTTP 和 SOCKS5 协议。

- **HTTP 代理**: 适用于 HTTP 和 HTTPS 请求
- **SOCKS5 代理**: 更通用的代理协议，支持 TCP 和 UDP

### Q: 如何配置带认证的代理？

A: 在配置代理时提供用户名和密码：

```bash
python .trae/skills/proxy-manager/scripts/setup_proxy.py http proxy.example.com 8080 username password
```

或者编辑 `.trae/proxy_config.json`：

```json
{
  "proxy": {
    "username": "username",
    "password": "password"
  }
}
```

### Q: 如何禁用自动 NO_PROXY 生成？

A: 使用 `--no-auto-no-proxy` 选项：

```bash
python .trae/skills/proxy-manager/scripts/setup_proxy.py http 127.0.0.1 10808 --no-auto-no-proxy
```

## 代理使用

### Q: 如何强制使用代理？

A: 使用 `--force-proxy` 选项：

```bash
python .trae/skills/proxy-manager/scripts/git_with_proxy.py --force-proxy clone https://github.com/user/repo.git
```

### Q: 如何强制直连？

A: 使用 `--force-direct` 选项：

```bash
python .trae/skills/proxy-manager/scripts/git_with_proxy.py --force-direct clone https://github.com/user/repo.git
```

### Q: 什么是强制代理域名？

A: 强制代理域名是配置在 `force_proxy_domains` 列表中的域名，这些域名会强制使用代理，不受直连测试影响。适用于需要确保连接稳定性的服务，如 GitHub。

**特点**：
- 优先级最高，不受直连测试影响
- 即使直连成功也会使用代理
- 支持通配符匹配

### Q: 如何配置强制代理域名？

A: 编辑 `.trae/proxy_config.json`，在 `proxy` 对象中添加 `force_proxy_domains` 数组：

```json
{
  "proxy": {
    "force_proxy_domains": ["github.com", "*.github.com"]
  }
}
```

**通配符支持**：
- `*.github.com` 匹配所有 `github.com` 的子域名
- `api.github.com`、`raw.githubusercontent.com` 等都会被匹配

### Q: 强制代理域名会影响其他服务吗？

A: 不会。强制代理域名只影响列表中指定的域名，其他服务仍然按智能代理逻辑判断是否使用代理。

**示例**：
```json
{
  "proxy": {
    "force_proxy_domains": ["github.com", "*.github.com"]
  }
}
```

- `github.com`：强制使用代理
- `api.github.com`：强制使用代理（通配符匹配）
- `google.com`：按智能代理逻辑判断

### Q: 智能代理如何判断是否需要代理？

A: 系统会按以下顺序判断：

1. **检查是否为强制代理域名**（v2.1 新增）
   - 如果目标域名在 `force_proxy_domains` 列表中，强制使用代理

2. **检查命令行参数**
   - `--force-proxy`：强制使用代理
   - `--force-direct`：强制直连

3. **检查目标地址是否为本地地址**
   - `localhost`、`127.0.0.1`、`::1`
   - 本地网络地址：`192.168.x.x`、`10.x.x.x`、`172.16-31.x.x`
   - 自动直连，无需代理

4. **检查目标地址是否在 NO_PROXY 列表中**
   - 如果在 NO_PROXY 列表中，直连

5. **尝试直连测试**（2秒超时）
   - 直连成功则不使用代理
   - 直连失败则使用代理

6. **默认配置**
   - 以上条件都不满足时，根据配置文件决定

## Git 代理

### Q: 如何配置 Git 全局代理？

A: 运行以下命令会配置 Git 全局代理：

```bash
python .trae/skills/proxy-manager/scripts/git_with_proxy.py --permanent
```

或者手动配置：

```bash
git config --global http.proxy http://127.0.0.1:10808
git config --global https.proxy http://127.0.0.1:10808
```

### Q: 如何清除 Git 代理配置？

A: 运行以下命令会清除 Git 代理配置：

```bash
git config --global --unset http.proxy
git config --global --unset https.proxy
```

或者运行：

```bash
python .trae/skills/proxy-manager/scripts/clear_proxy.py
```

### Q: Git 代理和 HTTP 代理有什么区别？

A: 区别如下：

- **HTTP 代理**：通过环境变量 `HTTP_PROXY` 和 `HTTPS_PROXY` 设置，影响所有 HTTP/HTTPS 请求
- **Git 代理**：通过 Git 配置 `http.proxy` 和 `https.proxy` 设置，只影响 Git 操作

**建议**：
- 如果只使用 Git，配置 Git 代理即可
- 如果需要其他工具也使用代理，配置 HTTP 代理

## 故障排查

### Q: 配置代理后仍然无法访问 GitHub？

A: 请按以下步骤排查：

1. **检查代理服务器是否正常运行**
   ```bash
   python .trae/skills/proxy-manager/scripts/apply_proxy.py --test
   ```

2. **检查代理配置是否正确**
   ```bash
   cat .trae/proxy_config.json
   ```

3. **检查代理服务器地址和端口**
   - 确认代理服务器地址和端口正确
   - 确认代理服务器类型（HTTP 或 SOCKS5）正确

4. **检查代理服务器认证**
   - 如果代理服务器需要认证，确认用户名和密码正确

5. **尝试强制使用代理**
   ```bash
   python .trae/skills/proxy-manager/scripts/git_with_proxy.py --force-proxy clone https://github.com/user/repo.git
   ```

### Q: 代理配置后本地服务无法访问？

A: 检查 `NO_PROXY` 配置是否包含本地地址：

```json
{
  "proxy": {
    "no_proxy": "localhost,127.0.0.1,::1,localaddress,*.local,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
  }
}
```

如果 `no_proxy` 配置不完整，可以手动添加本地地址。

### Q: Git 操作仍然超时？

A: 请按以下步骤排查：

1. **检查 Git 代理配置**
   ```bash
   git config --global --get http.proxy
   git config --global --get https.proxy
   ```

2. **检查 HTTP 代理环境变量**
   ```bash
   echo $HTTP_PROXY
   echo $HTTPS_PROXY
   ```

3. **测试代理连接**
   ```bash
   python .trae/skills/proxy-manager/scripts/apply_proxy.py --test
   ```

4. **尝试使用 git_with_proxy.py**
   ```bash
   python .trae/skills/proxy-manager/scripts/git_with_proxy.py clone https://github.com/user/repo.git
   ```

## 高级配置

### Q: 如何自定义 NO_PROXY 列表？

A: 编辑 `.trae/proxy_config.json`，修改 `proxy.no_proxy` 字段：

```json
{
  "proxy": {
    "no_proxy": "localhost,127.0.0.1,::1,localaddress,*.local,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,example.com,*.example.com"
  }
}
```

**支持通配符**：
- `*.example.com` 匹配所有 `example.com` 的子域名

### Q: 如何为不同的域名配置不同的代理？

A: 当前版本不支持为不同域名配置不同代理。所有域名使用相同的代理配置。

**变通方案**：
- 使用强制代理域名列表
- 使用 NO_PROXY 列表排除不需要代理的域名

### Q: 如何查看当前代理配置？

A: 运行以下命令：

```bash
python .trae/skills/proxy-manager/scripts/proxy_status.py
```

或者查看配置文件：

```bash
cat .trae/proxy_config.json
```

### Q: 如何测试代理工具模块？

A: 运行以下命令：

```bash
python .trae/skills/proxy-manager/scripts/proxy_utils.py
```

这会测试智能代理工具模块的所有功能。

### Q: 代理配置文件在哪里？

A: 代理配置文件位于项目根目录下的 `.trae/proxy_config.json`。

**注意**：
- 配置文件是 JSON 格式
- 可以手动编辑
- 编辑后需要重新运行 `apply_proxy.py` 应用配置

### Q: 如何备份代理配置？

A: 复制配置文件：

```bash
cp .trae/proxy_config.json .trae/proxy_config.json.backup
```

或者导出配置：

```bash
cat .trae/proxy_config.json
```

### Q: 如何恢复代理配置？

A: 从备份恢复：

```bash
cp .trae/proxy_config.json.backup .trae/proxy_config.json
```

或者重新配置：

```bash
python .trae/skills/proxy-manager/scripts/setup_proxy.py http 127.0.0.1 10808
```
