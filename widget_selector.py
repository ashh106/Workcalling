"""LLM-backed widget selection for completed assistant turns."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Iterable, List, Optional, Sequence

from google.genai import types

import config
from LLMclient import get_gemini_client

logger = logging.getLogger(__name__)

LEGACY_WIDGETS = {
    "bar_chart": "bar-chart",
    "line_chart": "line-chart",
    "donut_chart": "donut-chart",
    "radar": "radar",
    "scatter": "scatter",
    "heatmap": "heatmap",
    "funnel": "funnel",
    "waterfall": "waterfall",
    "treemap": "treemap",
    "sankey": "sankey",
    "sparkline": "sparkline",
    "network": "network",
    "tabs": "tabs",
    "form": "form",
}

TOOL_UI_WIDGETS = {
    "plan": "plan",
    "progress_tracker": "progress-tracker",
    "option_list": "option-list",
    "parameter_slider": "parameter-slider",
    "preferences_panel": "preferences-panel",
    "question_flow": "question-flow",
    "citation": "citation",
    "item_carousel": "item-carousel",
    "link_preview": "link-preview",
    "stats_display": "stats-display",
    "terminal": "terminal",
    "weather_widget": "weather-widget",
    "chart": "chart",
    "code_block": "code-block",
    "code_diff": "code-diff",
    "data_table": "data-table",
    "message_draft": "message-draft",
    "instagram_post": "instagram-post",
    "linkedin_post": "linkedin-post",
    "x_post": "x-post",
    "approval_card": "approval-card",
    "order_summary": "order-summary",
    "audio": "audio",
    "image": "image",
    "image_gallery": "image-gallery",
    "video": "video",
    "geo_map": "geo-map",
}

WIDGET_FUNCTIONS = {**LEGACY_WIDGETS, **TOOL_UI_WIDGETS}

WIDGET_DESCRIPTIONS = {
    "bar_chart": "Use for comparing values across categories.",
    "line_chart": "Use for trends over time or ordered series.",
    "donut_chart": "Use for part-to-whole category breakdowns.",
    "radar": "Use for comparing multiple dimensions on one entity or group.",
    "scatter": "Use for x/y correlation or distribution.",
    "heatmap": "Use for matrix intensity data.",
    "funnel": "Use for staged conversion or drop-off.",
    "waterfall": "Use for sequential positive and negative contributions.",
    "treemap": "Use for hierarchical or proportional category sizes.",
    "sankey": "Use for flows between stages or categories.",
    "sparkline": "Use for a compact trend summary.",
    "network": "Use for node and edge relationship data.",
    "tabs": "Use to organize several sections of structured content.",
    "form": "Use to collect short structured input from the user.",
    "plan": "Use to present step-by-step work or recommendations.",
    "progress_tracker": "Use to show operation progress or status by step.",
    "option_list": "Use when the user should pick one or more choices.",
    "parameter_slider": "Use when the user should adjust numeric values.",
    "preferences_panel": "Use when the user should configure several settings.",
    "question_flow": "Use for a guided multi-question input flow.",
    "citation": "Use to show source references or evidence links.",
    "item_carousel": "Use to browse a compact collection of items.",
    "link_preview": "Use to display a rich URL preview.",
    "stats_display": "Use to show KPI metrics in a compact grid.",
    "terminal": "Use to show command output, logs, or execution traces.",
    "weather_widget": "Use to show weather conditions or forecasts.",
    "chart": "Use for a general chart when the exact legacy chart is unclear.",
    "code_block": "Use to show syntax-highlighted code.",
    "code_diff": "Use to show before/after code changes.",
    "data_table": "Use to show tabular records.",
    "message_draft": "Use when the user should review draft text before sending.",
    "instagram_post": "Use to preview Instagram post content.",
    "linkedin_post": "Use to preview LinkedIn post content.",
    "x_post": "Use to preview X/Twitter post content.",
    "approval_card": "Use when the user should approve or deny an action.",
    "order_summary": "Use for itemized purchase or cost summaries.",
    "audio": "Use to present playable audio metadata.",
    "image": "Use to present one image with metadata.",
    "image_gallery": "Use to present multiple images.",
    "video": "Use to present playable video metadata.",
    "geo_map": "Use to present geolocated entities.",
}

SELECTOR_SYSTEM_PROMPT = """
You are a UI selection assistant for Workmind.

You receive only one completed assistant turn, including any assistant tool
calls, tool results, and the final assistant message. Choose zero or more UI
widgets that would make this completed turn easier to understand or act on.

