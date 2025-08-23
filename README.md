<h1 align="center">MCP-Mem0: Long-Term Memory for AI Agents</h1>

<p align="center">
  <img src="public/Mem0AndMCP.png" alt="Mem0 and MCP Integration" width="600">
</p>

A template implementation of the [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server integrated with [Mem0](https://mem0.ai) for providing AI agents with persistent memory capabilities.

Use this as a reference point to build your MCP servers yourself, or give this as an example to an AI coding assistant and tell it to follow this example for structure and code correctness!

## Overview

This project demonstrates how to build an MCP server that enables AI agents to store, retrieve, and search memories using semantic search with **complete user and session isolation**. It serves as a practical template for creating your own MCP servers, simply using Mem0 and a practical example.

The implementation follows the best practices laid out by Anthropic for building MCP servers, allowing seamless integration with any MCP-compatible client while ensuring data privacy and security through proper isolation mechanisms.

> **🚨 Breaking Changes**: This version introduces required `userId` parameters for all memory operations. See the [Migration Guide](README_USER_ISOLATION.md#migration-guide) for details on updating existing code.

## Features

The server provides four essential memory management tools with **user and session isolation**:

1. **`save_memory`**: Store any information in long-term memory with semantic indexing and user isolation
2. **`get_all_memories`**: Retrieve all stored memories for a specific user with optional session scoping
3. **`search_memories`**: Find relevant memories using semantic search within user and optional session boundaries
4. **`delete_memory`**: Remove specific memories with user-level access control

### 🔒 Security & Isolation Features
- **Required `userId`**: All operations require user identification for complete isolation
- **Optional `sessionId`**: Session-scoped memory access for conversation privacy
- **Cross-User Protection**: No data leakage between different users
- **Session Management**: Flexible memory access patterns (per-session or cross-session)

## Prerequisites

- Python 3.12+
- Supabase or any PostgreSQL database (for vector storage of memories)
- API keys for your chosen LLM provider (OpenAI, OpenRouter, or Ollama)
- Docker if running the MCP server as a container (recommended)

## Installation

### Using uv

1. Install uv if you don't have it:
   ```bash
   pip install uv
   ```

2. Clone this repository:
   ```bash
   git clone https://github.com/coleam00/mcp-mem0.git
   cd mcp-mem0
   ```

3. Install dependencies:
   ```bash
   uv pip install -e .
   ```

4. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

5. Configure your environment variables in the `.env` file (see Configuration section)

### Using Docker (Recommended)

1. Build the Docker image:
   ```bash
   docker build -t mcp/mem0 --build-arg PORT=8050 .
   ```

2. Create a `.env` file based on `.env.example` and configure your environment variables

## Configuration

The following environment variables can be configured in your `.env` file:

### Server Configuration
| Variable | Description | Example |
|----------|-------------|----------|
| `TRANSPORT` | Transport protocol (sse or stdio) | `sse` |
| `HOST` | Host to bind to when using SSE transport | `0.0.0.0` |
| `PORT` | Port to listen on when using SSE transport | `8050` |

### User & Application Identification
| Variable | Description | Example | Required |
|----------|-------------|----------|----------|
| `DEFAULT_USER_ID` | Default user ID for development | `default_user` | **Production** |
| `DEFAULT_AGENT_ID` | Default agent identifier | `my_agent` | Optional |
| `DEFAULT_APP_ID` | Default application identifier | `my_app` | Optional |

### LLM Configuration
| Variable | Description | Example |
|----------|-------------|----------|
| `LLM_PROVIDER` | LLM provider (openai, openrouter, or ollama) | `openai` |
| `LLM_BASE_URL` | Base URL for the LLM API | `https://api.openai.com/v1` |
| `LLM_API_KEY` | API key for the LLM provider | `sk-...` |
| `LLM_CHOICE` | LLM model to use | `gpt-4o-mini` |
| `EMBEDDING_MODEL_CHOICE` | Embedding model to use | `text-embedding-3-small` |

### Database Configuration
| Variable | Description | Example |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:port/db` |

> **⚠️ Security Note**: In production, **ALWAYS** override `DEFAULT_USER_ID` to prevent all users from sharing the same memory space. Use unique identifiers like authentication subject IDs, email hashes, or tenant+user combinations.

## Running the Server

### Using uv

#### SSE Transport

```bash
# Set TRANSPORT=sse in .env then:
uv run src/main.py
```

The MCP server will essentially be run as an API endpoint that you can then connect to with config shown below.

#### Stdio Transport

With stdio, the MCP client iself can spin up the MCP server, so nothing to run at this point.

### Using Docker

#### SSE Transport

```bash
docker run --env-file .env -p:8050:8050 mcp/mem0
```

The MCP server will essentially be run as an API endpoint within the container that you can then connect to with config shown below.

#### Stdio Transport

With stdio, the MCP client iself can spin up the MCP server container, so nothing to run at this point.

## Integration with MCP Clients

### SSE Configuration

Once you have the server running with SSE transport, you can connect to it using this configuration:

```json
{
  "mcpServers": {
    "mem0": {
      "transport": "sse",
      "url": "http://localhost:8050/sse"
    }
  }
}
```

> **Note for Windsurf users**: Use `serverUrl` instead of `url` in your configuration:
> ```json
> {
>   "mcpServers": {
>     "mem0": {
>       "transport": "sse",
>       "serverUrl": "http://localhost:8050/sse"
>     }
>   }
> }
> ```

> **Note for n8n users**: Use host.docker.internal instead of localhost since n8n has to reach outside of it's own container to the host machine:
> 
> So the full URL in the MCP node would be: http://host.docker.internal:8050/sse

Make sure to update the port if you are using a value other than the default 8050.

### Python with Stdio Configuration

Add this server to your MCP configuration for Claude Desktop, Windsurf, or any other MCP client:

```json
{
  "mcpServers": {
    "mem0": {
      "command": "your/path/to/mcp-mem0/.venv/Scripts/python.exe",
      "args": ["your/path/to/mcp-mem0/src/main.py"],
      "env": {
        "TRANSPORT": "stdio",
        "LLM_PROVIDER": "openai",
        "LLM_BASE_URL": "https://api.openai.com/v1",
        "LLM_API_KEY": "YOUR-API-KEY",
        "LLM_CHOICE": "gpt-4o-mini",
        "EMBEDDING_MODEL_CHOICE": "text-embedding-3-small",
        "DATABASE_URL": "YOUR-DATABASE-URL"
      }
    }
  }
}
```

### Docker with Stdio Configuration

```json
{
  "mcpServers": {
    "mem0": {
      "command": "docker",
      "args": ["run", "--rm", "-i", 
               "-e", "TRANSPORT", 
               "-e", "LLM_PROVIDER", 
               "-e", "LLM_BASE_URL", 
               "-e", "LLM_API_KEY", 
               "-e", "LLM_CHOICE", 
               "-e", "EMBEDDING_MODEL_CHOICE", 
               "-e", "DATABASE_URL", 
               "mcp/mem0"],
      "env": {
        "TRANSPORT": "stdio",
        "LLM_PROVIDER": "openai",
        "LLM_BASE_URL": "https://api.openai.com/v1",
        "LLM_API_KEY": "YOUR-API-KEY",
        "LLM_CHOICE": "gpt-4o-mini",
        "EMBEDDING_MODEL_CHOICE": "text-embedding-3-small",
        "DATABASE_URL": "YOUR-DATABASE-URL"
      }
    }
  }
}
```

## API Usage Examples

### Basic Memory Operations

```python
# Save a memory for a specific user
await save_memory(
    content="User prefers dark mode interface",
    userId="user_123"
)

# Save a memory with session isolation
await save_memory(
    content="Current conversation about web development",
    userId="user_123",
    sessionId="chat_session_abc123"
)

# Search memories within a session
results = await search_memories(
    query="interface preferences",
    userId="user_123",
    sessionId="chat_session_abc123"
)

# Search across all user sessions
all_results = await search_memories(
    query="Python",
    userId="user_123"
)

# Get all memories for a user
memories = await get_all_memories(userId="user_123")

# Delete a specific memory
await delete_memory(
    memoryId="mem_xyz789",
    userId="user_123"
)
```

### Security & Isolation

- **`userId` is REQUIRED** for all operations
- **`sessionId` is OPTIONAL** for conversation-level isolation
- Users can only access their own memories
- Sessions provide additional privacy boundaries
- No cross-user or cross-session data leakage

## Building Your Own Server

This template provides a foundation for building more complex MCP servers. To build your own:

1. Add your own tools by creating methods with the `@mcp.tool()` decorator
2. Create your own lifespan function to add your own dependencies (clients, database connections, etc.)
3. Modify the `utils.py` file for any helper functions you need for your MCP server
4. Feel free to add prompts and resources as well with `@mcp.resource()` and `@mcp.prompt()`

## Testing

Run the comprehensive test suite to verify user and session isolation:

```bash
python3 test_user_isolation.py
```

The test suite validates:
- ✅ User isolation (no cross-user data access)
- ✅ Session isolation (session-scoped searches)
- ✅ Cross-session searches (when no sessionId provided)
- ✅ Security validation (required userId)
- ✅ Error handling and edge cases

## Additional Resources

- **[User Isolation Documentation](README_USER_ISOLATION.md)** - Comprehensive guide to user and session isolation
- **[Implementation Summary](IMPLEMENTATION_SUMMARY.md)** - Complete overview of the implementation
- **[Environment Configuration](env.example)** - Example environment file with security notes
- **[Test Suite](test_user_isolation.py)** - Validation tests for all isolation features

## Security Considerations

- **Production Deployment**: Always override `DEFAULT_USER_ID` in production
- **User Identification**: Use stable, unique identifiers (UUIDs, auth subject IDs)
- **Session Management**: Generate transient session IDs for conversations
- **Environment Variables**: Secure all API keys and database credentials
- **Regular Testing**: Verify isolation features work correctly in your environment
