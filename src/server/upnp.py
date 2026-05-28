"""
UPnP port forwarding helpers.
Requires the 'miniupnpc' package; silently skips if not installed.

Lease duration is set to 0 (permanent) but many routers ignore this and
expire mappings after 30–60 min anyway. A background renewal thread
re-registers the mappings every RENEWAL_INTERVAL seconds to keep them alive.
"""

from __future__ import annotations
import threading

RENEWAL_INTERVAL = 1500  # 25 minutes — safely under most router TTLs

_renewal_thread: threading.Thread | None = None
_stop_event = threading.Event()
_renewal_lock = threading.Lock()


def setup_port_forwarding(port: int, description: str = "Game Server") -> bool:
    """Add TCP+UDP UPnP mapping for the given port. Returns True on success."""
    try:
        import miniupnpc
        upnp = miniupnpc.UPnP()
        upnp.discoverdelay = 200
        upnp.discover()
        upnp.selectigd()
        local_ip = upnp.lanaddr
        upnp.addportmapping(port, "TCP", local_ip, port, description, 0)
        upnp.addportmapping(port, "UDP", local_ip, port, description, 0)
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
    """Add UPnP mappings for each port and start the renewal thread."""
    for port in ports:
        setup_port_forwarding(port, description)
    _start_renewal(ports, description)


def remove_multiple(ports: list[int]) -> None:
    """Stop the renewal thread and remove UPnP mappings for each port."""
    _stop_renewal()
    for port in ports:
        remove_port_forwarding(port)


# ---------------------------------------------------------------------------
# Renewal thread — keeps mappings alive on routers that expire them
# ---------------------------------------------------------------------------

def _start_renewal(ports: list[int], description: str) -> None:
    global _renewal_thread
    with _renewal_lock:
        _stop_renewal()
        _stop_event.clear()

        def _loop():
            while not _stop_event.wait(RENEWAL_INTERVAL):
                print(f"[UPnP] Renewing {len(ports)} port mapping(s)...")
                for port in ports:
                    setup_port_forwarding(port, description)

        _renewal_thread = threading.Thread(target=_loop, daemon=True, name="upnp-renewal")
        _renewal_thread.start()
        print(f"[UPnP] Renewal thread started (interval: {RENEWAL_INTERVAL}s)")


def _stop_renewal() -> None:
    global _renewal_thread
    _stop_event.set()
    if _renewal_thread and _renewal_thread.is_alive():
        _renewal_thread.join(timeout=5)
    _renewal_thread = None
