from mem0 import Memory
import os
import time
import asyncio
from typing import Optional, Dict, Any

# Custom instructions for memory processing
# These aren't being used right now but Mem0 does support adding custom prompting
# for handling memory retrieval and processing.
CUSTOM_INSTRUCTIONS = """
Extract the Following Information:  

- Key Information: Identify and save the most important details.
- Context: Capture the surrounding context to understand the memory's relevance.
- Connections: Note any relationships to other topics or memories.
- Importance: Highlight why this information might be valuable in the future.
- Source: Record where this information came from when applicable.
"""

def is_database_error(error: Exception) -> bool:
    """Check if an error is related to database connectivity."""
    error_str = str(error).lower()
    database_keywords = [
        'database', 'connection', 'postgresql', 'supabase',
        'unable to open', 'connection refused', 'timeout',
        'network', 'host unreachable', 'connection pool',
        'authentication', 'permission denied'
    ]
    return any(keyword in error_str for keyword in database_keywords)

def get_actionable_error_message(error: Exception) -> str:
    """Generate actionable error messages for common database issues."""
    error_str = str(error).lower()
    
    if 'unable to open database file' in error_str:
        return (
            "Database connection lost. This usually means:\n"
            "1. Database server is restarting\n"
            "2. Network connection was interrupted\n"
            "3. Connection pool was exhausted\n"
            "4. Database permissions changed\n"
            "The service will automatically retry. If the problem persists:\n"
            "1. Check database server status\n"
            "2. Verify network connectivity\n"
            "3. Check database logs for errors\n"
            "4. Verify database credentials and permissions"
        )
    
    elif 'connection refused' in error_str:
        return (
            "Database connection refused. Please check:\n"
            "1. Database server is running\n"
            "2. Database port is accessible\n"
            "3. Firewall settings\n"
            "4. Database service status"
        )
    
    elif 'timeout' in error_str:
        return (
            "Database operation timed out. This could be due to:\n"
            "1. Slow database performance\n"
            "2. Network latency\n"
            "3. Database under heavy load\n"
            "4. Connection pool exhaustion"
        )
    
    elif 'authentication' in error_str or 'permission denied' in error_str:
        return (
            "Database authentication failed. Please check:\n"
            "1. Database credentials in .env file\n"
            "2. Database user permissions\n"
            "3. Database connection string format\n"
            "4. Database user account status"
        )
    
    else:
        return f"Unexpected database error: {str(error)}"

