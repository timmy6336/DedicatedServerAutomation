"""
ConfigManager — stores and retrieves per-game server configuration.

Storage location:
  Windows : %LOCALAPPDATA%/DedicatedServerAutomation/server_configs.json
  Unix    : ~/.config/DedicatedServerAutomation/server_configs.json

Each game's config is a flat dict keyed by the setting's `key` field from
the game JSON, e.g. {"server_name": "My Server", "password": "abc", ...}.
"""

from __future__ import annotations
import json
import os
import platform
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigManager:
    def __init__(self):
        self._config_dir = self._resolve_dir()
        self._config_dir.mkdir(parents=True, exist_ok=True)
        self._config_file = self._config_dir / "server_configs.json"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save(self, game_id: str, config: Dict[str, Any]) -> bool:
        """Persist config for one game, preserving all other games' configs."""
        try:
            all_configs = self._load_file()
            all_configs[game_id] = config
            with open(self._config_file, "w", encoding="utf-8") as f:
                json.dump(all_configs, f, indent=2)
            return True
        except Exception as exc:
            print(f"[ConfigManager] Failed to save {game_id}: {exc}")
            return False

    def load(self, game_id: str) -> Optional[Dict[str, Any]]:
        """Return saved config dict, or None if no config exists for this game."""
        try:
            return self._load_file().get(game_id)
        except Exception as exc:
            print(f"[ConfigManager] Failed to load {game_id}: {exc}")
            return None

    def delete(self, game_id: str) -> bool:
        """Remove a game's config entry."""
        try:
            all_configs = self._load_file()
            if game_id not in all_configs:
                return False
            del all_configs[game_id]
            with open(self._config_file, "w", encoding="utf-8") as f:
                json.dump(all_configs, f, indent=2)
            return True
        except Exception as exc:
            print(f"[ConfigManager] Failed to delete {game_id}: {exc}")
            return False

    def load_all(self) -> Dict[str, Dict[str, Any]]:
        return self._load_file()

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _load_file(self) -> Dict[str, Dict[str, Any]]:
        if not self._config_file.exists():
            return {}
        try:
            with open(self._config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    @staticmethod
    def _resolve_dir() -> Path:
        if platform.system().lower() == "windows":
            base = os.environ.get("LOCALAPPDATA", str(Path.home()))
        else:
            base = str(Path.home() / ".config")
        return Path(base) / "DedicatedServerAutomation"


# Singleton
config_manager = ConfigManager()
