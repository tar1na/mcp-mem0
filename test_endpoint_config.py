#!/usr/bin/env python3
"""
Test endpoint configuration.
"""

import os

def load_env_manually():
    """Load .env file manually."""
    env_file = '.env'
    if not os.path.exists(env_file):
        print(f"❌ {env_file} not found")
        return False
    
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
    
    return True

def test_endpoint_config():
    """Test endpoint configuration."""
    print("🌐 Testing Endpoint Configuration")
    print("=" * 50)
    
    if not load_env_manually():
        return False
    
    print("📋 Current Configuration:")
    print(f"  LLM_PROVIDER: {os.getenv('LLM_PROVIDER', 'NOT SET')}")
    print(f"  LLM_BASE_URL: {os.getenv('LLM_BASE_URL', 'NOT SET')}")
    print(f"  EMBEDDING_PROVIDER: {os.getenv('EMBEDDING_PROVIDER', 'NOT SET')}")
    print(f"  EMBEDDING_BASE_URL: {os.getenv('EMBEDDING_BASE_URL', 'NOT SET')}")
    print(f"  EMBEDDING_MODEL_CHOICE: {os.getenv('EMBEDDING_MODEL_CHOICE', 'NOT SET')}")
    print()
    
    # Test endpoint logic
    llm_provider = os.getenv('LLM_PROVIDER', 'openai')
    embedding_provider = os.getenv('EMBEDDING_PROVIDER', llm_provider)
    llm_base_url = os.getenv('LLM_BASE_URL', '')
    embedding_base_url = os.getenv('EMBEDDING_BASE_URL', '')
    
    print("🔧 Testing Endpoint Logic:")
    
    if llm_provider == 'openai':
        print(f"  LLM Provider: {llm_provider}")
        print(f"  LLM Base URL: {llm_base_url}")
        if llm_base_url and 'api.openai.com' not in llm_base_url:
            print(f"  ✅ Custom LLM endpoint: {llm_base_url}")
        else:
            print("  ⚠️  Using default OpenAI endpoint")
    
    if embedding_provider == 'openai':
        print(f"  Embedding Provider: {embedding_provider}")
        print(f"  Embedding Base URL: {embedding_base_url}")
        
        # Check if we have a dedicated embedding URL or fallback to LLM URL
        final_embedding_url = embedding_base_url or llm_base_url
        if final_embedding_url:
            if 'api.openai.com' not in final_embedding_url:
                print(f"  ✅ Custom embedding endpoint: {final_embedding_url}")
            else:
                print("  ⚠️  Using default OpenAI endpoint")
        else:
            print("  ⚠️  No custom endpoint configured")
    
    print("\n🎯 Expected Behavior:")
    print("- LLM operations will use: http://100.103.95.98:8009/v1")
    print("- Embedding operations will use: 100.90.213.64 (needs http:// prefix)")
    print("- Model mapping will convert snowflake-arctic-embed2:latest to text-embedding-3-small")
    
    # Check for potential issues
    print("\n⚠️  Potential Issues:")
    if embedding_base_url and not embedding_base_url.startswith('http'):
        print(f"  - EMBEDDING_BASE_URL should include protocol: {embedding_base_url} -> http://{embedding_base_url}")
    
    return True

if __name__ == '__main__':
    test_endpoint_config()
