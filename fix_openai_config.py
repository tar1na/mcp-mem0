#!/usr/bin/env python3
"""
Script to fix OpenAI configuration for custom endpoints.
This ensures the system uses your custom OpenAI endpoint instead of api.openai.com.
"""

import os
import sys

def fix_openai_config():
    """Fix OpenAI configuration for custom endpoints."""
    
    env_file = '.env'
    
    if not os.path.exists(env_file):
        print(f"ERROR: {env_file} file not found!")
        return False
    
    # Read current .env file
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Check current configuration
    print("🔍 Current Configuration:")
    print("=" * 40)
    
    lines = content.split('\n')
    for line in lines:
        if any(key in line for key in ['LLM_PROVIDER', 'EMBEDDING_PROVIDER', 'LLM_BASE_URL', 'LLM_API_KEY']):
            if 'API_KEY' in line and '=' in line:
                key, value = line.split('=', 1)
                print(f"  {key}={value[:8]}..." if len(value) > 8 else f"  {key}={value}")
            else:
                print(f"  {line}")
    
    print()
    
    # Check if configuration is correct
    llm_provider = None
    llm_base_url = None
    llm_api_key = None
    embedding_provider = None
    
    for line in lines:
        if line.startswith('LLM_PROVIDER='):
            llm_provider = line.split('=', 1)[1].strip()
        elif line.startswith('LLM_BASE_URL='):
            llm_base_url = line.split('=', 1)[1].strip().strip("'\"")
        elif line.startswith('LLM_API_KEY='):
            llm_api_key = line.split('=', 1)[1].strip()
        elif line.startswith('EMBEDDING_PROVIDER='):
            embedding_provider = line.split('=', 1)[1].strip()
    
    print("🔧 Configuration Analysis:")
    print("=" * 40)
    
    issues = []
    
    if llm_provider != 'openai':
        issues.append(f"❌ LLM_PROVIDER should be 'openai', currently: {llm_provider}")
    else:
        print("✅ LLM_PROVIDER is set to 'openai'")
    
    if not llm_base_url or 'api.openai.com' in llm_base_url:
        issues.append(f"❌ LLM_BASE_URL should be your custom endpoint, currently: {llm_base_url}")
    else:
        print(f"✅ LLM_BASE_URL is set to custom endpoint: {llm_base_url}")
    
    if not llm_api_key or llm_api_key == 'xxx':
        issues.append("❌ LLM_API_KEY should be set to your actual API key")
    else:
        print("✅ LLM_API_KEY is set")
    
    if embedding_provider != 'openai':
        issues.append(f"❌ EMBEDDING_PROVIDER should be 'openai', currently: {embedding_provider}")
    else:
        print("✅ EMBEDDING_PROVIDER is set to 'openai'")
    
    if issues:
        print("\n🚨 Issues Found:")
        for issue in issues:
            print(f"  {issue}")
        
        print("\n🔧 Recommended Fixes:")
        print("1. Set LLM_PROVIDER=openai")
        print("2. Set LLM_BASE_URL=http://db-server.local:8009/v1")
        print("3. Set LLM_API_KEY=your_actual_api_key")
        print("4. Set EMBEDDING_PROVIDER=openai")
        print("5. Restart your MCP service")
        
        return False
    else:
        print("\n✅ Configuration looks correct!")
        print("If you're still getting OpenAI API errors, the issue might be:")
        print("1. The service hasn't been restarted after configuration changes")
        print("2. Environment variables aren't being loaded properly")
        print("3. Mem0 library is using cached configuration")
        print("4. Your custom endpoint doesn't support the required API format")
        
        return True

def test_configuration():
    """Test the current configuration."""
    print("\n🧪 Testing Configuration:")
    print("=" * 40)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check environment variables
    llm_provider = os.getenv('LLM_PROVIDER')
    llm_base_url = os.getenv('LLM_BASE_URL')
    llm_api_key = os.getenv('LLM_API_KEY')
    embedding_provider = os.getenv('EMBEDDING_PROVIDER')
    
    print(f"LLM_PROVIDER: {llm_provider}")
    print(f"LLM_BASE_URL: {llm_base_url}")
    print(f"LLM_API_KEY: {'SET' if llm_api_key else 'NOT SET'}")
    print(f"EMBEDDING_PROVIDER: {embedding_provider}")
    
    # Check for conflicting variables
    openai_base_url = os.getenv('OPENAI_BASE_URL')
    if openai_base_url:
        print(f"OPENAI_BASE_URL: {openai_base_url}")
    else:
        print("OPENAI_BASE_URL: NOT SET (will use default)")

def main():
    """Main function."""
    print("🔧 MCP-MEM0 OpenAI Configuration Fix")
    print("=" * 50)
    
    # Test current configuration
    test_configuration()
    
    # Fix configuration
    if not fix_openai_config():
        print("\n❌ Configuration needs to be fixed manually.")
        print("\n📋 Steps to fix:")
        print("1. Edit your .env file")
        print("2. Set the correct values as shown above")
        print("3. Restart your MCP service")
        print("4. Check the debug logs for configuration details")
        sys.exit(1)
    else:
        print("\n✅ Configuration appears correct!")
        print("If you're still having issues, try:")
        print("1. Restart the MCP service")
        print("2. Check the service logs for debug information")
        print("3. Verify your custom endpoint is working")

if __name__ == '__main__':
    main()
