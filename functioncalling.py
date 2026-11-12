"""Gemini function calling support for Workmind."""

from __future__ import annotations

import copy
import json
import logging
from typing import Any, Dict, Iterator, List, Optional, Sequence, Tuple

from google.genai import types

import config
import prompt
import router
import tools
import utils
from LLMclient import get_gemini_client

logger = logging.getLogger(__name__)

MAX_TOOL_TURNS = 20

AVAILABLE_TOOLS = [
    tools.sqlite_query,
    tools.browser_automation_tool,
    tools.agentmail_list_inboxes,
    tools.agentmail_list_threads,
    tools.agentmail_list_messages,
    tools.agentmail_search_messages,
    tools.agentmail_get_message,
    tools.agentmail_send_message,
    tools.agentmail_reply_to_message,
    tools.happenstance_research,
]

logger.info(
    "Loaded %s available tools for Gemini function calling",
    len(AVAILABLE_TOOLS),
)


class ToolLoopLimitError(RuntimeError):
    """Raised when Gemini keeps asking for tools beyond the configured limit."""


def _normalize_schema_for_gemini(schema: Any) -> Any:
    """Return a Gemini-compatible copy of an OpenAI JSON schema fragment."""
    if isinstance(schema, list):
        return [_normalize_schema_for_gemini(item) for item in schema]

    if not isinstance(schema, dict):
        return schema

    normalized: Dict[str, Any] = {}
    for key, value in schema.items():
        if key in {"additionalProperties", "strict"}:
            continue
        if key == "anyOf":
            normalized.update(_collapse_any_of(value))
            continue
        normalized[key] = _normalize_schema_for_gemini(value)

    return normalized


def _collapse_any_of(options: Any) -> Dict[str, Any]:
    """
    Collapse simple ``anyOf`` schemas into one Gemini-safe schema.

    The current tools only use ``anyOf`` for recipient fields that accept either
    a string or a list of strings. A string keeps the existing Python handlers
    compatible and avoids Gemini schema rejection.
    """
    if not isinstance(options, list):
        return {}

    normalized_options = [_normalize_schema_for_gemini(option) for option in options]
    for option in normalized_options:
        if option.get("type") == "string":
            return option
    return normalized_options[0] if normalized_options else {}


def openai_tool_to_gemini_declaration(
    openai_tool: Dict[str, Any],
) -> Dict[str, Any]:
    """Convert one OpenAI-style function tool into a Gemini declaration."""
    function_schema = openai_tool.get("function", {})
    declaration = {
        "name": function_schema["name"],
        "description": function_schema.get("description", ""),
    }
    parameters = function_schema.get("parameters")
    if parameters:
        declaration["parameters"] = _normalize_schema_for_gemini(parameters)
    return declaration


def get_gemini_function_declarations() -> List[Dict[str, Any]]:
    """Return all registered tools as Gemini function declarations."""
    return [
        openai_tool_to_gemini_declaration(tool_definition)
        for tool_definition in AVAILABLE_TOOLS
    ]


def _get_message_text(message: Dict[str, Any]) -> str:
    content = message.get("content")
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    return json.dumps(content)


def _content_from_text(role: str, text: str) -> types.Content:
    return types.Content(role=role, parts=[types.Part.from_text(text=text)])


def app_messages_to_gemini_contents(
    messages: Sequence[Dict[str, Any]],
) -> Tuple[List[types.Content], Optional[str]]:
    """Convert API messages into Gemini contents and a system instruction."""
    contents: List[types.Content] = []
    system_parts: List[str] = []

    for message in messages:
        role = message.get("role")
        if role == "system":
            text = _get_message_text(message)
            if text:
                system_parts.append(text)
            continue
        if role == "tool":
            contents.append(
                _function_response_content(
                    name=message.get("name") or "tool_response",
                    response={"result": _get_message_text(message)},
                    call_id=message.get("tool_call_id"),
                )
            )
            continue

        if role == "assistant" and message.get("tool_calls"):
            contents.append(_assistant_tool_call_content(message))
            continue

        gemini_role = "model" if role == "assistant" else "user"
        contents.append(_content_from_text(gemini_role, _get_message_text(message)))

    return contents, "\n\n".join(system_parts) or None


