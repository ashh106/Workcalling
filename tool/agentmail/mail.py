"""AgentMail tool implementations."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import config
import utils

logger = logging.getLogger(__name__)

_mail_client = None


def _serialize(obj: Any) -> Any:
    if obj is None:
        return None
    if hasattr(obj, "model_dump"):
        return obj.model_dump(mode="json")
    if isinstance(obj, list):
        return [_serialize(item) for item in obj]
    if isinstance(obj, dict):
        return {key: _serialize(value) for key, value in obj.items()}
    return obj


def _get_mail_client():
    """Return a lazily constructed AgentMail client or None if unconfigured."""
    global _mail_client
    api_key = config.API_KEYS.get("AGENTMAIL_API_KEY")
    if not api_key:
        return None
    if _mail_client is None:
        from agentmail import AgentMail

        _mail_client = AgentMail(api_key=api_key)
    return _mail_client


def _mail_not_configured_response() -> Dict[str, Any]:
    return utils.create_error_response(
        "AgentMail is not configured",
        "Set AGENTMAIL_API_KEY in the environment.",
    )


def _resolve_inbox_id(inbox_id: Optional[str]) -> Optional[str]:
    if inbox_id:
        return inbox_id
    default_id = config.APP_SETTINGS.get("AGENTMAIL_INBOX_ID")
    return default_id if default_id else None


def _parse_optional_datetime(value: Optional[str]) -> Optional[datetime]:
    if value is None or value == "":
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        raise ValueError(f"Invalid ISO datetime: {value}") from None


def _build_list_kwargs(
    *,
    limit: Optional[int] = None,
    page_token: Optional[str] = None,
    labels: Optional[List[str]] = None,
    before: Optional[str] = None,
    after: Optional[str] = None,
    ascending: Optional[bool] = None,
    include_spam: Optional[bool] = None,
    include_blocked: Optional[bool] = None,
    include_trash: Optional[bool] = None,
) -> Dict[str, Any]:
    kwargs: Dict[str, Any] = {}
    if limit is not None:
        kwargs["limit"] = limit
    if page_token:
        kwargs["page_token"] = page_token
    if labels:
        kwargs["labels"] = labels
    if before is not None:
        kwargs["before"] = _parse_optional_datetime(before)
    if after is not None:
        kwargs["after"] = _parse_optional_datetime(after)
    if ascending is not None:
        kwargs["ascending"] = ascending
    if include_spam is not None:
        kwargs["include_spam"] = include_spam
    if include_blocked is not None:
        kwargs["include_blocked"] = include_blocked
    if include_trash is not None:
        kwargs["include_trash"] = include_trash
    return kwargs


def _message_matches_text_query(msg: Any, text_query: str) -> bool:
    stripped = text_query.strip()
    if not stripped:
        return True
    needle = stripped.lower()
    subject = getattr(msg, "subject", None) or ""
    preview = getattr(msg, "preview", None) or ""
    sender = getattr(msg, "from_", None) or ""
    haystack = f"{subject} {preview} {sender}".lower()
    return needle in haystack


def agentmail_list_inboxes(
    limit: Optional[int] = None,
    page_token: Optional[str] = None,
    ascending: Optional[bool] = None,
) -> Dict[str, Any]:
    """List AgentMail inboxes."""
    client = _get_mail_client()
    if not client:
        return _mail_not_configured_response()
    try:
        kwargs: Dict[str, Any] = {}
        if limit is not None:
            kwargs["limit"] = limit
        if page_token:
            kwargs["page_token"] = page_token
        if ascending is not None:
            kwargs["ascending"] = ascending
        result = client.inboxes.list(**kwargs)
        return utils.create_success_response(
            _serialize(result),
            "AgentMail inboxes listed successfully",
        )
    except Exception as exc:
        logger.exception("agentmail_list_inboxes failed")
        return utils.create_error_response("AgentMail list inboxes failed", str(exc))


def agentmail_list_threads(
    limit: Optional[int] = None,
    page_token: Optional[str] = None,
    labels: Optional[List[str]] = None,
    before: Optional[str] = None,
    after: Optional[str] = None,
    ascending: Optional[bool] = None,
    include_spam: Optional[bool] = None,
    include_blocked: Optional[bool] = None,
    include_trash: Optional[bool] = None,
) -> Dict[str, Any]:
    """List threads across the organization."""
    client = _get_mail_client()
    if not client:
        return _mail_not_configured_response()
    try:
        kwargs = _build_list_kwargs(
            limit=limit,
            page_token=page_token,
            labels=labels,
            before=before,
            after=after,
            ascending=ascending,
            include_spam=include_spam,
            include_blocked=include_blocked,
            include_trash=include_trash,
        )
        result = client.threads.list(**kwargs)
        return utils.create_success_response(
            _serialize(result),
            "AgentMail threads listed successfully",
        )
    except ValueError as exc:
        return utils.create_error_response("Invalid thread list parameters", str(exc))
    except Exception as exc:
        logger.exception("agentmail_list_threads failed")
        return utils.create_error_response("AgentMail list threads failed", str(exc))


def agentmail_list_messages(
    inbox_id: Optional[str] = None,
    limit: Optional[int] = None,
    page_token: Optional[str] = None,
    labels: Optional[List[str]] = None,
    before: Optional[str] = None,
    after: Optional[str] = None,
    ascending: Optional[bool] = None,
    include_spam: Optional[bool] = None,
    include_blocked: Optional[bool] = None,
    include_trash: Optional[bool] = None,
) -> Dict[str, Any]:
    """List messages in an inbox (per AgentMail List Messages API)."""
    resolved = _resolve_inbox_id(inbox_id)
    if not resolved:
        return utils.create_error_response(
            "Missing inbox_id",
            "Provide inbox_id or set AGENTMAIL_INBOX_ID.",
        )
    client = _get_mail_client()
    if not client:
        return _mail_not_configured_response()
    try:
        kwargs = _build_list_kwargs(
            limit=limit,
            page_token=page_token,
            labels=labels,
            before=before,
            after=after,
            ascending=ascending,
            include_spam=include_spam,
            include_blocked=include_blocked,
            include_trash=include_trash,
        )
        result = client.inboxes.messages.list(resolved, **kwargs)
        return utils.create_success_response(
            _serialize(result),
            "AgentMail messages listed successfully",
        )
    except ValueError as exc:
        return utils.create_error_response("Invalid message list parameters", str(exc))
    except Exception as exc:
        logger.exception("agentmail_list_messages failed")
        return utils.create_error_response("AgentMail list messages failed", str(exc))


def agentmail_search_messages(
    inbox_id: Optional[str] = None,
    text_query: Optional[str] = None,
    limit: Optional[int] = None,
    page_token: Optional[str] = None,
    labels: Optional[List[str]] = None,
    before: Optional[str] = None,
    after: Optional[str] = None,
    ascending: Optional[bool] = None,
    include_spam: Optional[bool] = None,
    include_blocked: Optional[bool] = None,
    include_trash: Optional[bool] = None,
    max_pages: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Filter messages by listing the inbox and matching text_query against subject,
    preview, and sender (client-side; not server full-text search).
    """
    resolved = _resolve_inbox_id(inbox_id)
    if not resolved:
        return utils.create_error_response(
            "Missing inbox_id",
            "Provide inbox_id or set AGENTMAIL_INBOX_ID.",
        )
    client = _get_mail_client()
    if not client:
        return _mail_not_configured_response()
    pages_cap = max_pages if max_pages is not None else 3
    if pages_cap < 1:
        pages_cap = 1
    if pages_cap > 10:
        pages_cap = 10
    query = text_query or ""
    matched: List[Any] = []
    pages_scanned = 0
    next_token: Optional[str] = page_token
    last_response: Optional[Any] = None
    try:
        base_kwargs = _build_list_kwargs(
            limit=limit,
            page_token=None,
            labels=labels,
            before=before,
            after=after,
            ascending=ascending,
            include_spam=include_spam,
            include_blocked=include_blocked,
            include_trash=include_trash,
        )
        while pages_scanned < pages_cap:
            kwargs = dict(base_kwargs)
            if next_token:
                kwargs["page_token"] = next_token
            last_response = client.inboxes.messages.list(resolved, **kwargs)
            for msg in last_response.messages:
                if _message_matches_text_query(msg, query):
                    matched.append(_serialize(msg))
            pages_scanned += 1
            next_token = last_response.next_page_token
            if not next_token:
                break
        payload = {
            "messages": matched,
            "pages_scanned": pages_scanned,
            "next_page_token": last_response.next_page_token if last_response else None,
            "note": (
                "Matches are substring search on subject, preview, and sender only; "
                "use agentmail_get_message for full bodies."
            ),
        }
        return utils.create_success_response(
            payload,
            "AgentMail message search completed",
        )
    except ValueError as exc:
        return utils.create_error_response("Invalid search parameters", str(exc))
    except Exception as exc:
        logger.exception("agentmail_search_messages failed")
        return utils.create_error_response("AgentMail search messages failed", str(exc))


