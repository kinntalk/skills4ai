import json
import platform
from pathlib import Path
from typing import Optional


def get_obsidian_config_path() -> Path:
    system = platform.system()

    if system == "Windows":
        config_path = Path.home() / "AppData" / "Roaming" / "obsidian" / "obsidian.json"
    elif system == "Darwin":
        config_path = Path.home() / "Library" / "Application Support" / "obsidian" / "obsidian.json"
    else:
        config_path = Path.home() / ".config" / "obsidian" / "obsidian.json"

    return config_path


def read_obsidian_config() -> dict:
    config_path = get_obsidian_config_path()

    if not config_path.exists():
        raise FileNotFoundError(f"Obsidian config file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    return config


def detect_vault_path() -> Optional[Path]:
    try:
        config = read_obsidian_config()
    except (FileNotFoundError, json.JSONDecodeError):
        return None

    vaults = config.get("vaults", {})

    if not vaults:
        return None

    if len(vaults) == 1:
        vault_id = list(vaults.keys())[0]
        vault_info = vaults[vault_id]
        vault_path = vault_info.get("path")
        if vault_path:
            return Path(vault_path)
        return None

    open_vaults = [
        (vault_id, vault_info)
        for vault_id, vault_info in vaults.items()
        if vault_info.get("open", False)
    ]

    if open_vaults:
        selected_vault = open_vaults[0]
    else:
        sorted_vaults = sorted(
            vaults.items(),
            key=lambda x: x[1].get("ts", 0),
            reverse=True
        )
        selected_vault = sorted_vaults[0]

    vault_info = selected_vault[1]
    vault_path = vault_info.get("path")

    if vault_path:
        return Path(vault_path)
    return None


def get_vault_attachment_folder(vault_path: Path) -> str:
    app_json_path = vault_path / ".obsidian" / "app.json"

    if not app_json_path.exists():
        return "assets"

    try:
        with open(app_json_path, "r", encoding="utf-8") as f:
            app_config = json.load(f)

        attachment_folder = app_config.get("attachmentFolderPath", "assets")
        return attachment_folder if attachment_folder else "assets"
    except (json.JSONDecodeError, IOError):
        return "assets"
