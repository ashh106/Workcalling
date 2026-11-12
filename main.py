"""FastAPI server for the Workmind assistant."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Iterator, List, Optional
import queue
import threading

from fastapi import FastAPI, HTTPException, WebSocket, UploadFile, File, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool
import os
import tempfile
import shutil
import voice_processor

import config
import prompt
import functioncalling
import utils
import widget_selector
import yaml_crud

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app instance
app = FastAPI(
    title="Virtual Assistant API",
    description=(
        "API for the virtual assistant that processes user queries "
        "and handles function calls"
    ),
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Pydantic models for request/response
class Message(BaseModel):
    """Model for individual chat messages."""

    role: str
    content: str = ""
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None

    class Config:
        """Pydantic configuration."""
        extra = "allow"


class TTSRequest(BaseModel):
    """Model for text-to-speech request."""
    text: str
    language_code: str = "en-IN"
    speaker: str = "shubh"


class ChatRequest(BaseModel):
    """Model for chat request containing list of messages."""

    messages: List[Message]


class WidgetSelectRequest(BaseModel):
    """Model for selecting widgets from one completed assistant turn."""

    events: List[Dict[str, Any]]


class ChatResponse(BaseModel):
    """Model for chat response containing processed messages and status."""

    messages: List[Dict[str, Any]]
    success: bool = True
    error: str = None


def process_user_conversation(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process a user conversation through Gemini and return the complete history.

    ``functioncalling`` owns Gemini content conversion, tool execution, and the
    multi-turn function-response loop. This wrapper preserves the existing
    main.py API shape.
    """
    new_messages = functioncalling.run_gemini_tool_loop(messages)
    return [*messages, *new_messages]


def extract_new_messages_from_conversation(
    original_messages: List[Dict],
    updated_conversation: List[Dict],
) -> List[Dict]:
    """
    Extract only the new messages that were added during conversation processing.

    Args:
        original_messages: The original list of messages before processing
        updated_conversation: The complete conversation after processing

    Returns:
        List[Dict]: Only the new messages that were added during processing
    """
    new_messages = []
    for message in updated_conversation:
        if message not in original_messages:
            new_messages.append(message)
    return new_messages

def process_chat_conversation(messages: List[Dict]) -> List[Dict]:
    """
    Process a complete chat conversation and return only new messages.

    Args:
        messages: List of message dictionaries from the chat request

    Returns:
        List[Dict]: New messages added during processing.
    """
    # Store original messages to identify what's new later
    original_messages = messages.copy()

    # Process the conversation through the language model and function calls
    complete_conversation = process_user_conversation(messages)

    # Extract only the new messages that were added during processing
    new_messages = extract_new_messages_from_conversation(
        original_messages,
        complete_conversation,
    )

    # Format only the new messages for API response
    formatted_new_messages = utils.format_conversation_for_response(new_messages)

    return formatted_new_messages


@app.post("/voice/stt")
async def handle_stt(file: UploadFile = File(...)):
    """Convert uploaded audio file to text."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    
    try:
        text = await run_in_threadpool(voice_processor.speech_to_text, tmp_path)
        return {"text": text}
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.post("/voice/tts")
async def handle_tts(request: TTSRequest):
    """Convert text to speech audio."""
    audio_content = await run_in_threadpool(voice_processor.text_to_speech, request.text, request.language_code, request.speaker)
    if audio_content:
        return Response(content=audio_content, media_type="audio/wav")
    else:
        raise HTTPException(status_code=500, detail="TTS Failed")


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time chat with tool execution feedback."""
    print("WEBSOCKET CONNECTION ATTEMPTED!")
    await websocket.accept()
    print("WEBSOCKET ACCEPTED!")
    try:
        while True:
            data = await websocket.receive_text()
            request_data = json.loads(data)
            messages = request_data.get("messages", [])
            
            # Convert incoming messages
            raw_messages = [Message(**m).dict(exclude_none=True) for m in messages]
            prepared_messages = ensure_system_prompt_in_conversation(raw_messages)
            
            def consume_stream(q, msgs):
                try:
                    for event in functioncalling.stream_gemini_tool_loop(msgs):
                        q.put(event)
                    q.put({"done": True})
                except Exception as e:
                    q.put({"error": str(e)})

            q = queue.Queue()
            thread = threading.Thread(target=consume_stream, args=(q, prepared_messages))
            thread.start()

            results = []
            turn_events = []
            while True:
                event = await run_in_threadpool(q.get)
                if "done" in event:
                    break
                if "error" in event:
                    logger.error(f"Error in stream: {event['error']}")
                    break
                
                turn_events.append(event)

                if event["event"] == "tool_call":
                    tool_call = event["tool_call"]
                    await websocket.send_json({
                        "type": "hint",
                        "content": f"Calling tool: {tool_call.get('function', {}).get('name')}...",
                        "tool": tool_call.get("function", {}).get("name")
                    })
                elif event["event"] == "assistant_message":
                    results.append(event["message"])
                elif event["event"] == "tool_result":
                    results.append(event["message"])

            has_final_assistant_message = any(
                message.get("role") == "assistant" and not message.get("tool_calls")
                for message in results
            )
            if config.APP_SETTINGS["WIDGET_SELECTOR_ENABLED"] and has_final_assistant_message:
                try:
                    widget_blocks = await run_in_threadpool(
                        widget_selector.select_widgets_for_turn,
                        turn_events,
                    )
                    widget_selector.attach_widgets_to_final_assistant_message(
                        results,
                        widget_blocks,
                    )
                except Exception as exc:
                    logger.error("Widget selector failed: %s", exc)
            
            formatted_new_messages = utils.format_conversation_for_response(results)
            
            await websocket.send_json({
                "type": "response",
                "messages": formatted_new_messages
            })
            
    except Exception as e:
        if "1006" not in str(e):
            logger.error(f"WebSocket error: {str(e)}")
    finally:
        try:
            await websocket.close()
        except RuntimeError:
            pass


