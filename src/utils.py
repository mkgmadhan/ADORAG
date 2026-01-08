"""Utility functions for the application."""

import logging
import os
from typing import Any, Dict

from dotenv import load_dotenv


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def load_config() -> Dict[str, Any]:
    """
    Load configuration from environment variables.

    Returns:
        Dictionary containing configuration values
    """
    load_dotenv()

    config = {
        # Azure DevOps
        "ado_organization": os.getenv("ADO_ORGANIZATION"),
        "ado_project_name": os.getenv("ADO_PROJECT_NAME"),
        "ado_pat": os.getenv("ADO_PAT"),
        # Azure OpenAI
        "openai_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "openai_api_key": os.getenv("AZURE_OPENAI_KEY"),
        "openai_api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
        "openai_embedding_deployment": os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small"),
        "openai_chat_deployment": os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o-mini"),
        # Azure AI Search
        "search_endpoint": os.getenv("AZURE_SEARCH_ENDPOINT"),
        "search_api_key": os.getenv("AZURE_SEARCH_KEY"),
        "search_index_name": os.getenv("AZURE_SEARCH_INDEX_NAME", "ado-workitems"),
        # Application
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
    }

    # Validate required fields
    required_fields = [
        "ado_organization",
        "ado_project_name",
        "ado_pat",
        "openai_endpoint",
        "openai_api_key",
        "search_endpoint",
        "search_api_key",
    ]

    missing_fields = [field for field in required_fields if not config.get(field)]

    if missing_fields:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_fields)}"
        )

    return config


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration values.

    Args:
        config: Configuration dictionary

    Returns:
        True if valid, raises ValueError otherwise
    """
    # Validate URLs
    if not config["ado_organization"].startswith("https://"):
        raise ValueError("ADO_ORGANIZATION must be a valid HTTPS URL")

    if not config["openai_endpoint"].startswith("https://"):
        raise ValueError("AZURE_OPENAI_ENDPOINT must be a valid HTTPS URL")

    if not config["search_endpoint"].startswith("https://"):
        raise ValueError("AZURE_SEARCH_ENDPOINT must be a valid HTTPS URL")

    return True
