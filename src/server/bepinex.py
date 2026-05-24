"""
BepInEx detection and installation.

When bepinex_download_url is empty in the game JSON, the latest stable
release is fetched automatically from the GitHub releases API.
"""

from __future__ import annotations
import os
import tempfile
import zipfile
from typing import Callable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.game_model import GameModel


def is_installed(game: "GameModel") -> bool:
    if not game.mod_support or not game.mod_support.bepinex_marker:
        return False
    return os.path.exists(
        os.path.join(game.get_install_path(), game.mod_support.bepinex_marker)
    )


def _get_download_url(game: "GameModel") -> str:
    if game.mod_support.bepinex_download_url:
        return game.mod_support.bepinex_download_url

    import requests
    resp = requests.get(
        "https://api.github.com/repos/BepInEx/BepInEx/releases/latest",
        timeout=10,
        headers={"Accept": "application/vnd.github.v3+json"},
    )
    resp.raise_for_status()
    for asset in resp.json().get("assets", []):
        name = asset["name"].lower()
        if name.endswith(".zip") and "win_x64" in name:
            return asset["browser_download_url"]
    raise ValueError("No suitable BepInEx win_x64 asset found in latest release")


def install(
    game: "GameModel",
    progress: Optional[Callable[[int], None]] = None,
    status: Optional[Callable[[str], None]] = None,
) -> bool:
    def p(v: int) -> None:
        if progress:
            progress(v)

    def s(msg: str) -> None:
        if status:
            status(msg)

    if not game.mod_support:
        s("This game does not support mods.")
        return False

    try:
        s("Finding latest BepInEx release...")
        url = _get_download_url(game)

        s("Downloading BepInEx...")
        import requests
        r = requests.get(url, stream=True, timeout=60)
        r.raise_for_status()

        total = int(r.headers.get("content-length", 0))
        downloaded = 0
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as f:
            tmp_path = f.name
            for chunk in r.iter_content(8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    p(int(downloaded / total * 70))

        s("Extracting BepInEx...")
        p(70)
        with zipfile.ZipFile(tmp_path, "r") as z:
            z.extractall(game.get_install_path())

        os.unlink(tmp_path)
        p(100)
        s("BepInEx installed successfully!")
        return True

    except Exception as exc:
        s(f"BepInEx install failed: {exc}")
        return False
