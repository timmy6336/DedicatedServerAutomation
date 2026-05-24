"""
Mod manager — install, list, enable/disable, and remove server mods.

Mods live in <install_dir>/<plugins_subdir>/ (e.g. BepInEx/plugins/).
Enable/disable is done by renaming .dll ↔ .dll.disabled.
"""

from __future__ import annotations
import os
import shutil
import zipfile
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.game_model import GameModel


def get_plugins_dir(game: "GameModel") -> str:
    if not game.mod_support or not game.mod_support.plugins_subdir:
        return ""
    return os.path.join(game.get_install_path(), game.mod_support.plugins_subdir)


def list_mods(game: "GameModel") -> list[dict]:
    """Return [{name, enabled, path}] for every mod in the plugins directory."""
    d = get_plugins_dir(game)
    if not d or not os.path.isdir(d):
        return []
    mods = []
    for f in sorted(os.listdir(d)):
        path = os.path.join(d, f)
        if f.endswith(".dll"):
            mods.append({"name": f[:-4], "enabled": True, "path": path})
        elif f.endswith(".dll.disabled"):
            mods.append({"name": f[:-13], "enabled": False, "path": path})
    return mods


def install_mod(game: "GameModel", file_path: str) -> list[str]:
    """
    Install a mod from a .dll or .zip file into the plugins directory.
    Returns a list of installed mod names (without extension).
    """
    plugins_dir = get_plugins_dir(game)
    if not plugins_dir:
        return []
    os.makedirs(plugins_dir, exist_ok=True)

    installed: list[str] = []
    lower = file_path.lower()

    if lower.endswith(".dll"):
        name = os.path.basename(file_path)
        shutil.copy2(file_path, os.path.join(plugins_dir, name))
        installed.append(name[:-4])

    elif lower.endswith(".zip"):
        try:
            with zipfile.ZipFile(file_path, "r") as z:
                for member in z.namelist():
                    basename = os.path.basename(member)
                    if basename.lower().endswith(".dll") and basename:
                        data = z.read(member)
                        dest = os.path.join(plugins_dir, basename)
                        with open(dest, "wb") as f:
                            f.write(data)
                        installed.append(basename[:-4])
        except zipfile.BadZipFile as exc:
            print(f"[ModManager] Bad zip file: {exc}")

    return installed


def toggle_mod(mod: dict, enabled: bool) -> bool:
    """Enable or disable a mod by renaming its .dll file."""
    path = mod["path"]
    try:
        if enabled and path.endswith(".dll.disabled"):
            os.rename(path, path[:-9])
        elif not enabled and path.endswith(".dll"):
            os.rename(path, path + ".disabled")
        return True
    except OSError as exc:
        print(f"[ModManager] Toggle failed: {exc}")
        return False


def remove_mod(mod: dict) -> bool:
    """Permanently delete a mod file."""
    try:
        os.remove(mod["path"])
        return True
    except OSError as exc:
        print(f"[ModManager] Remove failed: {exc}")
        return False
