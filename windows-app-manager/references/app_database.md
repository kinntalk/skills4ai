# Application Database

This document provides reference information for common Windows applications.

## Communication Apps

| App Name | Display Name | Process Name | Executable | Notes |
|----------|--------------|--------------|------------|-------|
| WeChat | WeChat/微信 | Weixin.exe | Weixin.exe | Executable is Weixin.exe |
| QQ | QQ | QQ.exe | QQ.exe | |
| WeCom | Enterprise WeChat | WeCom.exe | WeCom.exe | |
| DingTalk | DingTalk | DingTalk.exe | DingTalk.exe | |
| Feishu | Feishu (Lark) | Feishu.exe | Feishu.exe | ByteDance Feishu |
| Slack | Slack | slack.exe | slack.exe | |
| Discord | Discord | Discord.exe | Discord.exe | |
| Teams | Microsoft Teams | Teams.exe | Teams.exe | |
| Zoom | Zoom | Zoom.exe | Zoom.exe | |

## Remote Desktop

| App Name | Display Name | Process Name | Executable | Notes |
|----------|--------------|--------------|------------|-------|
| RustDesk | RustDesk | rustdesk.exe | rustdesk.exe | Case-sensitive (lowercase) |

## Browsers

| App Name | Display Name | Process Name | Executable | Notes |
|----------|--------------|--------------|------------|-------|
| Chrome | Google Chrome | chrome.exe | chrome.exe | |
| Edge | Microsoft Edge | msedge.exe | msedge.exe | |
| Firefox | Mozilla Firefox | firefox.exe | firefox.exe | |

## Development Tools

| App Name | Display Name | Process Name | Executable | Notes |
|----------|--------------|--------------|------------|-------|
| VSCode | Visual Studio Code | Code.exe | Code.exe | |
| Notepad++ | Notepad++ | notepad++.exe | notepad++.exe | |

## Note Taking

| App Name | Display Name | Process Name | Executable | Notes |
|----------|--------------|--------------|------------|-------|
| Obsidian | Obsidian | Obsidian.exe | Obsidian.exe | |
| Typora | Typora | Typora.exe | Typora.exe | |

## System Apps

| App Name | Display Name | Process Name | Executable | Notes |
|----------|--------------|--------------|------------|-------|
| Notepad | Notepad | notepad.exe | notepad.exe | Windows built-in |

## Process Patterns

Some applications spawn multiple processes:

| App Name | Process Patterns |
|----------|------------------|
| WeChat | Weixin.exe, WeChatAppEx.exe |
| QQ | QQ.exe, QQNT.exe |
| RustDesk | rustdesk.exe |
| Teams | Teams.exe |
| Chrome | chrome.exe |
| Edge | msedge.exe |

## Notes

- Process names are case-sensitive on Windows
- Some applications use different executable names than their display names
- Multiple processes may run for a single application
- Use `tasklist` or `Get-Process` to verify process names
