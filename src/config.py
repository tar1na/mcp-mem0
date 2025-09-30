"""
Configuration management for mcp-mem0 server.
Handles environment variables and provides safe defaults for development.
"""

import os
from typing import Optional

# Environment variables are now loaded in main.py before this module is imported
# from dotenv import load_dotenv
# load_dotenv()

# Default values for development/testing only - should be overridden in production
DEFAULT_USER_ID = os.getenv("DEFAULT_USER_ID", "default_user")

# Server configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8050"))
TRANSPORT = os.getenv("TRANSPORT", "sse")

# Mem0 configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_MODEL = os.getenv("LLM_CHOICE", "gpt-3.5-turbo")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL_CHOICE", "text-embedding-3-small")
EMBEDDING_MODEL_DIMS = int(os.getenv("EMBEDDING_MODEL_DIMS", "1536"))
LLM_BASE_URL = os.getenv("LLM_BASE_URL")

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

# Embedding configuration
EMBEDDING_BASE_URL = os.getenv("EMBEDDING_BASE_URL")
EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY")

# Database connection management settings
DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "5"))
DATABASE_MAX_CONNECTIONS = int(os.getenv("DATABASE_MAX_CONNECTIONS", "20"))
DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))
DATABASE_POOL_TIMEOUT = int(os.getenv("DATABASE_POOL_TIMEOUT", "30"))
DATABASE_POOL_RECYCLE = int(os.getenv("DATABASE_POOL_RECYCLE", "3600"))
DATABASE_HEALTH_CHECK_INTERVAL = int(os.getenv("DATABASE_HEALTH_CHECK_INTERVAL", "60"))
DATABASE_RETRY_ATTEMPTS = int(os.getenv("DATABASE_RETRY_ATTEMPTS", "3"))
DATABASE_RETRY_DELAY = float(os.getenv("DATABASE_RETRY_DELAY", "2.0"))
DATABASE_MAX_RETRY_DELAY = float(os.getenv("DATABASE_MAX_RETRY_DELAY", "60.0"))

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
    
    # Validate database connection settings
    if DATABASE_POOL_SIZE < 1:
        warnings.append(
            "WARNING: DATABASE_POOL_SIZE should be at least 1. "
            f"Current value: {DATABASE_POOL_SIZE}"
        )
    
    if DATABASE_MAX_CONNECTIONS < DATABASE_POOL_SIZE:
        warnings.append(
            "WARNING: DATABASE_MAX_CONNECTIONS should be >= DATABASE_POOL_SIZE. "
            f"Current values: pool_size={DATABASE_POOL_SIZE}, max_connections={DATABASE_MAX_CONNECTIONS}"
        )
    
    if DATABASE_POOL_TIMEOUT < 5:
        warnings.append(
            "WARNING: DATABASE_POOL_TIMEOUT should be at least 5 seconds. "
            f"Current value: {DATABASE_POOL_TIMEOUT}"
        )
    
    return warnings

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
