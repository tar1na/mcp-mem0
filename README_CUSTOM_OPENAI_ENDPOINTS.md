# Custom OpenAI Endpoints Configuration

This guide explains how to configure mcp-mem0 to use custom OpenAI-compatible API endpoints instead of the default `api.openai.com`.

## Overview

The system supports using custom OpenAI-compatible endpoints for both LLM and embedding operations. This is useful when you have:
- Your own OpenAI-compatible API server
- A proxy server for OpenAI API calls
- A different provider with OpenAI-compatible API
- Local or private API endpoints

## Configuration

### Environment Variables

Set these variables in your `.env` file:

```bash
# Use OpenAI provider
LLM_PROVIDER=openai

# Your custom API endpoint
LLM_BASE_URL=http://db-server.local:8009/v1

# Your API key (if required)
LLM_API_KEY=your_api_key_here

# Model to use
LLM_CHOICE=gpt-3.5-turbo

# Embedding configuration
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL_CHOICE=text-embedding-3-small
EMBEDDING_MODEL_DIMS=1536
```

### Example Configurations

#### 1. Custom OpenAI Server
```bash
LLM_PROVIDER=openai
LLM_BASE_URL=http://db-server.local:8009/v1
LLM_API_KEY=sk-your-custom-key
LLM_CHOICE=gpt-3.5-turbo
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL_CHOICE=text-embedding-3-small
```

#### 2. OpenAI with Proxy
```bash
LLM_PROVIDER=openai
LLM_BASE_URL=https://your-proxy.com/openai/v1
LLM_API_KEY=sk-your-openai-key
LLM_CHOICE=gpt-4
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL_CHOICE=text-embedding-3-large
```

#### 3. Mixed Configuration (Custom LLM + Default Embeddings)
```bash
LLM_PROVIDER=openai
LLM_BASE_URL=http://db-server.local:8009/v1
LLM_CHOICE=gpt-3.5-turbo
EMBEDDING_PROVIDER=openai
# No EMBEDDING_BASE_URL - uses default api.openai.com for embeddings
EMBEDDING_MODEL_CHOICE=text-embedding-3-small
```

## How It Works

### 1. LLM Configuration
When `LLM_PROVIDER=openai` and `LLM_BASE_URL` is set:
- The system configures the LLM to use your custom endpoint
- Sets `base_url` in the OpenAI client configuration
- Sets `OPENAI_BASE_URL` environment variable for Mem0 internal use

### 2. Embedding Configuration
When `EMBEDDING_PROVIDER=openai` and `LLM_BASE_URL` is set:
- The system configures the embedder to use your custom endpoint
- Uses the same base URL as the LLM (from `LLM_BASE_URL`)
- Sets `OPENAI_BASE_URL` environment variable for Mem0 internal use

### 3. Environment Variable Management
The system automatically:
- Sets `OPENAI_BASE_URL` to your custom endpoint
- Preserves your `OPENAI_API_KEY` if set
- Clears conflicting variables when using Ollama

## API Compatibility

Your custom endpoint must support the OpenAI API format:

### Required Endpoints

#### Chat Completions
```
POST /v1/chat/completions
Content-Type: application/json
Authorization: Bearer <api_key>

{
  "model": "gpt-3.5-turbo",
  "messages": [...],
  "temperature": 0.2,
  "max_tokens": 2000
}
```

#### Embeddings
```
POST /v1/embeddings
Content-Type: application/json
Authorization: Bearer <api_key>

{
  "model": "text-embedding-3-small",
  "input": "text to embed"
}
```

### Response Format
Your server must return responses in OpenAI format:

#### Chat Completions Response
```json
{
  "choices": [
    {
      "message": {
        "content": "Response text",
        "role": "assistant"
      }
    }
  ]
}
```

#### Embeddings Response
```json
{
  "data": [
    {
      "embedding": [0.1, 0.2, ...],
      "index": 0
    }
  ]
}
```

## Debugging

