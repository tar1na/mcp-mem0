#!/usr/bin/env python3
"""
Script to fix the embedding configuration for Ollama setup.
This ensures the system uses Ollama for both LLM and embeddings.
"""

import os
import sys

def fix_embedding_config():
    """Add EMBEDDING_PROVIDER=ollama to .env file if missing."""
    
    env_file = '.env'
    
    if not os.path.exists(env_file):
        print(f"ERROR: {env_file} file not found!")
        return False
    
    # Read current .env file
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Check if EMBEDDING_PROVIDER is already set
    embedding_provider_set = False
    for line in lines:
        if line.strip().startswith('EMBEDDING_PROVIDER='):
            embedding_provider_set = True
            break
    
    if embedding_provider_set:
        print("EMBEDDING_PROVIDER is already configured in .env file")
        return True
    
    # Find where to insert the EMBEDDING_PROVIDER setting
    insert_index = -1
    for i, line in enumerate(lines):
        if line.strip().startswith('LLM_PROVIDER='):
            insert_index = i + 1
            break
    
    if insert_index == -1:
        print("ERROR: Could not find LLM_PROVIDER in .env file")
        return False
    
    # Insert EMBEDDING_PROVIDER setting
    lines.insert(insert_index, '\n# The provider for your embedding model\n')
    lines.insert(insert_index + 1, '# Set this to either openai, openrouter, or ollama\n')
    lines.insert(insert_index + 2, '# If not set, will use the same provider as LLM_PROVIDER\n')
    lines.insert(insert_index + 3, 'EMBEDDING_PROVIDER=ollama\n')
    
    # Write updated .env file
    with open(env_file, 'w') as f:
        f.writelines(lines)
    
    print("✅ Added EMBEDDING_PROVIDER=ollama to .env file")
    print("✅ This should fix the OpenAI API key error")
    print("\nYour .env file now includes:")
    print("  LLM_PROVIDER=ollama")
    print("  EMBEDDING_PROVIDER=ollama")
    print("  LLM_BASE_URL=http://192.168.1.175:11434")
    print("  EMBEDDING_MODEL_CHOICE=snowflake-arctic-embed2:latest")
    
    return True

def verify_config():
    """Verify the current configuration."""
    print("\n🔍 Verifying current configuration...")
    
    # Check environment variables
    llm_provider = os.getenv('LLM_PROVIDER')
    embedding_provider = os.getenv('EMBEDDING_PROVIDER')
    llm_base_url = os.getenv('LLM_BASE_URL')
    embedding_model = os.getenv('EMBEDDING_MODEL_CHOICE')
    
    print(f"  LLM_PROVIDER: {llm_provider}")
    print(f"  EMBEDDING_PROVIDER: {embedding_provider}")
    print(f"  LLM_BASE_URL: {llm_base_url}")
    print(f"  EMBEDDING_MODEL_CHOICE: {embedding_model}")
    
    # Check for conflicting OpenAI settings
    openai_key = os.getenv('OPENAI_API_KEY')
    openai_base = os.getenv('OPENAI_BASE_URL')
    
    if openai_key:
        print(f"  ⚠️  OPENAI_API_KEY: SET (this might cause conflicts)")
    else:
        print(f"  ✅ OPENAI_API_KEY: NOT SET")
    
    if openai_base:
        print(f"  ⚠️  OPENAI_BASE_URL: {openai_base} (this might cause conflicts)")
    else:
        print(f"  ✅ OPENAI_BASE_URL: NOT SET")
    
    # Recommendations
    print("\n📋 Recommendations:")
    if not embedding_provider:
        print("  ❌ Add EMBEDDING_PROVIDER=ollama to your .env file")
    else:
        print("  ✅ EMBEDDING_PROVIDER is configured")
    
    if llm_provider == 'ollama' and embedding_provider == 'ollama':
        print("  ✅ Configuration looks correct for Ollama")
    else:
        print("  ⚠️  Make sure both LLM and embedding providers are set to 'ollama'")

if __name__ == '__main__':
    print("🔧 MCP-MEM0 Embedding Configuration Fix")
    print("=" * 50)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Verify current config
    verify_config()
    
    # Fix configuration
    print("\n🔧 Fixing configuration...")
    if fix_embedding_config():
        print("\n✅ Configuration fixed successfully!")
        print("\n🔄 Please restart your MCP service for changes to take effect.")
    else:
        print("\n❌ Failed to fix configuration. Please check manually.")
        sys.exit(1)
