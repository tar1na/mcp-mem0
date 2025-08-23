# User and Session Isolation in mcp-mem0

This document describes the implementation of user and session isolation in mcp-mem0, ensuring that memories are properly isolated between different users and conversation sessions.

## Overview

mcp-mem0 now supports **required** `userId` and **optional** `sessionId` parameters for all memory operations. This ensures:

- **User Isolation**: Users can only access their own memories
- **Session Isolation**: Conversations can be isolated by session when needed
- **Data Privacy**: No cross-user or cross-session data leakage
- **Security**: All operations require valid user identification

## Key Features

### 🔒 Required Parameters
- **`userId`**: **REQUIRED** - Unique identifier for each user
- **`sessionId`**: **OPTIONAL** - Conversation or session identifier

### 🛡️ Security Features
- Input validation for required parameters
- Environment variable fallbacks for development only
- Configuration warnings for production deployments
- Comprehensive error handling and logging

## API Reference

### 1. Save Memory

```python
@mcp.tool()
async def save_memory(
    ctx: Context, 
    content: str, 
    userId: str,                    # REQUIRED
    sessionId: Optional[str] = None, # OPTIONAL
    agentId: Optional[str] = None,   # OPTIONAL
    agentId: Optional[str] = None,   # OPTIONAL
    appId: Optional[str] = None,     # OPTIONAL
    metadata: Optional[Dict[str, Any]] = None
) -> str
```

**Example Usage:**
```json
{
  "tool": "save_memory",
  "args": {
    "content": "User prefers dark mode interface",
    "userId": "user_123",
    "sessionId": "chat_session_abc123",
    "agentId": "assistant_v1",
    "appId": "web_interface"
  }
}
```

### 2. Search Memories

```python
@mcp.tool()
async def search_memories(
    ctx: Context, 
    query: str, 
    userId: str,                    # REQUIRED
    sessionId: Optional[str] = None, # OPTIONAL
    agentId: Optional[str] = None,   # OPTIONAL
    appId: Optional[str] = None,     # OPTIONAL
    threshold: Optional[float] = None,
    filters: Optional[Dict[str, Any]] = None,
    topK: Optional[int] = None
) -> str
```

**Example Usage:**
```json
{
  "tool": "search_memories",
  "args": {
    "query": "interface preferences",
    "userId": "user_123",
    "sessionId": "chat_session_abc123",
    "topK": 5
    "topK": 5
  }
}
```

### 3. Get All Memories

```python
@mcp.tool()
async def get_all_memories(
    ctx: Context,
    userId: str,                    # REQUIRED
    sessionId: Optional[str] = None, # OPTIONAL
    agentId: Optional[str] = None,   # OPTIONAL
    appId: Optional[str] = None      # OPTIONAL
) -> str
```

**Example Usage:**
```json
{
  "tool": "get_all_memories",
  "args": {
    "userId": "user_123",
    "sessionId": "chat_session_abc123"
  }
}
```

### 4. Delete Memory

```python
@mcp.tool()
async def delete_memory(
    ctx: Context,
    memoryId: str,
    userId: str,                    # REQUIRED
    agentId: Optional[str] = None,   # OPTIONAL
    appId: Optional[str] = None      # OPTIONAL
) -> str
```

**Example Usage:**
```json
{
  "tool": "delete_memory",
  "args": {
    "memoryId": "mem_xyz789",
    "userId": "user_123"
  }
}
```

## Configuration

### Environment Variables

```bash
# Required for production (override defaults)
DEFAULT_USER_ID=your_production_user_id
DEFAULT_AGENT_ID=your_agent_id
DEFAULT_APP_ID=your_app_id

# Server configuration
HOST=0.0.0.0
PORT=8050
TRANSPORT=sse

# Mem0 configuration
LLM_PROVIDER=openai
LLM_API_KEY=your_api_key
LLM_CHOICE=gpt-3.5-turbo
EMBEDDING_MODEL_CHOICE=text-embedding-3-small
DATABASE_URL=your_database_url
```

### Development vs Production

**Development (Local Testing):**
- Uses default values for missing parameters
- Shows configuration warnings
- Allows testing with minimal setup

