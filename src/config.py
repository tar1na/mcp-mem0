"""
Configuration management for mcp-mem0 server.
Handles environment variables and provides safe defaults for development.
"""

import os
from typing import Optional

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Default values for development/testing only - should be overridden in production
DEFAULT_USER_ID = os.getenv("DEFAULT_USER_ID", "default_user")
DEFAULT_AGENT_ID = os.getenv("DEFAULT_AGENT_ID")
DEFAULT_APP_ID = os.getenv("DEFAULT_APP_ID")

# Server configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8050"))
TRANSPORT = os.getenv("TRANSPORT", "sse")

# Mem0 configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_MODEL = os.getenv("LLM_CHOICE", "gpt-3.5-turbo")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL_CHOICE", "text-embedding-3-small")
LLM_BASE_URL = os.getenv("LLM_BASE_URL")

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

def validate_config() -> list[str]:
    """
    Validate the configuration and return a list of warnings/errors.
    
    Returns:
        List of configuration warnings or errors
    """
    warnings = []
    
    # Check for development defaults in production-like environments
    # Note: DEFAULT_USER_ID is now optional and can use the default value
    
    if not LLM_API_KEY and LLM_PROVIDER != 'ollama':
        warnings.append(
            "WARNING: No LLM API key provided. "
            "Set LLM_API_KEY environment variable."
        )
    
    if not DATABASE_URL:
        warnings.append(
            "WARNING: No database URL provided. "
            "Set DATABASE_URL environment variable."
        )
    
    return warnings

def get_effective_config(
    user_id: str,
    session_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    app_id: Optional[str] = None
) -> dict:
    """
    Get effective configuration values for a specific request.
    
    Args:
        user_id: Required user identifier
        session_id: Optional session identifier
        agent_id: Optional agent identifier
        app_id: Optional application identifier
    
    Returns:
        Dictionary with effective configuration values
    """
    return {
        "user_id": user_id,
        "session_id": session_id,
        "agent_id": agent_id or DEFAULT_AGENT_ID,
        "app_id": app_id or DEFAULT_APP_ID,
    }

def is_production() -> bool:
    """
    Check if running in production environment.
    
    Returns:
        True if production-like environment detected
    """
    # Simple heuristic - can be enhanced based on your deployment setup
    return (
        os.getenv("NODE_ENV") == "production" or
        os.getenv("ENVIRONMENT") == "production" or
        os.getenv("FLASK_ENV") == "production"
    )
