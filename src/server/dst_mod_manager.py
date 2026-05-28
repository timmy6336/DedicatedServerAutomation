"""
DST Workshop mod manager — Steam Workshop integration for Don't Starve Together.

DST uses two files to manage mods:
  1. <install_dir>/mods/dedicated_server_mods_setup.lua  — which mods to download
  2. <cluster_dir>/<shard>/modoverrides.lua               — enable/config per shard

This module reads and writes both files, and can fetch mod metadata from the
Steam Web API (no API key required for GetPublishedFileDetails).
"""

from __future__ import annotations
import json
import os
import platform
import re
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from core.game_model import GameModel

DST_WORKSHOP_APPID = "322330"

_DETAILS_URL = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
_QUERY_URL = "https://api.steampowered.com/IPublishedFileService/QueryFiles/v1/"


# ── Paths ──────────────────────────────────────────────────────────────────────

def get_cluster_dir() -> str:
    """Absolute path to the Cluster_1 directory in the Klei save folder."""
    if platform.system().lower() == "windows":
        try:
            import ctypes
            import ctypes.wintypes
            CSIDL_PERSONAL = 5
            buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
            ctypes.windll.shell32.SHGetFolderPathW(0, CSIDL_PERSONAL, 0, 0, buf)
            docs = buf.value
        except Exception:
            docs = os.path.join(os.path.expandvars("%USERPROFILE%"), "Documents")
    else:
        docs = os.path.expanduser("~/Documents")
    return os.path.join(docs, "Klei", "DoNotStarveTogether", "Cluster_1")


def get_mods_setup_path(game: "GameModel") -> str:
    """Path to dedicated_server_mods_setup.lua inside the server installation."""
    return os.path.join(game.get_install_path(), "mods", "dedicated_server_mods_setup.lua")


def get_downloaded_mod_dir(game: "GameModel", workshop_id: str) -> str:
    """Path where DST downloads a workshop mod: <install>/mods/workshop-<id>/."""
    return os.path.join(game.get_install_path(), "mods", f"workshop-{workshop_id}")


# ── Mod Setup file ─────────────────────────────────────────────────────────────

def load_installed_workshop_ids(game: "GameModel") -> list[str]:
    """Parse dedicated_server_mods_setup.lua and return the list of workshop IDs."""
    path = get_mods_setup_path(game)
    if not os.path.exists(path):
        return []
    ids: list[str] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                m = re.search(r'ServerModSetup\(\s*"(\d+)"\s*\)', line)
                if m:
                    ids.append(m.group(1))
    except OSError:
        pass
    return ids


def save_mods_setup(game: "GameModel", workshop_ids: list[str]) -> None:
    """Write dedicated_server_mods_setup.lua with the given workshop IDs."""
    path = get_mods_setup_path(game)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("-- Managed by DedicatedServerAutomation --\n")
        for wid in workshop_ids:
            f.write(f'ServerModSetup("{wid}")\n')


# ── Mod Overrides ──────────────────────────────────────────────────────────────

def load_mod_overrides(game: "GameModel") -> dict:
    """
    Parse Master/modoverrides.lua.
    Returns {workshop_id: {"enabled": bool, "config": {key: value}}} dict.
    """
    cluster_dir = get_cluster_dir()
    path = os.path.join(cluster_dir, "Master", "modoverrides.lua")
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return _parse_modoverrides(f.read())
    except Exception as exc:
        print(f"[DSTModManager] Failed to parse modoverrides.lua: {exc}")
        return {}


def save_mod_overrides(game: "GameModel", overrides: dict) -> None:
    """Write modoverrides.lua to both Master and Caves shards."""
    cluster_dir = get_cluster_dir()
    content = _format_modoverrides(overrides)
    for shard in ("Master", "Caves"):
        shard_dir = os.path.join(cluster_dir, shard)
        os.makedirs(shard_dir, exist_ok=True)
        path = os.path.join(shard_dir, "modoverrides.lua")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)


# ── High-level mod operations ──────────────────────────────────────────────────

