"""
ServerManager — high-level orchestrator for the server lifecycle.

Provides a single, game-agnostic API:
    install(game, progress_cb, status_cb) -> bool
    start(game, config) -> bool
    stop(game) -> bool
    uninstall(game) -> bool
    is_installed(game) -> bool

No per-game if/elif chains here — all game-specific data comes from GameModel.
"""

from __future__ import annotations
import shutil
from typing import Callable, Optional, TYPE_CHECKING

from server import steamcmd, launcher, upnp, firewall

if TYPE_CHECKING:
    from core.game_model import GameModel

ProgressCB = Optional[Callable[[int], None]]
StatusCB   = Optional[Callable[[str], None]]


def install(
    game: "GameModel",
    progress: ProgressCB = None,
    status: StatusCB = None,
) -> bool:
    """
    Full install pipeline:
      1. Download SteamCMD (if needed)
      2. Install/update the server
      3. Configure firewall (if the game config asks for it — checked by caller)
      4. Set up UPnP (likewise)
    Returns True on success.
    """
    def p(v: int):
        if progress:
            progress(v)

    def s(msg: str):
        if status:
            status(msg)

    # Phase 1: SteamCMD (0 → 40)
    s("Step 1/2 — Downloading SteamCMD...")
    ok = steamcmd.download(
        progress=lambda v: p(int(v * 0.4)),
        status=status,
    )
    if not ok:
        s("SteamCMD download failed.")
        return False

    p(40)

    # Phase 2: Server files (40 → 100)
    s(f"Step 2/2 — Installing {game.name} server...")
    ok = steamcmd.install_server(
        app_id=game.steam_app_id,
        server_dir=game.get_install_path(),
        executable_name=game.executable,
        executable_subdir=game.executable_subdir,
        progress=lambda v: p(40 + int(v * 0.6)),
        status=status,
    )
    if not ok:
        s(f"{game.name} installation failed.")
        return False

    p(100)
    s(f"{game.name} server installed successfully!")
    return True


def start(game: "GameModel", config: dict) -> bool:
    """Launch the server. Returns True if the process was started."""
    # Optional: configure firewall / UPnP from config flags
    if config.get("configure_firewall"):
        ports_raw = [
            {"port": p.port, "protocol": p.protocol, "description": p.description}
            for p in game.ports
        ]
        firewall.add_rules_for_game(game.name, ports_raw)

    if config.get("enable_upnp"):
        upnp.setup_multiple([p.port for p in game.ports], f"{game.name} Server")

    return launcher.start(game, config)


def close_ports(game: "GameModel", config: dict) -> None:
    """Remove firewall rules and UPnP mappings for this game."""
    ports_raw = [
        {"port": p.port, "protocol": p.protocol, "description": p.description}
        for p in game.ports
    ]
    if config.get("configure_firewall"):
        firewall.remove_rules_for_game(game.name, ports_raw)
    if config.get("enable_upnp"):
        upnp.remove_multiple([p.port for p in game.ports])


def stop(game: "GameModel", config: dict | None = None) -> bool:
    """Terminate all server processes for this game and close ports."""
    killed = launcher.stop(game)
    if config:
        close_ports(game, config)
    return killed


def uninstall(game: "GameModel") -> bool:
    """Remove the server installation directory."""
    server_dir = game.get_install_path()
    import os
    if not os.path.exists(server_dir):
        return True
    try:
        shutil.rmtree(server_dir)
        print(f"[ServerManager] Uninstalled {game.name} from {server_dir}")
        return True
    except Exception as exc:
        print(f"[ServerManager] Failed to uninstall {game.name}: {exc}")
        return False


def is_installed(game: "GameModel") -> bool:
    return game.is_installed()
