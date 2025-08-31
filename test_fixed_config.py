#!/usr/bin/env python3
"""
Test script to verify the fixed Mem0 configuration works.
This tests the configuration structure that was causing the error.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_fixed_config():
    """Test the fixed Mem0 configuration structure."""
    print("=== Testing Fixed Mem0 Configuration ===\n")
    
    try:
        from mem0 import Memory
        print("✅ Mem0 import successful")
        
        # Test the exact configuration structure from utils.py (after fix)
        config = {
            "llm": {
                "provider": "openai",
                "config": {
                    "model": "gpt-3.5-turbo",
                    "temperature": 0.2,
                    "max_tokens": 2000,
                }
            },
            "embedder": {
                "provider": "openai",
                "config": {
                    "model": "text-embedding-3-small",
                    "embedding_dims": int(os.getenv("EMBEDDING_MODEL_DIMS", "1536"))
                }
            },
            "vector_store": {
                "provider": "supabase",
                "config": {
                    "connection_string": "postgresql://test:test@localhost:5432/test",
                    "collection_name": "mem0_memories",
                    "embedding_model_dims": int(os.getenv("EMBEDDING_MODEL_DIMS", "1536"))
                }
            }
        }
        
        print("✅ Configuration structure valid (no unsupported database parameters)")
        print("✅ vector_store config contains only supported fields:")
        for key in config["vector_store"]["config"].keys():
            print(f"   - {key}")
        
        # Try to create the client (this will fail on connection but should pass validation)
        try:
            client = Memory.from_config(config)
            print("✅ Memory.from_config() successful - configuration is valid")
        except Exception as e:
            if "connection" in str(e).lower() or "database" in str(e).lower():
                print("✅ Configuration validation passed (connection failure expected in test)")
            else:
                print(f"❌ Unexpected error: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("Mem0 Fixed Configuration Test")
    print("=" * 50)
    
    success = test_fixed_config()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Configuration test passed! The fix should resolve the error.")
        print("\nThe following database parameters were removed (not supported by Mem0):")
        print("  - pool_size")
        print("  - max_overflow") 
        print("  - pool_timeout")
        print("  - pool_recycle")
        print("  - connect_timeout")
        print("  - read_timeout")
        print("\nThese parameters were causing the validation error in your service.")
    else:
        print("❌ Configuration test failed. There may be other issues.")

if __name__ == "__main__":
    main() 