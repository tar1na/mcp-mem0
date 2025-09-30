#!/usr/bin/env python3
"""
Setup script for configuring separate API keys for LLM and embedding operations.
This helps users set up different authentication for different services.
"""

import os
import sys

def setup_separate_keys():
    """Interactive setup for separate API keys."""
    
    print("🔧 MCP-MEM0 Separate API Keys Setup")
    print("=" * 50)
    print()
    print("This script helps you configure separate API keys for LLM and embedding operations.")
    print("This is useful when you have different servers or authentication for different services.")
    print()
    
    # Check if .env file exists
    env_file = '.env'
    if not os.path.exists(env_file):
        print(f"❌ {env_file} file not found!")
        print("Please create a .env file first with your basic configuration.")
        return False
    
    # Read current configuration
    with open(env_file, 'r') as f:
        content = f.read()
    
    print("📋 Current Configuration:")
    print("-" * 30)
    
    lines = content.split('\n')
    current_config = {}
    for line in lines:
        if '=' in line and not line.strip().startswith('#'):
            key, value = line.split('=', 1)
            current_config[key.strip()] = value.strip().strip("'\"")
    
    # Display current settings
    for key in ['LLM_PROVIDER', 'LLM_BASE_URL', 'LLM_API_KEY', 'EMBEDDING_PROVIDER', 'EMBEDDING_BASE_URL', 'EMBEDDING_API_KEY']:
        value = current_config.get(key, 'NOT SET')
        if 'API_KEY' in key and value != 'NOT SET':
            value = value[:8] + '...' if len(value) > 8 else value
        print(f"  {key}: {value}")
    
    print()
    
    # Ask user what they want to configure
    print("🎯 What would you like to configure?")
    print("1. Add separate embedding base URL")
    print("2. Add separate embedding API key")
    print("3. Both base URL and API key")
    print("4. View example configurations")
    print("5. Exit")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == '1':
        setup_embedding_url(current_config)
    elif choice == '2':
        setup_embedding_api_key(current_config)
    elif choice == '3':
        setup_embedding_url(current_config)
        setup_embedding_api_key(current_config)
    elif choice == '4':
        show_examples()
    elif choice == '5':
        print("Goodbye!")
        return True
    else:
        print("Invalid choice. Please try again.")
        return False
    
    return True

def setup_embedding_url(current_config):
    """Setup separate embedding base URL."""
    print("\n🌐 Setting up Embedding Base URL")
    print("-" * 35)
    
    current_url = current_config.get('EMBEDDING_BASE_URL', 'NOT SET')
    llm_url = current_config.get('LLM_BASE_URL', 'NOT SET')
    
    print(f"Current LLM Base URL: {llm_url}")
    print(f"Current Embedding Base URL: {current_url}")
    print()
    
    if current_url != 'NOT SET':
        print("You already have an embedding base URL configured.")
        change = input("Do you want to change it? (y/n): ").strip().lower()
        if change != 'y':
            return
    
    print("Enter the embedding base URL (or press Enter to use LLM_BASE_URL):")
    print("Examples:")
    print("  - http://embedding-server.local:8009/v1")
    print("  - https://embedding-api.example.com/v1")
    print("  - http://localhost:8009/v1")
    
    new_url = input("\nEmbedding Base URL: ").strip()
    
    if new_url:
        update_env_file('EMBEDDING_BASE_URL', new_url)
        print(f"✅ Set EMBEDDING_BASE_URL to: {new_url}")
    else:
        print("ℹ️  Will use LLM_BASE_URL for embeddings")

def setup_embedding_api_key(current_config):
    """Setup separate embedding API key."""
    print("\n🔑 Setting up Embedding API Key")
    print("-" * 35)
    
    current_key = current_config.get('EMBEDDING_API_KEY', 'NOT SET')
    llm_key = current_config.get('LLM_API_KEY', 'NOT SET')
    
    print(f"Current LLM API Key: {llm_key[:8] + '...' if llm_key != 'NOT SET' else 'NOT SET'}")
    print(f"Current Embedding API Key: {current_key[:8] + '...' if current_key != 'NOT SET' else 'NOT SET'}")
    print()
    
    if current_key != 'NOT SET':
        print("You already have an embedding API key configured.")
        change = input("Do you want to change it? (y/n): ").strip().lower()
        if change != 'y':
            return
    
    print("Enter the embedding API key (or press Enter to use LLM_API_KEY):")
    print("Examples:")
    print("  - sk-embedding-your-embedding-key-here")
    print("  - sk-llm-your-llm-key-here")
    print("  - your-custom-api-key")
    
    new_key = input("\nEmbedding API Key: ").strip()
    
    if new_key:
        update_env_file('EMBEDDING_API_KEY', new_key)
        print(f"✅ Set EMBEDDING_API_KEY to: {new_key[:8]}...")
    else:
        print("ℹ️  Will use LLM_API_KEY for embeddings")

def update_env_file(key, value):
    """Update a key-value pair in the .env file."""
    env_file = '.env'
    
    # Read current file
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Check if key already exists
    key_found = False
    for i, line in enumerate(lines):
        if line.strip().startswith(f'{key}='):
            lines[i] = f'{key}={value}\n'
            key_found = True
            break
    
    # If key not found, add it
    if not key_found:
        lines.append(f'{key}={value}\n')
    
    # Write back to file
    with open(env_file, 'w') as f:
        f.writelines(lines)

def show_examples():
    """Show example configurations."""
    print("\n📚 Example Configurations")
    print("=" * 30)
    
    print("\n1️⃣ Same Server, Same API Key:")
    print("   LLM_BASE_URL=http://server.local:8009/v1")
    print("   LLM_API_KEY=sk-your-key")
    print("   # EMBEDDING_BASE_URL not set (uses LLM_BASE_URL)")
    print("   # EMBEDDING_API_KEY not set (uses LLM_API_KEY)")
    
    print("\n2️⃣ Different Servers, Same API Key:")
    print("   LLM_BASE_URL=http://llm-server.local:8009/v1")
    print("   LLM_API_KEY=sk-your-key")
    print("   EMBEDDING_BASE_URL=http://embedding-server.local:8009/v1")
    print("   # EMBEDDING_API_KEY not set (uses LLM_API_KEY)")
    
    print("\n3️⃣ Different Servers, Different API Keys:")
    print("   LLM_BASE_URL=http://llm-server.local:8009/v1")
    print("   LLM_API_KEY=sk-llm-your-llm-key")
    print("   EMBEDDING_BASE_URL=http://embedding-server.local:8009/v1")
    print("   EMBEDDING_API_KEY=sk-embedding-your-embedding-key")
    
    print("\n4️⃣ Same Server, Different API Keys:")
    print("   LLM_BASE_URL=http://server.local:8009/v1")
    print("   LLM_API_KEY=sk-llm-your-llm-key")
    print("   # EMBEDDING_BASE_URL not set (uses LLM_BASE_URL)")
    print("   EMBEDDING_API_KEY=sk-embedding-your-embedding-key")
    
    print("\n💡 Benefits of separate configuration:")
    print("   - Load balancing across different servers")
    print("   - Different authentication for different services")
    print("   - Independent scaling of LLM and embedding services")
    print("   - Separate monitoring and cost tracking")
    print("   - Better security isolation")

def main():
    """Main function."""
    try:
        if setup_separate_keys():
            print("\n✅ Setup completed successfully!")
            print("\n🔄 Don't forget to restart your MCP service for changes to take effect.")
        else:
            print("\n❌ Setup failed. Please check your configuration manually.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
