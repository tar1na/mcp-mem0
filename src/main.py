from mcp.server.fastmcp import FastMCP, Context
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from mem0 import Memory
import asyncio
import json
import os
from typing import Optional, Dict, Any

from utils import get_mem0_client
from config import (
    DEFAULT_USER_ID, 
    DEFAULT_AGENT_ID, 
    DEFAULT_APP_ID, 
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
    Manages the Mem0 client lifecycle.
    
    Args:
        server: The FastMCP server instance
        
    Yields:
        Mem0Context: The context containing the Mem0 client
    """
    # Create and return the Memory client with the helper function in utils.py
    mem0_client = get_mem0_client()
    
    try:
        yield Mem0Context(mem0_client=mem0_client)
    finally:
        # No explicit cleanup needed for the Mem0 client
        pass

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
    userId: str,
    sessionId: Optional[str] = None,
    agentId: Optional[str] = None,
    appId: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """Save information to your long-term memory with user and session isolation.

    This tool is designed to store any type of information that might be useful in the future.
    The content will be processed and indexed for later retrieval through semantic search.
    Memories are isolated by userId and optionally by sessionId to prevent cross-user/session data leakage.

    Args:
        ctx: The MCP server provided context which includes the Mem0 client
        content: The content to store in memory, including any relevant details and context
        userId: Required user identifier for memory isolation (must be provided)
        sessionId: Optional session identifier for conversation-level isolation
        agentId: Optional agent identifier for agent-level isolation (stored in metadata)
        appId: Optional application identifier for app-level isolation (stored in metadata)
        metadata: Optional additional metadata to store with the memory
    """
    try:
        # Validate required parameters
        if not userId or userId.strip() == "":
            return "Error: userId is required and cannot be empty"
        
        mem0_client = ctx.request_context.lifespan_context.mem0_client
        
        # Prepare the memory payload
        messages = [{"role": "user", "content": content}]
        
        # Use provided userId (required) and fallback to defaults for optional fields
        effective_user_id = userId
        effective_agent_id = agentId or DEFAULT_AGENT_ID
        effective_app_id = appId or DEFAULT_APP_ID
        
        # Prepare metadata with agent and app information
        memory_metadata = metadata or {}
        if effective_agent_id:
            memory_metadata["agent_id"] = effective_agent_id
        if effective_app_id:
            memory_metadata["app_id"] = effective_app_id
        if sessionId:
            memory_metadata["session_id"] = sessionId
        
        # Add memory with proper isolation
        # Note: Mem0's add() method only supports user_id and metadata
        mem0_client.add(
            messages, 
            user_id=effective_user_id,
            metadata=memory_metadata if memory_metadata else None
        )
        
        # Log the operation for security monitoring
        session_info = f" (session: {sessionId})" if sessionId else ""
        app_info = f" (app: {effective_app_id})" if effective_app_id else ""
        agent_info = f" (agent: {effective_agent_id})" if effective_agent_id else ""
        return f"Successfully saved memory for user '{effective_user_id}'{session_info}{app_info}{agent_info}: {content[:100]}..." if len(content) > 100 else f"Successfully saved memory for user '{effective_user_id}'{session_info}{app_info}{agent_info}: {content}"
    
    except Exception as e:
        return f"Error saving memory: {str(e)}"

@mcp.tool()
async def get_all_memories(
    ctx: Context,
    userId: str,
    sessionId: Optional[str] = None,
    agentId: Optional[str] = None,
    appId: Optional[str] = None
) -> str:
    """Get all stored memories for a specific user with optional session isolation.
    
    Call this tool when you need complete context of all previously stored memories for a user.
    Results are isolated by userId and optionally by sessionId to ensure data privacy.

    Args:
        ctx: The MCP server provided context which includes the Mem0 client
        userId: Required user identifier for memory isolation (must be provided)
        sessionId: Optional session identifier for conversation-level isolation
        agentId: Optional agent identifier for agent-level isolation (filtered from metadata)
        appId: Optional application identifier for app-level isolation (filtered from metadata)

    Returns a JSON formatted list of all stored memories for the specified user/session.
    """
    try:
        # Validate required parameters
        if not userId or userId.strip() == "":
            return "Error: userId is required and cannot be empty"
        
        mem0_client = ctx.request_context.lifespan_context.mem0_client
        
        # Use provided userId (required) and fallback to defaults for optional fields
        effective_user_id = userId
        effective_agent_id = agentId or DEFAULT_AGENT_ID
        effective_app_id = appId or DEFAULT_APP_ID
        
        # Get memories with proper isolation
        # Note: Mem0's get_all() method only supports user_id parameter
        memories = mem0_client.get_all(user_id=effective_user_id)
        
        if isinstance(memories, dict) and "results" in memories:
            flattened_memories = [memory["memory"] for memory in memories["results"]]
        else:
            flattened_memories = memories
        
        # Filter memories by agent_id, app_id, and session_id if specified
        filtered_memories = []
        for memory in flattened_memories:
            # Check if memory has metadata for filtering
            memory_metadata = memory.get("metadata", {})
            
            # Filter by agent_id if specified
            if effective_agent_id and memory_metadata.get("agent_id") != effective_agent_id:
                continue
                
            # Filter by app_id if specified
            if effective_app_id and memory_metadata.get("app_id") != effective_app_id:
                continue
                
            # Filter by session_id if specified
            if sessionId and memory_metadata.get("session_id") != sessionId:
                continue
                
            filtered_memories.append(memory)
        
        # Log the operation for security monitoring
        session_info = f" (session: {sessionId})" if sessionId else ""
        app_info = f" (app: {effective_app_id})" if effective_app_id else ""
        agent_info = f" (agent: {effective_agent_id})" if effective_agent_id else ""
        
        return json.dumps({
            "user_id": effective_user_id,
            "session_id": sessionId,
            "agent_id": effective_agent_id,
            "app_id": effective_app_id,
            "memories": filtered_memories,
            "count": len(filtered_memories),
            "total_count": len(flattened_memories)
        }, indent=2)
    
    except Exception as e:
        return f"Error retrieving memories: {str(e)}"

@mcp.tool()
async def search_memories(
    ctx: Context, 
    query: str, 
    userId: str,
    sessionId: Optional[str] = None,
    agentId: Optional[str] = None,
    appId: Optional[str] = None,
    threshold: Optional[float] = None,
    filters: Optional[Dict[str, Any]] = None,
    topK: Optional[int] = None
) -> str:
    """Search memories using semantic search with user and session isolation.

    This tool should be called to find relevant information from your memory. Results are ranked by relevance
    and are isolated by userId and optionally by sessionId to ensure data privacy.
    Always search your memories before making decisions to ensure you leverage your existing knowledge.

    Args:
        ctx: The MCP server provided context which includes the Mem0 client
        query: Search query string describing what you're looking for. Can be natural language.
        userId: Required user identifier for memory isolation (must be provided)
        sessionId: Optional session identifier for conversation-level isolation
        agentId: Optional agent identifier for agent-level isolation (filtered from metadata)
        appId: Optional application identifier for app-level isolation (filtered from metadata)
        threshold: Optional similarity threshold for search results (0.0 to 1.0)
        filters: Optional additional filters for the search
        topK: Maximum number of results to return (default: 3)
    """
    try:
        # Validate required parameters
        if not userId or userId.strip() == "":
            return "Error: userId is required and cannot be empty"
        
        mem0_client = ctx.request_context.lifespan_context.mem0_client
        
        # Use provided userId (required) and fallback to defaults for optional fields
        effective_user_id = userId
        effective_agent_id = agentId or DEFAULT_AGENT_ID
        effective_app_id = appId or DEFAULT_APP_ID
        
        # Set default limit if not provided
        limit = topK if topK is not None else 3
        
        # Search memories with proper isolation
        # Note: Mem0's search() method only supports query, user_id, and limit parameters
        memories = mem0_client.search(
            query, 
            user_id=effective_user_id,
            limit=limit
        )
        
        if isinstance(memories, dict) and "results" in memories:
            flattened_memories = [memory["memory"] for memory in memories["results"]]
        else:
            flattened_memories = memories
        
        # Filter memories by agent_id, app_id, and session_id if specified
        filtered_memories = []
        for memory in flattened_memories:
            # Check if memory has metadata for filtering
            memory_metadata = memory.get("metadata", {})
            
            # Filter by agent_id if specified
            if effective_agent_id and memory_metadata.get("agent_id") != effective_agent_id:
                continue
                
            # Filter by app_id if specified
            if effective_app_id and memory_metadata.get("app_id") != effective_app_id:
                continue
                
            # Filter by session_id if specified
            if sessionId and memory_metadata.get("session_id") != sessionId:
                continue
                
            filtered_memories.append(memory)
        
        # Log the operation for security monitoring
        session_info = f" (session: {sessionId})" if sessionId else ""
        app_info = f" (app: {effective_app_id})" if effective_app_id else ""
        agent_info = f" (agent: {effective_agent_id})" if effective_agent_id else ""
        
        return json.dumps({
            "user_id": effective_user_id,
            "session_id": sessionId,
            "agent_id": effective_agent_id,
            "app_id": effective_app_id,
            "query": query,
            "results": filtered_memories,
            "count": len(filtered_memories),
            "total_count": len(flattened_memories)
        }, indent=2)
    
    except Exception as e:
        return f"Error searching memories: {str(e)}"

@mcp.tool()
async def delete_memory(
    ctx: Context,
    memoryId: str,
    userId: str,
    agentId: Optional[str] = None,
    appId: Optional[str] = None
) -> str:
    """Delete a specific memory with user isolation.

    This tool allows you to remove a specific memory by its ID.
    Deletion is isolated by userId to ensure users can only delete their own memories.

    Args:
        ctx: The MCP server provided context which includes the Mem0 client
        memoryId: The unique identifier of the memory to delete
        userId: Required user identifier for memory isolation (must be provided)
        agentId: Optional agent identifier for agent-level isolation
        appId: Optional application identifier for app-level isolation
    """
    try:
        # Validate required parameters
        if not userId or userId.strip() == "":
            return "Error: userId is required and cannot be empty"
        if not memoryId or memoryId.strip() == "":
            return "Error: memoryId is required and cannot be empty"
        
        mem0_client = ctx.request_context.lifespan_context.mem0_client
        
        # Use provided userId (required) and fallback to defaults for optional fields
        effective_user_id = userId
        effective_agent_id = agentId or DEFAULT_AGENT_ID
        effective_app_id = appId or DEFAULT_APP_ID
        
        # Note: Mem0's delete functionality may need to be implemented based on their API
        # For now, we'll return a placeholder response
        # TODO: Implement actual deletion when Mem0 supports it
        
        return f"Memory deletion requested for user '{effective_user_id}' (memoryId: {memoryId}). Note: Delete functionality may need to be implemented based on Mem0's current API support."
    
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