Rules:
- Use function calls only. Each function call creates one widget.
- You may call multiple widget functions in parallel when useful.
- Do not restate the assistant answer as text.
- Prefer data_table, stats_display, chart, and legacy charts for analytical
  data. Prefer input widgets only when the final answer asks the user to choose,
  approve, configure, or provide structured input.
- Return no function calls when plain text is sufficient.
- Fill the data argument with final renderable values, not placeholders.
""".strip()


def _widget_parameters_schema() -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Short optional title shown above the widget.",
            },
            "data": {
                "type": "object",
                "description": (
                    "Renderable widget payload. Use arrays inside this object "
                    "when a widget needs rows, options, items, steps, or series."
                ),
            },
        },
        "required": ["data"],
    }


def get_widget_function_declarations() -> List[Dict[str, Any]]:
    """Return Gemini function declarations for all selectable widgets."""
    parameters = _widget_parameters_schema()
    return [
        {
            "name": function_name,
            "description": WIDGET_DESCRIPTIONS.get(
                function_name,
                f"Create a {widget_type} widget.",
            ),
            "parameters": parameters,
        }
        for function_name, widget_type in WIDGET_FUNCTIONS.items()
    ]


def _content_from_events(events: Sequence[Dict[str, Any]]) -> types.Content:
    serialized = json.dumps(events, ensure_ascii=False, default=str, indent=2)
    return types.Content(
        role="user",
        parts=[
            types.Part.from_text(
                text=(
                    "Select widgets for this completed assistant turn:\n\n"
                    f"{serialized}"
                )
            )
        ],
    )


def _extract_function_calls(response: Any) -> List[Any]:
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


def _normalize_widget_data(widget_type: str, data: Any) -> Any:
    if not isinstance(data, dict):
        return data

    if widget_type in {
        "bar-chart",
        "line-chart",
        "donut-chart",
        "radar",
        "scatter",
        "funnel",
        "waterfall",
        "treemap",
        "sankey",
        "sparkline",
    }:
        for key in ("data", "rows", "items", "series", "values"):
            value = data.get(key)
            if isinstance(value, list):
                return value

    return data


def _function_call_to_widget_block(function_call: Any) -> Optional[Dict[str, Any]]:
    function_name = getattr(function_call, "name", "")
    widget_type = WIDGET_FUNCTIONS.get(function_name)
    if not widget_type:
        logger.warning("Selector returned unknown widget function: %s", function_name)
        return None

    args = dict(getattr(function_call, "args", {}) or {})
    raw_data = args.get("data")
    if raw_data is None:
        logger.warning("Selector widget %s omitted data", function_name)
        return None

    widget: Dict[str, Any] = {
        "type": widget_type,
        "data": _normalize_widget_data(widget_type, raw_data),
    }
    title = args.get("title")
    if isinstance(title, str) and title.strip():
        widget["title"] = title.strip()

    return {
        "kind": "widget",
        "widget": widget,
    }


def select_widgets_for_turn(
    events: Sequence[Dict[str, Any]],
    model: str = config.APP_SETTINGS["WIDGET_SELECTOR_MODEL"],
    client: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    """Select widget blocks for one completed assistant turn."""
    if not events:
        return []

    gemini_client = client or get_gemini_client()
    response = gemini_client.models.generate_content(
        model=model,
        contents=[_content_from_events(events)],
        config=types.GenerateContentConfig(
            tools=[
                types.Tool(
                    function_declarations=get_widget_function_declarations(),
                )
            ],
            temperature=0.1,
            max_output_tokens=min(config.APP_SETTINGS["MAX_TOKENS"], 3000),
            system_instruction=SELECTOR_SYSTEM_PROMPT,
        ),
    )

    blocks: List[Dict[str, Any]] = []
    for function_call in _extract_function_calls(response):
        block = _function_call_to_widget_block(function_call)
        if block:
            blocks.append(block)
    return blocks


def attach_widgets_to_final_assistant_message(
    messages: List[Dict[str, Any]],
    widget_blocks: Iterable[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Attach selected widget blocks to the final assistant message in-place."""
    blocks_to_add = list(widget_blocks)
    if not blocks_to_add:
        return messages

    for message in reversed(messages):
        if message.get("role") != "assistant":
            continue
        if message.get("tool_calls"):
            continue

        existing_blocks = message.get("blocks")
        if not isinstance(existing_blocks, list):
            existing_blocks = []
            content = message.get("content")
            if isinstance(content, str) and content.strip():
                existing_blocks.append({"kind": "text", "text": content})

        message["blocks"] = [*existing_blocks, *blocks_to_add]
        return messages

    return messages
