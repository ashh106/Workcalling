import os
import logging
import base64
import re
from typing import Optional
from dotenv import load_dotenv
from sarvamai import SarvamAI

load_dotenv()

logger = logging.getLogger(__name__)

def get_sarvam_client() -> Optional[SarvamAI]:
    key = os.getenv("SARVAM_API_KEY")
    if not key:
        return None
    return SarvamAI(api_subscription_key=key)

def speech_to_text(audio_file_path: str, language_code: str = "en-IN") -> Optional[str]:
    """
    Convert speech to text using Sarvam AI Saaras v3 via the Python SDK.
    """
    client = get_sarvam_client()
    if not client:
        logger.error("SARVAM_API_KEY not found in environment")
        return None

    if not os.path.exists(audio_file_path):
        logger.error(f"Error: The file '{audio_file_path}' was not found.")
        return None

    try:
        with open(audio_file_path, "rb") as audio_file:
            response = client.speech_to_text.transcribe(
                file=audio_file,
                model="saaras:v3",
                mode="transcribe",
                language_code=language_code
            )
            return response.transcript
    except Exception as e:
        logger.error(f"Exception in Sarvam STT: {str(e)}")
        return None

def clean_text_for_speech(text: str) -> str:
    """Remove markdown and truncate for TTS limits."""
    # Remove common markdown symbols that sound bad when spoken
    for char in ['*', '#', '`', '_', '~']:
        text = text.replace(char, '')
    
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    
    text = text.strip()
    
    if len(text) > 490:
        truncated = text[:490]
        # Try to find a good breaking point
        break_chars = ['.', '?', '!', '\n']
        best_break = -1
        for char in break_chars:
            pos = truncated.rfind(char)
            if pos > best_break:
                best_break = pos
                
        if best_break > 0:
            text = truncated[:best_break+1]
        else:
            # If no punctuation, just cut at the last space
            last_space = truncated.rfind(' ')
            if last_space > 0:
                text = truncated[:last_space]
            else:
                text = truncated
                
    return text.strip()

def text_to_speech(text: str, language_code: str = "en-IN", speaker: str = "shubh") -> Optional[bytes]:
    """
    Convert text to speech using Sarvam AI Bulbul v3 via the Python SDK.
    """
    client = get_sarvam_client()
    if not client:
        logger.error("SARVAM_API_KEY not found in environment")
        return None

    clean_text = clean_text_for_speech(text)
    if not clean_text:
        return None

    try:
        response = client.text_to_speech.convert(
            target_language_code=language_code,
            text=clean_text,
            model="bulbul:v3",
            speaker=speaker
        )
        
        if hasattr(response, 'audios') and response.audios:
            return base64.b64decode(response.audios[0])
        else:
            logger.error("No audio found in Sarvam JSON response")
            return None
    except Exception as e:
        logger.error(f"Exception in Sarvam TTS: {str(e)}")
        return None
