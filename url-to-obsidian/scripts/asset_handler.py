"""
Asset handler module for url-to-obsidian skill.

Handles:
- File downloading from URLs
- Asset filename generation
- Asset management in Obsidian vault
"""

import re
import logging
from pathlib import Path
from typing import Tuple, Optional
from datetime import datetime
from urllib.parse import urlparse, unquote

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    import urllib.request
    import urllib.error
    HAS_REQUESTS = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def sanitize_filename(name: str, max_length: int = 100) -> str:
    """Sanitize a string for use as a filename.

    Removes or replaces characters that are invalid in filenames.

    Args:
        name: String to sanitize
        max_length: Maximum filename length

    Returns:
        Sanitized filename string
    """
    if not name:
        return "unnamed"

    sanitized = re.sub(r'[<>:"/\\|?*]', '-', name)
    sanitized = re.sub(r'[\x00-\x1f]', '', sanitized)
    sanitized = re.sub(r'\s+', '-', sanitized)
    sanitized = re.sub(r'-+', '-', sanitized)
    sanitized = sanitized.strip('-_.')

    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized or "unnamed"


def get_extension_from_url(url: str) -> str:
    """Extract file extension from URL.

    Args:
        url: URL to extract extension from

    Returns:
        File extension including the dot (e.g., '.png'), defaults to '.bin'
    """
    try:
        parsed = urlparse(url)
        path = unquote(parsed.path)
        filename = path.split('/')[-1]

        if '.' in filename:
            ext = filename.rsplit('.', 1)[-1]
            ext = re.sub(r'[^a-zA-Z0-9]', '', ext.lower())
            if ext and len(ext) <= 10:
                return f'.{ext}'
    except Exception as e:
        logger.debug(f"Error extracting extension from URL: {e}")

    return '.bin'


def download_file(url: str, output_path: Path, timeout: int = 30) -> Tuple[bool, str]:
    """Download a file from URL to specified path.

    Args:
        url: URL to download from
        output_path: Path to save the file
        timeout: Download timeout in seconds

    Returns:
        Tuple of (success, error_message or file_path)
    """
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if HAS_REQUESTS:
            return _download_with_requests(url, output_path, timeout)
        else:
            return _download_with_urllib(url, output_path, timeout)

    except Exception as e:
        error_msg = f"Download failed: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def _download_with_requests(url: str, output_path: Path, timeout: int) -> Tuple[bool, str]:
    """Download file using requests library.

    Args:
        url: URL to download from
        output_path: Path to save the file
        timeout: Download timeout in seconds

    Returns:
        Tuple of (success, error_message or file_path)
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=timeout, stream=True)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        logger.info(f"Downloaded: {url} -> {output_path}")
        return True, str(output_path)

    except requests.exceptions.Timeout:
        return False, f"Download timeout after {timeout} seconds"
    except requests.exceptions.ConnectionError as e:
        return False, f"Connection error: {str(e)}"
    except requests.exceptions.HTTPError as e:
        return False, f"HTTP error: {str(e)}"
    except requests.exceptions.RequestException as e:
        return False, f"Request error: {str(e)}"


def _download_with_urllib(url: str, output_path: Path, timeout: int) -> Tuple[bool, str]:
    """Download file using urllib library.

    Args:
        url: URL to download from
        output_path: Path to save the file
        timeout: Download timeout in seconds

    Returns:
        Tuple of (success, error_message or file_path)
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        request = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(request, timeout=timeout) as response:
            with open(output_path, 'wb') as f:
                f.write(response.read())

        logger.info(f"Downloaded: {url} -> {output_path}")
        return True, str(output_path)

    except urllib.error.URLError as e:
        return False, f"URL error: {str(e)}"
    except urllib.error.HTTPError as e:
        return False, f"HTTP error {e.code}: {str(e)}"
    except TimeoutError:
        return False, f"Download timeout after {timeout} seconds"


