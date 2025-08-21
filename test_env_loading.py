#!/usr/bin/env python3
"""
Test script to verify environment variable loading
"""

import sys
import os

def test_env_loading():
    """Test if environment variables are loading correctly."""
    print("🔍 Testing Environment Variable Loading")
    print("=" * 50)
    
    try:
        # Try to import the config
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        from backend.app.config import settings
        
        print("✅ Config imported successfully")
        
        # Check key environment variables
        required_vars = [
            "OPENAI_API_KEY",
            "TAVILY_API_KEY", 
            "COHERE_API_KEY",
            "LANGSMITH_API_KEY"
        ]
        
        print("\n📋 Environment Variables Status:")
        print("-" * 30)
        
        for var in required_vars:
            value = getattr(settings, var, None)
            if value:
                # Mask the API key for security
                masked_value = value[:10] + "..." if len(value) > 10 else value
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"❌ {var}: NOT FOUND")
        
        # Test specific values
        print(f"\n🔑 OpenAI API Key: {settings.OPENAI_API_KEY[:20]}...")
        print(f"🔑 Tavily API Key: {settings.TAVILY_API_KEY[:20]}...")
        print(f"🔑 Cohere API Key: {settings.COHERE_API_KEY[:20] if settings.COHERE_API_KEY else 'None'}...")
        
        print(f"\n✅ Environment variables loaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Environment variable loading failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_env_loading()
    if success:
        print("\n🚀 Environment setup: SUCCESSFUL!")
        print("✅ Ready to run real performance tests")
        sys.exit(0)
    else:
        print("\n❌ Environment setup: FAILED!")
        sys.exit(1)
