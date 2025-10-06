#!/usr/bin/env python3
"""
Test MCP server with specific userId.
"""

import asyncio
import json
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_mcp_server():
    """Test MCP server with specific userId."""
    print("🧪 Testing MCP Server with UserId")
    print("=" * 50)
    
    # Test userId
    test_user_id = "V2lcGnAnHLPBRXr2d8kz9gf9Gq22"
    print(f"👤 Testing with userId: {test_user_id}")
    print()
    
    try:
        # Import the MCP server
        from main import mcp
        print("✅ MCP server imported successfully")
        
        # Test adding a memory
        print("\n📝 Testing save_memory...")
        add_result = await mcp.call_tool(
            "save_memory",
            {
                "userId": test_user_id,
                "content": "I love working with AI and machine learning technologies. My favorite programming language is Python.",
                "metadata": {"category": "personal", "timestamp": "2024-10-01"}
            }
        )
        print(f"Add memory result: {add_result}")
        
        # Test getting all memories
        print("\n📖 Testing get_all_memories...")
        get_all_result = await mcp.call_tool(
            "get_all_memories",
            {"userId": test_user_id}
        )
        print(f"Get all memories result: {get_all_result}")
        
        # Test searching memories
        print("\n🔍 Testing search_memories...")
        search_result = await mcp.call_tool(
            "search_memories",
            {
                "userId": test_user_id,
                "query": "programming language",
                "limit": 5
            }
        )
        print(f"Search memories result: {search_result}")
        
        # Test health check
        print("\n🏥 Testing health_check...")
        health_result = await mcp.call_tool("health_check", {})
        print(f"Health check result: {health_result}")
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    asyncio.run(test_mcp_server())
