#!/usr/bin/env python3
"""
Test MCP server directly without starting a new instance.
"""

import asyncio
import json
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_direct_mcp():
    """Test MCP server directly."""
    print("🧪 Testing MCP Server Directly")
    print("=" * 50)
    
    # Test userId
    test_user_id = "V2lcGnAnHLPBRXr2d8kz9gf9Gq22"
    print(f"👤 Testing with userId: {test_user_id}")
    print()
    
    try:
        # Import the MCP server
        from main import mcp
        print("✅ MCP server imported successfully")
        
        # Test the tools directly
        print("\n🔧 Available tools:")
        tools = await mcp.list_tools()
        for tool_name in tools:
            print(f"  - {tool_name}")
        
        # Test adding a memory
        print(f"\n📝 Testing save_memory for user {test_user_id}...")
        try:
            add_result = await mcp.call_tool(
                "save_memory",
                {
                    "userId": test_user_id,
                    "content": "I love working with AI and machine learning technologies. My favorite programming language is Python."
                }
            )
            print(f"✅ Save memory result: {add_result}")
        except Exception as e:
            print(f"❌ Save memory failed: {e}")
        
        # Test getting all memories
        print(f"\n📖 Testing get_all_memories for user {test_user_id}...")
        try:
            get_all_result = await mcp.call_tool(
                "get_all_memories",
                {"userId": test_user_id}
            )
            print(f"✅ Get all memories result: {get_all_result}")
        except Exception as e:
            print(f"❌ Get all memories failed: {e}")
        
        # Test searching memories
        print(f"\n🔍 Testing search_memories for user {test_user_id}...")
        try:
            search_result = await mcp.call_tool(
                "search_memories",
                {
                    "userId": test_user_id,
                    "query": "programming language",
                    "limit": 5
                }
            )
            print(f"✅ Search memories result: {search_result}")
        except Exception as e:
            print(f"❌ Search memories failed: {e}")
        
        # Test health check
        print("\n🏥 Testing health_check...")
        try:
            health_result = await mcp.call_tool("health_check", {})
            print(f"✅ Health check result: {health_result}")
        except Exception as e:
            print(f"❌ Health check failed: {e}")
        
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    asyncio.run(test_direct_mcp())