def generate_asset_filename(
    original_url: str,
    note_title: str,
    index: int,
    naming_template: str = "{title}-{timestamp}-{index}"
) -> str:
    """Generate a standardized asset filename.

    Args:
        original_url: Original URL of the asset
        note_title: Title of the associated note
        index: Index number for the asset
        naming_template: Template string with placeholders
            Supported placeholders: {title}, {timestamp}, {index}

    Returns:
        Generated filename with extension
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    sanitized_title = sanitize_filename(note_title, max_length=50)

    filename = naming_template.format(
        title=sanitized_title,
        timestamp=timestamp,
        index=index
    )

    filename = sanitize_filename(filename, max_length=150)

    extension = get_extension_from_url(original_url)

    return f"{filename}{extension}"


class AssetHandler:
    """Handler for managing assets in Obsidian vault."""

    def __init__(
        self,
        vault_path: Path,
        assets_folder: str = "assets",
        naming_template: str = "{title}-{timestamp}-{index}"
    ):
        """Initialize asset handler.

        Args:
            vault_path: Path to the Obsidian vault
            assets_folder: Folder name for storing assets (relative to vault)
            naming_template: Template for generating asset filenames
        """
        self.vault_path = Path(vault_path)
        self.assets_folder = assets_folder
        self.naming_template = naming_template
        self._assets_path: Optional[Path] = None

    def get_assets_path(self) -> Path:
        """Get the full path to the assets folder.

        Creates the folder if it doesn't exist.

        Returns:
            Path to the assets folder
        """
        if self._assets_path is None:
            self._assets_path = self.vault_path / self.assets_folder

        self._assets_path.mkdir(parents=True, exist_ok=True)
        return self._assets_path

    def asset_exists(self, filename: str) -> bool:
        """Check if an asset file already exists.

        Args:
            filename: Name of the asset file

        Returns:
            True if the asset exists, False otherwise
        """
        asset_path = self.get_assets_path() / filename
        return asset_path.exists()

    def download_asset(
        self,
        url: str,
        note_title: str,
        index: int
    ) -> Tuple[bool, str, Optional[Path]]:
        """Download a single asset from URL.

        Args:
            url: URL of the asset to download
            note_title: Title of the associated note
            index: Index number for the asset

        Returns:
            Tuple of (success, message, local_path)
        """
        if not url:
            return False, "Empty URL provided", None

        if url.startswith('data:'):
            return False, "Data URLs are not supported for asset download", None

        filename = generate_asset_filename(
            original_url=url,
            note_title=note_title,
            index=index,
            naming_template=self.naming_template
        )

        if self.asset_exists(filename):
            existing_path = self.get_assets_path() / filename
            logger.info(f"Asset already exists: {existing_path}")
            return True, f"Asset already exists: {filename}", existing_path

        output_path = self.get_assets_path() / filename

        success, result = download_file(url, output_path)

        if success:
            relative_path = Path(self.assets_folder) / filename
            return True, f"Downloaded: {filename}", output_path
        else:
            return False, result, None

    def get_asset_relative_path(self, filename: str) -> str:
        """Get the relative path to an asset from the vault root.

        Args:
            filename: Name of the asset file

        Returns:
            Relative path string (e.g., 'assets/image.png')
        """
        return f"{self.assets_folder}/{filename}"

    def cleanup_unused_assets(self, used_files: set) -> int:
        """Remove assets that are no longer referenced.

        Args:
            used_files: Set of filenames that are still in use

        Returns:
            Number of files removed
        """
        removed_count = 0
        assets_path = self.get_assets_path()

        if not assets_path.exists():
            return 0

        for asset_file in assets_path.iterdir():
            if asset_file.is_file() and asset_file.name not in used_files:
                try:
                    asset_file.unlink()
                    removed_count += 1
                    logger.info(f"Removed unused asset: {asset_file}")
                except Exception as e:
                    logger.warning(f"Failed to remove {asset_file}: {e}")

        return removed_count


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Asset handler for url-to-obsidian")
    parser.add_argument("--test-url", help="Test download from URL")
    parser.add_argument("--vault", help="Vault path for testing")
    parser.add_argument("--assets-folder", default="assets", help="Assets folder name")

    args = parser.parse_args()

    if args.test_url and args.vault:
        handler = AssetHandler(
            vault_path=Path(args.vault),
            assets_folder=args.assets_folder
        )

        success, message, path = handler.download_asset(
            url=args.test_url,
            note_title="test-note",
            index=1
        )

        print(f"Success: {success}")
        print(f"Message: {message}")
        print(f"Path: {path}")
    else:
        print("Asset Handler Module")
        print(f"Requests library available: {HAS_REQUESTS}")
        print("\nExample usage:")
        print("  handler = AssetHandler(Path('/path/to/vault'))")
        print("  success, msg, path = handler.download_asset(url, 'note-title', 1)")
