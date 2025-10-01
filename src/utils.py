from mem0 import Memory
import os
import time
import asyncio
from typing import Optional, Dict, Any
from logger import debug_log, info_log, warning_log, error_log
from config import LLM_MAX_TOKENS, LLM_CONTEXT_LENGTH, AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_VERSION, AZURE_OPENAI_DEPLOYMENT_NAME

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
        debug_log("Starting Mem0 client configuration...")
        
        # Get LLM provider and configuration
        llm_provider = os.getenv('LLM_PROVIDER')
        llm_api_key = os.getenv('LLM_API_KEY')
        llm_model = os.getenv('LLM_CHOICE')
        embedding_model = os.getenv('EMBEDDING_MODEL_CHOICE')
        embedding_api_key = os.getenv('EMBEDDING_API_KEY')
        
        debug_log(f"LLM_PROVIDER: {llm_provider}")
        debug_log(f"LLM_CHOICE: {llm_model}")
        debug_log(f"EMBEDDING_MODEL_CHOICE: {embedding_model}")
        debug_log(f"LLM_BASE_URL: {os.getenv('LLM_BASE_URL')}")
        debug_log(f"DATABASE_URL: {'SET' if os.getenv('DATABASE_URL') else 'NOT SET'}")
        debug_log(f"LLM_MAX_TOKENS: {LLM_MAX_TOKENS}")
        debug_log(f"LLM_CONTEXT_LENGTH: {LLM_CONTEXT_LENGTH}")
        
        # Validate required environment variables
        if not llm_provider:
            raise ValueError("LLM_PROVIDER environment variable is required")
        
        # For Ollama, API key is typically not required
        # For other providers, API key is optional (can be empty for servers that don't require auth)
        if llm_provider != 'ollama' and llm_api_key is None:
            warning_log("LLM_API_KEY not set. Some servers may require authentication.")
        
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
                    "max_tokens": LLM_MAX_TOKENS,
                }
            }
            
            # Set custom base URL if provided
            llm_base_url = os.getenv('LLM_BASE_URL')
            if llm_base_url:
                # Set in environment for Mem0 internal use (LLM config doesn't support base_url)
                os.environ["OPENAI_BASE_URL"] = llm_base_url
                debug_log(f"Set custom OpenAI base URL: {llm_base_url}")
            
            # Set API key in environment if not already set
            # Handle empty API keys (for servers that don't require authentication)
            if llm_api_key is not None and not os.environ.get("OPENAI_API_KEY"):
                os.environ["OPENAI_API_KEY"] = llm_api_key
                if llm_api_key.strip() == "":
                    debug_log("Using empty API key (server may not require authentication)")
                else:
                    debug_log("Using LLM_API_KEY for OpenAI configuration")
                
            # For OpenRouter, set the specific API key
            if llm_provider == 'openrouter' and llm_api_key:
                os.environ["OPENROUTER_API_KEY"] = llm_api_key
        
        elif llm_provider == 'ollama':
            config["llm"] = {
                "provider": "ollama",
                "config": {
                    "model": llm_model,
                    "temperature": 0.2,
                    "max_tokens": LLM_MAX_TOKENS,
                }
            }
            
        elif llm_provider == 'azure':
            # Validate Azure OpenAI configuration
            if not AZURE_OPENAI_API_KEY:
                raise ValueError("AZURE_OPENAI_API_KEY is required for Azure OpenAI")
            if not AZURE_OPENAI_ENDPOINT:
                raise ValueError("AZURE_OPENAI_ENDPOINT is required for Azure OpenAI")
            if not AZURE_OPENAI_DEPLOYMENT_NAME:
                raise ValueError("AZURE_OPENAI_DEPLOYMENT_NAME is required for Azure OpenAI")
            
            # Set Azure OpenAI environment variables for Mem0 internal use
            os.environ["OPENAI_API_KEY"] = AZURE_OPENAI_API_KEY
            
            # Construct proper Azure OpenAI URL format with deployment name in path and API version as query parameter
            azure_base_url = AZURE_OPENAI_ENDPOINT.rstrip('/')
            if not azure_base_url.endswith('/openai/deployments/' + AZURE_OPENAI_DEPLOYMENT_NAME):
                azure_base_url = f"{azure_base_url}/openai/deployments/{AZURE_OPENAI_DEPLOYMENT_NAME}"
            
            # Set base URL without query parameter (Mem0 will add /chat/completions)
            os.environ["OPENAI_BASE_URL"] = azure_base_url
            os.environ["OPENAI_API_VERSION"] = AZURE_OPENAI_API_VERSION
            debug_log(f"Configured Azure OpenAI through OpenAI client: {azure_base_url}")
            
            config["llm"] = {
                "provider": "openai",
                "config": {
                    "model": AZURE_OPENAI_DEPLOYMENT_NAME,  # Use the deployment name
                    "temperature": 0.2,
                    "max_tokens": LLM_MAX_TOKENS,
                }
            }
            
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_provider}")
        
        # Configure embedder based on provider
        # Check if we have a specific embedding provider configured
        embedding_provider = os.getenv('EMBEDDING_PROVIDER', llm_provider)
        
        # Clear OpenAI environment variables only if BOTH LLM and embedder are using Ollama
        if llm_provider == 'ollama' and embedding_provider == 'ollama':
            # Remove any OpenAI API keys that might interfere
            for key in ['OPENAI_API_KEY', 'OPENAI_BASE_URL', 'OPENAI_ORGANIZATION']:
                if key in os.environ:
                    del os.environ[key]
                    debug_log(f"Cleared {key} environment variable for Ollama configuration")
        elif llm_provider == 'ollama' and embedding_provider == 'openai':
            debug_log("Mixed configuration - LLM using Ollama, Embedder using OpenAI")
            debug_log("Keeping OpenAI environment variables for embedder")
            # Ensure we have the correct base URL for OpenAI embedder
            embedding_base_url = os.getenv('EMBEDDING_BASE_URL') or os.getenv('LLM_BASE_URL')
            if embedding_base_url and 'api.openai.com' not in embedding_base_url:
                # Ensure the URL has a protocol
                if not embedding_base_url.startswith(('http://', 'https://')):
                    embedding_base_url = f"http://{embedding_base_url}"
                    debug_log(f"Added http:// protocol to embedding URL: {embedding_base_url}")
                
                os.environ["OPENAI_BASE_URL"] = embedding_base_url
                debug_log(f"Set OpenAI base URL for mixed configuration: {embedding_base_url}")
        elif llm_provider == 'openai':
            # For OpenAI, ensure we're using the custom base URL if provided
            llm_base_url = os.getenv('LLM_BASE_URL')
            if llm_base_url and 'api.openai.com' not in llm_base_url:
                debug_log(f"Will use custom OpenAI endpoint via environment: {llm_base_url}")
            else:
                debug_log("Will use default OpenAI endpoint (api.openai.com)")
        
        if embedding_provider == 'openai':
            config["embedder"] = {
                "provider": "openai",
                "config": {
                    "model": embedding_model or "text-embedding-3-small",
                    "embedding_dims": int(os.getenv("EMBEDDING_MODEL_DIMS", "1536"))
                }
            }
            
            # Set custom base URL if provided
            # Check for dedicated embedding base URL first, then fall back to LLM_BASE_URL
            embedding_base_url = os.getenv('EMBEDDING_BASE_URL') or os.getenv('LLM_BASE_URL')
            if embedding_base_url:
                # Ensure the URL has a protocol
                if not embedding_base_url.startswith(('http://', 'https://')):
                    embedding_base_url = f"http://{embedding_base_url}"
                    debug_log(f"Added http:// protocol to embedding URL: {embedding_base_url}")
                
                # Set in environment for Mem0 internal use (embedder doesn't support base_url in config)
                os.environ["OPENAI_BASE_URL"] = embedding_base_url
                debug_log(f"Set custom OpenAI base URL for embedder: {embedding_base_url}")
                if os.getenv('EMBEDDING_BASE_URL'):
                    debug_log("Using dedicated EMBEDDING_BASE_URL")
                else:
                    debug_log("Using LLM_BASE_URL for embeddings")
            
            # Set API key in environment if not already set
            # Use embedding API key if available, otherwise fall back to LLM API key
            api_key_to_use = embedding_api_key if embedding_api_key is not None else llm_api_key
            if api_key_to_use is not None and not os.environ.get("OPENAI_API_KEY"):
                os.environ["OPENAI_API_KEY"] = api_key_to_use
                if embedding_api_key is not None:
                    if embedding_api_key.strip() == "":
                        debug_log(f"Using empty EMBEDDING_API_KEY for embeddings (server may not require authentication)")
                    else:
                        debug_log(f"Using dedicated EMBEDDING_API_KEY for embeddings")
                else:
                    if llm_api_key and llm_api_key.strip() == "":
                        debug_log(f"Using empty LLM_API_KEY for embeddings (server may not require authentication)")
                    else:
                        debug_log(f"Using LLM_API_KEY for embeddings")
        
        elif embedding_provider == 'ollama':
            # Map OpenAI model names to appropriate Ollama models if there's a mismatch
            if embedding_model and 'text-embedding' in embedding_model.lower():
                debug_log(f"Detected OpenAI model name '{embedding_model}' with Ollama provider")
                debug_log("Mapping to appropriate Ollama embedding model")
                # Map common OpenAI embedding models to Ollama equivalents
                if 'text-embedding-3-small' in embedding_model.lower():
                    embedding_model = "nomic-embed-text"
                    debug_log(f"Mapped to Ollama model: {embedding_model}")
                elif 'text-embedding-3-large' in embedding_model.lower():
                    embedding_model = "nomic-embed-text"
                    debug_log(f"Mapped to Ollama model: {embedding_model}")
                else:
                    embedding_model = "nomic-embed-text"
                    debug_log(f"Mapped to default Ollama model: {embedding_model}")
            
            config["embedder"] = {
                "provider": "ollama",
                "config": {
                    "model": embedding_model or "nomic-embed-text",
                    "embedding_dims": int(os.getenv("EMBEDDING_MODEL_DIMS", "1024"))
                }
            }
            
            # Set base URL for Ollama if provided
            embedding_base_url = os.getenv('EMBEDDING_BASE_URL') or os.getenv('LLM_BASE_URL')
            if embedding_base_url:
                config["embedder"]["config"]["ollama_base_url"] = embedding_base_url
                # Also set the base URL in environment for Mem0 internal use
                os.environ["OLLAMA_BASE_URL"] = embedding_base_url
                debug_log(f"Set OLLAMA_BASE_URL for embedder: {embedding_base_url}")
                if os.getenv('EMBEDDING_BASE_URL'):
                    debug_log("Using dedicated EMBEDDING_BASE_URL for Ollama")
                else:
                    debug_log("Using LLM_BASE_URL for Ollama embeddings")
        
        else:
            # Default to using the same provider as LLM if no specific embedding provider is set
            if llm_provider == 'openai':
                config["embedder"] = {
                    "provider": "openai",
                    "config": {
                        "model": embedding_model or "text-embedding-3-small",
                        "embedding_dims": int(os.getenv("EMBEDDING_MODEL_DIMS", "1536"))
                    }
                }
                
                # Set custom base URL if provided
                # Check for dedicated embedding base URL first, then fall back to LLM_BASE_URL
                embedding_base_url = os.getenv('EMBEDDING_BASE_URL') or os.getenv('LLM_BASE_URL')
                if embedding_base_url:
                    # Set in environment for Mem0 internal use (embedder doesn't support base_url in config)
                    os.environ["OPENAI_BASE_URL"] = embedding_base_url
                    debug_log(f"Set custom OpenAI base URL for embedder (fallback): {embedding_base_url}")
                    if os.getenv('EMBEDDING_BASE_URL'):
                        debug_log("Using dedicated EMBEDDING_BASE_URL (fallback)")
                    else:
                        debug_log("Using LLM_BASE_URL for embeddings (fallback)")
                
                # Set API key in environment if not already set
                # Use embedding API key if available, otherwise fall back to LLM API key
                api_key_to_use = embedding_api_key if embedding_api_key is not None else llm_api_key
                if api_key_to_use is not None and not os.environ.get("OPENAI_API_KEY"):
                    os.environ["OPENAI_API_KEY"] = api_key_to_use
                    if embedding_api_key is not None:
                        if embedding_api_key.strip() == "":
                            debug_log(f"Using empty EMBEDDING_API_KEY for embeddings (fallback - server may not require authentication)")
                        else:
                            debug_log(f"Using dedicated EMBEDDING_API_KEY for embeddings (fallback)")
                    else:
                        if llm_api_key and llm_api_key.strip() == "":
                            debug_log(f"Using empty LLM_API_KEY for embeddings (fallback - server may not require authentication)")
                        else:
                            debug_log(f"Using LLM_API_KEY for embeddings (fallback)")
            
            elif llm_provider == 'ollama':
                config["embedder"] = {
                    "provider": "ollama",
                    "config": {
                        "model": embedding_model or "nomic-embed-text",
                        "embedding_dims": int(os.getenv("EMBEDDING_MODEL_DIMS", "1024"))
                    }
                }
                
                # Set base URL for Ollama if provided
                embedding_base_url = os.getenv('LLM_BASE_URL')
                if embedding_base_url:
                    config["embedder"]["config"]["ollama_base_url"] = embedding_base_url
                    # Also set the base URL in environment for Mem0 internal use
                    os.environ["OLLAMA_BASE_URL"] = embedding_base_url
                    debug_log(f"Set OLLAMA_BASE_URL for embedder (fallback): {embedding_base_url}")
        
        # Configure Supabase vector store
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is required")
            
        config["vector_store"] = {
            "provider": "supabase",
            "config": {
                "connection_string": database_url,
                "collection_name": "mem0_memories",
                "embedding_model_dims": int(os.getenv("EMBEDDING_MODEL_DIMS", "1536" if llm_provider == "openai" else "1024"))
            }
        }

        # config["custom_fact_extraction_prompt"] = CUSTOM_INSTRUCTIONS
        
        debug_log(f"Final Mem0 config: {config}")
        debug_log("Creating Mem0 client...")
        
        # Additional debugging for environment variables
        debug_log(f"Environment check - OPENAI_API_KEY: {'SET' if os.environ.get('OPENAI_API_KEY') else 'NOT SET'}")
        debug_log(f"Environment check - OPENAI_BASE_URL: {'SET' if os.environ.get('OPENAI_BASE_URL') else 'NOT SET'}")
        debug_log(f"Environment check - LLM_BASE_URL: {os.environ.get('LLM_BASE_URL', 'NOT SET')}")
        
        # Debug embedder config specifically
        if "embedder" in config:
            debug_log(f"Embedder config: {config['embedder']}")
            if "config" in config["embedder"]:
                debug_log(f"Embedder config details: {config['embedder']['config']}")
        
        # Create and return the Memory client
        try:
            client = Memory.from_config(config)
            debug_log(f"Mem0 client created successfully: {type(client)}")
            
            # Test the client configuration by checking its internal state
            if hasattr(client, '_llm') and hasattr(client._llm, 'client'):
                debug_log(f"Mem0 LLM client type: {type(client._llm.client)}")
            if hasattr(client, '_embedder') and hasattr(client._embedder, 'client'):
                debug_log(f"Mem0 Embedder client type: {type(client._embedder.client)}")
            
            return client
        except Exception as e:
            debug_log(f"Error creating Mem0 client: {e}")
            debug_log(f"Error type: {type(e)}")
            debug_log(f"Error args: {e.args}")
            raise
        
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