def agentmail_get_message(
    message_id: str,
    inbox_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Fetch a single message including body fields."""
    if not message_id:
        return utils.create_error_response("message_id is required", "")
    resolved = _resolve_inbox_id(inbox_id)
    if not resolved:
        return utils.create_error_response(
            "Missing inbox_id",
            "Provide inbox_id or set AGENTMAIL_INBOX_ID.",
        )
    client = _get_mail_client()
    if not client:
        return _mail_not_configured_response()
    try:
        result = client.inboxes.messages.get(resolved, message_id)
        return utils.create_success_response(
            _serialize(result),
            "AgentMail message retrieved successfully",
        )
    except Exception as exc:
        logger.exception("agentmail_get_message failed")
        return utils.create_error_response("AgentMail get message failed", str(exc))


def _normalize_recipients(
    value: Optional[Union[str, List[str]]],
) -> Optional[Union[str, List[str]]]:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, list) and value:
        return value
    return None


def agentmail_send_message(
    to: Union[str, List[str]],
    subject: str,
    text: Optional[str] = None,
    html: Optional[str] = None,
    cc: Optional[Union[str, List[str]]] = None,
    bcc: Optional[Union[str, List[str]]] = None,
    inbox_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Send a new email from an inbox."""
    resolved = _resolve_inbox_id(inbox_id)
    if not resolved:
        return utils.create_error_response(
            "Missing inbox_id",
            "Provide inbox_id or set AGENTMAIL_INBOX_ID.",
        )
    client = _get_mail_client()
    if not client:
        return _mail_not_configured_response()
    recipients = _normalize_recipients(to)
    if not recipients:
        return utils.create_error_response("to recipients are required", "")
    if not subject:
        return utils.create_error_response("subject is required", "")
    if not text and not html:
        return utils.create_error_response("Provide at least one of text or html", "")
    try:
        send_kw: Dict[str, Any] = {"to": recipients, "subject": subject}
        if text is not None:
            send_kw["text"] = text
        if html is not None:
            send_kw["html"] = html
        cc_norm = _normalize_recipients(cc)
        if cc_norm is not None:
            send_kw["cc"] = cc_norm
        bcc_norm = _normalize_recipients(bcc)
        if bcc_norm is not None:
            send_kw["bcc"] = bcc_norm
        result = client.inboxes.messages.send(resolved, **send_kw)
        return utils.create_success_response(
            _serialize(result),
            "AgentMail message sent successfully",
        )
    except Exception as exc:
        logger.exception("agentmail_send_message failed")
        return utils.create_error_response("AgentMail send message failed", str(exc))


def agentmail_reply_to_message(
    message_id: str,
    text: Optional[str] = None,
    html: Optional[str] = None,
    cc: Optional[Union[str, List[str]]] = None,
    bcc: Optional[Union[str, List[str]]] = None,
    reply_all: Optional[bool] = None,
    inbox_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Reply to an existing message."""
    if not message_id:
        return utils.create_error_response("message_id is required", "")
    resolved = _resolve_inbox_id(inbox_id)
    if not resolved:
        return utils.create_error_response(
            "Missing inbox_id",
            "Provide inbox_id or set AGENTMAIL_INBOX_ID.",
        )
    client = _get_mail_client()
    if not client:
        return _mail_not_configured_response()
    if not text and not html:
        return utils.create_error_response("Provide at least one of text or html", "")
    try:
        reply_kw: Dict[str, Any] = {}
        if text is not None:
            reply_kw["text"] = text
        if html is not None:
            reply_kw["html"] = html
        cc_norm = _normalize_recipients(cc)
        if cc_norm is not None:
            reply_kw["cc"] = cc_norm
        bcc_norm = _normalize_recipients(bcc)
        if bcc_norm is not None:
            reply_kw["bcc"] = bcc_norm
        if reply_all is not None:
            reply_kw["reply_all"] = reply_all
        result = client.inboxes.messages.reply(resolved, message_id, **reply_kw)
        return utils.create_success_response(
            _serialize(result),
            "AgentMail reply sent successfully",
        )
    except Exception as exc:
        logger.exception("agentmail_reply_to_message failed")
        return utils.create_error_response("AgentMail reply failed", str(exc))