def _sse_event(event_name: str, data: Dict[str, Any]) -> str:
    """Serialize one Server-Sent Event frame."""
    return (
        f"event: {event_name}\n"
        f"data: {json.dumps(data, default=str)}\n\n"
    )


def _format_stream_payload(event: Dict[str, Any]) -> Dict[str, Any]:
    """Shape tool-loop events for streaming clients."""
    event_name = event["event"]
    payload: Dict[str, Any] = {"type": event_name}

    if "message" in event:
        message = event["message"]
        formatted_message = utils.process_dict_message(message)
        payload["message"] = formatted_message or message

    if "tool_call" in event:
        payload["tool_call"] = event["tool_call"]

    return payload


def stream_chat_conversation(messages: List[Dict[str, Any]]) -> Iterator[str]:
    """Yield chat results as complete SSE message/tool events."""
    try:
        for event in functioncalling.stream_gemini_tool_loop(messages):
            yield _sse_event(event["event"], _format_stream_payload(event))
        yield _sse_event("done", {"type": "done", "success": True})

    except functioncalling.ToolLoopLimitError as exc:
        logger.error("Tool loop limit exceeded: %s", exc)
        yield _sse_event(
            "error",
            {
                "type": "error",
                "success": False,
                "error": str(exc),
            },
        )

    except Exception as exc:
        logger.error("Error streaming chat request: %s", exc)
        yield _sse_event(
            "error",
            {
                "type": "error",
                "success": False,
                "error": str(exc),
            },
        )


def _model_to_dict(model: BaseModel) -> Dict[str, Any]:
    """Return a dict for Pydantic v1 or v2 models."""
    if hasattr(model, "model_dump"):
        return model.model_dump(exclude_none=True)
    return model.dict(exclude_none=True)


@app.get("/")
async def get_api_information():
    """Root endpoint that returns API information and documentation."""
    return {
        "message": "Virtual Assistant API",
        "version": "1.0.0",
        "description": (
            "API for processing chat conversations with database "
            "analysis capabilities"
        ),
        "endpoints": {
            "chat": {
                "path": "/chat",
                "method": "POST",
                "description": (
                    "Main chat endpoint - processes conversations with "
                    "system prompt injection"
                )
            },
            "chat_stream": {
                "path": "/chat/stream",
                "method": "POST",
                "description": (
                    "Streaming chat endpoint - emits complete assistant "
                    "messages, tool calls, and tool results as SSE events"
                )
            },
            "widgets_select": {
                "path": "/widgets/select",
                "method": "POST",
                "description": (
                    "Select UI widget blocks for one completed assistant turn"
                )
            },
            "quick_query": {
                "path": "/quick-query",
                "method": "POST",
                "description": "Quick query endpoint for simple text queries"
            },
            "health": {
                "path": "/health",
                "method": "GET",
                "description": "Health check endpoint"
            }
        },
        "conversation_flow": [
            "1. Add system message with system prompt if not present",
            "2. Send conversation to language model for processing",
            "3. Handle any function calls and execute them",
            "4. Return the formatted conversation results (excluding system messages)"
        ]
    }

@app.get("/health")
async def check_api_health():
    """Health check endpoint to verify API status."""
    return {"status": "healthy", "service": "Virtual Assistant API"}


