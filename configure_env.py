#!/usr/bin/env python3
"""
Interactive .env file configurator for mcp-mem0.
This script will guide you through setting up all required environment variables.
"""

import os
import sys
from pathlib import Path
from typing import Optional

def get_input(prompt: str, default: Optional[str] = None, required: bool = False, password: bool = False) -> str:
    """Get user input with optional default value and password masking."""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    while True:
        if password:
            import getpass
            value = getpass.getpass(prompt)
        else:
            value = input(prompt).strip()
        
        if value:
            return value
        elif default and not required:
            return default
        elif required:
            print("❌ This field is required. Please provide a value.")
        else:
            return ""

def validate_database_url(url: str) -> bool:
    """Validate database URL format."""
    if not url.startswith(('postgresql://', 'postgres://')):
        print("❌ Database URL must start with 'postgresql://' or 'postgres://'")
        return False
    
    try:
        # Basic parsing
        if '@' not in url or '/' not in url:
            print("❌ Invalid database URL format")
            return False
        
        # Check if it has the basic structure: postgresql://user:pass@host:port/db
        parts = url.split('@')
        if len(parts) != 2:
            print("❌ Invalid database URL format")
            return False
        
        return True
    except:
        print("❌ Invalid database URL format")
        return False

def validate_port(port_str: str) -> bool:
    """Validate port number."""
    try:
        port = int(port_str)
        if 1 <= port <= 65535:
            return True
        else:
            print("❌ Port must be between 1 and 65535")
            return False
    except ValueError:
        print("❌ Port must be a valid number")
        return False

def configure_llm_provider() -> dict:
    """Configure LLM provider settings."""
    print("\n🔧 LLM Configuration")
    print("=" * 40)
    
    # LLM Provider
    print("\nAvailable LLM providers:")
    print("1. OpenAI (OpenAI API)")
    print("2. OpenRouter (Multiple models)")
    print("3. Ollama (Local models)")
    
    while True:
        choice = input("\nSelect LLM provider (1-3): ").strip()
        if choice == "1":
            provider = "openai"
            break
        elif choice == "2":
            provider = "openrouter"
            break
        elif choice == "3":
            provider = "ollama"
            break
        else:
            print("❌ Please select 1, 2, or 3")
    
    config = {"provider": provider}
    
    if provider in ["openai", "openrouter"]:
        # API Key
        api_key = get_input("API Key", required=True, password=True)
        config["api_key"] = api_key
        
        # Model choice
        if provider == "openai":
            default_model = "gpt-3.5-turbo"
            model = get_input("LLM Model", default_model)
            config["model"] = model
            
            # Embedding model
            default_embedding = "text-embedding-3-small"
            embedding = get_input("Embedding Model", default_embedding)
            config["embedding"] = embedding
            
        elif provider == "openrouter":
            default_model = "anthropic/claude-3.5-sonnet"
            model = get_input("LLM Model", default_model)
            config["model"] = model
            
            # For OpenRouter, we'll use OpenAI embeddings
            default_embedding = "text-embedding-3-small"
            embedding = get_input("Embedding Model", default_embedding)
            config["embedding"] = embedding
    
    elif provider == "ollama":
        # Base URL
        default_url = "http://127.0.0.1:11434"
        base_url = get_input("Ollama Base URL", default_url)
        config["base_url"] = base_url
        
        # Model choice
        default_model = "llama3.2:latest"
        model = get_input("LLM Model", default_model)
        config["model"] = model
        
        # Embedding model
        default_embedding = "snowflake-arctic-embed2:latest"
        embedding = get_input("Embedding Model", default_embedding)
        config["embedding"] = embedding
    
    return config

def configure_server() -> dict:
    """Configure server settings."""
    print("\n🌐 Server Configuration")
    print("=" * 40)
    
    config = {}
    
    # Transport method
    print("\nTransport methods:")
    print("1. SSE (Server-Sent Events) - for web clients")
    print("2. STDIO (Standard I/O) - for CLI clients")
    
    while True:
        choice = input("\nSelect transport method (1-2): ").strip()
        if choice == "1":
            config["transport"] = "sse"
            break
        elif choice == "2":
            config["transport"] = "stdio"
            break
        else:
            print("❌ Please select 1 or 2")
    
    if config["transport"] == "sse":
        # Host
        default_host = "0.0.0.0"
        host = get_input("Host to bind to", default_host)
        config["host"] = host
        
        # Port
        while True:
            default_port = "8050"
            port = get_input("Port to listen on", default_port)
            if validate_port(port):
                config["port"] = port
                break
    
    return config

