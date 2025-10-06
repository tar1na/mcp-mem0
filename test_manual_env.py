#!/usr/bin/env python3
"""
Test manual environment variable loading.
"""

import os

def load_env_manually():
    """Load .env file manually."""
    env_file = '.env'
    if not os.path.exists(env_file):
        print(f"❌ {env_file} not found")
        return False
    
    print(f"📁 Loading {env_file} manually...")
    
    with open(env_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Remove quotes if present
                if value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                elif value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                
                os.environ[key] = value
                print(f"  {key} = {value}")
    
    return True

def test_manual_env():
    """Test manual environment loading."""
    print("🔍 Testing Manual Environment Loading")
    print("=" * 50)
    
    if not load_env_manually():
        return False
    
    print("\n📋 Environment Variables:")
    print(f"  LLM_PROVIDER: {os.getenv('LLM_PROVIDER', 'NOT SET')}")
    print(f"  LLM_BASE_URL: {os.getenv('LLM_BASE_URL', 'NOT SET')}")
    print(f"  EMBEDDING_PROVIDER: {os.getenv('EMBEDDING_PROVIDER', 'NOT SET')}")
    print(f"  EMBEDDING_MODEL_CHOICE: {os.getenv('EMBEDDING_MODEL_CHOICE', 'NOT SET')}")
    print(f"  OPENAI_BASE_URL: {os.getenv('OPENAI_BASE_URL', 'NOT SET')}")
    print(f"  OLLAMA_BASE_URL: {os.getenv('OLLAMA_BASE_URL', 'NOT SET')}")
    
    print("\n🔍 Analysis:")
    llm_provider = os.getenv('LLM_PROVIDER', 'openai')
    embedding_provider = os.getenv('EMBEDDING_PROVIDER', llm_provider)
    embedding_model = os.getenv('EMBEDDING_MODEL_CHOICE', '')
    
    print(f"  LLM Provider: {llm_provider}")
    print(f"  Embedding Provider: {embedding_provider}")
    print(f"  Embedding Model: {embedding_model}")
    
    if embedding_provider == 'openai' and 'ollama' in embedding_model.lower():
        print("  ⚠️  MISMATCH: Embedding provider is OpenAI but model name suggests Ollama")
        print("  💡 Suggestion: Use an OpenAI embedding model like 'text-embedding-3-small'")
    elif embedding_provider == 'ollama' and 'openai' in embedding_model.lower():
        print("  ⚠️  MISMATCH: Embedding provider is Ollama but model name suggests OpenAI")
        print("  💡 Suggestion: Use an Ollama embedding model like 'nomic-embed-text'")
    else:
        print("  ✅ Configuration looks consistent")
    
    # Check base URLs
    llm_base_url = os.getenv('LLM_BASE_URL', '')
    if llm_base_url.startswith("'") and llm_base_url.endswith("'"):
        print("  ⚠️  LLM_BASE_URL has quotes - this might cause issues")
        print(f"  Raw value: {repr(llm_base_url)}")
        print(f"  Stripped: {llm_base_url.strip(chr(39))}")
    
    return True

if __name__ == '__main__':
    test_manual_env()