def _assistant_tool_call_content(message: Dict[str, Any]) -> types.Content:
    """Convert an OpenAI-style assistant tool-call message to Gemini content."""
    parts: List[types.Part] = []
    text = _get_message_text(message)
    if text:
        parts.append(types.Part.from_text(text=text))

    for tool_call in message.get("tool_calls", []):
        function_payload = tool_call.get("function", {})
        raw_args = function_payload.get("arguments") or "{}"
        try:
            args = json.loads(raw_args)
        except json.JSONDecodeError:
            args = {}
        function_call_kwargs = {
            "name": function_payload.get("name", ""),
            "args": args,
        }
        if tool_call.get("id"):
            function_call_kwargs["id"] = tool_call["id"]
        function_call = types.FunctionCall(**function_call_kwargs)
        parts.append(types.Part(function_call=function_call))

    return types.Content(role="model", parts=parts)


def _extract_function_calls(response: Any) -> List[Any]:
    """Extract all function call parts from a Gemini response."""
    function_calls = getattr(response, "function_calls", None)
    if function_calls:
        return list(function_calls)

    calls = []
    for candidate in getattr(response, "candidates", []) or []:
        content = getattr(candidate, "content", None)
        for part in getattr(content, "parts", []) or []:
            function_call = getattr(part, "function_call", None)
            if function_call:
                calls.append(function_call)
    return calls


def _extract_response_text(response: Any) -> str:
    text = getattr(response, "text", None)
    if text:
        return text

    chunks: List[str] = []
    for candidate in getattr(response, "candidates", []) or []:
        content = getattr(candidate, "content", None)
        for part in getattr(content, "parts", []) or []:
            part_text = getattr(part, "text", None)
            if part_text:
                chunks.append(part_text)
    return "\n".join(chunks)


def _extract_model_content(response: Any) -> Optional[types.Content]:
    candidates = getattr(response, "candidates", None) or []
    if not candidates:
        return None
    return getattr(candidates[0], "content", None)

def _function_response_part(
    name: str,
    response: Dict[str, Any],
    call_id: Optional[str] = None,
) -> types.Part:
    """Build a Gemini function response part."""
    # Ensure response is a dict. The API strictly requires dict[str, Any].
    if not isinstance(response, dict):
        response = {"result": response}
        
    function_response_kwargs = {"name": name, "response": response}
    if call_id:
        function_response_kwargs["id"] = call_id
    try:
        return types.Part.from_function_response(**function_response_kwargs)
    except TypeError:
        function_response = types.FunctionResponse(**function_response_kwargs)
        return types.Part(function_response=function_response)


def _function_response_content(
    name: str,
    response: Dict[str, Any],
    call_id: Optional[str] = None,
) -> types.Content:
    return types.Content(
        role="user",
        parts=[_function_response_part(name, response, call_id)],
    )


def _function_call_to_message(function_call: Any) -> Dict[str, Any]:
    args = getattr(function_call, "args", {}) or {}
    return {
        "id": getattr(function_call, "id", None),
        "type": "function",
        "function": {
            "name": getattr(function_call, "name", ""),
            "arguments": json.dumps(dict(args)),
        },
    }


def _response_to_assistant_message(response: Any) -> Dict[str, Any]:
    function_calls = _extract_function_calls(response)
    message = {
        "role": "assistant",
        "content": _extract_response_text(response),
    }
    if function_calls:
        message["tool_calls"] = [
            _function_call_to_message(function_call)
            for function_call in function_calls
        ]
    return message


def _tool_response_message(
    function_call: Any,
    execution_result: Any,
) -> Dict[str, Any]:
    return {
        "role": "tool",
        "tool_call_id": getattr(function_call, "id", None),
        "name": getattr(function_call, "name", ""),
        "content": json.dumps(execution_result),
        "_original_content": execution_result,
    }


def _execute_function_call(function_call: Any) -> Dict[str, Any]:
    function_name = getattr(function_call, "name", "")
    function_args = dict(getattr(function_call, "args", {}) or {})

    logger.info(
        "Executing Gemini function: %s with args: %s",
        function_name,
        function_args,
    )
    result = router.execute_function_call(function_name, function_args)
    if result is None:
        return utils.create_error_response(
            f"Function '{function_name}' not found or failed to execute"
        )
    if isinstance(result, dict):
        return result
    return utils.create_success_response(result)


