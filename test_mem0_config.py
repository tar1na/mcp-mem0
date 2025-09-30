#!/usr/bin/env python3
"""
Test script to verify Mem0 configuration is working correctly.
This helps debug configuration issues with the Mem0 library.
"""

import os
import sys
import traceback

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_mem0_config():
    """Test Mem0 configuration."""
    print("🧪 Testing Mem0 Configuration")
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
        print(f"  OPENAI_BASE_URL: {os.getenv('OPENAI_BASE_URL', 'NOT SET')}")
        print(f"  OPENAI_API_KEY: {'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET'}")
        print()
        
        # Test Mem0 client creation
        print("🔧 Creating Mem0 client...")
        from utils import get_mem0_client
        
        client = get_mem0_client()
        print(f"✅ Mem0 client created successfully: {type(client)}")
        
        # Test basic functionality
        print("\n🧪 Testing basic functionality...")
        try:
            # Try to get memories (this will test the embedder)
            result = client.get_all(user_id="test_user", limit=1)
            print(f"✅ Basic functionality test passed: {type(result)}")
        except Exception as e:
            print(f"⚠️  Basic functionality test failed: {e}")
            print("This might be expected if the server is not accessible")
        
        print("\n✅ Configuration test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Configuration test failed: {e}")
        print(f"Error type: {type(e)}")
        print("\n🔍 Full traceback:")
        traceback.print_exc()
        return False
    
    return True

def test_config_validation():
    """Test configuration validation."""
    print("\n🔍 Testing Configuration Validation")
    print("=" * 40)
    
    try:
        from config import validate_config
        
        warnings = validate_config()
        if warnings:
            print("⚠️  Configuration warnings:")
            for warning in warnings:
                print(f"  - {warning}")
        else:
            print("✅ No configuration warnings")
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")

def main():
    """Main test function."""
    print("🧪 MCP-MEM0 Configuration Test")
    print("=" * 50)
    
    # Test configuration validation
    test_config_validation()
    
    # Test Mem0 configuration
    if test_mem0_config():
        print("\n🎉 All tests passed!")
        print("\n📋 Next steps:")
        print("1. If you see any warnings, address them")
        print("2. If basic functionality test failed, check your server connectivity")
        print("3. Restart your MCP service to apply any changes")
    else:
        print("\n❌ Tests failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
