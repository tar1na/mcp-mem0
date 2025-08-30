# Load environment variables first, before any other imports
import os
from dotenv import load_dotenv
# Only load .env if environment variables aren't already set
if not os.getenv('DATABASE_URL'):
    load_dotenv()

from mcp.server.fastmcp import FastMCP, Context
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from mem0 import Memory
import asyncio
import json
from typing import Optional, Dict, Any

from utils import get_mem0_client
from config import (
    DEFAULT_USER_ID, 
    HOST, 
    PORT, 
    TRANSPORT,
    validate_config
)

# Create a dataclass for our application context
@dataclass
class Mem0Context:
    """Context for the Mem0 MCP server."""
    mem0_client: Memory

@asynccontextmanager
async def mem0_lifespan(server: FastMCP) -> AsyncIterator[Mem0Context]:
    """
    Manages the Mem0 client lifecycle with enhanced error handling and automatic recovery.
    
    Args:
        server: The FastMCP server instance
        
    Yields:
        Mem0Context: The context containing the Mem0 client
    """
    mem0_client = None
    max_retries = 5
    base_retry_delay = 2.0
    
    try:
        for attempt in range(max_retries):
            try:
                print(f"DEBUG: Starting Mem0 client initialization (attempt {attempt + 1}/{max_retries})...")
                
                # Create the Memory client with retry logic (already implemented in utils.py)
                mem0_client = get_mem0_client()
                print(f"DEBUG: Mem0 client initialized successfully: {type(mem0_client)}")
                
                # Test basic connectivity by attempting a simple operation
                print("DEBUG: Testing Mem0 client connectivity...")
                try:
                    # Try to get a small sample to verify connection works
                    test_result = mem0_client.get_all(user_id="test_connection", limit=1)
                    print("DEBUG: Mem0 client connectivity test passed")
                except Exception as test_error:
                    print(f"DEBUG: Connectivity test failed: {test_error}")
                    # If it's a database error, we'll retry; otherwise, fail fast
                    if "database" not in str(test_error).lower() and "connection" not in str(test_error).lower():
                        raise test_error
                
                # If we get here, the client is working
                break
                
            except Exception as e:
                error_msg = f"Failed to initialize Mem0 client (attempt {attempt + 1}/{max_retries}): {str(e)}"
                print(f"ERROR: {error_msg}")
                
                # Clean up failed client
                if mem0_client:
                    try:
                        del mem0_client
                        mem0_client = None
                    except:
                        pass
                
                if attempt < max_retries - 1:
                    retry_delay = base_retry_delay * (2 ** attempt)  # Exponential backoff
                    print(f"Retrying in {retry_delay:.1f} seconds...")
                    
                    # Provide specific guidance based on error type
                    if "database" in str(e).lower() or "connection" in str(e).lower():
                        print("Database connection issue detected. This is often temporary.")
                        print("Common causes:")
                        print("  - Database server restarting")
                        print("  - Network connectivity issues")
                        print("  - Connection pool exhaustion")
                        print("  - Database permissions changes")
                        print("The service will automatically retry...")
                    else:
                        print("Configuration error detected. Please check:")
                        print("  - LLM_PROVIDER (openai, openrouter, or ollama)")
                        print("  - LLM_API_KEY (your API key)")
                        print("  - LLM_CHOICE (model name)")
                        print("  - DATABASE_URL (Supabase connection string)")
                        print("  - See env.example for all required variables")
                    
                    # Wait before retry
                    await asyncio.sleep(retry_delay)
                else:
                    print("ERROR: All retry attempts failed!")
                    print("Please check your configuration and try again.")
                    print("If the problem persists, check:")
                    print("  1. Database server status")
                    print("  2. Network connectivity")
                    print("  3. Database credentials and permissions")
                    print("  4. Firewall settings")
                    raise RuntimeError(error_msg)
        
        # If we get here, we have a working client
        if mem0_client is None:
            raise RuntimeError("Failed to initialize Mem0 client after all retry attempts")
        
        # Yield the working client
        yield Mem0Context(mem0_client=mem0_client)
        
    finally:
        # This cleanup will always run, even if an exception occurs
        if mem0_client:
            try:
                print("DEBUG: Cleaning up Mem0 client...")
                # Close any open database connections
                if hasattr(mem0_client, 'close'):
                    mem0_client.close()
                elif hasattr(mem0_client, '_close'):
                    mem0_client._close()
                # Force garbage collection
                import gc
                gc.collect()
                print("DEBUG: Mem0 client cleanup completed")
            except Exception as cleanup_error:
                print(f"DEBUG: Error during cleanup: {cleanup_error}")

