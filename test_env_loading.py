#!/usr/bin/env python3
"""
Test environment variable loading.
"""

import os

def test_env_loading():
    """Test environment variable loading."""
    print("🔍 Testing Environment Variable Loading")
    print("=" * 50)
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ dotenv loaded successfully")
    except ImportError:
        print("⚠️  dotenv not available, using system environment variables")
    
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

if __name__ == '__main__':
    test_env_loading()
