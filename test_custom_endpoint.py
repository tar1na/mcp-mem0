#!/usr/bin/env python3
"""
Test script to verify your custom OpenAI endpoint is working correctly.
"""

import requests
import json
import os
import sys

def test_custom_endpoint():
    """Test the custom OpenAI endpoint."""
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    base_url = os.getenv('LLM_BASE_URL', 'http://db-server.local:8009/v1')
    api_key = os.getenv('LLM_API_KEY', 'xxx')
    embedding_base_url = os.getenv('EMBEDDING_BASE_URL')
    embedding_api_key = os.getenv('EMBEDDING_API_KEY')
    
    print(f"🧪 Testing Custom OpenAI Endpoints")
    print("=" * 50)
    print(f"LLM Base URL: {base_url}")
    print(f"LLM API Key: {'SET' if api_key and api_key != 'xxx' else 'NOT SET'}")
    if embedding_base_url:
        print(f"Embedding Base URL: {embedding_base_url}")
        print(f"Embedding API Key: {'SET' if embedding_api_key else 'NOT SET'}")
    else:
        print("Embedding Base URL: Using LLM_BASE_URL")
        print("Embedding API Key: Using LLM_API_KEY")
    print()
    
    # Test 1: Chat Completions
    print("1️⃣ Testing Chat Completions...")
    try:
        chat_url = f"{base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hello, this is a test."}],
            "max_tokens": 10
        }
        
        response = requests.post(chat_url, headers=headers, json=data, timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Chat completions working!")
            if 'choices' in result and len(result['choices']) > 0:
                print(f"   Response: {result['choices'][0]['message']['content']}")
        else:
            print(f"   ❌ Chat completions failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Chat completions error: {e}")
    
    print()
    
    # Test 2: Embeddings
    print("2️⃣ Testing Embeddings...")
    try:
        # Use embedding URL and API key if available, otherwise use LLM settings
        embed_url = f"{embedding_base_url or base_url}/embeddings"
        embed_api_key = embedding_api_key or api_key
        headers = {
            "Authorization": f"Bearer {embed_api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "text-embedding-3-small",
            "input": "This is a test embedding."
        }
        
        response = requests.post(embed_url, headers=headers, json=data, timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Embeddings working!")
            if 'data' in result and len(result['data']) > 0:
                embedding = result['data'][0]['embedding']
                print(f"   Embedding dimensions: {len(embedding)}")
        else:
            print(f"   ❌ Embeddings failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Embeddings error: {e}")
    
    print()
    
    # Test 3: Check if it's hitting the right endpoints
    print("3️⃣ Verifying Endpoints...")
    if 'api.openai.com' in base_url:
        print("   ⚠️  WARNING: LLM is using the default OpenAI endpoint!")
        print("   This means your custom LLM endpoint configuration isn't working.")
    else:
        print(f"   ✅ LLM using custom endpoint: {base_url}")
    
    if embedding_base_url:
        if 'api.openai.com' in embedding_base_url:
            print("   ⚠️  WARNING: Embeddings are using the default OpenAI endpoint!")
        else:
            print(f"   ✅ Embeddings using custom endpoint: {embedding_base_url}")
    else:
        print(f"   ℹ️  Embeddings using LLM endpoint: {base_url}")
    
    print()
    print("📋 Summary:")
    print("If both tests pass, your custom endpoint is working correctly.")
    print("If they fail, check:")
    print("1. Your custom server is running")
    print("2. The API key is correct")
    print("3. The server supports OpenAI API format")
    print("4. Network connectivity is working")

if __name__ == '__main__':
    test_custom_endpoint()