def retry_with_backoff(max_retries: int = 3, base_delay: float = 2.0, max_delay: float = 60.0):
    """Decorator for retrying operations with exponential backoff."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_retries - 1:
                        raise last_exception
                    
                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    
                    print(f"Attempt {attempt + 1} failed: {e}")
                    print(f"Retrying in {delay:.1f} seconds...")
                    
                    time.sleep(delay)
            
            raise last_exception
        return wrapper
    return decorator

@retry_with_backoff(max_retries=3, base_delay=2.0)
def get_mem0_client():
    try:
        print("DEBUG: Starting Mem0 client configuration...")
        
        # Get LLM provider and configuration
        llm_provider = os.getenv('LLM_PROVIDER')
        llm_api_key = os.getenv('LLM_API_KEY')
        llm_model = os.getenv('LLM_CHOICE')
        embedding_model = os.getenv('EMBEDDING_MODEL_CHOICE')
        
        print(f"DEBUG: LLM_PROVIDER: {llm_provider}")
        print(f"DEBUG: LLM_CHOICE: {llm_model}")
        print(f"DEBUG: EMBEDDING_MODEL_CHOICE: {embedding_model}")
        print(f"DEBUG: LLM_BASE_URL: {os.getenv('LLM_BASE_URL')}")
        print(f"DEBUG: DATABASE_URL: {'SET' if os.getenv('DATABASE_URL') else 'NOT SET'}")
        
        # Validate required environment variables
        if not llm_provider:
            raise ValueError("LLM_PROVIDER environment variable is required")
        
        # For Ollama, API key is typically not required
        if llm_provider != 'ollama' and not llm_api_key:
            raise ValueError("LLM_API_KEY environment variable is required for non-Ollama providers")
        
        if not llm_model:
            raise ValueError("LLM_CHOICE environment variable is required")
        
        # Initialize config dictionary
        config = {}
        
        # Configure LLM based on provider
        if llm_provider == 'openai' or llm_provider == 'openrouter':
            config["llm"] = {
                "provider": "openai",
                "config": {
                    "model": llm_model,
                    "temperature": 0.2,
                    "max_tokens": 2000,
                }
            }
            
            # Set API key in environment if not already set
            if llm_api_key and not os.environ.get("OPENAI_API_KEY"):
                os.environ["OPENAI_API_KEY"] = llm_api_key
                
            # For OpenRouter, set the specific API key
            if llm_provider == 'openrouter' and llm_api_key:
                os.environ["OPENROUTER_API_KEY"] = llm_api_key
        
        elif llm_provider == 'ollama':
            config["llm"] = {
                "provider": "ollama",
                "config": {
                    "model": llm_model,
                    "temperature": 0.2,
                    "max_tokens": 2000,
                }
            }
            
            # Set base URL for Ollama if provided
            llm_base_url = os.getenv('LLM_BASE_URL')
            if llm_base_url:
                config["llm"]["config"]["ollama_base_url"] = llm_base_url
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_provider}")
        
        # Configure embedder based on provider
        if llm_provider == 'openai':
            config["embedder"] = {
                "provider": "openai",
                "config": {
                    "model": embedding_model or "text-embedding-3-small",
                    "embedding_dims": 1536  # Default for text-embedding-3-small
                }
            }
            
            # Set API key in environment if not already set
            if llm_api_key and not os.environ.get("OPENAI_API_KEY"):
                os.environ["OPENAI_API_KEY"] = llm_api_key
        
        elif llm_provider == 'ollama':
            config["embedder"] = {
                "provider": "ollama",
                "config": {
                    "model": embedding_model or "nomic-embed-text",
                    "embedding_dims": 768  # Default for nomic-embed-text
                }
            }
            
            # Set base URL for Ollama if provided
            embedding_base_url = os.getenv('LLM_BASE_URL')
            if embedding_base_url:
                config["embedder"]["config"]["ollama_base_url"] = embedding_base_url
        
        # Configure Supabase vector store
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is required")
            
        config["vector_store"] = {
            "provider": "supabase",
            "config": {
                "connection_string": database_url,
                "collection_name": "mem0_memories",
                "embedding_model_dims": 1536 if llm_provider == "openai" else 1024
            }
        }

        # config["custom_fact_extraction_prompt"] = CUSTOM_INSTRUCTIONS
        
        print(f"DEBUG: Final Mem0 config: {config}")
        print("DEBUG: Creating Mem0 client...")
        
        # Create and return the Memory client
        client = Memory.from_config(config)
        print(f"DEBUG: Mem0 client created successfully: {type(client)}")
        return client
        
    except Exception as e:
        # Enhanced error handling with specific database error detection
        if is_database_error(e):
            print(f"Database connection error detected: {e}")
            print(get_actionable_error_message(e))
            # Re-raise as a specific database error for better handling
            raise RuntimeError(f"Database connection failed: {str(e)}")
        
        # Handle other types of errors
        error_msg = f"Failed to initialize Mem0 client: {str(e)}"
        if "LLM_API_KEY" in str(e) and llm_provider != 'ollama':
            error_msg += ". Please set the LLM_API_KEY environment variable."
        elif "DATABASE_URL" in str(e):
            error_msg += ". Please set the DATABASE_URL environment variable."
        elif "LLM_PROVIDER" in str(e):
            error_msg += ". Please set the LLM_PROVIDER environment variable."
        
        raise RuntimeError(error_msg)