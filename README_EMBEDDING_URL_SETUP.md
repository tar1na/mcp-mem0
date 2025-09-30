# Embedding Provider URL Setup Guide

This guide explains how to configure different URLs for LLM and embedding operations in mcp-mem0.

## Overview

By default, the system uses the same `LLM_BASE_URL` for both LLM and embedding operations. However, you can configure separate endpoints for embeddings using `EMBEDDING_BASE_URL`.

## Configuration Options

### Option 1: Same URL for LLM and Embeddings (Default)

```bash
# Both LLM and embeddings use the same endpoint
LLM_PROVIDER=openai
LLM_BASE_URL=http://db-server.local:8009/v1
LLM_API_KEY=your_api_key
EMBEDDING_PROVIDER=openai
# EMBEDDING_BASE_URL is not set, so it uses LLM_BASE_URL
```

### Option 2: Different URLs for LLM and Embeddings

```bash
# LLM uses one endpoint
LLM_PROVIDER=openai
LLM_BASE_URL=http://llm-server.local:8009/v1
LLM_API_KEY=your_llm_api_key

# Embeddings use a different endpoint
EMBEDDING_PROVIDER=openai
EMBEDDING_BASE_URL=http://embedding-server.local:8009/v1
# Note: Uses the same API key unless you configure differently
```

### Option 3: Mixed Providers

```bash
# LLM uses OpenAI
LLM_PROVIDER=openai
LLM_BASE_URL=http://db-server.local:8009/v1
LLM_API_KEY=your_api_key

# Embeddings use Ollama
EMBEDDING_PROVIDER=ollama
EMBEDDING_BASE_URL=http://ollama-server.local:11434
EMBEDDING_MODEL_CHOICE=nomic-embed-text
```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `LLM_PROVIDER` | Provider for LLM operations | `openai`, `ollama`, `openrouter` |
| `LLM_BASE_URL` | Base URL for LLM operations | `http://db-server.local:8009/v1` |
| `LLM_API_KEY` | API key for LLM operations | `sk-your-api-key` |
| `EMBEDDING_PROVIDER` | Provider for embedding operations | `openai`, `ollama` |

### Optional Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `EMBEDDING_BASE_URL` | Base URL for embedding operations | `http://embedding-server.local:8009/v1` |
| `EMBEDDING_API_KEY` | API key for embedding operations | `sk-embedding-your-key` |
| `EMBEDDING_MODEL_CHOICE` | Model for embeddings | `text-embedding-3-small` |
| `EMBEDDING_MODEL_DIMS` | Embedding dimensions | `1536` |

## Configuration Examples

### Example 1: Single Server Setup

```bash
# All operations use the same server
LLM_PROVIDER=openai
LLM_BASE_URL=http://db-server.local:8009/v1
LLM_API_KEY=sk-your-key
LLM_CHOICE=gpt-3.5-turbo
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL_CHOICE=text-embedding-3-small
EMBEDDING_MODEL_DIMS=1536
```

### Example 2: Separate LLM and Embedding Servers

```bash
# LLM server
LLM_PROVIDER=openai
LLM_BASE_URL=http://llm-server.local:8009/v1
LLM_API_KEY=sk-llm-key
LLM_CHOICE=gpt-4

# Embedding server
EMBEDDING_PROVIDER=openai
EMBEDDING_BASE_URL=http://embedding-server.local:8009/v1
EMBEDDING_MODEL_CHOICE=text-embedding-3-large
EMBEDDING_MODEL_DIMS=3072
```

### Example 2b: Separate Servers with Different API Keys

```bash
# LLM server with its own API key
LLM_PROVIDER=openai
LLM_BASE_URL=http://llm-server.local:8009/v1
LLM_API_KEY=sk-llm-your-llm-api-key
LLM_CHOICE=gpt-4

# Embedding server with its own API key
EMBEDDING_PROVIDER=openai
EMBEDDING_BASE_URL=http://embedding-server.local:8009/v1
EMBEDDING_API_KEY=sk-embedding-your-embedding-api-key
EMBEDDING_MODEL_CHOICE=text-embedding-3-large
EMBEDDING_MODEL_DIMS=3072
```

