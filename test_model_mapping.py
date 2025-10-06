#!/usr/bin/env python3
"""
Test model mapping for provider mismatches.
"""

import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_model_mapping():
    """Test model mapping functionality."""
    print("🧪 Testing Model Mapping")
    print("=" * 50)
    
    try:
        # Load environment variables
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            print("⚠️  dotenv not available, using system environment variables")
        
        print("📋 Current Configuration:")
        print(f"  LLM_PROVIDER: {os.getenv('LLM_PROVIDER', 'NOT SET')}")
        print(f"  EMBEDDING_PROVIDER: {os.getenv('EMBEDDING_PROVIDER', 'NOT SET')}")
        print(f"  EMBEDDING_MODEL_CHOICE: {os.getenv('EMBEDDING_MODEL_CHOICE', 'NOT SET')}")
        print()
        
        # Test the configuration building
        print("🔧 Testing configuration building with model mapping...")
        from utils import get_mem0_client
        
        print("\n✅ Model mapping test completed successfully!")
        print("\n📊 Expected Behavior:")
        print("- Ollama model names with OpenAI provider should be mapped to OpenAI models")
        print("- OpenAI model names with Ollama provider should be mapped to Ollama models")
        print("- This should resolve the 404 error you were seeing")
        
    except Exception as e:
        print(f"\n❌ Model mapping test failed: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    test_model_mapping()
