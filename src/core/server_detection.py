"""
Server Detection — data-driven, no per-game if/elif chains.

All game-specific info (process names, ports) comes from the GameModel.
"""

from __future__ import annotations
import platform
import socket
import subprocess
import time
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

import psutil
import requests

if TYPE_CHECKING:
    from core.game_model import GameModel

# Public IP cache
_public_ip_cache: Optional[str] = None
_public_ip_cache_time: float = 0.0
_PUBLIC_IP_TTL = 300          # seconds
_NETWORK_TIMEOUT = 2          # seconds
_UNABLE = "Unable to determine"


@dataclass
class ServerStatus:
    is_running: bool = False
    local_ip: str = _UNABLE
    public_ip: str = _UNABLE
    port: int = 0
    connection_string: str = ""
    firewall_ok: bool = True


# ---------------------------------------------------------------------------
# IP helpers
# ---------------------------------------------------------------------------

def get_local_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return _UNABLE


def get_public_ip() -> str:
    global _public_ip_cache, _public_ip_cache_time
    now = time.time()
    if (_public_ip_cache and _public_ip_cache != _UNABLE
            and now - _public_ip_cache_time < _PUBLIC_IP_TTL):
        return _public_ip_cache

    for url in ("https://api.ipify.org", "https://ipinfo.io/ip"):
        try:
            r = requests.get(url, timeout=_NETWORK_TIMEOUT)
            if r.status_code == 200:
                ip = r.text.strip()
                _public_ip_cache = ip
                _public_ip_cache_time = now
                return ip
        except Exception:
            continue

    _public_ip_cache = _UNABLE
    _public_ip_cache_time = now
    return _UNABLE


# ---------------------------------------------------------------------------
# Process & port scanning
# ---------------------------------------------------------------------------

def _is_process_running(process_names: list[str]) -> bool:
    """Return True if any process in the list is currently running."""
    if not process_names:
        return False
    names_lower = {n.lower() for n in process_names}
    try:
        for proc in psutil.process_iter(attrs=["name"]):
            try:
                proc_name = (proc.info.get("name") or "").lower()
                if proc_name in names_lower:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    except Exception:
        pass
    return False


def _detect_active_port(candidate_ports: list[int]) -> int:
    """Return the first listening port from the candidate list, or 0."""
    if not candidate_ports:
        return 0
    try:
        listening = {
            conn.laddr.port
            for conn in psutil.net_connections(kind="inet")
            if conn.status == psutil.CONN_LISTEN and conn.laddr
        }
        for port in candidate_ports:
            if port in listening:
                return port
    except Exception:
        pass
    return 0


# ---------------------------------------------------------------------------
# Firewall rule check
# ---------------------------------------------------------------------------

def _check_firewall_rules(game: "GameModel") -> bool:
    """Return True if at least one expected firewall rule exists for this game."""
    if platform.system().lower() != "windows" or not game.ports:
        return True
    p = game.ports[0]
    rule_name = f"{game.name} Server - {p.port} {p.description}".strip()
    try:
        result = subprocess.run(
            f'netsh advfirewall firewall show rule name="{rule_name}"',
            shell=True, capture_output=True, text=True, timeout=5,
        )
        return "Rule Name:" in result.stdout
    except Exception:
        return True  # can't check — don't show a false warning


# ---------------------------------------------------------------------------
# Main public API
# ---------------------------------------------------------------------------

def get_status(game: "GameModel", skip_public_ip: bool = False) -> ServerStatus:
    """
    Return a ServerStatus for the given game.
    If skip_public_ip is True the public_ip field will be left as the
    'Unable to determine' sentinel (for fast, immediate UI refresh).
    """
    is_running = _is_process_running(game.process_names)
    local_ip = get_local_ip()
    public_ip = _UNABLE if skip_public_ip else get_public_ip()

    port = 0
    connection_string = ""
    firewall_ok = True

    if is_running:
        candidate_ports = [p.port for p in game.ports] if game.ports else [game.default_port]
        port = _detect_active_port(candidate_ports) or game.default_port
        if local_ip != _UNABLE:
            connection_string = f"{local_ip}:{port}"
        firewall_ok = _check_firewall_rules(game)

    return ServerStatus(
        is_running=is_running,
        local_ip=local_ip,
        public_ip=public_ip,
        port=port,
        connection_string=connection_string,
        firewall_ok=firewall_ok,
    )


def get_status_fast(game: "GameModel") -> ServerStatus:
    """Immediate status check without public IP lookup."""
    return get_status(game, skip_public_ip=True)
