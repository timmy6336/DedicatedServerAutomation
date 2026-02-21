"""
Windows Firewall helpers using netsh.
Does nothing (and does not error) on non-Windows platforms.
"""

from __future__ import annotations
import platform
import subprocess


def _is_windows() -> bool:
    return platform.system().lower() == "windows"


def _run(cmd: str) -> bool:
    if not _is_windows():
        return True
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except Exception as exc:
        print(f"[Firewall] Command failed: {exc}")
        return False


def add_rule(name: str, port: int, protocol: str = "UDP") -> bool:
    """
    Add an inbound Windows Firewall rule for the given port.
    protocol — 'TCP', 'UDP', or 'TCP,UDP' / 'any'
    """
    proto_lower = protocol.lower()
    if proto_lower in ("tcp/udp", "tcp,udp", "any"):
        return (
            add_rule(name + " (TCP)", port, "TCP") and
            add_rule(name + " (UDP)", port, "UDP")
        )
    cmd = (
        f'netsh advfirewall firewall add rule '
        f'name="{name}" dir=in action=allow protocol={protocol} '
        f'localport={port}'
    )
    ok = _run(cmd)
    if ok:
        print(f"[Firewall] Added rule '{name}' port {port}/{protocol}")
    else:
        print(f"[Firewall] Failed to add rule '{name}' port {port}/{protocol}")
    return ok


def remove_rule(name: str) -> bool:
    cmd = f'netsh advfirewall firewall delete rule name="{name}"'
    return _run(cmd)


def add_rules_for_game(game_name: str, ports: list[dict]) -> None:
    """
    ports is a list of dicts: [{"port": 2456, "protocol": "UDP", "description": "..."}]
    """
    for p in ports:
        port = p.get("port", 0)
        proto = p.get("protocol", "UDP")
        desc = p.get("description", "")
        rule_name = f"{game_name} Server - {port} {desc}".strip()
        add_rule(rule_name, port, proto)