def _build_generation_config(
    system_instruction: Optional[str],
) -> types.GenerateContentConfig:
    function_declarations = get_gemini_function_declarations()
    return types.GenerateContentConfig(
        tools=[types.Tool(function_declarations=function_declarations)],
        temperature=config.APP_SETTINGS["TEMPERATURE"],
        max_output_tokens=config.APP_SETTINGS["MAX_TOKENS"],
        system_instruction=system_instruction,
    )


def run_gemini_tool_loop(
    messages: Sequence[Dict[str, Any]],
    model: str = config.APP_SETTINGS["DEFAULT_LLM_MODEL_DEPLOYMENT"],
    max_tool_turns: int = MAX_TOOL_TURNS,
    client: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    """Run a Gemini conversation until it returns final text or hits the turn cap."""
    return [
        event["message"]
        for event in stream_gemini_tool_loop(messages, model, max_tool_turns, client)
        if event["event"] in {"assistant_message", "tool_result"}
    ]


def stream_gemini_tool_loop(
    messages: Sequence[Dict[str, Any]],
    model: str = config.APP_SETTINGS["DEFAULT_LLM_MODEL_DEPLOYMENT"],
    max_tool_turns: int = MAX_TOOL_TURNS,
    client: Optional[Any] = None,
) -> Iterator[Dict[str, Any]]:
    """
    Run a Gemini tool loop and yield complete events as each step finishes.

    This intentionally does not use Gemini token streaming. Each event contains
    a full assistant message, a complete tool-call request, or a complete tool
    result so API clients can update incrementally without rendering partial
    model text.
    """
    gemini_client = client or get_gemini_client()
    contents, system_instruction = app_messages_to_gemini_contents(messages)
    generation_config = _build_generation_config(
        system_instruction or prompt.system_prompt,
    )

    for turn_index in range(max_tool_turns + 1):
        logger.info(
            "Sending Gemini request to %s with %s content turns",
            model,
            len(contents),
        )
        response = gemini_client.models.generate_content(
            model=model,
            contents=contents,
            config=generation_config,
        )

        model_content = _extract_model_content(response)
        if model_content is not None:
            contents.append(model_content)

        assistant_message = _response_to_assistant_message(response)
        function_calls = _extract_function_calls(response)

        if not function_calls:
            yield {
                "event": "assistant_message",
                "message": assistant_message,
            }
            return

        yield {
            "event": "assistant_message",
            "message": assistant_message,
        }
        if turn_index >= max_tool_turns:
            raise ToolLoopLimitError(
                f"Gemini requested tool calls for more than {max_tool_turns} turns."
            )

        for function_call in function_calls:
            yield {
                "event": "tool_call",
                "tool_call": _function_call_to_message(function_call),
            }
            is_valid, error_message = router.validate_function_call(
                getattr(function_call, "name", ""),
                dict(getattr(function_call, "args", {}) or {}),
            )
            if not is_valid:
                execution_result = utils.create_error_response(error_message)
                yield {
                    "event": "tool_result",
                    "message": _tool_response_message(function_call, execution_result),
                }
                return

            execution_result = _execute_function_call(function_call)
            yield {
                "event": "tool_result",
                "message": _tool_response_message(function_call, execution_result),
            }
            contents.append(
                _function_response_content(
                    name=getattr(function_call, "name", ""),
                    response={"result": execution_result},
                    call_id=getattr(function_call, "id", None),
                )
            )

    raise ToolLoopLimitError(
        f"Gemini requested tool calls for more than {max_tool_turns} turns."
    )


def get_chat_completion(
    messages: List[Dict[str, Any]],
    model: str = None,
) -> List[Dict[str, Any]]:
    """Compatibility wrapper returning new conversation messages."""
    selected_model = model or config.APP_SETTINGS["DEFAULT_LLM_MODEL_DEPLOYMENT"]
    return run_gemini_tool_loop(messages, model=selected_model)


def get_available_tools_list() -> List[Dict[str, Any]]:
    """Get the OpenAI-style tool definitions maintained by the app."""
    return copy.deepcopy(AVAILABLE_TOOLS)


def validate_tool_call_arguments(tool_name: str, arguments: Dict[str, Any]) -> bool:
    """Validate arguments for a specific tool call."""
    is_valid, _ = router.validate_function_call(tool_name, arguments)
    return is_valid