**Production:**
- **MUST** override `DEFAULT_USER_ID`
- **MUST** provide proper `LLM_API_KEY` and `DATABASE_URL`
- All tool calls **MUST** include valid `userId`

## Usage Patterns

### 1. User-Specific Memory Storage

```python
# Store user preference
await save_memory(
    content="User prefers Python over JavaScript",
    userId="user_123"
)

# Store session-specific information
await save_memory(
    content="Current conversation about web development",
    userId="user_123",
    sessionId="web_dev_chat_001"
)
```

### 2. Session-Isolated Search

```python
# Search within current session only
results = await search_memories(
    query="web development",
    userId="user_123",
    sessionId="web_dev_chat_001"
)

# Search across all user sessions
all_results = await search_memories(
    query="Python",
    userId="user_123"
)
```

### 3. Cross-Session Memory Access

```python
# Get all memories for a user across all sessions
all_memories = await get_all_memories(userId="user_123")

# Get memories from specific session only
session_memories = await get_all_memories(
    userId="user_123",
    sessionId="web_dev_chat_001"
)
```

## Security Considerations

### 1. User ID Validation
- **Never** accept empty or null `userId`
- **Always** validate `userId` before processing
- Use stable, unique identifiers (e.g., auth subject, tenant+user key)

### 2. Session Management
- `sessionId` should be transient (conversation UUID, HTTP session ID)
- Don't rely on session IDs for long-term user identification
- Consider session expiration and cleanup

### 3. Environment Security
- **Never** use default user IDs in production
- **Always** set proper environment variables
- Monitor configuration warnings and errors

## Testing

### Run Isolation Tests

```bash
python test_user_isolation.py
```

### Test Coverage

The test suite validates:
- ✅ User isolation (no cross-user data access)
- ✅ Session isolation (session-scoped searches)
- ✅ Cross-session searches (when no sessionId provided)
- ✅ Security validation (required userId)
- ✅ Error handling and edge cases

### Manual Testing

```bash
# Start the server
python src/main.py

# Test with different user IDs
curl -X POST http://localhost:8050/tools/save_memory \
  -H "Content-Type: application/json" \
  -d '{"content": "Test memory", "userId": "user_123"}'

curl -X POST http://localhost:8050/tools/search_memories \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "userId": "user_123"}'
```

## Migration Guide

### From Previous Version

1. **Update Tool Calls**: Add `userId` parameter to all memory operations
2. **Set Environment Variables**: Configure production user IDs
3. **Update Client Code**: Ensure all calls include valid user identification
4. **Test Isolation**: Verify no cross-user data access

### Example Migration

**Before:**
```python
await save_memory(ctx, "User preference")
await search_memories(ctx, "query", limit=5)
```

**After:**
```python
await save_memory(ctx, "User preference", userId="user_123")
await search_memories(ctx, "query", userId="user_123", topK=5)
```

## Troubleshooting

### Common Issues

1. **"userId is required" Error**
   - Ensure all tool calls include `userId` parameter
   - Check environment variable configuration

2. **Configuration Warnings**
   - Set proper environment variables for production
   - Override default values

3. **Memory Isolation Issues**
   - Verify `userId` is unique per user
   - Check session ID handling in your application

### Debug Mode

Enable debug logging by setting:
```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
```

## Best Practices

### 1. User Identification
- Use stable, unique identifiers (e.g., UUID, email hash)
- Avoid sequential or predictable IDs
- Consider user authentication integration

### 2. Session Management
- Generate unique session IDs for each conversation
- Use appropriate session granularity (per-chat, per-day, etc.)
- Implement session cleanup and expiration

### 3. Error Handling
- Always check for required parameters
- Provide meaningful error messages
- Log security-related events

### 4. Performance
- Use session IDs for conversation-scoped searches
- Avoid cross-session searches for large memory sets
- Consider memory pagination for large result sets

## Support

For issues and questions:
- Check the test suite for usage examples
- Review configuration warnings
- Ensure proper environment variable setup
- Verify user ID uniqueness and stability

---

**Note**: This implementation follows Mem0's MCP tool specifications and ensures proper isolation between users and sessions. Always test thoroughly in your specific environment before deploying to production.