def add_mod(game: "GameModel", workshop_id: str) -> bool:
    """
    Add a workshop ID to setup.lua and enable it in modoverrides.lua.
    Returns False if already present, True if newly added.
    """
    ids = load_installed_workshop_ids(game)
    if workshop_id in ids:
        return False
    ids.append(workshop_id)
    save_mods_setup(game, ids)
    overrides = load_mod_overrides(game)
    if workshop_id not in overrides:
        overrides[workshop_id] = {"enabled": True, "config": {}}
        save_mod_overrides(game, overrides)
    return True


def remove_mod(game: "GameModel", workshop_id: str) -> None:
    """Remove a mod from both setup.lua and modoverrides.lua."""
    ids = [i for i in load_installed_workshop_ids(game) if i != workshop_id]
    save_mods_setup(game, ids)
    overrides = load_mod_overrides(game)
    overrides.pop(workshop_id, None)
    save_mod_overrides(game, overrides)


def toggle_mod(game: "GameModel", workshop_id: str, enabled: bool) -> None:
    """Enable or disable a mod in modoverrides.lua."""
    overrides = load_mod_overrides(game)
    entry = overrides.get(workshop_id, {"enabled": True, "config": {}})
    entry["enabled"] = enabled
    overrides[workshop_id] = entry
    save_mod_overrides(game, overrides)


def set_mod_config(game: "GameModel", workshop_id: str, config: dict) -> None:
    """Update the configuration_options for a mod in modoverrides.lua."""
    overrides = load_mod_overrides(game)
    entry = overrides.get(workshop_id, {"enabled": True, "config": {}})
    entry["config"] = config
    overrides[workshop_id] = entry
    save_mod_overrides(game, overrides)


# ── Steam Workshop API ─────────────────────────────────────────────────────────

def get_workshop_details(workshop_ids: list[str]) -> list[dict]:
    """
    Fetch mod metadata from the Steam API for a batch of workshop IDs.
    Uses ISteamRemoteStorage/GetPublishedFileDetails — no API key required.
    Returns list of dicts: {workshop_id, title, description, preview_url, author, subscriptions}.
    """
    if not workshop_ids:
        return []
    try:
        import urllib.parse
        import urllib.request

        params: dict[str, str] = {"itemcount": str(len(workshop_ids))}
        for i, wid in enumerate(workshop_ids):
            params[f"publishedfileids[{i}]"] = wid
        data = urllib.parse.urlencode(params).encode("utf-8")
        req = urllib.request.Request(
            _DETAILS_URL,
            data=data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "DedicatedServerAutomation/1.0",
            },
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            payload = json.loads(resp.read().decode("utf-8"))

        results = []
        for item in payload.get("response", {}).get("publishedfiledetails", []):
            if item.get("result", 1) != 1:
                continue
            results.append({
                "workshop_id": item.get("publishedfileid", ""),
                "title": item.get("title", f"Mod {item.get('publishedfileid', '')}"),
                "description": item.get("description", ""),
                "preview_url": item.get("preview_url", ""),
                "author": item.get("creator", ""),
                "subscriptions": item.get("subscriptions", 0),
            })
        return results
    except Exception as exc:
        print(f"[DSTModManager] get_workshop_details failed: {exc}")
        return []


def search_workshop(query: str = "", page: int = 1, per_page: int = 20) -> list[dict]:
    """
    Browse/search Steam Workshop for DST mods (appid 322330).

    - query="" (default): returns the most-subscribed (popular) mods, great for
      an initial "discover" view when the widget first opens.
    - query="text": full-text search ranked by relevance.
    - page/per_page: used to implement pagination ("Load More").

    Returns a list of mod dicts on success, empty list on failure.
    The Steam API accepts an empty key for public workshop browsing.
    """
    try:
        import urllib.parse
        import urllib.request

        trimmed = query.strip()
        params: dict[str, str] = {
            "key": "",
            "appid": DST_WORKSHOP_APPID,
            # query_type 0 = ranked by vote/relevance (good for text search)
            # query_type 12 = ranked by total unique subscriptions (popular)
            "query_type": "0" if trimmed else "12",
            "numperpage": str(per_page),
            "page": str(page),
            "return_metadata": "1",
            "return_short_description": "1",
            "return_previews": "1",
            "return_children": "0",
            "return_tags": "0",
        }
        if trimmed:
            params["search_text"] = trimmed

        url = _QUERY_URL + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"User-Agent": "DedicatedServerAutomation/1.0"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            payload = json.loads(resp.read().decode("utf-8"))

        items = []
        for item in payload.get("response", {}).get("publishedfiledetails", []):
            items.append({
                "workshop_id": item.get("publishedfileid", ""),
                "title": item.get("title", ""),
                "description": item.get("short_description", item.get("description", "")),
                "preview_url": item.get("preview_url", ""),
                "author": item.get("creator", ""),
                "subscriptions": item.get("subscriptions", 0),
            })
        return items
    except Exception as exc:
        print(f"[DSTModManager] search_workshop failed: {exc}")
        return []