@app.post("/chat", response_model=ChatResponse)
async def handle_chat_conversation(request: ChatRequest):
    """
    Main chat endpoint that processes user conversations through the virtual assistant.
    """
    try:
        messages = [
            _model_to_dict(message)
            for message in request.messages
        ]

        validation_errors = validate_conversation_messages(messages)
        if validation_errors:
            error_message = "Message validation failed: " + "; ".join(validation_errors)
            logger.error(error_message)
            return ChatResponse(
                messages=[{
                    "role": "assistant",
                    "content": error_message
                }],
                success=False,
                error=error_message
            )

        prepared_messages = ensure_system_prompt_in_conversation(messages)

        logger.info(f"Processing conversation with {len(prepared_messages)} messages")
        conversation_results = process_chat_conversation(prepared_messages)

        return ChatResponse(
            messages=conversation_results,
            success=True
        )

    except functioncalling.ToolLoopLimitError as exc:
        logger.error("Tool loop limit exceeded: %s", exc)
        return ChatResponse(
            messages=[{
                "role": "assistant",
                "content": str(exc),
            }],
            success=False,
            error=str(exc),
        )

    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")

        error_response = utils.create_error_response(
            message="Failed to process chat request",
            details=str(e)
        )

        return ChatResponse(
            messages=[{
                "role": "assistant",
                "content": error_response["data"]["message"]
            }],
            success=False,
            error=str(e)
        )

@app.post("/chat/stream")
async def handle_chat_conversation_stream(request: ChatRequest):
    """
    Stream complete assistant/tool events for a chat conversation.
    """
    messages = [_model_to_dict(message) for message in request.messages]

    validation_errors = validate_conversation_messages(messages)
    if validation_errors:
        error_message = "Message validation failed: " + "; ".join(validation_errors)
        logger.error(error_message)

        def validation_error_stream() -> Iterator[str]:
            yield _sse_event(
                "error",
                {
                    "type": "error",
                    "success": False,
                    "error": error_message,
                    "message": {
                        "role": "assistant",
                        "content": error_message,
                    },
                },
            )

        return StreamingResponse(
            validation_error_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    prepared_messages = ensure_system_prompt_in_conversation(messages)
    logger.info(
        "Streaming conversation with %s prepared messages",
        len(prepared_messages),
    )

    return StreamingResponse(
        stream_chat_conversation(prepared_messages),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/widgets/select")
async def handle_widget_selection(request: WidgetSelectRequest):
    """Select widget blocks for a completed assistant turn."""
    try:
        widget_blocks = await run_in_threadpool(
            widget_selector.select_widgets_for_turn,
            request.events,
        )
        return {
            "success": True,
            "blocks": widget_blocks,
        }
    except Exception as exc:
        logger.error("Error selecting widgets: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=f"Error selecting widgets: {exc}",
        ) from exc


@app.post("/quick-query")
async def handle_quick_query(query: str):
    """
    Quick query endpoint for processing simple text queries.
    """
    try:
        messages = [
            {
                "role": "system",
                "content": prompt.system_prompt
            },
            {
                "role": "user",
                "content": query
            }
        ]

        conversation_results = process_chat_conversation(messages)

        return {
            "query": query,
            "response": conversation_results,
            "success": True
        }

    except functioncalling.ToolLoopLimitError as exc:
        logger.error("Tool loop limit exceeded: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    except Exception as e:
        logger.error(f"Error processing quick query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

def ensure_system_prompt_in_conversation(
    messages: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Ensure conversation starts with a system prompt message."""
    has_system_message = any(message.get("role") == "system" for message in messages)

    if not has_system_message:
        system_message = {
            "role": "system",
            "content": prompt.system_prompt
        }
        messages.insert(0, system_message)
        logger.info("Added system prompt to conversation")

    return messages

def validate_conversation_messages(messages: List[Dict[str, Any]]) -> List[str]:
    """Validate conversation messages for required fields and proper structure."""
    validation_errors = []

    if not messages:
        validation_errors.append("Messages list cannot be empty")
        return validation_errors

    valid_roles = ["system", "user", "assistant", "tool"]

    for index, message in enumerate(messages):
        missing_fields = utils.validate_required_fields(
            message,
            ["role", "content"],
        )
        if missing_fields:
            validation_errors.append(
                f"Message {index}: Missing required fields: {missing_fields}"
            )

        message_role = message.get("role")
        if message_role not in valid_roles:
            validation_errors.append(
                f"Message {index}: Invalid role '{message_role}'. "
                f"Must be one of: {valid_roles}"
            )

    return validation_errors

# Register YAML CRUD endpoints.
yaml_crud.register_yaml_crud(app)

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Virtual Assistant API server")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
