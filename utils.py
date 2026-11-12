"""
Utility Functions Module

This module provides common utility functions for the virtual assistant,
including JSON processing, response formatting, validation, and conversation
formatting for API responses.
"""

import json
import logging
from typing import Dict, Any, List, Union, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def clean_json_data(input_json: Union[Dict, str]) -> Dict:
    """
    Clean and normalize JSON data from various input formats.
    
    This function handles JSON data that may come in as either a dictionary
    or a JSON string, and ensures that nested JSON strings (particularly
    in the 'data' field) are properly parsed.
    
    Args:
        input_json: Either a dictionary or a JSON string to be cleaned
        
    Returns:
        Dict: Normalized dictionary with properly parsed fields
        
    Example:
        >>> data = '{"data": "[1,2,3]", "type": "success"}'
        >>> cleaned = clean_json_data(data)
        >>> print(cleaned["data"])  # [1, 2, 3] (as list, not string)
    """
    # Convert input to dictionary if it's a string
    if isinstance(input_json, dict):
        data_dict = input_json
    else:
        try:
            data_dict = json.loads(input_json)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse input JSON: {e}")
            return {"error": "Invalid JSON format"}

    # Ensure the 'data' field is properly parsed if it's a JSON string
    if isinstance(data_dict.get("data"), str):
        try:
            data_dict["data"] = json.loads(data_dict["data"])  # Convert string to proper data structure
            logger.debug("Successfully parsed 'data' field from JSON string")
        except json.JSONDecodeError:
            logger.warning("Failed to parse 'data' field as JSON, keeping as string")
            # If parsing fails, keep the original string value

    return data_dict


def create_error_response(message: str, details: Optional[Any] = None) -> Dict[str, Any]:
    """
    Create a standardized error response dictionary.
    
    This function ensures all error responses follow a consistent format
    throughout the application, making error handling more predictable.
    
    Args:
        message: The main error message describing what went wrong
        details: Optional additional details about the error (exception info, stack trace, etc.)
        
    Returns:
        Dict[str, Any]: A standardized error response dictionary
        
    Example:
        >>> error = create_error_response("Database connection failed", "Connection timeout after 30s")
        >>> print(error)
        {'type': 'error', 'data': {'message': 'Database connection failed', 'details': 'Connection timeout after 30s'}}
    """
    response = {
        "type": "error",
        "data": {
            "message": message
        }
    }
    
    if details:
        response["data"]["details"] = details
        
    logger.debug(f"Created error response: {message}")
    return response


