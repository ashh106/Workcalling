import tool.database.prompt.prompts as prompt

_AGENTMAIL_LIST_DOC = (
    "Uses the AgentMail HTTP API (https://docs.agentmail.to/). "
    "Requires AGENTMAIL_API_KEY; inbox_id defaults to AGENTMAIL_INBOX_ID when omitted."
)

_MAIL_LIST_FILTERS = {
    "limit": {
        "type": "integer",
        "description": "Maximum items returned per API page.",
    },
    "page_token": {
        "type": "string",
        "description": "Pagination token from a previous list response (next_page_token).",
    },
    "labels": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Only messages carrying these labels.",
    },
    "before": {
        "type": "string",
        "description": "ISO 8601 datetime (RFC3339); messages strictly before this instant.",
    },
    "after": {
        "type": "string",
        "description": "ISO 8601 datetime (RFC3339); messages strictly after this instant.",
    },
    "ascending": {
        "type": "boolean",
        "description": "When true, sort by timestamp ascending.",
    },
    "include_spam": {
        "type": "boolean",
        "description": "Include spam in results.",
    },
    "include_blocked": {
        "type": "boolean",
        "description": "Include blocked messages in results.",
    },
    "include_trash": {
        "type": "boolean",
        "description": "Include trash in results.",
    },
}


sqlite_query = {
    "type": "function",
    "function": {
        "name": "execute_sql_query",
        "description": (
            "Executes a SQL query against the local SQLite database configured by "
            "SQLITE_DB_PATH and returns structured rows. "
            + prompt.getPrompt()
        ),
        "strict": True,
        "parameters": {
            "type": "object",
            "required": ["sql_query", "explanation"],
            "properties": {
                "sql_query": {
                    "type": "string",
                    "description": "The SQLite SQL query to execute against the local database.",
                },
                "explanation": {
                    "type": "string",
                    "description": "A short explanation of what the SQL query is intended to do.",
                },
            },
            "additionalProperties": False,
        },
    },
}

browser_automation_tool = {
    "type": "function",
    "function": {
        "name": "execute_browser_task",
        "description": "Executes a browser automation task based on the user's prompt. Can navigate websites, extract data, and perform actions on the internet.",
        "strict": True,
        "parameters": {
            "type": "object",
            "required": ["task"],
            "properties": {
                "task": {
                    "type": "string",
                    "description": "The clear and detailed task description for the browser agent to execute.",
                },
            },
            "additionalProperties": False,
        },
    },
}


agentmail_list_inboxes = {
    "type": "function",
    "function": {
        "name": "agentmail_list_inboxes",
        "description": f"List AgentMail inboxes for the authenticated organization. {_AGENTMAIL_LIST_DOC}",
        "strict": False,
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum inboxes per page.",
                },
                "page_token": {
                    "type": "string",
                    "description": "Pagination token from a prior inbox list.",
                },
                "ascending": {
                    "type": "boolean",
                    "description": "Sort ascending when true.",
                },
            },
            "required": [],
            "additionalProperties": False,
        },
    },
}


agentmail_list_threads = {
    "type": "function",
    "function": {
        "name": "agentmail_list_threads",
        "description": (
            "List email threads across the organization (AgentMail GET /v0/threads). "
            f"{_AGENTMAIL_LIST_DOC}"
        ),
        "strict": False,
        "parameters": {
            "type": "object",
            "properties": _MAIL_LIST_FILTERS,
            "required": [],
            "additionalProperties": False,
        },
    },
}


agentmail_list_messages = {
    "type": "function",
    "function": {
        "name": "agentmail_list_messages",
        "description": (
            "List messages in one inbox (AgentMail list messages API). "
            f"{_AGENTMAIL_LIST_DOC}"
        ),
        "strict": False,
        "parameters": {
            "type": "object",
            "properties": {
                "inbox_id": {
                    "type": "string",
                    "description": "Target inbox ID; omit to use AGENTMAIL_INBOX_ID.",
                },
                **_MAIL_LIST_FILTERS,
            },
            "required": [],
            "additionalProperties": False,
        },
    },
}


agentmail_search_messages = {
    "type": "function",
    "function": {
        "name": "agentmail_search_messages",
        "description": (
            "Search-like filtering: repeatedly lists inbox messages (up to max_pages) and keeps "
            "items whose subject, preview, or sender contains text_query (case-insensitive substring). "
            "This is not AgentMail server-side full-text search. "
            f"{_AGENTMAIL_LIST_DOC}"
        ),
        "strict": False,
        "parameters": {
            "type": "object",
            "properties": {
                "inbox_id": {
                    "type": "string",
                    "description": "Target inbox ID; omit to use AGENTMAIL_INBOX_ID.",
                },
                "text_query": {
                    "type": "string",
                    "description": "Substring to match against subject, preview, and From; empty lists all fetched pages.",
                },
                "max_pages": {
                    "type": "integer",
                    "description": "Maximum API pages to scan (default 3, capped at 10).",
                },
                **_MAIL_LIST_FILTERS,
            },
            "required": [],
            "additionalProperties": False,
        },
    },
}


