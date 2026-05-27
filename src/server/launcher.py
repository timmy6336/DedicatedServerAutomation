"""
Launcher — starts and stops server processes.

Handles two launch modes:
  "steam"          — single process, args from game JSON launch_args template
  "dst_dual_shard" — two separate processes (Master + Caves) for DST
"""

from __future__ import annotations
import os
import platform
import subprocess
import tempfile
import time
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.game_model import GameModel


def start(game: "GameModel", config: dict) -> bool:
    """
    Launch the server for the given game using the saved config.
    Returns True if the launch command was issued without error.
    (Does not wait for the server to be fully ready.)
    """
    mode = game.launch_mode
    if mode == "dst_dual_shard":
        return _launch_dst(game, config)
    else:
        return _launch_steam(game, config)


def stop(game: "GameModel") -> bool:
    """
    Attempt to terminate any running server processes for this game.
    Returns True if at least one process was found and terminated.
    """
    import psutil
    names_lower = {n.lower() for n in game.process_names}
    killed = False
    try:
        for proc in psutil.process_iter(attrs=["name", "pid"]):
            try:
                if (proc.info.get("name") or "").lower() in names_lower:
                    proc.terminate()
                    killed = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as exc:
        print(f"[Launcher] Error stopping {game.name}: {exc}")
    return killed


# ---------------------------------------------------------------------------
# Steam launch (single process)
# ---------------------------------------------------------------------------

def _launch_steam(game: "GameModel", config: dict) -> bool:
    exe_path = game.get_executable_path()
    if not os.path.exists(exe_path):
        print(f"[Launcher] Executable not found: {exe_path}")
        return False

    work_dir = os.path.dirname(exe_path)
    args = game.build_launch_args(config)

    # On Windows we launch via a temp batch file so the server gets its own
    # console window and path quoting is handled cleanly.
    if platform.system().lower() == "windows":
        return _launch_via_batch(game.name, exe_path, work_dir, args)
    else:
        return _launch_direct(exe_path, work_dir, args)


def _launch_via_batch(title: str, exe_path: str, work_dir: str, args: list[str]) -> bool:
    cmd_parts = [f'"{exe_path}"'] + [f'"{a}"' if " " in a else a for a in args]
    cmd_line = " ".join(cmd_parts)

    # Strip characters that would break batch file structure (newlines, special chars)
    safe_title = "".join(c for c in title if c.isalnum() or c in " _-()")

    batch = f"""@echo off
title {safe_title} Dedicated Server
cd /d "{work_dir}"
echo Starting {safe_title} server...
{cmd_line}
"""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".bat", delete=False, encoding="utf-8"
        ) as f:
            f.write(batch)
            batch_path = f.name

        subprocess.Popen(["cmd", "/c", "start", f"{safe_title} Server", batch_path])
        print(f"[Launcher] Started {title} via batch: {batch_path}")
        return True
    except Exception as exc:
        print(f"[Launcher] Failed to launch {title}: {exc}")
        return False


def _launch_direct(exe_path: str, work_dir: str, args: list[str]) -> bool:
    try:
        cmd = [exe_path] + args
        subprocess.Popen(cmd, cwd=work_dir)
        print(f"[Launcher] Started: {' '.join(cmd)}")
        return True
    except Exception as exc:
        print(f"[Launcher] Direct launch failed: {exc}")
        return False


# ---------------------------------------------------------------------------
# DST dual-shard launch
# ---------------------------------------------------------------------------

