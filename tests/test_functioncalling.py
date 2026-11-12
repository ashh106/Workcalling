from types import SimpleNamespace

import pytest
from google.genai import types

import functioncalling
import utils


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


def make_text_response(text):
    content = types.Content(
        role="model",
        parts=[types.Part.from_text(text=text)],
    )
    return SimpleNamespace(
        text=text,
        function_calls=None,
        candidates=[SimpleNamespace(content=content)],
    )


def make_tool_response(name, args=None, call_id="call-1"):
    function_call = types.FunctionCall(name=name, args=args or {}, id=call_id)
    content = types.Content(
        role="model",
        parts=[types.Part(function_call=function_call)],
    )
    return SimpleNamespace(
        text="",
        function_calls=[function_call],
        candidates=[SimpleNamespace(content=content)],
    )


def test_openai_tool_schema_is_converted_for_gemini():
    declaration = functioncalling.openai_tool_to_gemini_declaration(
        {
            "type": "function",
            "function": {
                "name": "send",
                "description": "Send a message.",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "to": {
                            "anyOf": [
                                {"type": "string"},
                                {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            ],
                        },
                    },
                },
            },
        }
    )

    assert declaration["name"] == "send"
    assert "strict" not in declaration
    assert "additionalProperties" not in declaration["parameters"]
    assert declaration["parameters"]["properties"]["to"]["type"] == "string"
    assert "anyOf" not in declaration["parameters"]["properties"]["to"]


def test_app_messages_to_gemini_contents_preserves_system_instruction():
    contents, system_instruction = functioncalling.app_messages_to_gemini_contents(
        [
            {"role": "system", "content": "Be concise."},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
        ]
    )

    assert system_instruction == "Be concise."
    assert [content.role for content in contents] == ["user", "model"]
    assert contents[0].parts[0].text == "Hello"
    assert contents[1].parts[0].text == "Hi"


def test_single_tool_call_flow(monkeypatch):
    client = FakeClient(
        [
            make_tool_response(
                "execute_sql_query",
                {"sql_query": "select 1", "explanation": "Test query"},
            ),
            make_text_response("The answer is 1."),
        ]
    )
    monkeypatch.setattr(
        functioncalling.router,
        "execute_function_call",
        lambda name, args: utils.create_success_response({"rows": [{"x": 1}]}),
    )

    messages = functioncalling.run_gemini_tool_loop(
        [{"role": "user", "content": "Run a test query"}],
        client=client,
    )

    assert [message["role"] for message in messages] == [
        "assistant",
        "tool",
        "assistant",
    ]
    assert messages[-1]["content"] == "The answer is 1."
    assert len(client.models.calls) == 2


def test_stream_tool_loop_yields_complete_step_events(monkeypatch):
    client = FakeClient(
        [
            make_tool_response(
                "execute_sql_query",
                {"sql_query": "select 1", "explanation": "Test query"},
            ),
            make_text_response("The answer is 1."),
        ]
    )
    monkeypatch.setattr(
        functioncalling.router,
        "execute_function_call",
        lambda name, args: utils.create_success_response({"rows": [{"x": 1}]}),
    )

    events = list(
        functioncalling.stream_gemini_tool_loop(
            [{"role": "user", "content": "Run a test query"}],
            client=client,
        )
    )

    assert [event["event"] for event in events] == [
        "assistant_message",
        "tool_call",
        "tool_result",
        "assistant_message",
    ]
    assert events[1]["tool_call"]["function"]["name"] == "execute_sql_query"
    assert events[-1]["message"]["content"] == "The answer is 1."
    assert len(client.models.calls) == 2


def test_multi_turn_tool_call_flow(monkeypatch):
    client = FakeClient(
        [
            make_tool_response("agentmail_list_inboxes", {}, "call-1"),
            make_tool_response(
                "agentmail_list_messages",
                {"inbox_id": "inbox-1"},
                "call-2",
            ),
            make_text_response("Found the message."),
        ]
    )
    monkeypatch.setattr(
        functioncalling.router,
        "execute_function_call",
        lambda name, args: utils.create_success_response({"tool": name}),
    )

    messages = functioncalling.run_gemini_tool_loop(
        [{"role": "user", "content": "Check mail"}],
        client=client,
    )

    assert len(client.models.calls) == 3
    assert messages[-1]["content"] == "Found the message."
    assert [message["role"] for message in messages].count("tool") == 2


def test_tool_loop_limit(monkeypatch):
    client = FakeClient(
        [
            make_tool_response(
                "execute_sql_query",
                {"sql_query": "select 1", "explanation": "Test query"},
                f"call-{index}",
            )
            for index in range(3)
        ]
    )
    monkeypatch.setattr(
        functioncalling.router,
        "execute_function_call",
        lambda name, args: utils.create_success_response({"ok": True}),
    )

    with pytest.raises(functioncalling.ToolLoopLimitError):
        functioncalling.run_gemini_tool_loop(
            [{"role": "user", "content": "Loop"}],
            max_tool_turns=1,
            client=client,
        )


def test_unknown_tool_returns_clean_error():
    function_call = types.FunctionCall(name="missing_tool", args={})

    result = functioncalling._execute_function_call(function_call)

    assert result["type"] == "error"
    assert "missing_tool" in result["data"]["message"]