def extract_workshop_id(url_or_id: str) -> str | None:
    """
    Extract a numeric workshop ID from a URL or bare numeric string.
    Accepts:
      https://steamcommunity.com/sharedfiles/filedetails/?id=378160973
      steam://openurl/...?id=378160973
      378160973
    """
    text = url_or_id.strip()
    m = re.search(r"[?&]id=(\d+)", text)
    if m:
        return m.group(1)
    if re.fullmatch(r"\d+", text):
        return text
    return None


# ── modinfo.lua parsing ────────────────────────────────────────────────────────

def parse_mod_config_options(game: "GameModel", workshop_id: str) -> list[dict]:
    """
    Parse modinfo.lua from the downloaded mod directory to discover configurable options.

    DST downloads mods to <install>/mods/workshop-<id>/ when the server runs.
    If the mod hasn't been downloaded yet, returns an empty list.

    Each returned option dict: {name, label, hover, type, options, default}
      type: "choice" | "bool" | "number" | "string"
      options (for "choice"): [{description, data}, ...]
    """
    modinfo_path = os.path.join(
        get_downloaded_mod_dir(game, workshop_id), "modinfo.lua"
    )
    if not os.path.exists(modinfo_path):
        return []
    try:
        with open(modinfo_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        return _parse_modinfo_config_options(content)
    except Exception as exc:
        print(f"[DSTModManager] Failed to parse modinfo.lua for {workshop_id}: {exc}")
        return []


# ── Lua file formatting ────────────────────────────────────────────────────────

def _format_modoverrides(overrides: dict) -> str:
    lines = ["return {\n"]
    for wid, entry in overrides.items():
        enabled_str = "true" if entry.get("enabled", True) else "false"
        config = entry.get("config", {})
        cfg_parts = [f"    {k} = {_lua_literal(v)}," for k, v in config.items()]
        cfg_inner = ("\n" + "\n".join(cfg_parts) + "\n  ") if cfg_parts else ""
        lines.append(
            f'  ["workshop-{wid}"] = '
            f'{{ enabled={enabled_str}, configuration_options={{{cfg_inner}}}}},\n'
        )
    lines.append("}\n")
    return "".join(lines)


def _lua_literal(v: Any) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str):
        return f'"{v}"'
    return str(v)


# ── Lua parsers ────────────────────────────────────────────────────────────────

def _parse_modoverrides(content: str) -> dict:
    """Parse the return { ... } block from modoverrides.lua."""
    result: dict = {}
    pattern = re.compile(r'\["workshop-(\d+)"\]\s*=\s*\{')
    for m in pattern.finditer(content):
        wid = m.group(1)
        block, _ = _balanced(content, m.end() - 1)
        if block is None:
            continue
        enabled = True
        em = re.search(r"\benabled\s*=\s*(true|false)", block)
        if em:
            enabled = em.group(1) == "true"
        config: dict = {}
        co_m = re.search(r"\bconfiguration_options\s*=\s*\{", block)
        if co_m:
            co_block, _ = _balanced(block, co_m.end() - 1)
            if co_block:
                config = _parse_flat_table(co_block)
        result[wid] = {"enabled": enabled, "config": config}
    return result


def _parse_modinfo_config_options(content: str) -> list[dict]:
    """Extract configuration_options list from modinfo.lua content."""
    m = re.search(r"\bconfiguration_options\s*=\s*\{", content)
    if not m:
        return []
    block, _ = _balanced(content, m.end() - 1)
    if block is None:
        return []
    options = []
    i = 0
    while i < len(block):
        if block[i] == "{":
            entry, end = _balanced(block, i)
            if entry is not None:
                opt = _parse_option_entry(entry)
                if opt:
                    options.append(opt)
                i = end + 1
            else:
                i += 1
        else:
            i += 1
    return options


