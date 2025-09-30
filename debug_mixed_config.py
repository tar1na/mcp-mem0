#!/usr/bin/env python3
"""
Debug script for mixed LLM/embedder configuration.
"""

import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def debug_mixed_config():
    """Debug mixed configuration."""
    print("🔍 Debugging Mixed Configuration")
    print("=" * 50)
    
    try:
        # Load environment variables
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            print("⚠️  dotenv not available, using system environment variables")
        
        print("📋 Environment Variables:")
        print(f"  LLM_PROVIDER: {os.getenv('LLM_PROVIDER', 'NOT SET')}")
        print(f"  LLM_BASE_URL: {os.getenv('LLM_BASE_URL', 'NOT SET')}")
        print(f"  LLM_API_KEY: {'SET' if os.getenv('LLM_API_KEY') else 'NOT SET'}")
        print(f"  EMBEDDING_PROVIDER: {os.getenv('EMBEDDING_PROVIDER', 'NOT SET')}")
        print(f"  EMBEDDING_BASE_URL: {os.getenv('EMBEDDING_BASE_URL', 'NOT SET')}")
        print(f"  EMBEDDING_API_KEY: {'SET' if os.getenv('EMBEDDING_API_KEY') else 'NOT SET'}")
        print(f"  EMBEDDING_MODEL_CHOICE: {os.getenv('EMBEDDING_MODEL_CHOICE', 'NOT SET')}")
        print(f"  OPENAI_BASE_URL: {os.getenv('OPENAI_BASE_URL', 'NOT SET')}")
        print(f"  OPENAI_API_KEY: {'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET'}")
        print(f"  OLLAMA_BASE_URL: {os.getenv('OLLAMA_BASE_URL', 'NOT SET')}")
        print()
        
        # Test configuration building
        print("🔧 Testing configuration building...")
        from utils import get_mem0_client
        
        print("\n📊 Configuration Analysis:")
        llm_provider = os.getenv('LLM_PROVIDER', 'openai')
        embedding_provider = os.getenv('EMBEDDING_PROVIDER', llm_provider)
        
        print(f"  LLM Provider: {llm_provider}")
        print(f"  Embedding Provider: {embedding_provider}")
        
        if llm_provider == 'ollama' and embedding_provider == 'openai':
            print("  ✅ Mixed configuration detected")
            print("  📍 LLM will use Ollama")
            print("  📍 Embedder will use OpenAI")
            
            # Check if we have the right base URL for OpenAI
            embedding_base_url = os.getenv('EMBEDDING_BASE_URL') or os.getenv('LLM_BASE_URL')
            if embedding_base_url and 'api.openai.com' not in embedding_base_url:
                print(f"  ✅ Custom OpenAI endpoint: {embedding_base_url}")
            else:
                print("  ⚠️  Will use default OpenAI endpoint")
        else:
            print("  ℹ️  Not a mixed configuration")
        
        print("\n✅ Debug completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Debug failed: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    debug_mixed_config()
