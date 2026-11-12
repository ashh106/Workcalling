from types import SimpleNamespace

from google.genai import types

import widget_selector


class FakeModels:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        return self.responses.pop(0)


class FakeClient:
    def __init__(self, responses):
        self.models = FakeModels(responses)


def make_selector_response(*calls):
    content = types.Content(
        role="model",
        parts=[types.Part(function_call=call) for call in calls],
    )
    return SimpleNamespace(
        text="",
        function_calls=list(calls),
        candidates=[SimpleNamespace(content=content)],
    )


def test_selector_receives_only_current_turn_events():
    client = FakeClient(
        [
            make_selector_response(
                types.FunctionCall(
                    name="stats_display",
                    args={"title": "KPIs", "data": {"stats": [{"label": "Rows", "value": 3}]}},
                    id="widget-1",
                )
            )
        ]
    )
    events = [
        {"event": "tool_call", "tool_call": {"function": {"name": "execute_sql_query"}}},
        {"event": "tool_result", "message": {"role": "tool", "content": '{"rows": [1, 2, 3]}'}},
        {"event": "assistant_message", "message": {"role": "assistant", "content": "There are 3 rows."}},
    ]

    blocks = widget_selector.select_widgets_for_turn(events, client=client)

    assert blocks == [
        {
            "kind": "widget",
            "widget": {
                "type": "stats-display",
                "title": "KPIs",
                "data": {"stats": [{"label": "Rows", "value": 3}]},
            },
        }
    ]
    sent_contents = client.models.calls[0]["contents"]
    assert len(sent_contents) == 1
    sent_text = sent_contents[0].parts[0].text
    assert "execute_sql_query" in sent_text
    assert "There are 3 rows." in sent_text
    assert "previous user question" not in sent_text


def test_selector_supports_parallel_widget_calls():
    client = FakeClient(
        [
            make_selector_response(
                types.FunctionCall(
                    name="data_table",
                    args={"title": "Rows", "data": {"rows": [{"name": "A", "value": 1}]}},
                    id="widget-1",
                ),
                types.FunctionCall(
                    name="bar_chart",
                    args={"title": "Chart", "data": {"rows": [{"name": "A", "value": 1}]}},
                    id="widget-2",
                ),
            )
        ]
    )

    blocks = widget_selector.select_widgets_for_turn(
        [{"event": "assistant_message", "message": {"role": "assistant", "content": "A is 1."}}],
        client=client,
    )

    assert [block["widget"]["type"] for block in blocks] == ["data-table", "bar-chart"]
    assert blocks[1]["widget"]["data"] == [{"name": "A", "value": 1}]


def test_invalid_selector_calls_are_skipped():
    client = FakeClient(
        [
            make_selector_response(
                types.FunctionCall(
                    name="missing_widget",
                    args={"title": "Nope", "data": {"rows": []}},
                    id="widget-1",
                ),
                types.FunctionCall(
                    name="data_table",
                    args={"title": "Missing data"},
                    id="widget-2",
                ),
            )
        ]
    )

    blocks = widget_selector.select_widgets_for_turn(
        [{"event": "assistant_message", "message": {"role": "assistant", "content": "Plain."}}],
        client=client,
    )

    assert blocks == []


def test_attach_widgets_to_final_assistant_message_only():
    messages = [
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [{"function": {"name": "execute_sql_query"}}],
        },
        {"role": "tool", "content": "{}"},
        {"role": "assistant", "content": "Final answer."},
    ]
    widget_blocks = [
        {
            "kind": "widget",
            "widget": {"type": "data-table", "data": {"rows": []}},
        }
    ]

    widget_selector.attach_widgets_to_final_assistant_message(messages, widget_blocks)

    assert "blocks" not in messages[0]
    assert messages[-1]["blocks"] == [
        {"kind": "text", "text": "Final answer."},
        {"kind": "widget", "widget": {"type": "data-table", "data": {"rows": []}}},
    ]
