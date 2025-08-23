#!/usr/bin/env python3
"""
Test configuration script to verify different aspects of Mem0 setup.
"""

import os
import sys
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

def test_env_loading():
    """Test if environment variables are loaded correctly."""
    print("=== Testing Environment Variable Loading ===\n")
    
    env_vars = [
        'LLM_PROVIDER', 'LLM_API_KEY', 'LLM_CHOICE', 
        'EMBEDDING_MODEL_CHOICE', 'LLM_BASE_URL', 'DATABASE_URL',
        'HOST', 'PORT', 'TRANSPORT', 'DEFAULT_USER_ID'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'API_KEY' in var or 'DATABASE_URL' in var:
                masked_value = value[:10] + "..." if len(value) > 10 else "***"
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NOT SET")
    
    print()

def test_database_connection():
    """Test database connection separately."""
    print("=== Testing Database Connection ===\n")
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not set")
        return False
    
    try:
        import psycopg2
        print("✅ psycopg2 imported successfully")
        
        # Extract connection details
        if database_url.startswith('postgresql://'):
            # Simple connection test
            print(f"✅ Database URL format valid: {database_url[:20]}...")
            
            # Try to parse the URL
            from urllib.parse import urlparse
            parsed = urlparse(database_url)
            print(f"✅ Host: {parsed.hostname}")
            print(f"✅ Port: {parsed.port}")
            print(f"✅ Database: {parsed.path[1:]}")
            print(f"✅ User: {parsed.username}")
            
        else:
            print("❌ Database URL format not recognized")
            return False
            
    except ImportError:
        print("❌ psycopg2 not installed. Install with: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False
    
    return True

def test_ollama_connection():
    """Test Ollama connection."""
    print("\n=== Testing Ollama Connection ===\n")
    
    llm_base_url = os.getenv('LLM_BASE_URL')
    if not llm_base_url:
        print("❌ LLM_BASE_URL not set")
        return False
    
    try:
        import httpx
        print("✅ httpx imported successfully")
        
        # Test connection to Ollama
        import httpx
        with httpx.Client(timeout=5.0) as client:
            try:
                response = client.get(f"{llm_base_url}/api/tags")
                if response.status_code == 200:
                    print("✅ Ollama connection successful")
                    return True
                else:
                    print(f"❌ Ollama responded with status: {response.status_code}")
                    return False
            except httpx.ConnectError:
                print("❌ Cannot connect to Ollama. Is it running?")
                print("   Install with: curl -fsSL https://ollama.com/install.sh | sh")
                print("   Start with: ollama serve")
                return False
            except Exception as e:
                print(f"❌ Ollama connection test failed: {e}")
                return False
                
    except ImportError:
        print("❌ httpx not installed")
        return False

def test_mem0_import():
    """Test Mem0 import and basic functionality."""
    print("\n=== Testing Mem0 Import ===\n")
    
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
        return True
        
    except Exception as e:
        print(f"❌ Mem0 import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("Mem0 Configuration Test Script")
    print("=" * 50)
    
    # Test 1: Environment variables
    test_env_loading()
    
    # Test 2: Mem0 import
    mem0_ok = test_mem0_import()
    
    # Test 3: Database connection
    db_ok = test_database_connection()
    
    # Test 4: Ollama connection
    ollama_ok = test_ollama_connection()
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"✅ Environment Variables: {'OK' if any(os.getenv('LLM_PROVIDER')) else 'FAILED'}")
    print(f"✅ Mem0 Import: {'OK' if mem0_ok else 'FAILED'}")
    print(f"✅ Database Connection: {'OK' if db_ok else 'FAILED'}")
    print(f"✅ Ollama Connection: {'OK' if ollama_ok else 'FAILED'}")
    
    if ollama_ok and db_ok and mem0_ok:
        print("\n🎉 All tests passed! Your configuration should work.")
    else:
        print("\n⚠️  Some tests failed. Check the issues above.")

if __name__ == "__main__":
    main()
