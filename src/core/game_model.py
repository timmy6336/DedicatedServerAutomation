"""
GameModel — the single data class for a supported game.

Loaded by GameRegistry from a JSON file in src/games/.
All UI and server-management code consumes this; no game-name if/elif
chains anywhere else in the codebase.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PortDef:
    """A single port that the server needs."""
    port: int
    protocol: str = "UDP"          # "TCP", "UDP", or "TCP/UDP"
    description: str = ""


@dataclass
class ModSupport:
    """Mod framework config for a game, read from JSON mod_support block."""
    framework: str = ""           # "bepinex" | "steam_workshop"
    plugins_subdir: str = ""      # relative to install dir, e.g. "BepInEx/plugins"
    bepinex_marker: str = ""      # file that confirms BepInEx is installed
    bepinex_download_url: str = ""  # empty = auto-fetch latest from GitHub
    # steam_workshop only
    workshop_app_id: str = ""     # Steam appid whose workshop to browse (e.g. "322330" for DST)
    mods_subdir: str = ""         # subdir inside install path containing server mod files


@dataclass
class SettingDef:
    """
    One configurable server setting, read from the JSON's server_settings list.

    Supported types:
        string   → QLineEdit
        password → QLineEdit (echo=Password) + optional help_url link
        int      → QSpinBox
        bool     → QCheckBox
        choice   → QComboBox (options list required)
    """
    key: str
    label: str
    type: str = "string"           # string | password | int | bool | choice
    default: Any = ""
    required: bool = False
    # string / password
    min_length: int = 0
    max_length: int = 0            # 0 = unlimited
    placeholder: str = ""
    help_url: str = ""             # shown as clickable link for password/token fields
    # int
    min: int = 0
    max: int = 65535
    # choice
    options: list[str] = field(default_factory=list)
    # world_picker
    worlds_path_windows: str = ""
    worlds_path_linux: str = ""
    # display
    tooltip: str = ""


@dataclass
class GameModel:
    """
    All metadata and server-launch information for one game.

    Populated by GameRegistry.load_all() from a JSON file.
    Only fields actually used by the UI or server manager are listed;
    the rest of the JSON is available via extra_data if needed.
    """
    # ---- identity ----
    id: str                           # JSON filename stem, e.g. "valheim"
    name: str                         # Display name, e.g. "Valheim"
    description: str = ""
    genre: str = ""
    developer: str = ""
    platforms: list[str] = field(default_factory=list)

    # ---- image ----
    image: str = ""                   # Relative path, e.g. "images/valheim_image.jpg"

    # ---- server core ----
    steam_app_id: str = ""
    launch_mode: str = "steam"        # "steam" | "dst_dual_shard"
    server_dir_name: str = ""         # Folder name under Steam/steamapps/common/
    executable: str = ""              # Server executable filename
    executable_subdir: str = ""       # Subdirectory containing exe (e.g. "bin" for DST)
    launch_args: str = ""             # Template string; {key} replaced from saved config
    process_names: list[str] = field(default_factory=list)   # For detection

    # ---- ports ----
    default_port: int = 0
    ports: list[PortDef] = field(default_factory=list)

    # ---- config form ----
    server_settings: list[SettingDef] = field(default_factory=list)

    # ---- multiplayer ----
    max_players: int = 0
    min_players: int = 1

    # ---- mod support ----
    mod_support: ModSupport | None = None

    # ---- raw extras ----
    extra_data: dict = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Helpers used by UI / server manager
    # ------------------------------------------------------------------

    def get_default_config(self) -> dict:
        """Return a dict of {key: default_value} from server_settings."""
        return {s.key: s.default for s in self.server_settings}

    def get_install_path(self) -> str:
        """
        Absolute path to the server installation directory.
        Uses platform-appropriate Steam path.
        """
        import os
        import platform as _platform
        if _platform.system().lower() == "windows":
            base = os.path.expandvars(r"%USERPROFILE%\Steam\steamapps\common")
        else:
            base = os.path.expanduser("~/Steam/steamapps/common")
        return os.path.join(base, self.server_dir_name)

    def get_executable_path(self) -> str:
        """Absolute path to the server executable."""
        import os
        install = self.get_install_path()
        if self.executable_subdir:
            return os.path.join(install, self.executable_subdir, self.executable)
        return os.path.join(install, self.executable)

    def is_installed(self) -> bool:
        """Quick check — does the server executable exist on disk?"""
        import os
        return os.path.exists(self.get_executable_path())

    def build_launch_args(self, config: dict) -> list[str]:
        """
        Format self.launch_args template with values from config dict.
        Returns a list of string tokens ready for subprocess.
        """
        if not self.launch_args:
            return []
        try:
            formatted = self.launch_args.format(**config)
        except KeyError:
            # Missing keys: just pass the raw template
            formatted = self.launch_args
        import shlex
        return shlex.split(formatted)