### Example 3: OpenAI LLM + Ollama Embeddings

```bash
# LLM uses OpenAI
LLM_PROVIDER=openai
LLM_BASE_URL=http://db-server.local:8009/v1
LLM_API_KEY=sk-your-key
LLM_CHOICE=gpt-3.5-turbo

# Embeddings use Ollama
EMBEDDING_PROVIDER=ollama
EMBEDDING_BASE_URL=http://ollama-server.local:11434
EMBEDDING_MODEL_CHOICE=nomic-embed-text
EMBEDDING_MODEL_DIMS=1024
```

### Example 4: Load Balanced Setup

```bash
# LLM with load balancer
LLM_PROVIDER=openai
LLM_BASE_URL=http://llm-lb.local:8009/v1
LLM_API_KEY=sk-your-key

# Embeddings with different load balancer
EMBEDDING_PROVIDER=openai
EMBEDDING_BASE_URL=http://embedding-lb.local:8009/v1
EMBEDDING_MODEL_CHOICE=text-embedding-3-small
```

### Example 5: No Authentication Required

```bash
# Servers that don't require API key authentication
LLM_PROVIDER=openai
LLM_BASE_URL=http://no-auth-server.local:8009/v1
LLM_API_KEY=
LLM_CHOICE=gpt-3.5-turbo

EMBEDDING_PROVIDER=openai
EMBEDDING_BASE_URL=http://no-auth-embedding.local:8009/v1
EMBEDDING_API_KEY=
EMBEDDING_MODEL_CHOICE=text-embedding-3-small
```

## How It Works

### URL Resolution Logic

1. **If `EMBEDDING_BASE_URL` is set**: Use it for embedding operations
2. **If `EMBEDDING_BASE_URL` is not set**: Use `LLM_BASE_URL` for embedding operations
3. **If neither is set**: Use default provider endpoints

### API Key Resolution Logic

1. **If `EMBEDDING_API_KEY` is set**: Use it for embedding operations
2. **If `EMBEDDING_API_KEY` is not set**: Use `LLM_API_KEY` for embedding operations
3. **If neither is set**: Use default provider authentication

### Empty API Key Handling

The system supports empty API keys for servers that don't require authentication:

- **Empty string (`""`)**: Server doesn't require authentication
- **Not set (`null`)**: Use default authentication behavior
- **Valid key**: Use the provided API key

This is useful for:
- Local development servers
- Internal servers with IP-based access control
- Public APIs without authentication
- Servers using other authentication methods

### Debug Logging

The system will log which URLs and API keys are being used:

```
DEBUG: Set custom OpenAI base URL: http://db-server.local:8009/v1
DEBUG: Set custom OpenAI base URL for embedder: http://embedding-server.local:8009/v1
DEBUG: Using dedicated EMBEDDING_BASE_URL
DEBUG: Using dedicated EMBEDDING_API_KEY for embeddings
```

**Note**: The embedder configuration doesn't support `base_url` parameter directly. Instead, the system sets the `OPENAI_BASE_URL` environment variable, which Mem0 uses internally for embedding operations.

Or when using the same API key:

```
DEBUG: Set custom OpenAI base URL for embedder: http://embedding-server.local:8009/v1
DEBUG: Using dedicated EMBEDDING_BASE_URL
DEBUG: Using LLM_API_KEY for embeddings
```

Or when using empty API keys:

```
DEBUG: Set custom OpenAI base URL: http://no-auth-server.local:8009/v1
DEBUG: Using empty API key (server may not require authentication)
DEBUG: Set custom OpenAI base URL for embedder: http://no-auth-embedding.local:8009/v1
DEBUG: Using empty EMBEDDING_API_KEY for embeddings (server may not require authentication)
```

## API Compatibility

### OpenAI-Compatible Endpoints

Your embedding server must support:

#### Embeddings Endpoint
```
POST /v1/embeddings
Content-Type: application/json
Authorization: Bearer <api_key>

{
  "model": "text-embedding-3-small",
  "input": "text to embed"
}
```

