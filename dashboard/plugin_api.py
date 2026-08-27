"""Hermes GitHub plugin — backend API routes.

Mounted at ``/api/plugins/hermes-github/`` by the dashboard plugin system
(``dashboard/manifest.json`` -> ``api: plugin_api.py``).

Two jobs:

1. **Token auto-detect.** The GitHub token is resolved on the server, never
   in the renderer, via an ordered ladder:

   a. ``GITHUB_TOKEN`` / ``GH_TOKEN`` / ``GITHUB_PAT`` / ``GH_PAT`` in the
      process environment
   b. ``gh auth token`` (the gh CLI the user is logged into)
   c. the same variable names in ``$HERMES_HOME/.env`` (or ``~/.hermes/.env``)

   The token itself is never returned by any endpoint — the renderer only
   learns ``{token: bool, source, login}``. A token the user types manually
   in the plugin UI stays in the renderer and is passed per-request in the
   search body as an explicit override (server prefers it, then falls back
   to the ladder).

2. **Search proxy.** GitHub REST calls go through ``/search`` so the token
   never touches plugin storage or the renderer.

Security notes: routes ride the dashboard's session-token auth middleware;
the plugin is a ``user`` plugin so its backend only mounts when the plugin
is in ``plugins.enabled`` (``hermes plugins enable hermes-github``).
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Optional, Tuple

from fastapi import APIRouter, HTTPException

log = logging.getLogger(__name__)
router = APIRouter()

GITHUB_SEARCH = "https://api.github.com/search/issues"
TOKEN_VARS = ("GITHUB_TOKEN", "GH_TOKEN", "GITHUB_PAT", "GH_PAT")
CACHE_TTL_S = 60.0
GH_TIMEOUT_S = 20

_lock = threading.Lock()
_cache: dict = {"token": "", "source": None, "at": 0.0}


# ---------------------------------------------------------------------------
# Token detection ladder
# ---------------------------------------------------------------------------

def _env_token() -> Tuple[str, Optional[str]]:
    for var in TOKEN_VARS:
        val = os.environ.get(var, "").strip()
        if val:
            return val, f"env:{var}"
    return "", None


def _gh_cli_token() -> Tuple[str, Optional[str]]:
    try:
        out = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return "", None
    token = out.stdout.strip() if out.returncode == 0 else ""
    return (token, "gh-cli") if token else ("", None)


def _dotenv_candidates() -> list:
    homes: list = []
    for var in ("HERMES_HOME", "HERMES_ROOT"):
        val = os.environ.get(var, "").strip()
        if val:
            homes.append(Path(val))
    homes.append(Path.home() / ".hermes")
    seen, out = set(), []
    for home in homes:
        resolved = home.resolve()
        if resolved not in seen:
            seen.add(resolved)
            out.append(resolved / ".env")
    return out


def _dotenv_token() -> Tuple[str, Optional[str]]:
    for env_file in _dotenv_candidates():
        try:
            lines = env_file.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key in TOKEN_VARS and value:
                return value, f"dotenv:{env_file.name}"
    return "", None


def detect_token() -> Tuple[str, Optional[str]]:
    """Resolve a GitHub token: env -> gh CLI -> dotenv files.

    Cached briefly so repeated renderer pings don't spawn ``gh`` every call.
    """
    now = time.time()
    with _lock:
        if _cache["token"] and now - _cache["at"] < CACHE_TTL_S:
            return _cache["token"], _cache["source"]
    for fn in (_env_token, _gh_cli_token, _dotenv_token):
        token, source = fn()
        if token:
            with _lock:
                _cache["token"], _cache["source"], _cache["at"] = token, source, now
            return token, source
    return "", None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/status")
def status() -> dict:
    """Presence + provenance only — never the token itself."""
    token, source = detect_token()
    login: Optional[str] = None
    if source == "gh-cli":
        try:
            out = subprocess.run(
                ["gh", "api", "user", "-q", ".login"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            login = out.stdout.strip() if out.returncode == 0 else None
        except (OSError, subprocess.SubprocessError):
            login = None
    with _lock:
        rate = _cache.get("rate")
    return {"token": bool(token), "source": source, "login": login, "rate": rate}


@router.post("/search")
def search(payload: dict) -> dict:
    """Proxy the GitHub search API.

    ``payload``: ``{"q": str, "per_page": int, "token": str|null}`` —
    ``token`` is a renderer-supplied manual override; when empty the server
    resolves one via :func:`detect_token`. Token-less requests are sent
    unauthenticated (60 req/hr budget).
    """
    q = str(payload.get("q", "")).strip()
    if not q:
        raise HTTPException(status_code=400, detail="missing query")
    try:
        per_page = min(int(payload.get("per_page", 40) or 40), 100)
    except (TypeError, ValueError):
        per_page = 40

    manual = str(payload.get("token", "") or "").strip()
    detected, _ = detect_token()
    token = manual or detected

    url = GITHUB_SEARCH + "?" + urllib.parse.urlencode(
        {
            "q": q,
            "per_page": per_page,
            "sort": "updated",
            "order": "desc",
        }
    )
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "hermes-github",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=GH_TIMEOUT_S) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            rate_remaining = resp.headers.get("X-RateLimit-Remaining")
            rate_limit = resp.headers.get("X-RateLimit-Limit")
    except urllib.error.HTTPError as exc:
        detail = f"GitHub returned {exc.code}"
        try:
            body = json.loads(exc.read().decode("utf-8"))
            if isinstance(body, dict) and body.get("message"):
                detail = body["message"]
        except Exception:
            pass
        raise HTTPException(status_code=exc.code, detail=detail)
    except (urllib.error.URLError, OSError) as exc:
        raise HTTPException(status_code=502, detail=f"GitHub unreachable: {exc}")

    rate = None
    if rate_remaining is not None and rate_limit is not None:
        try:
            rate = {"remaining": int(rate_remaining), "limit": int(rate_limit)}
            with _lock:
                _cache["rate"] = rate
        except (TypeError, ValueError):
            pass

    return {
        "total_count": data.get("total_count", 0),
        "items": data.get("items", []),
        "token_used": bool(token),
        "token_source": "manual" if manual else (detect_token()[1] or None),
    }