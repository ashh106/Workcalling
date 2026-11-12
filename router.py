"""
Function Router Module

This module provides centralized routing for function calls in the virtual assistant.
It maps function names to their implementations and handles execution with proper
error handling and logging.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple

import utils
from tool.database.connector import sqlitedb
from tool.browser.automation import run_browser_automation
from tool.agentmail import mail as agentmail_mail
from tool.happenstance.research import happenstance_research

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Function routing registry - Maps function names to their implementations
# Organized by category for better maintainability and readability
FUNCTION_REGISTRY = {
    # Database query functions
    "execute_sql_query": sqlitedb.run_query,
    # Browser automation functions
    "execute_browser_task": run_browser_automation,
    # AgentMail (https://docs.agentmail.to/)
    "agentmail_list_inboxes": agentmail_mail.agentmail_list_inboxes,
    "agentmail_list_threads": agentmail_mail.agentmail_list_threads,
    "agentmail_list_messages": agentmail_mail.agentmail_list_messages,
    "agentmail_search_messages": agentmail_mail.agentmail_search_messages,
    "agentmail_get_message": agentmail_mail.agentmail_get_message,
    "agentmail_send_message": agentmail_mail.agentmail_send_message,
    "agentmail_reply_to_message": agentmail_mail.agentmail_reply_to_message,
    # Happenstance (https://api.happenstance.ai/)
    "happenstance_research": happenstance_research,
}

logger.info(f"Function registry initialized with {len(FUNCTION_REGISTRY)} available functions")


def execute_function_call(function_name: str, function_arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Route and execute a function call to the appropriate implementation.
    
    This function serves as the central dispatcher that routes function calls
    to their appropriate handlers based on the function name. It provides
    comprehensive error handling and logging for all function executions.
    
    Args:
        function_name: The name of the function to call (must match a key in FUNCTION_REGISTRY)
        function_arguments: A dictionary of arguments to pass to the function
    
    Returns:
        Optional[Dict[str, Any]]: The response from the executed function, or None if execution failed
        
    Example:
        >>> result = execute_function_call("execute_sql_query", {"sql_query": "SELECT * FROM users LIMIT 5", "explanation": "Preview users"})
        >>> if result:
        ...     print(f"Query executed successfully: {result}")
    """
    try:
        # Check if the requested function exists in our registry
        if function_name not in FUNCTION_REGISTRY:
            error_message = f"Function '{function_name}' not found in registry"
            logger.warning(error_message)
            return utils.create_error_response(error_message)
        
        # Get the function handler from registry
        function_handler = FUNCTION_REGISTRY[function_name]
        logger.info(f"Routing function call to: {function_name}")
        logger.debug(f"Function arguments: {function_arguments}")
        
        # Execute the function with provided arguments
        execution_result = function_handler(**function_arguments)
        logger.info(f"Function '{function_name}' executed successfully")
        
        return execution_result
        
    except TypeError as e:
        # Handle cases where function arguments don't match the function signature
        error_message = f"Invalid arguments for function '{function_name}': {str(e)}"
        logger.error(error_message)
        return utils.create_error_response(
            message=f"Invalid arguments for function '{function_name}'",
            details=str(e)
        )
        
    except Exception as e:
        # Handle any other errors during function execution
        error_message = f"Error executing function '{function_name}': {str(e)}"
        logger.error(error_message)
        return utils.create_error_response(
            message=f"Error executing function '{function_name}'", 
            details=str(e)
        )


def get_available_functions() -> List[str]:
    """
    Get a list of all available function names that can be called.
    
    Returns:
        List[str]: List of available function names
    """
    return list(FUNCTION_REGISTRY.keys())


def get_function_categories() -> Dict[str, List[str]]:
    """
    Get functions organized by category for better understanding and documentation.
    
    Returns:
        Dict[str, List[str]]: Dictionary mapping categories to lists of function names
    """
    categories = {
        "database": [
            "execute_sql_query"
        ],
        "browser": [
            "execute_browser_task"
        ],
        "agentmail": [
            "agentmail_list_inboxes",
            "agentmail_list_threads",
            "agentmail_list_messages",
            "agentmail_search_messages",
            "agentmail_get_message",
            "agentmail_send_message",
            "agentmail_reply_to_message",
        ],
        "happenstance": [
            "happenstance_research",
        ],
    }
    return categories


def validate_function_call(function_name: str, function_arguments: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate a function call before execution.
    
    Args:
        function_name: Name of the function to validate
        function_arguments: Arguments to validate
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message). error_message is empty if valid.
    """
    # Check if function exists
    if function_name not in FUNCTION_REGISTRY:
        return False, f"Function '{function_name}' not found in registry"
    
    # Check if arguments is a dictionary
    if not isinstance(function_arguments, dict):
        return False, f"Function arguments must be a dictionary, got {type(function_arguments)}"
    
    # Additional validation could be added here for specific functions
    return True, ""


if __name__ == "__main__":
    # Example usage and testing
    logger.info("Function router module loaded successfully")
    
    # Print available functions for debugging
    available_functions = get_available_functions()
    logger.info(f"Available functions: {available_functions}")
    
    # Print function categories
    categories = get_function_categories()
    for category, functions in categories.items():
        logger.info(f"{category.title()} functions: {functions}")
            
        
        