#### Response Format
```json
{
  "data": [
    {
      "embedding": [0.1, 0.2, 0.3, ...],
      "index": 0
    }
  ]
}
```

### Ollama Endpoints

For Ollama, the endpoint format is different:

```
POST /api/embeddings
Content-Type: application/json

{
  "model": "nomic-embed-text",
  "prompt": "text to embed"
}
```

## Testing Your Configuration

### 1. Test Script

Use the provided test script:

```bash
python3 test_custom_endpoint.py
```

### 2. Manual Testing

Test your embedding endpoint directly:

```bash
curl -X POST "http://embedding-server.local:8009/v1/embeddings" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "text-embedding-3-small",
    "input": "test embedding"
  }'
```

### 3. Check Debug Logs

Look for these debug messages in your service logs:

```
DEBUG: Using dedicated EMBEDDING_BASE_URL
DEBUG: Set custom OpenAI base URL for embedder: http://embedding-server.local:8009/v1
```

## Common Issues

### 1. Embeddings Still Use LLM URL

**Problem**: Embeddings are using `LLM_BASE_URL` instead of `EMBEDDING_BASE_URL`

**Solution**: 
- Check that `EMBEDDING_BASE_URL` is set correctly
- Verify there are no typos in the variable name
- Restart the service after making changes

### 2. API Key Issues

**Problem**: "Incorrect API key provided" for embeddings

**Solution**:
- Ensure your embedding server accepts the same API key
- Check if your embedding server requires a different API key format
- Verify the API key is valid for the embedding endpoint

### 3. Model Not Found

**Problem**: "Model not found" errors for embeddings

**Solution**:
- Verify the model name in `EMBEDDING_MODEL_CHOICE`
- Check if your embedding server supports the model
- Try a different model name

### 4. Network Issues

**Problem**: Connection timeouts or refused connections

**Solution**:
- Verify network connectivity to the embedding server
- Check if the embedding server is running
- Ensure firewall rules allow connections

## Performance Considerations

### 1. Latency

- Use geographically close servers for embeddings
- Consider using CDN for embedding endpoints
- Monitor response times

### 2. Load Balancing

- Use load balancers for high availability
- Implement health checks for embedding servers
- Consider auto-scaling for embedding services

### 3. Caching

- Implement response caching for embeddings
- Use Redis or similar for embedding cache
- Set appropriate cache TTL

## Security Considerations

### 1. API Key Management

- Use different API keys for different services
- Rotate API keys regularly
- Store keys securely (not in code)

### 2. Network Security

- Use HTTPS for production endpoints
- Implement proper authentication
- Use VPN or private networks when possible

### 3. Access Control

- Implement rate limiting
- Monitor API usage
- Log all embedding requests

## Monitoring

### 1. Health Checks

Monitor both LLM and embedding endpoints:

```bash
# Check LLM endpoint
curl -f "http://llm-server.local:8009/v1/models"

# Check embedding endpoint
curl -f "http://embedding-server.local:8009/v1/embeddings" \
  -H "Authorization: Bearer your-key" \
  -H "Content-Type: application/json" \
  -d '{"model": "text-embedding-3-small", "input": "test"}'
```

### 2. Metrics

Track these metrics:
- Response times for both endpoints
- Error rates
- API key usage
- Model availability

### 3. Alerts

Set up alerts for:
- High response times
- High error rates
- Service unavailability
- API key failures

## Troubleshooting Checklist

- [ ] `EMBEDDING_BASE_URL` is set correctly
- [ ] `EMBEDDING_PROVIDER` matches your server type
- [ ] API key is valid for the embedding endpoint
- [ ] Embedding server is running and accessible
- [ ] Network connectivity is working
- [ ] Model name is correct
- [ ] Service has been restarted after changes
- [ ] Debug logs show the correct URLs being used
- [ ] No conflicting environment variables

This configuration allows you to optimize your setup by using the most appropriate servers for different operations while maintaining full functionality.
