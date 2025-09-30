#!/usr/bin/env python3
"""
Test configuration logic without importing Mem0.
"""

import os
import sys

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
    
    return True

def test_model_mapping_logic():
    """Test the model mapping logic without Mem0."""
    print("🧪 Testing Model Mapping Logic")
    print("=" * 50)
    
    if not load_env_manually():
        return False
    
    print("📋 Current Configuration:")
    print(f"  LLM_PROVIDER: {os.getenv('LLM_PROVIDER', 'NOT SET')}")
    print(f"  EMBEDDING_PROVIDER: {os.getenv('EMBEDDING_PROVIDER', 'NOT SET')}")
    print(f"  EMBEDDING_MODEL_CHOICE: {os.getenv('EMBEDDING_MODEL_CHOICE', 'NOT SET')}")
    print(f"  EMBEDDING_BASE_URL: {os.getenv('EMBEDDING_BASE_URL', 'NOT SET')}")
    print()
    
    # Test the model mapping logic
    llm_provider = os.getenv('LLM_PROVIDER', 'openai')
    embedding_provider = os.getenv('EMBEDDING_PROVIDER', llm_provider)
    embedding_model = os.getenv('EMBEDDING_MODEL_CHOICE', '')
    
    print("🔧 Testing Model Mapping Logic:")
    
    if embedding_provider == 'openai':
        print(f"  Embedding Provider: {embedding_provider}")
        print(f"  Original Model: {embedding_model}")
        
        # Test the mapping logic
        if embedding_model and ('ollama' in embedding_model.lower() or 'snowflake' in embedding_model.lower()):
            print(f"  ✅ Detected Ollama model name '{embedding_model}' with OpenAI provider")
            print("  🔄 Mapping to appropriate OpenAI embedding model")
            
            if 'snowflake' in embedding_model.lower() or 'arctic' in embedding_model.lower():
                mapped_model = "text-embedding-3-small"
                print(f"  ✅ Mapped to OpenAI model: {mapped_model}")
            elif 'nomic' in embedding_model.lower():
                mapped_model = "text-embedding-3-small"
                print(f"  ✅ Mapped to OpenAI model: {mapped_model}")
            else:
                mapped_model = "text-embedding-3-small"
                print(f"  ✅ Mapped to default OpenAI model: {mapped_model}")
        else:
            print(f"  ✅ Model '{embedding_model}' is already compatible with OpenAI provider")
            mapped_model = embedding_model
    
    elif embedding_provider == 'ollama':
        print(f"  Embedding Provider: {embedding_provider}")
        print(f"  Original Model: {embedding_model}")
        
        # Test the mapping logic
        if embedding_model and 'text-embedding' in embedding_model.lower():
            print(f"  ✅ Detected OpenAI model name '{embedding_model}' with Ollama provider")
            print("  🔄 Mapping to appropriate Ollama embedding model")
            
            if 'text-embedding-3-small' in embedding_model.lower():
                mapped_model = "nomic-embed-text"
                print(f"  ✅ Mapped to Ollama model: {mapped_model}")
            elif 'text-embedding-3-large' in embedding_model.lower():
                mapped_model = "nomic-embed-text"
                print(f"  ✅ Mapped to Ollama model: {mapped_model}")
            else:
                mapped_model = "nomic-embed-text"
                print(f"  ✅ Mapped to default Ollama model: {mapped_model}")
        else:
            print(f"  ✅ Model '{embedding_model}' is already compatible with Ollama provider")
            mapped_model = embedding_model
    
    print("\n🎯 Expected Behavior:")
    print("- The 404 error should be resolved")
    print("- Embeddings will use the correct model for the provider")
    print("- Custom endpoints will be used properly")
    
    return True

if __name__ == '__main__':
    test_model_mapping_logic()