### Enable Debug Logging
Add to your `.env` file:
```bash
LOG_LEVEL=DEBUG
```

### Check Configuration
The system will log:
```
DEBUG: Set custom OpenAI base URL: http://db-server.local:8009/v1
DEBUG: Using custom OpenAI endpoint: http://db-server.local:8009/v1
```

### Test Configuration
Use the test script:
```bash
python3 test_ollama_config.py
```

## Common Issues

### 1. API Key Errors
**Problem**: "Incorrect API key provided"
**Solution**: 
- Check your `LLM_API_KEY` is correct
- Verify your custom server accepts the API key format
- Ensure the API key is valid for your custom endpoint

### 2. Connection Errors
**Problem**: "Connection refused" or timeout errors
**Solution**:
- Verify `LLM_BASE_URL` is accessible
- Check network connectivity
- Ensure the server is running and accepting connections

### 3. Model Not Found
**Problem**: "Model not found" errors
**Solution**:
- Verify the model name in `LLM_CHOICE` exists on your server
- Check if your server supports the specific model
- Try a different model name

### 4. Embedding Errors
**Problem**: Embeddings still use `api.openai.com`
**Solution**:
- Ensure `EMBEDDING_PROVIDER=openai` is set
- Check that `LLM_BASE_URL` is set
- Verify the debug logs show the custom URL being used

## Advanced Configuration

### Separate Endpoints for LLM and Embeddings
If you need different endpoints for LLM and embeddings:

```bash
# LLM endpoint
LLM_PROVIDER=openai
LLM_BASE_URL=http://llm-server:8009/v1
LLM_CHOICE=gpt-3.5-turbo

# Embedding endpoint (would need code modification)
EMBEDDING_PROVIDER=openai
# Note: Currently uses LLM_BASE_URL, would need EMBEDDING_BASE_URL support
```

### Custom Headers
If your server requires custom headers, you may need to modify the configuration in `utils.py`:

```python
config["llm"]["config"]["headers"] = {
    "X-Custom-Header": "value"
}
```

## Security Considerations

1. **API Key Security**: Store API keys securely, not in code
2. **Network Security**: Use HTTPS for production endpoints
3. **Access Control**: Implement proper authentication on your custom server
4. **Rate Limiting**: Consider rate limiting on your custom endpoint
5. **Logging**: Monitor API usage and errors

## Performance Optimization

1. **Connection Pooling**: The system uses connection pooling for database operations
2. **Caching**: Consider implementing response caching on your custom server
3. **Load Balancing**: Use multiple instances of your custom server
4. **Monitoring**: Monitor response times and error rates

## Troubleshooting Checklist

- [ ] `LLM_PROVIDER=openai` is set
- [ ] `LLM_BASE_URL` points to your custom endpoint
- [ ] `EMBEDDING_PROVIDER=openai` is set (if using OpenAI embeddings)
- [ ] `LLM_API_KEY` is set and valid
- [ ] Custom server is running and accessible
- [ ] Custom server supports required API endpoints
- [ ] Model names match what your server supports
- [ ] Network connectivity is working
- [ ] Debug logs show custom URL being used
- [ ] No conflicting environment variables

## Example Server Implementations

### Simple Python Flask Server
```python
from flask import Flask, request, jsonify
import openai

app = Flask(__name__)

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    # Forward to OpenAI or your custom logic
    response = openai.ChatCompletion.create(**request.json)
    return jsonify(response)

@app.route('/v1/embeddings', methods=['POST'])
def embeddings():
    # Forward to OpenAI or your custom logic
    response = openai.Embedding.create(**request.json)
    return jsonify(response)
```

### Nginx Proxy
```nginx
location /v1/ {
    proxy_pass https://api.openai.com/v1/;
    proxy_set_header Authorization $http_authorization;
    proxy_set_header Content-Type $http_content_type;
}
```

This configuration allows you to use any OpenAI-compatible endpoint while maintaining full functionality of the mcp-mem0 service.