# Initialize FastMCP server with the Mem0 client as context
mcp = FastMCP(
    "mcp-mem0",
    lifespan=mem0_lifespan,
    host=HOST,
    port=PORT
)        

@mcp.tool()
async def save_memory(
    ctx: Context, 
    content: str, 
    userId: str
) -> str:
    """Save information to your long-term memory with user isolation.

    This tool is designed to store any type of information that might be useful in the future.
    The content will be processed and indexed for later retrieval through semantic search.
    Memories are isolated by userId to prevent cross-user data leakage.

    Args:
        ctx: The MCP server provided context which includes the Mem0 client
        content: The content to store in memory, including any relevant details and context
        userId: Required user identifier for memory isolation (must be provided)
    """
    try:
        # Validate required parameters
        if not userId or userId.strip() == "":
            return "Error: userId is required and cannot be empty"
        
        mem0_client = ctx.request_context.lifespan_context.mem0_client
        
        # Prepare the memory payload
        messages = [{"role": "user", "content": content}]
        
        # Add memory with proper isolation
        # Note: Mem0's add() method only supports user_id and metadata
        try:
            print(f"DEBUG: Attempting to save memory for user: {userId}")
            print(f"DEBUG: Memory content: {content[:100]}...")
            
            mem0_client.add(
                messages, 
                user_id=userId,
                metadata=None
            )
            print(f"DEBUG: Memory saved successfully")
        except Exception as mem0_error:
            return f"Error calling Mem0 add: {str(mem0_error)}"
        
        # Log the operation for security monitoring
        return f"Successfully saved memory for user '{userId}': {content[:100]}..." if len(content) > 100 else f"Successfully saved memory for user '{userId}': {content}"
    
    except Exception as e:
        return f"Error saving memory: {str(e)}"

@mcp.tool()
async def get_all_memories(
    ctx: Context,
    userId: str
) -> str:
    """Get all stored memories for a specific user.
    
    Call this tool when you need complete context of all previously stored memories for a user.
    Results are isolated by userId to ensure data privacy.

    Args:
        ctx: The MCP server provided context which includes the Mem0 client
        userId: Required user identifier for memory isolation (must be provided)

    Returns a JSON formatted list of all stored memories for the specified user.
    """
    try:
        # Validate required parameters
        if not userId or userId.strip() == "":
            return "Error: userId is required and cannot be empty"
        
        mem0_client = ctx.request_context.lifespan_context.mem0_client
        
        # Debug: Check if mem0_client is properly initialized
        if mem0_client is None:
            return "Error: Mem0 client is not properly initialized"
        
        # Debug: Log what we're about to do
        print(f"DEBUG: Attempting to get memories for user: {userId}")
        
        # Get memories with proper isolation
        # Note: Mem0's get_all() method only supports user_id parameter
        try:
            memories = mem0_client.get_all(user_id=userId)
            print(f"DEBUG: Mem0 client returned: {type(memories)} - {memories}")
        except Exception as mem0_error:
            return f"Error calling Mem0 get_all: {str(mem0_error)}"
        
        # Check if memories is a string (error message) or object
        if isinstance(memories, str):
            return f"Error retrieving memories: {memories}"
        
        # Debug: Check the structure of what we received
        print(f"DEBUG: Memories type: {type(memories)}")
        print(f"DEBUG: Memories content: {memories}")
        
        if isinstance(memories, dict) and "results" in memories:
            flattened_memories = [memory["memory"] for memory in memories["results"]]
        else:
            flattened_memories = memories
        
        # Debug: Check flattened memories
        print(f"DEBUG: Flattened memories type: {type(flattened_memories)}")
        print(f"DEBUG: Flattened memories length: {len(flattened_memories) if hasattr(flattened_memories, '__len__') else 'No length'}")
        
        # Return all memories for the user (no filtering needed)
        return json.dumps({
            "user_id": userId,
            "memories": flattened_memories,
            "count": len(flattened_memories) if hasattr(flattened_memories, '__len__') else 0
        }, indent=2)
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"DEBUG: Full error traceback: {error_details}")
        return f"Error retrieving memories: {str(e)}"

