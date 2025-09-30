#!/usr/bin/env python3
"""
Check Mem0 library version and available configuration parameters.
"""

import sys
import inspect

def check_mem0_version():
    """Check Mem0 library version and configuration options."""
    print("🔍 Checking Mem0 Library")
    print("=" * 30)
    
    try:
        import mem0
        print(f"✅ Mem0 version: {mem0.__version__}")
        
        # Check Memory class
        from mem0 import Memory
        print(f"✅ Memory class: {Memory}")
        
        # Check if we can inspect the configuration classes
        try:
            from mem0.config import BaseEmbedderConfig
            print(f"✅ BaseEmbedderConfig: {BaseEmbedderConfig}")
            
            # Get the __init__ signature
            sig = inspect.signature(BaseEmbedderConfig.__init__)
            print(f"✅ BaseEmbedderConfig.__init__ parameters: {list(sig.parameters.keys())}")
            
            # Check if base_url is supported
            if 'base_url' in sig.parameters:
                print("✅ base_url parameter is supported in BaseEmbedderConfig")
            else:
                print("❌ base_url parameter is NOT supported in BaseEmbedderConfig")
                print("   This explains the error you're seeing!")
                
        except ImportError as e:
            print(f"⚠️  Could not import BaseEmbedderConfig: {e}")
        
        # Check LLM config
        try:
            from mem0.config import BaseLLMConfig
            print(f"✅ BaseLLMConfig: {BaseLLMConfig}")
            
            sig = inspect.signature(BaseLLMConfig.__init__)
            print(f"✅ BaseLLMConfig.__init__ parameters: {list(sig.parameters.keys())}")
            
            if 'base_url' in sig.parameters:
                print("✅ base_url parameter is supported in BaseLLMConfig")
            else:
                print("❌ base_url parameter is NOT supported in BaseLLMConfig")
                
        except ImportError as e:
            print(f"⚠️  Could not import BaseLLMConfig: {e}")
        
        # Check what embedder providers are available
        try:
            from mem0.config import EmbedderConfig
            print(f"✅ EmbedderConfig: {EmbedderConfig}")
            
            sig = inspect.signature(EmbedderConfig.__init__)
            print(f"✅ EmbedderConfig.__init__ parameters: {list(sig.parameters.keys())}")
            
        except ImportError as e:
            print(f"⚠️  Could not import EmbedderConfig: {e}")
        
        print("\n📋 Recommendations:")
        print("1. The embedder configuration doesn't support base_url parameter")
        print("2. Use environment variables (OPENAI_BASE_URL) instead")
        print("3. This is the correct approach for Mem0 library")
        
    except ImportError as e:
        print(f"❌ Could not import Mem0: {e}")
        print("Please install Mem0: pip install mem0ai")
        return False
    except Exception as e:
        print(f"❌ Error checking Mem0: {e}")
        return False
    
    return True

if __name__ == '__main__':
    check_mem0_version()
