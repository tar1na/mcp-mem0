#!/usr/bin/env python3
"""
Test script to verify Ollama configuration is working correctly.
This helps debug the OpenAI API key issue.
"""

import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_environment():
    """Test environment variables."""
    print("🔍 Testing Environment Variables")
    print("=" * 40)
    
    # Load .env file
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check key variables
    variables = [
        'LLM_PROVIDER',
        'EMBEDDING_PROVIDER', 
        'LLM_BASE_URL',
        'LLM_CHOICE',
        'EMBEDDING_MODEL_CHOICE',
        'OPENAI_API_KEY',
        'OPENAI_BASE_URL'
    ]
    
    for var in variables:
        value = os.getenv(var)
        if value:
            if 'API_KEY' in var and value:
                print(f"  {var}: {'*' * 8} (hidden)")
            else:
                print(f"  {var}: {value}")
        else:
            print(f"  {var}: NOT SET")
    
    print()

def test_mem0_config():
    """Test Mem0 configuration."""
    print("🔧 Testing Mem0 Configuration")
    print("=" * 40)
    
    try:
        from utils import get_mem0_client
        
        print("Creating Mem0 client...")
        client = get_mem0_client()
        print(f"✅ Mem0 client created: {type(client)}")
        
        # Check client internals
        if hasattr(client, '_llm'):
            print(f"  LLM provider: {getattr(client._llm, 'provider', 'unknown')}")
            if hasattr(client._llm, 'client'):
                print(f"  LLM client type: {type(client._llm.client)}")
        
        if hasattr(client, '_embedder'):
            print(f"  Embedder provider: {getattr(client._embedder, 'provider', 'unknown')}")
            if hasattr(client._embedder, 'client'):
                print(f"  Embedder client type: {type(client._embedder.client)}")
        
        # Test a simple operation
        print("\n🧪 Testing simple operation...")
        try:
            # This should not make any API calls, just test the client
            result = client.get_all(user_id="test_user", limit=1)
            print(f"✅ Test operation successful: {type(result)}")
        except Exception as e:
            print(f"❌ Test operation failed: {e}")
            if "openai" in str(e).lower() or "api.openai.com" in str(e):
                print("  🚨 This is the OpenAI API issue we're trying to fix!")
        
    except Exception as e:
        print(f"❌ Failed to create Mem0 client: {e}")
        if "openai" in str(e).lower() or "api.openai.com" in str(e):
            print("  🚨 This is the OpenAI API issue we're trying to fix!")

def main():
    """Main test function."""
    print("🧪 MCP-MEM0 Ollama Configuration Test")
    print("=" * 50)
    
    test_environment()
    test_mem0_config()
    
    print("\n📋 Summary:")
    print("If you see OpenAI API errors above, the issue is that Mem0")
    print("is still trying to use OpenAI internally despite your Ollama configuration.")
    print("\nThis could be due to:")
    print("1. Mem0 library version incompatibility")
    print("2. Missing environment variable configuration")
    print("3. Mem0 internal hardcoded OpenAI usage")
    print("\nNext steps:")
    print("1. Restart your MCP service")
    print("2. Check the debug logs for configuration details")
    print("3. Consider updating Mem0 library if the issue persists")

if __name__ == '__main__':
    main()