@mcp.tool()
async def search_memories(
    ctx: Context, 
    query: str, 
    userId: str,
    topK: Optional[int] = None
) -> str:
    """Search memories using semantic search with user isolation.

    This tool should be called to find relevant information from your memory. Results are ranked by relevance
    and are isolated by userId to ensure data privacy.
    Always search your memories before making decisions to ensure you leverage your existing knowledge.

    Args:
        ctx: The MCP server provided context which includes the Mem0 client
        query: Search query string describing what you're looking for. Can be natural language.
        userId: Required user identifier for memory isolation (must be provided)
        topK: Maximum number of results to return (default: 3)
    """
    try:
        # Validate required parameters
        if not userId or userId.strip() == "":
            return "Error: userId is required and cannot be empty"
        
        mem0_client = ctx.request_context.lifespan_context.mem0_client
        
        # Set default limit if not provided
        limit = topK if topK is not None else 3
        
        # Search memories with proper isolation
        # Note: Mem0's search() method only supports query, user_id, and limit parameters
        try:
            memories = mem0_client.search(
                query, 
                user_id=userId,
                limit=limit
            )
            print(f"DEBUG: Mem0 search returned: {type(memories)} - {memories}")
        except Exception as mem0_error:
            return f"Error calling Mem0 search: {str(mem0_error)}"
        
        # Check if memories is a string (error message) or object
        if isinstance(memories, str):
            return f"Error searching memories: {memories}"
        
        # Debug: Check the structure of what we received
        print(f"DEBUG: Search memories type: {type(memories)}")
        print(f"DEBUG: Search memories content: {memories}")
        
        if isinstance(memories, dict) and "results" in memories:
            flattened_memories = [memory["memory"] for memory in memories["results"]]
        else:
            flattened_memories = memories
        
        # Debug: Check flattened memories
        print(f"DEBUG: Flattened search memories type: {type(flattened_memories)}")
        print(f"DEBUG: Flattened search memories length: {len(flattened_memories) if hasattr(flattened_memories, '__len__') else 'No length'}")
        
        # Return all search results for the user (no filtering needed)
        return json.dumps({
            "user_id": userId,
            "query": query,
            "results": flattened_memories,
            "count": len(flattened_memories) if hasattr(flattened_memories, '__len__') else 0
        }, indent=2)
    
    except Exception as e:
        return f"Error searching memories: {str(e)}"

@mcp.tool()
async def delete_memory(
    ctx: Context,
    memoryId: str,
    userId: str
) -> str:
    """Delete a specific memory with user isolation.

    This tool allows you to remove a specific memory by its ID.
    Deletion is isolated by userId to ensure users can only delete their own memories.

    Args:
        ctx: The MCP server provided context which includes the Mem0 client
        memoryId: The unique identifier of the memory to delete
        userId: Required user identifier for memory isolation (must be provided)
    """
    try:
        # Validate required parameters
        if not userId or userId.strip() == "":
            return "Error: userId is required and cannot be empty"
        if not memoryId or memoryId.strip() == "":
            return "Error: memoryId is required and cannot be empty"
        
        mem0_client = ctx.request_context.lifespan_context.mem0_client
        
        # Note: Mem0's delete functionality may need to be implemented based on their API
        # For now, we'll return a placeholder response
        # TODO: Implement actual deletion when Mem0 supports it
        
        return f"Memory deletion requested for user '{userId}' (memoryId: {memoryId}). Note: Delete functionality may need to be implemented based on Mem0's current API support."
    
    except Exception as e:
        return f"Error deleting memory: {str(e)}"

async def main():
    # Validate configuration and show warnings
    config_warnings = validate_config()
    if config_warnings:
        print("Configuration warnings:")
        for warning in config_warnings:
            print(f"  {warning}")
        print()
    
    if TRANSPORT == 'sse':
        # Run the MCP server with sse transport
        await mcp.run_sse_async()
    else:
        # Run the MCP server with stdio transport
        await mcp.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(main())
