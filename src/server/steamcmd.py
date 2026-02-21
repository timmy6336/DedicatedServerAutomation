"""
SteamCMD — download, install, and invoke SteamCMD for server installs.

All progress is reported via optional callbacks:
    progress_callback(int)   — 0-100
    status_callback(str)     — human-readable status line
"""

from __future__ import annotations
import os
import platform
import shutil
import subprocess
import time
import urllib.request
import zipfile
from typing import Callable, Optional, Tuple


_STEAMCMD_URL = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip"

ProgressCB = Optional[Callable[[int], None]]
StatusCB   = Optional[Callable[[str], None]]


def _paths() -> Tuple[str, str]:
    """Return (steamcmd_dir, steamcmd_exe)."""
    if platform.system().lower() == "windows":
        d = os.path.expandvars(r"%USERPROFILE%\SteamCMD")
        return d, os.path.join(d, "steamcmd.exe")
    else:
        d = os.path.expanduser("~/SteamCMD")
        return d, os.path.join(d, "steamcmd.sh")


def is_installed() -> bool:
    _, exe = _paths()
    return os.path.exists(exe)


def download(progress: ProgressCB = None, status: StatusCB = None) -> bool:
    """Download and extract SteamCMD if not already present. Returns True on success."""
    def p(v: int):
        if progress:
            progress(v)

    def s(msg: str):
        if status:
            status(msg)
        print(msg)

    p(10)
    s("Checking SteamCMD installation...")
    steamcmd_dir, steamcmd_exe = _paths()
    os.makedirs(steamcmd_dir, exist_ok=True)

    if os.path.exists(steamcmd_exe):
        s("SteamCMD already installed — skipping download.")
        p(100)
        return True

    zip_path = os.path.join(steamcmd_dir, "steamcmd.zip")
    s("Downloading SteamCMD...")
    p(20)

    def _hook(block_num, block_size, total_size):
        if progress and total_size > 0:
            pct = min(int((block_num * block_size / total_size) * 60) + 20, 80)
            progress(pct)

    try:
        urllib.request.urlretrieve(_STEAMCMD_URL, zip_path, reporthook=_hook)
        s("Extracting SteamCMD...")
        p(85)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(steamcmd_dir)
        os.remove(zip_path)
        s("SteamCMD ready.")
        p(100)
        return True
    except Exception as exc:
        s(f"Failed to download SteamCMD: {exc}")
        return False


def install_server(
    app_id: str,
    server_dir: str,
    executable_name: str,
    executable_subdir: str = "",
    progress: ProgressCB = None,
    status: StatusCB = None,
) -> bool:
    """
    Run SteamCMD to install or update a server.

    executable_subdir — if non-empty, the exe lives at server_dir/executable_subdir/executable_name
                        (e.g. 'bin' for DST).
    """
    def p(v: int):
        if progress:
            progress(v)

    def s(msg: str):
        if status:
            status(msg)
        print(msg)

    p(10)
    s("Checking server installation...")

    exe_path = (
        os.path.join(server_dir, executable_subdir, executable_name)
        if executable_subdir
        else os.path.join(server_dir, executable_name)
    )

    if os.path.exists(exe_path):
        s("Server already installed — skipping.")
        p(100)
        return True

    _, steamcmd_exe = _paths()
    if not os.path.exists(steamcmd_exe):
        s("SteamCMD not found. Please install SteamCMD first.")
        return False

    os.makedirs(server_dir, exist_ok=True)

    cmd = [
        steamcmd_exe,
        "+force_install_dir", server_dir,
        "+login", "anonymous",
        "+app_update", app_id, "validate",
        "+quit",
    ]

    s("Starting SteamCMD download...")
    p(30)

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=0,
            shell=True,
        )

        progress_val = 30.0
        last_update_time = time.time()
        lines_seen = 0
        recent_lines: list[str] = []

        while True:
            if process.poll() is not None:
                remaining = process.stdout.read()
                if remaining:
                    for ln in remaining.strip().split("\n"):
                        if ln.strip():
                            progress_val = _parse_line(ln.strip(), progress_val, status)
                break

            line = process.stdout.readline()
            if line:
                line = line.strip()
                if line:
                    lines_seen += 1
                    recent_lines.append(line)
                    if len(recent_lines) > 20:
                        recent_lines.pop(0)

                    progress_val = _parse_line(line, progress_val, status)

                    if lines_seen % 5 == 0:
                        progress_val = min(progress_val + 0.5, 89)

                    if progress:
                        progress(int(progress_val))
            else:
                now = time.time()
                if now - last_update_time >= 5:
                    if lines_seen > 20 and progress_val < 85:
                        progress_val = min(progress_val + 0.5, 89)
                    if progress:
                        progress(int(progress_val))
                    if status and lines_seen > 20:
                        status("Installation in progress...")
                    last_update_time = now

        # Verify by checking if executable now exists
        if os.path.exists(exe_path):
            s("Server installed successfully!")
            p(100)
            return True
        else:
            rc = process.poll()
            s(f"Installation incomplete — executable not found (exit code: {rc})")
            if any("Error! App" in ln for ln in recent_lines):
                s("Tip: Steam sometimes fails transiently — try again.")
            return False

    except Exception as exc:
        s(f"Error during installation: {exc}")
        return False


def uninstall_steamcmd() -> bool:
    d, _ = _paths()
    if os.path.exists(d):
        try:
            shutil.rmtree(d)
            return True
        except Exception as exc:
            print(f"[SteamCMD] Failed to remove: {exc}")
            return False
    return False


# ---------------------------------------------------------------------------
# Internal — parse SteamCMD output for meaningful status/progress
# ---------------------------------------------------------------------------

def _parse_line(line: str, progress_val: float, status: StatusCB) -> float:
    def s(msg: str):
        if status:
            status(msg)

    if "Error!" in line and "state is 0x" in line:
        s(f"Steam error: {line}")
        return progress_val
    if "stopping" in line and "progress:" in line:
        s(f"Download interrupted: {line}")
        return progress_val

    if "Downloading" in line or "downloading" in line:
        s(f"Downloading: {line}")
        return min(progress_val + 2, 85)
    if "Verifying" in line or "verifying" in line:
        s(f"Verifying: {line}")
        return min(progress_val + 1, 90)
    if "Success" in line or "fully installed" in line or "Up-To-Date" in line:
        s("Download completed successfully.")
        return 95
    if "Logged in OK" in line:
        s("Logged into Steam.")
        return min(progress_val + 5, 50)
    if "preallocating" in line:
        s("Allocating disk space...")
        return min(progress_val + 1, 85)
    if "Update state" in line:
        if "0x61" in line:
            s("Downloading...")
            return min(progress_val + 1, 80)
        if "0x101" in line:
            s("Committing changes...")
            return min(progress_val + 2, 88)
        s(line)
        return progress_val
    if "%" in line and ("downloaded" in line or "progress" in line):
        import re
        m = re.search(r"(\d+)%", line)
        if m:
            pct = int(m.group(1))
            adjusted = min(30 + int(pct * 0.6), 90)
            s(f"Downloading: {pct}%")
            return float(adjusted)

    if line and not line.startswith("Steam>") and len(line) > 3:
        return min(progress_val + 0.2, 90)

    return progress_val
