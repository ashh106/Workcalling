"""Happenstance Research API — start async research and poll until completion."""

from __future__ import annotations

import json
import logging
import time
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

import config
import utils

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.happenstance.ai/v1"
_HTTP_TIMEOUT = 120.0
_TERMINAL_STATUSES = frozenset({"COMPLETED", "FAILED", "FAILED_AMBIGUOUS"})


def _get_api_key() -> Optional[str]:
    return config.API_KEYS.get("HAPPENSTANCE_API_KEY")


def _request_json(
    method: str,
    path: str,
    *,
    api_key: str,
    body: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    url = f"{_BASE_URL}{path}"
    payload: Optional[bytes] = None
    headers = {"Authorization": f"Bearer {api_key}"}
    if body is not None:
        payload = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=payload, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=_HTTP_TIMEOUT) as resp:
            raw = resp.read().decode()
            if not raw:
                return {}
            parsed: Dict[str, Any] = json.loads(raw)
            return parsed
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise RuntimeError(f"Happenstance HTTP {exc.code}: {detail}") from exc


def happenstance_research(
    description: str,
    poll_interval_seconds: float = 7.0,
    max_wait_seconds: float = 600.0,
) -> Dict[str, Any]:
    """
    Start a person/research job and block until it completes or fails.

    Polls GET /v1/research/{id} every ``poll_interval_seconds`` (clamped to 5–10s)
    until status is COMPLETED, FAILED, FAILED_AMBIGUOUS, or ``max_wait_seconds`` elapses.
    """
    api_key = _get_api_key()
    if not api_key:
        return utils.create_error_response(
            "Happenstance is not configured",
            "Set HAPPENSTANCE_API_KEY in the environment.",
        )

    stripped = (description or "").strip()
    if not stripped:
        return utils.create_error_response(
            "Invalid Happenstance research request",
            "description must be a non-empty string.",
        )

    interval = max(5.0, min(float(poll_interval_seconds), 10.0))
    max_wait = max(interval, float(max_wait_seconds))
    deadline = time.monotonic() + max_wait

    try:
        start = _request_json("POST", "/research", api_key=api_key, body={"description": stripped})
    except Exception as exc:
        logger.exception("happenstance_research POST failed")
        return utils.create_error_response("Happenstance research start failed", str(exc))

    research_id = start.get("id")
    if not research_id or not isinstance(research_id, str):
        return utils.create_error_response(
            "Happenstance research start failed",
            f"Unexpected response: {start!r}",
        )

    last_payload: Dict[str, Any] = {}

    while time.monotonic() < deadline:
        try:
            last_payload = _request_json(
                "GET",
                f"/research/{research_id}",
                api_key=api_key,
            )
        except Exception as exc:
            logger.exception("happenstance_research poll failed")
            return utils.create_error_response("Happenstance research poll failed", str(exc))

        status = last_payload.get("status")
        if status in _TERMINAL_STATUSES:
            if status == "COMPLETED":
                return utils.create_success_response(
                    last_payload,
                    "Happenstance research completed",
                )
            return utils.create_error_response(
                f"Happenstance research ended with status {status}",
                last_payload,
            )

        time.sleep(interval)

    return utils.create_error_response(
        "Happenstance research timed out waiting for completion",
        {"id": research_id, "last_response": last_payload, "max_wait_seconds": max_wait},
    )
