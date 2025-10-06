#!/usr/bin/env python3
"""
Test Mem0 client directly with the specified userId.
"""

import os
import sys
import asyncio

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

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

async def test_mem0_direct():
    """Test Mem0 client directly."""
    print("🧪 Testing Mem0 Client Directly")
    print("=" * 50)
    
    # Test userId
    test_user_id = "V2lcGnAnHLPBRXr2d8kz9gf9Gq22"
    print(f"👤 Testing with userId: {test_user_id}")
    print()
    
    if not load_env_manually():
        return False
    
    try:
        # Import and create Mem0 client
        from utils import get_mem0_client
        print("✅ Mem0 client imported successfully")
        
        # Create the client
        print("🔧 Creating Mem0 client...")
        mem0_client = get_mem0_client()
        print("✅ Mem0 client created successfully")
        
        # Test adding a memory
        print(f"\n📝 Testing add memory for user {test_user_id}...")
        try:
            add_result = mem0_client.add(
                user_id=test_user_id,
                messages="I love working with AI and machine learning technologies. My favorite programming language is Python.",
                metadata={"category": "personal", "timestamp": "2024-10-01"}
            )
            print(f"✅ Add memory result: {add_result}")
        except Exception as e:
            print(f"❌ Add memory failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test getting all memories
        print(f"\n📖 Testing get all memories for user {test_user_id}...")
        try:
            get_all_result = mem0_client.get_all(user_id=test_user_id)
            print(f"✅ Get all memories result: {get_all_result}")
        except Exception as e:
            print(f"❌ Get all memories failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test searching memories
        print(f"\n🔍 Testing search memories for user {test_user_id}...")
        try:
            search_result = mem0_client.search(
                query="programming language",
                user_id=test_user_id,
                limit=5
            )
            print(f"✅ Search memories result: {search_result}")
        except Exception as e:
            print(f"❌ Search memories failed: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    asyncio.run(test_mem0_direct())
