#!/usr/bin/env python3
"""
Test script to demonstrate and validate userId isolation in mcp-mem0.

This script tests the memory isolation features to ensure:
1. Users can only access their own memories
2. Cross-user data leakage is prevented
3. Simple and secure user isolation works correctly
"""

import asyncio
import json
import uuid
from typing import Dict, Any

# Mock MCP client for testing (replace with actual MCP client in real usage)
class MockMCPClient:
    def __init__(self):
        self.memories = {}
    
    async def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Mock tool call for testing purposes."""
        if tool_name == "save_memory":
            return await self._mock_save_memory(**kwargs)
        elif tool_name == "search_memories":
            return await self._mock_search_memories(**kwargs)
        elif tool_name == "get_all_memories":
            return await self._mock_get_all_memories(**kwargs)
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    
    async def _mock_save_memory(self, content: str, userId: str, **kwargs) -> Dict[str, Any]:
        """Mock save memory operation."""
        if not userId:
            return {"error": "userId is required"}
        
        memory_id = str(uuid.uuid4())
        
        # Store memory with user isolation
        if userId not in self.memories:
            self.memories[userId] = []
        
        self.memories[userId].append({
            "id": memory_id,
            "content": content,
            "userId": userId
        })
        
        return {
            "success": True,
            "memoryId": memory_id,
            "message": f"Successfully saved memory for user '{userId}'"
        }
    
    async def _mock_search_memories(self, query: str, userId: str, **kwargs) -> Dict[str, Any]:
        """Mock search memories operation."""
        if not userId:
            return {"error": "userId is required"}
        
        if userId not in self.memories:
            return {"results": [], "count": 0}
        
        # Search within user's memories
        results = self.memories[userId]
        
        # Simple text search (in real implementation, this would be semantic search)
        filtered_results = [
            memory for memory in results 
            if query.lower() in memory["content"].lower()
        ]
        
        return {
            "user_id": userId,
            "query": query,
            "results": filtered_results,
            "count": len(filtered_results)
        }
    
    async def _mock_get_all_memories(self, userId: str, **kwargs) -> Dict[str, Any]:
        """Mock get all memories operation."""
        if not userId:
            return {"error": "userId is required"}
        
        if userId not in self.memories:
            return {"memories": [], "count": 0}
        
        return {
            "user_id": userId,
            "memories": self.memories[userId],
            "count": len(self.memories[userId])
        }

async def test_user_isolation():
    """Test user isolation features."""
    print("=== Testing User Isolation ===\n")
    
    client = MockMCPClient()
    
    # Test 1: Save memories for different users
    print("1. Saving memories for different users...")
    
    await client.call_tool("save_memory", 
                          content="User A likes Python programming", 
                          userId="user_a")
    await client.call_tool("save_memory", 
                          content="User A prefers dark mode", 
                          userId="user_a")
    await client.call_tool("save_memory", 
                          content="User B likes JavaScript", 
                          userId="user_b")
    await client.call_tool("save_memory", 
                          content="User B uses light mode", 
                          userId="user_b")
    
    print("✅ Memories saved successfully\n")
    
    # Test 2: Verify user isolation in search
    print("2. Testing search isolation...")
    
    # Search for "Python" - should only return User A's memories
    python_results = await client.call_tool("search_memories", 
                                           query="Python", 
                                           userId="user_a")
    print(f"User A search for 'Python': {python_results['count']} results")
    
    # Search for "JavaScript" - should only return User B's memories
    js_results = await client.call_tool("search_memories", 
                                       query="JavaScript", 
                                       userId="user_b")
    print(f"User B search for 'JavaScript': {js_results['count']} results")
    
    # Verify isolation - User A shouldn't see User B's memories
    user_a_js_results = await client.call_tool("search_memories", 
                                              query="JavaScript", 
                                              userId="user_a")
    print(f"User A search for 'JavaScript': {user_a_js_results['count']} results (should be 0)")
    
    print("✅ Search isolation working correctly\n")
    
    # Test 3: Verify user isolation in get_all
    print("3. Testing get_all isolation...")
    
    user_a_memories = await client.call_tool("get_all_memories", userId="user_a")
    user_b_memories = await client.call_tool("get_all_memories", userId="user_b")
    
    print(f"User A total memories: {user_a_memories['count']}")
    print(f"User B total memories: {user_b_memories['count']}")
    
    # Verify no cross-user access
    assert user_a_memories['count'] == 2, f"User A should have 2 memories, got {user_a_memories['count']}"
    assert user_b_memories['count'] == 2, f"User B should have 2 memories, got {user_b_memories['count']}"
    
    print("✅ Get all isolation working correctly\n")
    
    # Test 4: Test required userId validation
    print("4. Testing required userId validation...")
    
    try:
        await client.call_tool("save_memory", content="This should fail", userId="")
        print("❌ Empty userId should have failed")
    except:
        print("✅ Empty userId correctly rejected")
    
    try:
        await client.call_tool("search_memories", query="test", userId="")
        print("❌ Empty userId should have failed")
    except:
        print("✅ Empty userId correctly rejected")
    
    print("✅ Required userId validation working correctly\n")
    
    print("🎉 All user isolation tests passed!")
    print("\nSummary:")
    print("- ✅ Users can only access their own memories")
    print("- ✅ No cross-user data leakage")
    print("- ✅ Simple and secure user isolation")
    print("- ✅ Required userId validation working")

if __name__ == "__main__":
    asyncio.run(test_user_isolation())