def create_success_response(data: Any, message: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a standardized success response dictionary.
    
    Args:
        data: The main response data (query results, processed information, etc.)
        message: Optional success message to include
        
    Returns:
        Dict[str, Any]: A standardized success response dictionary
        
    Example:
        >>> result = create_success_response([{"id": 1, "name": "John"}], "Query executed successfully")
        >>> print(result["type"])  # "success"
    """
    response = {
        "type": "success",
        "data": data
    }
    
    if message:
        response["message"] = message
        
    logger.debug("Created success response")
    return response


def create_text_response(text: str) -> Dict[str, Any]:
    """
    Create a standardized text response dictionary.
    
    Used for simple text responses that don't fit into success/error categories.
    
    Args:
        text: The text content to include in the response
        
    Returns:
        Dict[str, Any]: A standardized text response dictionary
    """
    return {
        "type": "text",
        "data": text
    }


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """
    Validate that all required fields are present and not None in a dictionary.
    
    Args:
        data: The dictionary to validate
        required_fields: List of field names that must be present and not None
        
    Returns:
        List[str]: List of missing field names (empty list if all fields are present)
        
    Example:
        >>> data = {"name": "John", "age": None, "email": "john@example.com"}
        >>> missing = validate_required_fields(data, ["name", "age", "phone"])
        >>> print(missing)  # ["age", "phone"]
    """
    missing_fields = []
    
    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)
    
    if missing_fields:
        logger.warning(f"Missing required fields: {missing_fields}")
    
    return missing_fields 


def format_conversation_for_response(conversation: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Format a conversation for API response, handling various message types and tool responses.
    
    This function processes a conversation that may contain:
    - Regular chat messages
    - Tool call responses with data
    - Error responses from failed tool calls
    - Gemini or legacy completion-like message objects
    
    System messages are excluded from the response to avoid returning internal prompt information to users.
    
    Args:
        conversation: List of conversation messages in various formats
        
    Returns:
        List[Dict[str, Any]]: Formatted conversation ready for API response (excluding system messages)
    """
    formatted_messages = []
    
    for message in conversation:
        # Skip system messages - don't return them to the user
        if isinstance(message, dict) and message.get("role") == "system":
            continue
            
        if isinstance(message, dict):
            formatted_message = process_dict_message(message)
            if formatted_message:
                formatted_messages.append(formatted_message)
        else:
            # Handle ChatCompletionMessage objects or other non-dict types
            formatted_message = process_completion_message(message)
            if formatted_message:
                formatted_messages.append(formatted_message)
    
    return formatted_messages


def process_dict_message(message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Process a dictionary message and format it appropriately.
    
    Args:
        message: Dictionary message to process
        
    Returns:
        Optional[Dict[str, Any]]: Formatted message or None if processing fails
    """
    # Skip system messages - they should not be returned to users
    if message.get("role") == "system":
        return None
        
    # Handle tool responses.
    if message.get("role") == "tool":
        return process_tool_response(message)
    
    # Handle regular messages (user, assistant)
    return message


def process_tool_response(tool_message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Process a tool response message.
    
    Args:
        tool_message: Tool response message to process
        
    Returns:
        Optional[Dict[str, Any]]: Formatted tool response
    """
    # Get the original content if available, otherwise parse the content
    tool_content = tool_message.get("_original_content")
    if tool_content is None:
        content = tool_message.get("content")
        if isinstance(content, str):
            try:
                tool_content = json.loads(content)
            except json.JSONDecodeError:
                tool_content = content
        else:
            tool_content = content
    
    if isinstance(tool_content, dict) and tool_content.get("type") == "error":
        return format_tool_error_response(tool_content)
    
    return {
        **tool_message,
        "content": str(tool_content)
    }


def format_tool_error_response(tool_content: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a tool error response for display.
    
    Args:
        tool_content: Tool error response content
        
    Returns:
        Dict[str, Any]: Formatted error message
    """
    error_message = tool_content.get('data', {}).get('message', 'Unknown error occurred')
    return {
        "role": "assistant",
        "content": f"Error: {error_message}"
    }


def process_completion_message(completion_message) -> Optional[Dict[str, Any]]:
    """
    Process ChatCompletion messages with potential tool calls.
    
    Args:
        completion_message: ChatCompletion message object
        
    Returns:
        Optional[Dict[str, Any]]: Formatted message or None
    """
    # Handle messages with tool calls
    if hasattr(completion_message, 'tool_calls') and completion_message.tool_calls:
        return process_tool_calls(completion_message.tool_calls)
    
    # Handle messages with regular content
    elif hasattr(completion_message, 'content') and completion_message.content:
        return {
            "role": "assistant",
            "content": completion_message.content
        }
    
    return None


def process_tool_calls(tool_calls) -> Dict[str, Any]:
    """
    Process tool calls from a ChatCompletion message.
    
    Args:
        tool_calls: List of tool calls from ChatCompletion
        
    Returns:
        Dict[str, Any]: Formatted message with tool call information
    """
    # For now, just return the first tool call information
    # This could be enhanced to handle multiple tool calls
    if tool_calls:
        tool_call = tool_calls[0]
        if tool_call.type == 'function' and hasattr(tool_call, 'function'):
            try:
                arguments = json.loads(tool_call.function.arguments)
                return {
                    "role": "assistant",
                    "content": f"Function: {tool_call.function.name}\nArguments: {arguments}"
                }
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse function arguments: {tool_call.function.arguments}")
                return {
                    "role": "assistant",
                    "content": f"Function: {tool_call.function.name}\nArguments: {tool_call.function.arguments}"
                }
    
    return {
        "role": "assistant",
        "content": "Tool call processed"
    }


# Backward compatibility aliases for old function names
format_success_response = create_success_response
format_error_response = create_error_response
