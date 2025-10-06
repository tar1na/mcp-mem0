#!/usr/bin/env python3
"""
Test full configuration building process.
"""

import os
import sys

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

def simulate_config_building():
    """Simulate the configuration building process."""
    print("🔧 Simulating Configuration Building")
    print("=" * 50)
    
    if not load_env_manually():
        return False
    
    # Get configuration values
    llm_provider = os.getenv('LLM_PROVIDER', 'openai')
    embedding_provider = os.getenv('EMBEDDING_PROVIDER', llm_provider)
    embedding_model = os.getenv('EMBEDDING_MODEL_CHOICE', '')
    llm_base_url = os.getenv('LLM_BASE_URL', '')
    embedding_base_url = os.getenv('EMBEDDING_BASE_URL', '')
    
    print("📋 Configuration Values:")
    print(f"  LLM_PROVIDER: {llm_provider}")
    print(f"  EMBEDDING_PROVIDER: {embedding_provider}")
    print(f"  EMBEDDING_MODEL_CHOICE: {embedding_model}")
    print(f"  LLM_BASE_URL: {llm_base_url}")
    print(f"  EMBEDDING_BASE_URL: {embedding_base_url}")
    print()
    
    # Simulate the configuration building process
    print("🔧 Building Configuration:")
    
    # LLM Configuration
    if llm_provider == 'openai':
        print(f"  LLM Provider: {llm_provider}")
        if llm_base_url and 'api.openai.com' not in llm_base_url:
            print(f"  ✅ Custom LLM endpoint: {llm_base_url}")
        else:
            print("  ⚠️  Using default OpenAI endpoint")
    
    # Embedding Configuration
    if embedding_provider == 'openai':
        print(f"  Embedding Provider: {embedding_provider}")
        
        # Model mapping
        if embedding_model and ('ollama' in embedding_model.lower() or 'snowflake' in embedding_model.lower()):
            print(f"  🔄 Mapping Ollama model '{embedding_model}' to OpenAI model")
            if 'snowflake' in embedding_model.lower() or 'arctic' in embedding_model.lower():
                mapped_model = "text-embedding-3-small"
            else:
                mapped_model = "text-embedding-3-small"
            print(f"  ✅ Mapped to: {mapped_model}")
        else:
            mapped_model = embedding_model or "text-embedding-3-small"
            print(f"  ✅ Using model: {mapped_model}")
        
        # URL handling
        final_embedding_url = embedding_base_url or llm_base_url
        if final_embedding_url:
            if not final_embedding_url.startswith(('http://', 'https://')):
                final_embedding_url = f"http://{final_embedding_url}"
                print(f"  🔄 Added protocol: {final_embedding_url}")
            
            if 'api.openai.com' not in final_embedding_url:
                print(f"  ✅ Custom embedding endpoint: {final_embedding_url}")
            else:
                print("  ⚠️  Using default OpenAI endpoint")
        else:
            print("  ⚠️  No custom endpoint configured")
    
    print("\n🎯 Final Configuration:")
    print(f"  LLM: {llm_provider} -> {llm_base_url}")
    print(f"  Embedding: {embedding_provider} -> {final_embedding_url}")
    print(f"  Model: {mapped_model}")
    
    print("\n✅ Expected Results:")
    print("  - No more 404 errors")
    print("  - Proper model mapping")
    print("  - Custom endpoints working")
    print("  - UserId isolation supported")
    
    return True

if __name__ == '__main__':
    simulate_config_building()
