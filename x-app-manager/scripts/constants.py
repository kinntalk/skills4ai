import os
from typing import Dict, List

APP_TRANSLATIONS: Dict[str, List[str]] = {
    "wechat": ["wechat", "weixin", "wechatapp"],
    "feishu": ["feishu", "lark"],
    "dingtalk": ["dingtalk", "ding"],
    "qq": ["qq"],
    "wecom": ["wecom", "wxwork"],
    "douyin": ["douyin", "tiktok"],
    "taobao": ["taobao"],
    "jd": ["jd", "jingdong"],
    "alipay": ["alipay"],
    "cloudmusic": ["cloudmusic", "neteasemusic"],
    "qqmusic": ["qqmusic"],
    "wechatdevtools": ["wechatdevtools"],
    "vscode": ["code", "vscode"],
    "chrome": ["chrome"],
    "edge": ["msedge", "edge"],
    "firefox": ["firefox"],
    "rustdesk": ["rustdesk"],
    "notepad": ["notepad"],
    "tabbit": ["tabbit"],
}

APP_EXECUTABLE_NAMES: Dict[str, List[str]] = {
    "wechat": ["WeChat.exe", "Weixin.exe"],
    "weixin": ["Weixin.exe", "WeChat.exe"],
    "feishu": ["Feishu.exe", "Lark.exe"],
    "dingtalk": ["DingTalk.exe", "DingtalkLauncher.exe"],
    "qq": ["QQ.exe", "QQScLauncher.exe"],
    "wecom": ["WeCom.exe", "WXWork.exe"],
    "chrome": ["chrome.exe"],
    "msedge": ["msedge.exe"],
    "firefox": ["firefox.exe"],
    "rustdesk": ["rustdesk.exe"],
    "notepad": ["notepad.exe", "NOTEPAD.EXE"],
    "tabbit": ["Tabbit.exe"],
}

LOGIN_REQUIRED_APPS = ["wechat", "feishu", "dingtalk", "qq", "wecom"]

COMMON_INSTALL_DIRS: List[str] = [
    "install",
    "apps",
    "app",
    "software",
    "programs",
    "Program Files",
    "Program Files (x86)",
]

MSG_EN: Dict[str, str] = {
    "starting": "Starting: {app_name}",
    "already_running": "{app_name} already running",
    "started_success": "{app_name} started",
    "failed_to_start": "Failed: {message}",
    "cannot_find": "Not found: {app_name}",
    "stopping": "Stopping: {app_name}",
    "not_running": "{app_name} not running",
    "stopped_success": "{app_name} stopped",
    "found_apps": "Found {count} apps",
    "found_results": "Found {count} results",
    "result": "Result: {message}",
    "error_get_process": "Error getting process list: {error}",
}

MSG = {"en": MSG_EN}


def _t(key: str, **kwargs) -> str:
    lang = os.environ.get("SKILL_LANG", "en")
    template = MSG.get(lang, MSG["en"]).get(key, MSG["en"].get(key, key))
    return template.format(**kwargs)


def get_translated_names(app_name: str) -> List[str]:
    names = []
    app_name_lower = app_name.lower().strip()
    
    names.append(app_name + ".exe")
    names.append(app_name_lower + ".exe")
    names.append(app_name.upper() + ".exe")
    names.append(app_name.replace(" ", "") + ".exe")
    
    for cn_name, en_names in APP_TRANSLATIONS.items():
        if app_name == cn_name:
            for en_name in en_names:
                names.append(en_name + ".exe")
                names.append(en_name.capitalize() + ".exe")
        if app_name_lower in [en.lower() for en in en_names]:
            for en_name in en_names:
                names.append(en_name + ".exe")
                names.append(en_name.capitalize() + ".exe")
    
    for key, exe_names in APP_EXECUTABLE_NAMES.items():
        if key in app_name_lower:
            names.extend(exe_names)
    
    return list(set(names))


def get_process_keywords(app_name: str) -> List[str]:
    keywords = []
    app_name_lower = app_name.lower().strip()
    
    keywords.append(app_name_lower)
    
    for cn_name, en_names in APP_TRANSLATIONS.items():
        if cn_name in app_name_lower or app_name_lower in cn_name:
            keywords.extend(en_names)
        for en_name in en_names:
            if en_name in app_name_lower:
                keywords.extend(en_names)
                break
    
    return list(set([k for k in keywords if len(k) >= 2]))


def get_app_id(app_name: str) -> str:
    app_name_lower = app_name.lower().strip()
    for app_id, aliases in APP_TRANSLATIONS.items():
        if app_name_lower == app_id or app_name_lower in aliases:
            return app_id
    return app_name_lower


def is_login_required(app_name: str) -> bool:
    app_id = get_app_id(app_name)
    return app_id in LOGIN_REQUIRED_APPS