def configure_database() -> dict:
    """Configure database settings."""
    print("\n🗄️  Database Configuration")
    print("=" * 40)
    
    config = {}
    
    print("\nDatabase types:")
    print("1. Supabase (PostgreSQL)")
    print("2. Custom PostgreSQL")
    
    while True:
        choice = input("\nSelect database type (1-2): ").strip()
        if choice == "1":
            config["type"] = "supabase"
            break
        elif choice == "2":
            config["type"] = "custom_postgres"
            break
        else:
            print("❌ Please select 1 or 2")
    
    if config["type"] == "supabase":
        print("\n📋 Supabase Setup Instructions:")
        print("1. Go to your Supabase dashboard")
        print("2. Click 'Settings' → 'Database'")
        print("3. Find 'Connection string' under 'Connection pooling'")
        print("4. Copy the connection string")
        
        while True:
            database_url = get_input("Supabase Connection String", required=True)
            if validate_database_url(database_url):
                config["url"] = database_url
                break
    
    elif config["type"] == "custom_postgres":
        print("\n📋 Custom PostgreSQL Setup:")
        print("Format: postgresql://username:password@host:port/database")
        
        while True:
            database_url = get_input("PostgreSQL Connection String", required=True)
            if validate_database_url(database_url):
                config["url"] = database_url
                break
    
    return config

def configure_user() -> dict:
    """Configure user settings."""
    print("\n👤 User Configuration")
    print("=" * 40)
    
    config = {}
    
    # Default user ID
    default_user_id = "default_user"
    user_id = get_input("Default User ID (optional)", default_user_id)
    config["user_id"] = user_id
    
    return config

def generate_env_content(config: dict) -> str:
    """Generate .env file content from configuration."""
    
    env_content = f"""# Environment configuration for mcp-mem0
# Generated by configure_env.py

# =============================================================================
# User Configuration
# =============================================================================
DEFAULT_USER_ID={config['user']['user_id']}

# =============================================================================
# Server Configuration
# =============================================================================
TRANSPORT={config['server']['transport']}
"""
    
    if config['server']['transport'] == 'sse':
        env_content += f"HOST={config['server']['host']}\nPORT={config['server']['port']}\n"
    
    env_content += f"""
# =============================================================================
# Mem0 Configuration
# =============================================================================
LLM_PROVIDER={config['llm']['provider']}
"""
    
    if config['llm']['provider'] in ['openai', 'openrouter']:
        env_content += f"""LLM_API_KEY={config['llm']['api_key']}
LLM_CHOICE={config['llm']['model']}
EMBEDDING_MODEL_CHOICE={config['llm']['embedding']}
"""
    elif config['llm']['provider'] == 'ollama':
        env_content += f"""LLM_API_KEY=
LLM_CHOICE={config['llm']['model']}
EMBEDDING_MODEL_CHOICE={config['llm']['embedding']}
LLM_BASE_URL={config['llm']['base_url']}
"""
    
    env_content += f"""
# =============================================================================
# Database Configuration
# =============================================================================
DATABASE_URL={config['database']['url']}

# =============================================================================
# Development Settings
# =============================================================================
DEBUG=true
LOG_LEVEL=DEBUG
"""
    
    return env_content

def main():
    """Main configuration function."""
    print("🚀 mcp-mem0 Environment Configuration")
    print("=" * 50)
    print("This script will help you configure all required environment variables.")
    print("Make sure you have your API keys and database credentials ready.\n")
    
    # Check if .env already exists
    env_file = Path(".env")
    if env_file.exists():
        print("⚠️  .env file already exists!")
        overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Configuration cancelled.")
            return
    
    try:
        # Collect configuration
        llm_config = configure_llm_provider()
        server_config = configure_server()
        database_config = configure_database()
        user_config = configure_user()
        
        # Combine all configurations
        config = {
            "llm": llm_config,
            "server": server_config,
            "database": database_config,
            "user": user_config
        }
        
        # Generate .env content
        env_content = generate_env_content(config)
        
        # Show configuration summary
        print("\n" + "=" * 50)
        print("📋 Configuration Summary")
        print("=" * 50)
        print(f"LLM Provider: {config['llm']['provider']}")
        print(f"Transport: {config['server']['transport']}")
        if config['server']['transport'] == 'sse':
            print(f"Host: {config['server']['host']}")
            print(f"Port: {config['server']['port']}")
        print(f"Database: {config['database']['type']}")
        print(f"Default User ID: {config['user']['user_id']}")
        
        # Confirm before saving
        print("\n" + "=" * 50)
        confirm = input("Save this configuration to .env? (Y/n): ").strip().lower()
        if confirm in ['', 'y', 'yes']:
            # Write .env file
            with open(env_file, 'w') as f:
                f.write(env_content)
            
            print(f"\n✅ .env file created successfully!")
            print(f"📁 Location: {env_file.absolute()}")
            
            print("\n📋 Next steps:")
            print("1. Review the .env file to ensure all values are correct")
            print("2. Start the MCP server: python -m src.main")
            print("3. Test the connection with one of the MCP tools")
            
            if config['llm']['provider'] == 'ollama':
                print("\n⚠️  For Ollama:")
                print("   - Make sure Ollama is installed and running")
                print("   - Pull the required models:")
                print(f"     ollama pull {config['llm']['model']}")
                print(f"     ollama pull {config['llm']['embedding']}")
            
        else:
            print("Configuration cancelled.")
            
    except KeyboardInterrupt:
        print("\n\n❌ Configuration cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error during configuration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
