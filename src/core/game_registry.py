"""
GameRegistry — scans the games/ directory and loads every JSON file into
a GameModel. No game names are hardcoded here; adding a new game is as
simple as dropping a JSON file into games/.
"""

from __future__ import annotations
import json
import os
from pathlib import Path
from typing import List

from core.game_model import GameModel, ModSupport, PortDef, SettingDef


_GAMES_DIR = Path(__file__).parent.parent / "games"


def _load_game(json_path: Path) -> GameModel | None:
    """Parse one JSON file and return a GameModel, or None on error."""
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"[GameRegistry] Failed to load {json_path.name}: {exc}")
        return None

    game_id = json_path.stem  # e.g. "valheim"
    server_info = data.get("server_info", {})
    multiplayer = data.get("multiplayer", {})

    # --- ports ---
    ports: list[PortDef] = []
    for p in data.get("ports", []):
        ports.append(PortDef(
            port=int(p.get("port", 0)),
            protocol=p.get("protocol", "UDP"),
            description=p.get("description", ""),
        ))

    # --- server settings ---
    settings: list[SettingDef] = []
    raw_settings = data.get("server_settings", [])
    # Support both the new list format and the old object format (ignored)
    if isinstance(raw_settings, list):
        for s in raw_settings:
            settings.append(SettingDef(
                key=s.get("key", ""),
                label=s.get("label", s.get("key", "")),
                type=s.get("type", "string"),
                default=s.get("default", ""),
                required=s.get("required", False),
                min_length=s.get("min_length", 0),
                max_length=s.get("max_length", 0),
                placeholder=s.get("placeholder", ""),
                help_url=s.get("help_url", ""),
                min=s.get("min", 0),
                max=s.get("max", 65535),
                options=s.get("options", []),
                worlds_path_windows=s.get("worlds_path_windows", ""),
                worlds_path_linux=s.get("worlds_path_linux", ""),
                tooltip=s.get("tooltip", ""),
            ))

    mod_raw = data.get("mod_support")
    mod_support = None
    if mod_raw:
        mod_support = ModSupport(
            framework=mod_raw.get("framework", ""),
            plugins_subdir=mod_raw.get("plugins_subdir", ""),
            bepinex_marker=mod_raw.get("bepinex_marker", ""),
            bepinex_download_url=mod_raw.get("bepinex_download_url", ""),
        )

    model = GameModel(
        id=game_id,
        name=data.get("display_name") or data.get("name", game_id),
        description=data.get("description", ""),
        genre=data.get("genre", ""),
        developer=data.get("developer", ""),
        platforms=data.get("platforms", []),
        image=data.get("image", ""),
        steam_app_id=server_info.get("app_id", ""),
        launch_mode=server_info.get("launch_mode", "steam"),
        server_dir_name=server_info.get("server_dir_name", ""),
        executable=server_info.get("executable", ""),
        executable_subdir=server_info.get("executable_subdir", ""),
        launch_args=server_info.get("launch_args", ""),
        process_names=server_info.get("process_names", []),
        default_port=int(server_info.get("default_port", 0)),
        ports=ports,
        server_settings=settings,
        mod_support=mod_support,
        max_players=int(multiplayer.get("max_players", 0)),
        min_players=int(multiplayer.get("min_players", 1)),
        extra_data=data,
    )
    return model


def load_all() -> List[GameModel]:
    """
    Scan the games/ directory and return a list of GameModels, sorted by name.
    Unknown or malformed JSON files are silently skipped.
    """
    if not _GAMES_DIR.exists():
        print(f"[GameRegistry] games directory not found: {_GAMES_DIR}")
        return []

    games: list[GameModel] = []
    for json_file in sorted(_GAMES_DIR.glob("*.json")):
        model = _load_game(json_file)
        if model:
            games.append(model)

    return games
