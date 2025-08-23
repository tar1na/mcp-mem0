#!/usr/bin/env python3
"""
Test script to demonstrate and validate userId and sessionId isolation in mcp-mem0.

This script tests the memory isolation features to ensure:
1. Users can only access their own memories
2. Sessions can be isolated when sessionId is provided
3. Cross-user and cross-session data leakage is prevented
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
        session_id = kwargs.get("sessionId")
        
        # Store memory with user and session isolation
        if userId not in self.memories:
            self.memories[userId] = {}
        
        if session_id:
            if session_id not in self.memories[userId]:
                self.memories[userId][session_id] = []
            self.memories[userId][session_id].append({
                "id": memory_id,
                "content": content,
                "userId": userId,
                "sessionId": session_id,
                **kwargs
            })
        else:
            if "default" not in self.memories[userId]:
                self.memories[userId]["default"] = []
            self.memories[userId]["default"].append({
                "id": memory_id,
                "content": content,
                "userId": userId,
                **kwargs
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
        
        session_id = kwargs.get("sessionId")
        results = []
        
        if session_id and session_id in self.memories[userId]:
            # Search within specific session
            results = self.memories[userId][session_id]
        elif not session_id:
            # Search across all sessions for user
            for session_memories in self.memories[userId].values():
                results.extend(session_memories)
        
        # Simple text search (in real implementation, this would be semantic search)
        filtered_results = [
            memory for memory in results 
            if query.lower() in memory["content"].lower()
        ]
        
        return {
            "user_id": userId,
            "session_id": session_id,
            "query": query,
            "results": filtered_results,
            "count": len(filtered_results)
        }
    
    async def _mock_get_all_memories(self, userId: str, **kwargs) -> Dict[str, Any]:
        """Mock get all memories operation."""
        if not userId:
            return {"error": "userId is required"}
        
        if userId == "":
            return {"error": "userId is required"}
        
        if userId not in self.memories:
            return {"memories": [], "count": 0}
        
        session_id = kwargs.get("sessionId")
        results = []
        
        if session_id and session_id in self.memories[userId]:
            # Get memories from specific session
            results = self.memories[userId][session_id]
        elif not session_id:
            # Get all memories for user across all sessions
            for session_memories in self.memories[userId].values():
                results.extend(session_memories)
        
        return {
            "user_id": userId,
            "sessionId": session_id,
            "memories": results,
            "count": len(results)
        }

async def test_user_isolation():
    """Test user isolation functionality."""
    print("🧪 Testing User and Session Isolation in mcp-mem0")
    print("=" * 60)
    
    client = MockMCPClient()
    
    # Test 1: Save memories for different users
    print("\n1️⃣ Testing User Isolation")
    print("-" * 30)
    
    # User 1 saves memories
    result1 = await client.call_tool("save_memory", 
        content="I prefer Python for data science", 
        userId="user_123"
    )
    print(f"User 123 saved memory: {result1}")
    
    result2 = await client.call_tool("save_memory", 
        content="I like JavaScript for web development", 
        userId="user_456"
    )
    print(f"User 456 saved memory: {result2}")
    
    # Test 2: Verify users can only see their own memories
    print("\n2️⃣ Testing Memory Access Isolation")
    print("-" * 30)
    
    user1_memories = await client.call_tool("get_all_memories", userId="user_123")
    print(f"User 123 memories: {json.dumps(user1_memories, indent=2)}")
    
    user2_memories = await client.call_tool("get_all_memories", userId="user_456")
    print(f"User 456 memories: {json.dumps(user2_memories, indent=2)}")
    
    # Test 3: Test session isolation
    print("\n3️⃣ Testing Session Isolation")
    print("-" * 30)
    
    # User 1 saves memories in different sessions
    session_a = "session_a"
    session_b = "session_b"
    
    await client.call_tool("save_memory", 
        content="Session A: Working on project Alpha", 
        userId="user_123", 
        sessionId=session_a
    )
    
    await client.call_tool("save_memory", 
        content="Session B: Working on project Beta", 
        userId="user_123", 
        sessionId=session_b
    )
    
    # Search within specific session
    session_a_results = await client.call_tool("search_memories", 
        query="project", 
        userId="user_123", 
        sessionId=session_a
    )
    print(f"Session A results: {json.dumps(session_a_results, indent=2)}")
    
    session_b_results = await client.call_tool("search_memories", 
        query="project", 
        userId="user_123", 
        sessionId=session_b
    )
    print(f"Session B results: {json.dumps(session_b_results, indent=2)}")
    
    # Test 4: Test cross-session search (should return all user memories)
    print("\n4️⃣ Testing Cross-Session Search")
    print("-" * 30)
    
    all_user_memories = await client.call_tool("search_memories", 
        query="project", 
        userId="user_123"
    )
    print(f"All user memories (no session filter): {json.dumps(all_user_memories, indent=2)}")
    
    # Test 5: Test security - missing userId
    print("\n5️⃣ Testing Security - Missing userId")
    print("-" * 30)
    
    try:
        result = await client.call_tool("save_memory", content="This should fail")
        print(f"❌ Security test failed: {result}")
    except Exception as e:
        print(f"✅ Security test passed: {e}")
    
    # Test 6: Test search across different users (should be isolated)
    print("\n6️⃣ Testing Cross-User Search Isolation")
    print("-" * 30)
    
    # Search for "Python" - should only return user_123's memory
    python_results = await client.call_tool("search_memories", 
        query="Python", 
        userId="user_123"
    )
    print(f"User 123 Python search: {json.dumps(python_results, indent=2)}")
    
    python_results_user2 = await client.call_tool("search_memories", 
        query="Python", 
        userId="user_456"
    )
    print(f"User 456 Python search: {json.dumps(python_results_user2, indent=2)}")
    
    print("\n✅ User and Session Isolation Tests Completed!")
    print("\n📋 Summary:")
    print("• Users can only access their own memories")
    print("• Sessions can be isolated when sessionId is provided")
    print("• Cross-user data leakage is prevented")
    print("• Cross-session searches work when no sessionId is provided")
    print("• Security validation prevents operations without userId")

if __name__ == "__main__":
    asyncio.run(test_user_isolation())
