"""
Configuration Module for Virtual Assistant

This module centralizes configuration settings for the assistant,
including API keys, service endpoints, application settings, and validation.
"""

import os
import logging
from typing import Any, Optional
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file if it exists
load_dotenv(override=True)


class ConfigurationManager:
    """
    Centralized configuration manager for the virtual assistant.

    This class handles all configuration-related functionality including
    environment variable loading, validation, and providing access to
    application settings.
    """

    def __init__(self):
        """Initialize the configuration manager and validate settings."""
        self._load_api_credentials()
        self._load_application_settings()
        self._validate_critical_configuration()

    def _load_api_credentials(self) -> None:
        """Load API credentials from environment variables."""
        self.api_credentials = {
            "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
            "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
            "AGENTMAIL_API_KEY": os.getenv("AGENTMAIL_API_KEY"),
            "HAPPENSTANCE_API_KEY": os.getenv("HAPPENSTANCE_API_KEY"),
        }

    def _load_application_settings(self) -> None:
        """Load application-specific settings."""
        self.app_settings = {
            "DEBUG": os.getenv("DEBUG", "True").lower() == "true",
            "HOST": os.getenv("HOST", "127.0.0.1"),
            "PORT": int(os.getenv("PORT", "8000")),
            "TOOLS_FILE": "tools.py",
            "DEFAULT_LLM_MODEL_DEPLOYMENT": os.getenv(
                "DEFAULT_LLM_MODEL",
                "gemini-3-flash-preview",
            ),
            "WIDGET_SELECTOR_MODEL": os.getenv(
                "WIDGET_SELECTOR_MODEL",
                os.getenv("DEFAULT_LLM_MODEL", "gemini-3-flash-preview"),
            ),
            "WIDGET_SELECTOR_ENABLED": os.getenv(
                "WIDGET_SELECTOR_ENABLED",
                "true",
            ).lower() not in {"0", "false", "no", "off"},
            "MAX_TOKENS": int(os.getenv("MAX_TOKENS", "4000")),
            "TEMPERATURE": float(os.getenv("TEMPERATURE", "0.7")),
            "REQUEST_TIMEOUT": int(os.getenv("REQUEST_TIMEOUT", "30")),
            "SQLITE_DB_PATH": os.getenv(
                "SQLITE_DB_PATH",
                os.path.join("data", "workmind.db"),
            ),
            "AGENTMAIL_INBOX_ID": os.getenv("AGENTMAIL_INBOX_ID"),
        }

    def _validate_critical_configuration(self) -> None:
        """
        Validate that critical configuration settings are present.

        Raises:
            EnvironmentError: If any required configuration is missing
        """
        missing_keys = []

        if not (
            self.api_credentials.get("GEMINI_API_KEY")
            or self.api_credentials.get("GOOGLE_API_KEY")
        ):
            missing_keys.append("GEMINI_API_KEY or GOOGLE_API_KEY")

        # Raise error if any required keys are missing
        if missing_keys:
            error_msg = (
                "Missing required environment variables: "
                f"{', '.join(missing_keys)}"
            )
            logger.error(error_msg)
            raise EnvironmentError(error_msg)

        logger.info("Configuration validation completed successfully")

    def get_api_credential(self, key: str) -> Optional[str]:
        """
        Get an API credential by key.

        Args:
            key: The credential key to retrieve

        Returns:
            Optional[str]: The credential value or None if not found
        """
        return self.api_credentials.get(key)

    def get_app_setting(self, key: str, default: Any = None) -> Any:
        """
        Get an application setting by key.

        Args:
            key: The setting key to retrieve
            default: Default value if setting is not found

        Returns:
            Any: The setting value or default
        """
        return self.app_settings.get(key, default)

    def is_debug_mode(self) -> bool:
        """Check if the application is running in debug mode."""
        return self.app_settings.get("DEBUG", False)


# Global configuration instance
config_manager = ConfigurationManager()

# Legacy compatibility - maintaining old variable names for backward compatibility
API_KEYS = config_manager.api_credentials
APP_SETTINGS = config_manager.app_settings

def get_project_root() -> str:
    """
    Get the project root directory path.

    Returns:
        str: Absolute path to the project root directory
    """
    # Assuming this config.py file is in the project root
    return os.path.dirname(os.path.abspath(__file__))


def get_log_level() -> int:
    """
    Get the logging level from environment variables.

    Returns:
        int: Logging level (default: INFO)
    """
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    return log_levels.get(log_level_str, logging.INFO)


def update_logging_configuration() -> None:
    """Update logging configuration based on current settings."""
    log_level = get_log_level()

    # Update the root logger level
    logging.getLogger().setLevel(log_level)

    # Update format for better debugging if in debug mode
    if config_manager.is_debug_mode():
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(message)s"
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    # Apply formatter to all handlers
    for handler in logging.getLogger().handlers:
        handler.setFormatter(formatter)

    logger.info(
        "Logging configuration updated - Level: %s",
        logging.getLevelName(log_level),
    )


# Legacy function for backward compatibility
def validate_config() -> None:
    """
    Legacy function for validating configuration.

    This function is maintained for backward compatibility.
    New code should use ConfigurationManager.validate_critical_configuration() instead.
    """
    config_manager._validate_critical_configuration()


# Initialize logging configuration
update_logging_configuration()

# Log successful configuration loading
logger.info("Configuration module loaded successfully")
logger.debug(f"Application settings: {APP_SETTINGS}")
logger.debug(f"API credentials loaded: {list(API_KEYS.keys())}")