def _launch_dst(game: "GameModel", config: dict) -> bool:
    """
    Launch Don't Starve Together in dual-shard mode:
      - Process 1: Master (overworld) on default_port
      - Process 2: Caves on default_port+1
    Both processes receive the cluster config from the saved config dict.
    """
    import os

    exe_path = game.get_executable_path()
    if not os.path.exists(exe_path):
        print(f"[Launcher] DST executable not found: {exe_path}")
        return False

    # Build and write Klei cluster config files first
    try:
        _write_dst_cluster_config(game, config)
    except Exception as exc:
        print(f"[Launcher] Failed to write DST config: {exc}")
        return False

    cluster_name = config.get("server_name", "DST Server")
    work_dir = os.path.dirname(exe_path)

    master_args = [
        "-console",
        "-cluster", "Cluster_1",
        "-shard", "Master",
    ]
    caves_args = [
        "-console",
        "-cluster", "Cluster_1",
        "-shard", "Caves",
    ]

    ok1 = (
        _launch_via_batch(f"{game.name} (Master)", exe_path, work_dir, master_args)
        if platform.system().lower() == "windows"
        else _launch_direct(exe_path, work_dir, master_args)
    )

    if ok1:
        # Brief delay so Master initialises before Caves starts
        time.sleep(5)
        ok2 = (
            _launch_via_batch(f"{game.name} (Caves)", exe_path, work_dir, caves_args)
            if platform.system().lower() == "windows"
            else _launch_direct(exe_path, work_dir, caves_args)
        )
        return ok2

    return False


def _write_dst_cluster_config(game: "GameModel", config: dict) -> None:
    """
    Write the cluster.ini and server.ini files that DST reads on startup.
    Files go into Documents/Klei/DoNotStarveTogether/<cluster_name>/
    """
    import platform as _platform
    if _platform.system().lower() == "windows":
        # Use the shell API so OneDrive-redirected Documents folders are resolved
        # correctly (e.g. C:\Users\X\OneDrive\Documents instead of C:\Users\X\Documents).
        try:
            import ctypes.wintypes
            CSIDL_PERSONAL = 5
            buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
            ctypes.windll.shell32.SHGetFolderPathW(0, CSIDL_PERSONAL, 0, 0, buf)
            docs = buf.value
        except Exception:
            docs = os.path.join(os.path.expandvars("%USERPROFILE%"), "Documents")
    else:
        docs = os.path.expanduser("~/Documents")

    cluster_name = config.get("server_name", "DST Server")
    # DST always reads from the fixed "Cluster_1" directory; cluster_name is
    # only used as the display name inside cluster.ini, not as the folder name.
    cluster_dir = os.path.join(docs, "Klei", "DoNotStarveTogether", "Cluster_1")
    master_dir = os.path.join(cluster_dir, "Master")
    caves_dir = os.path.join(cluster_dir, "Caves")

    os.makedirs(master_dir, exist_ok=True)
    os.makedirs(caves_dir, exist_ok=True)

    # cluster.ini
    cluster_ini = f"""[GAMEPLAY]
game_mode = {config.get("game_mode", "survival")}
max_players = {config.get("max_players", 6)}
pvp = {str(config.get("pvp", False)).lower()}
pause_when_empty = {str(config.get("pause_when_empty", True)).lower()}

[NETWORK]
cluster_name = {cluster_name}
cluster_description = {config.get("server_description", "")}
cluster_password = {config.get("password", "")}
cluster_intention = cooperative

[MISC]
console_enabled = true

[SHARD]
shard_enabled = true
bind_ip = 127.0.0.1
master_ip = 127.0.0.1
master_port = 10888
cluster_key = dst_cluster_key
"""
    with open(os.path.join(cluster_dir, "cluster.ini"), "w", encoding="utf-8") as f:
        f.write(cluster_ini)

    # cluster_token.txt — strip whitespace; DST requires a clean token + newline
    token = config.get("server_token", "").strip()
    token_path = os.path.join(cluster_dir, "cluster_token.txt")
    with open(token_path, "w", encoding="ascii", errors="replace", newline="\n") as f:
        f.write(token + "\n")
    print(f"[Launcher] Token written ({len(token)} chars) to: {token_path}")

    # Master/server.ini
    master_port = config.get("port", game.default_port)
    master_server_ini = f"""[NETWORK]
server_port = {master_port}

[SHARD]
is_master = true
"""
    with open(os.path.join(master_dir, "server.ini"), "w", encoding="utf-8") as f:
        f.write(master_server_ini)

    # Caves/server.ini
    caves_port = master_port + 1
    caves_server_ini = f"""[NETWORK]
server_port = {caves_port}

[SHARD]
is_master = false
name = Caves
"""
    with open(os.path.join(caves_dir, "server.ini"), "w", encoding="utf-8") as f:
        f.write(caves_server_ini)

    print(f"[Launcher] DST cluster config written to: {cluster_dir}")