def _parse_option_entry(content: str) -> dict | None:
    """Parse one configuration option block from modinfo.lua."""
    name = _lua_str(content, "name")
    if not name:
        return None
    label = _lua_str(content, "label") or name
    hover = _lua_str(content, "hover") or ""

    # Parse the options list (choice values)
    choices: list[dict] = []
    opts_m = re.search(r"\boptions\s*=\s*\{", content)
    if opts_m:
        opts_block, _ = _balanced(content, opts_m.end() - 1)
        if opts_block:
            j = 0
            while j < len(opts_block):
                if opts_block[j] == "{":
                    item, end = _balanced(opts_block, j)
                    if item is not None:
                        desc = _lua_str(item, "description") or ""
                        data = _lua_any(item, "data")
                        if desc:
                            choices.append({"description": desc, "data": data})
                        j = end + 1
                    else:
                        j += 1
                else:
                    j += 1

    # Parse default value
    default = _lua_any(content, "default")

    # Infer type
    if choices:
        opt_type = "choice"
    elif isinstance(default, bool):
        opt_type = "bool"
    elif isinstance(default, (int, float)):
        opt_type = "number"
    else:
        opt_type = "string"

    return {
        "name": name,
        "label": label,
        "hover": hover,
        "type": opt_type,
        "options": choices,
        "default": default,
    }


def _parse_flat_table(content: str) -> dict:
    """Parse a flat key=value Lua table body into a Python dict."""
    result: dict = {}
    for m in re.finditer(r"\b(\w+)\s*=\s*", content):
        key = m.group(1)
        rest = content[m.end():].lstrip()
        if not rest:
            continue
        val = _read_lua_value(rest)
        if val is not None:
            result[key] = val
    return result


def _read_lua_value(text: str) -> Any:
    """Read one Lua value from the start of text."""
    if text.startswith('"'):
        end = text.find('"', 1)
        return text[1:end] if end > 0 else None
    if text.startswith("'"):
        end = text.find("'", 1)
        return text[1:end] if end > 0 else None
    if text.startswith("true"):
        return True
    if text.startswith("false"):
        return False
    m = re.match(r"-?[\d.]+", text)
    if m:
        v = m.group(0)
        try:
            return int(v)
        except ValueError:
            return float(v)
    return None


def _lua_any(content: str, key: str) -> Any:
    """Extract any Lua value assigned to key."""
    m = re.search(rf"\b{re.escape(key)}\s*=\s*", content)
    if not m:
        return None
    return _read_lua_value(content[m.end():].lstrip())


def _lua_str(content: str, key: str) -> str | None:
    m = re.search(rf'\b{re.escape(key)}\s*=\s*"([^"]*)"', content)
    if m:
        return m.group(1)
    m = re.search(rf"\b{re.escape(key)}\s*=\s*'([^']*)'", content)
    if m:
        return m.group(1)
    m = re.search(rf"\b{re.escape(key)}\s*=\s*\[\[([^\]]*)\]\]", content, re.DOTALL)
    if m:
        return m.group(1)
    return None


def _balanced(text: str, start: int) -> tuple[str | None, int]:
    """
    Starting at text[start] (must be '{'), find the matching closing '}'.
    Returns (inner_content, closing_brace_index) or (None, -1).
    Handles nested braces and string literals.
    """
    if start >= len(text) or text[start] != "{":
        return None, -1
    depth = 0
    in_single = in_double = in_long = False
    i = start
    while i < len(text):
        c = text[i]
        if in_long:
            if text[i : i + 2] == "]]":
                in_long = False
                i += 2
                continue
        elif in_single:
            if c == "'" and (i == 0 or text[i - 1] != "\\"):
                in_single = False
        elif in_double:
            if c == '"' and (i == 0 or text[i - 1] != "\\"):
                in_double = False
        else:
            if text[i : i + 2] == "[[":
                in_long = True
                i += 2
                continue
            elif c == "'":
                in_single = True
            elif c == '"':
                in_double = True
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    return text[start + 1 : i], i
        i += 1
    return None, -1
