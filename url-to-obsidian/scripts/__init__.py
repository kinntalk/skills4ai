"""
URL to Obsidian Markdown Converter

Convert web pages to Obsidian Flavored Markdown and save to Obsidian vault.
"""

from .config_manager import ConfigManager, get_config_manager
from .converter import UrlToObsidianConverter, convert_url
from .ofm_formatter import format_ofm, generate_filename, sanitize_filename
from .asset_handler import (
    AssetHandler,
    download_file,
    generate_asset_filename,
    sanitize_filename as sanitize_asset_filename,
    get_extension_from_url,
)

__version__ = "1.0.0"
__all__ = [
    'ConfigManager',
    'get_config_manager',
    'UrlToObsidianConverter',
    'convert_url',
    'format_ofm',
    'generate_filename',
    'sanitize_filename',
    'AssetHandler',
    'download_file',
    'generate_asset_filename',
    'sanitize_asset_filename',
    'get_extension_from_url',
]
