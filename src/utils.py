"""Utility functions for the application."""

import logging
import os
from typing import Any, Dict

from dotenv import load_dotenv

# Try to import Streamlit for secrets support
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False


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


def _get_secret(key: str, default: Any = None) -> Any:
    """
    Get secret from Streamlit secrets or environment variables.
    
    Args:
        key: Configuration key name
        default: Default value if not found
        
    Returns:
        Configuration value
    """
    # Try Streamlit secrets first (for Streamlit Cloud)
    if HAS_STREAMLIT:
        try:
            if key in st.secrets:
                return st.secrets[key]
        except (AttributeError, FileNotFoundError):
            pass
    
    # Fall back to environment variables
    return os.getenv(key, default)


def load_config() -> Dict[str, Any]:
    """
    Load configuration from Streamlit secrets or environment variables.
    
    Supports both:
    - Local development: .env files via python-dotenv
    - Streamlit Cloud: st.secrets from secrets.toml
    
    Returns:
        Dictionary containing configuration values
    """
    # Load .env file for local development
    load_dotenv()

    config = {
        # Azure DevOps
        "ado_organization": _get_secret("ADO_ORGANIZATION"),
        "ado_project_name": _get_secret("ADO_PROJECT_NAME"),
        "ado_pat": _get_secret("ADO_PAT"),
        # Azure OpenAI
        "openai_endpoint": _get_secret("AZURE_OPENAI_ENDPOINT"),
        "openai_api_key": _get_secret("AZURE_OPENAI_KEY"),
        "openai_api_version": _get_secret("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
        "openai_embedding_deployment": _get_secret("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small"),
        "openai_chat_deployment": _get_secret("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o-mini"),
        # Azure AI Search
        "search_endpoint": _get_secret("AZURE_SEARCH_ENDPOINT"),
        "search_api_key": _get_secret("AZURE_SEARCH_KEY"),
        "search_index_name": _get_secret("AZURE_SEARCH_INDEX_NAME", "ado-workitems"),
        # Application
        "log_level": _get_secret("LOG_LEVEL", "INFO"),
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
