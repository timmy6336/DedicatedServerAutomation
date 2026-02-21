"""
UPnP port forwarding helpers.
Requires the 'miniupnpc' package; silently skips if not installed.
"""

from __future__ import annotations


def setup_port_forwarding(port: int, description: str = "Game Server") -> bool:
    """Add TCP+UDP UPnP mapping for the given port. Returns True on success."""
    try:
        import miniupnpc
        upnp = miniupnpc.UPnP()
        upnp.discoverdelay = 200
        upnp.discover()
        upnp.selectigd()
        local_ip = upnp.lanaddr
        upnp.addportmapping(port, "TCP", local_ip, port, description, "")
        upnp.addportmapping(port, "UDP", local_ip, port, description, "")
        print(f"[UPnP] Port {port} forwarded (TCP+UDP) to {local_ip}")
        return True
    except ImportError:
        print("[UPnP] miniupnpc not installed — skipping UPnP setup.")
        return False
    except Exception as exc:
        print(f"[UPnP] Port forwarding failed: {exc}")
        return False


def remove_port_forwarding(port: int) -> bool:
    """Remove TCP+UDP UPnP mappings for the given port."""
    try:
        import miniupnpc
        upnp = miniupnpc.UPnP()
        upnp.discoverdelay = 200
        upnp.discover()
        upnp.selectigd()
        removed = False
        for proto in ("TCP", "UDP"):
            try:
                result = upnp.deleteportmapping(port, proto, "")
                if result:
                    removed = True
            except Exception:
                pass
        return removed
    except ImportError:
        return False
    except Exception as exc:
        print(f"[UPnP] Failed to remove port forwarding: {exc}")
        return False


def setup_multiple(ports: list[int], description: str = "Game Server") -> None:
    """Attempt UPnP setup for each port in the list."""
    for port in ports:
        setup_port_forwarding(port, description)
