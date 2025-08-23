from mem0 import Memory
import os

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
        # Return a more descriptive error message
        error_msg = f"Failed to initialize Mem0 client: {str(e)}"
        if "LLM_API_KEY" in str(e) and llm_provider != 'ollama':
            error_msg += ". Please set the LLM_API_KEY environment variable."
        elif "DATABASE_URL" in str(e):
            error_msg += ". Please set the DATABASE_URL environment variable."
        elif "LLM_PROVIDER" in str(e):
            error_msg += ". Please set the LLM_PROVIDER environment variable."
        
        # For now, we'll raise the error so the server can handle it gracefully
        # In a production environment, you might want to log this and return a fallback client
        raise RuntimeError(error_msg)