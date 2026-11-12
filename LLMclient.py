"""Gemini client helpers for Workmind."""

import logging
import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from google import genai

logger = logging.getLogger(__name__)


def get_gemini_api_key() -> str:
    """Return the configured Gemini API key."""
    load_dotenv(override=True)

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable is required "
            "(GOOGLE_API_KEY is also supported)."
        )
    return api_key


def get_gemini_client() -> genai.Client:
    """Initialize and return a Google GenAI client."""
    client = genai.Client(api_key=get_gemini_api_key())
    logger.info("Gemini client initialized successfully")
    return client


def get_language_model_response(conversation: List[Dict[str, Any]]) -> str:
    """
    Get a plain text response from Gemini without tool declarations.

    This helper is kept for compatibility with older imports. The main chat path
    uses ``functioncalling.run_gemini_tool_loop`` so tool calls can be handled.
    """
    from google.genai import types

    client = get_gemini_client()
    contents = [
        types.Content(
            role="model" if message.get("role") == "assistant" else "user",
            parts=[types.Part.from_text(text=str(message.get("content", "")))],
        )
        for message in conversation
        if message.get("role") != "system"
    ]
    system_instruction = "\n\n".join(
        str(message.get("content", ""))
        for message in conversation
        if message.get("role") == "system"
    ) or None

    response = client.models.generate_content(
        model=os.getenv("DEFAULT_LLM_MODEL", "gemini-3-flash-preview"),
        contents=contents,
        config=types.GenerateContentConfig(system_instruction=system_instruction),
    )
    return response.text or ""
