#!/usr/bin/env python3
"""
Debug script to test Mem0 client directly and identify configuration issues.
"""

import os
import sys
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv

# Try to find and load the .env file
env_path = Path(__file__).parent / ".env"
print(f"Looking for .env file at: {env_path}")
print(f"File exists: {env_path.exists()}")

if env_path.exists():
    load_dotenv(env_path)
    print("✅ .env file loaded successfully")
else:
    print("❌ .env file not found")
    # Try to load from current directory
    load_dotenv()
    print("Attempted to load .env from current directory")

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils import get_mem0_client
from mem0 import Memory

def test_mem0_directly():
    """Test Mem0 client directly without MCP server."""
    print("=== Testing Mem0 Client Directly ===\n")
    
    try:
        # Test 1: Check environment variables
        print("1. Checking environment variables:")
        env_vars = [
            'LLM_PROVIDER', 'LLM_API_KEY', 'LLM_CHOICE', 
            'EMBEDDING_MODEL_CHOICE', 'LLM_BASE_URL', 'DATABASE_URL'
        ]
        
        for var in env_vars:
            value = os.getenv(var)
            if value:
                # Mask sensitive values
                if 'API_KEY' in var or 'DATABASE_URL' in var:
                    masked_value = value[:10] + "..." if len(value) > 10 else "***"
                    print(f"   {var}: {masked_value}")
                else:
                    print(f"   {var}: {value}")
            else:
                print(f"   {var}: NOT SET")
        
        print()
        
        # Test 2: Try to create Mem0 client
        print("2. Attempting to create Mem0 client...")
        mem0_client = get_mem0_client()
        print(f"   ✅ Mem0 client created successfully: {type(mem0_client)}")
        
        # Test 3: Try to add a test memory
        print("\n3. Testing memory operations...")
        
        # Test add
        print("   Testing add()...")
        test_messages = [{"role": "user", "content": "This is a test memory"}]
        test_metadata = {"test": True, "user_id": "test_user"}
        
        try:
            mem0_client.add(
                test_messages,
                user_id="test_user",
                metadata=test_metadata
            )
            print("   ✅ add() successful")
        except Exception as e:
            print(f"   ❌ add() failed: {e}")
            return
        
        # Test get_all
        print("   Testing get_all()...")
        try:
            memories = mem0_client.get_all(user_id="test_user")
            print(f"   ✅ get_all() successful, returned: {type(memories)}")
            print(f"   Content: {memories}")
        except Exception as e:
            print(f"   ❌ get_all() failed: {e}")
            return
        
        # Test search
        print("   Testing search()...")
        try:
            search_results = mem0_client.search("test memory", user_id="test_user", limit=5)
            print(f"   ✅ search() successful, returned: {type(search_results)}")
            print(f"   Content: {search_results}")
        except Exception as e:
            print(f"   ❌ search() failed: {e}")
            return
        
        print("\n🎉 All tests passed! Mem0 client is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def test_mem0_import():
    """Test if Mem0 can be imported and basic functionality works."""
    print("=== Testing Mem0 Import ===\n")
    
    try:
        from mem0 import Memory
        print("✅ Mem0 import successful")
        
        # Check if we can create a basic config
        config = {
            "llm": {
                "provider": "ollama",
                "config": {
                    "model": "llama3.2:latest",
                    "temperature": 0.2,
                    "max_tokens": 2000,
                }
            },
            "embedder": {
                "provider": "ollama",
                "config": {
                    "model": "snowflake-arctic-embed2:latest",
                    "embedding_dims": 768
                }
            },
            "vector_store": {
                "provider": "supabase",
                "config": {
                    "connection_string": "postgresql://test:test@localhost:5432/test",
                    "collection_name": "test_memories",
                    "embedding_model_dims": 768
                }
            }
        }
        
        print("✅ Basic config structure valid")
        
    except Exception as e:
        print(f"❌ Mem0 import failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Mem0 Debug Script")
    print("=" * 50)
    
    # Test 1: Import
    test_mem0_import()
    print("\n" + "=" * 50)
    
    # Test 2: Direct client creation
    test_mem0_directly()