agentmail_get_message = {
    "type": "function",
    "function": {
        "name": "agentmail_get_message",
        "description": (
            "Retrieve one message by ID including bodies (text/html/extracted_* fields). "
            f"{_AGENTMAIL_LIST_DOC}"
        ),
        "strict": False,
        "parameters": {
            "type": "object",
            "properties": {
                "message_id": {
                    "type": "string",
                    "description": "AgentMail message_id to fetch.",
                },
                "inbox_id": {
                    "type": "string",
                    "description": "Inbox containing the message; omit to use AGENTMAIL_INBOX_ID.",
                },
            },
            "required": ["message_id"],
            "additionalProperties": False,
        },
    },
}


agentmail_send_message = {
    "type": "function",
    "function": {
        "name": "agentmail_send_message",
        "description": (
            "Send an outbound email from an inbox; supply at least one of text or html. "
            f"{_AGENTMAIL_LIST_DOC}"
        ),
        "strict": False,
        "parameters": {
            "type": "object",
            "properties": {
                "to": {
                    "anyOf": [
                        {"type": "string"},
                        {"type": "array", "items": {"type": "string"}},
                    ],
                    "description": "Primary recipient(s).",
                },
                "subject": {
                    "type": "string",
                    "description": "Email subject line.",
                },
                "text": {
                    "type": "string",
                    "description": "Plain-text body.",
                },
                "html": {
                    "type": "string",
                    "description": "HTML body.",
                },
                "cc": {
                    "anyOf": [
                        {"type": "string"},
                        {"type": "array", "items": {"type": "string"}},
                    ],
                    "description": "Cc recipients.",
                },
                "bcc": {
                    "anyOf": [
                        {"type": "string"},
                        {"type": "array", "items": {"type": "string"}},
                    ],
                    "description": "Bcc recipients.",
                },
                "inbox_id": {
                    "type": "string",
                    "description": "Sending inbox; omit to use AGENTMAIL_INBOX_ID.",
                },
            },
            "required": ["to", "subject"],
            "additionalProperties": False,
        },
    },
}


agentmail_reply_to_message = {
    "type": "function",
    "function": {
        "name": "agentmail_reply_to_message",
        "description": (
            "Reply to an existing AgentMail message; provide text and/or html. "
            f"{_AGENTMAIL_LIST_DOC}"
        ),
        "strict": False,
        "parameters": {
            "type": "object",
            "properties": {
                "message_id": {
                    "type": "string",
                    "description": "Message being replied to.",
                },
                "text": {
                    "type": "string",
                    "description": "Plain-text reply body.",
                },
                "html": {
                    "type": "string",
                    "description": "HTML reply body.",
                },
                "cc": {
                    "anyOf": [
                        {"type": "string"},
                        {"type": "array", "items": {"type": "string"}},
                    ],
                    "description": "Additional Cc recipients.",
                },
                "bcc": {
                    "anyOf": [
                        {"type": "string"},
                        {"type": "array", "items": {"type": "string"}},
                    ],
                    "description": "Bcc recipients.",
                },
                "reply_all": {
                    "type": "boolean",
                    "description": "When true, reply-all semantics.",
                },
                "inbox_id": {
                    "type": "string",
                    "description": "Inbox holding the original message; omit to use AGENTMAIL_INBOX_ID.",
                },
            },
            "required": ["message_id"],
            "additionalProperties": False,
        },
    },
}


happenstance_research = {
    "type": "function",
    "function": {
        "name": "happenstance_research",
        "description": (
            "Runs Happenstance person research: submits a natural-language description "
            "(e.g. name and company), polls until the job completes (often 1–3 minutes), "
            "and returns profile metadata, employment, and summary. Requires HAPPENSTANCE_API_KEY."
        ),
        "strict": False,
        "parameters": {
            "type": "object",
            "properties": {
                "description": {
                    "type": "string",
                    "description": "Who or what to research (e.g. 'Garry Tan Y Combinator').",
                },
                "poll_interval_seconds": {
                    "type": "number",
                    "description": "Seconds between status polls; clamped between 5 and 10 (default 7).",
                },
                "max_wait_seconds": {
                    "type": "number",
                    "description": "Maximum seconds to wait for completion before timing out (default 600).",
                },
            },
            "required": ["description"],
            "additionalProperties": False,
        },
    },
}
