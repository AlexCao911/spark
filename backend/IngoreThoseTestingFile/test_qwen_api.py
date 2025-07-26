#!/usr/bin/env python3
"""
Test script for Qwen API connection.
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_qwen_connection():
    """Test connection to Qwen API."""
    try:
        from openai import OpenAI
        from spark.config import config
        
        print("🔍 Testing Qwen API connection...")
        print(f"API Key: {config.CHATBOT_API_KEY[:10]}...")
        print(f"Endpoint: {config.CHATBOT_API_ENDPOINT}")
        print(f"Model: {config.CHATBOT_MODEL}")
        print()
        
        # Initialize client
        client = OpenAI(
            api_key=config.CHATBOT_API_KEY,
            base_url=config.CHATBOT_API_ENDPOINT
        )
        
        # Test simple completion
        print("📤 Sending test message...")
        response = client.chat.completions.create(
            model=config.CHATBOT_MODEL,
            messages=[
                {"role": "system", "content": "你是一个有用的AI助手。"},
                {"role": "user", "content": "你好，请简单介绍一下你自己。"}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        print("✅ API connection successful!")
        print(f"📝 Response: {response.choices[0].message.content}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_chatbot_core():
    """Test ChatbotCore with Qwen."""
    try:
        from spark.chatbot.core import ChatbotCore
        
        print("🤖 Testing ChatbotCore with Qwen...")
        
        chatbot = ChatbotCore()
        
        # Test engagement
        result = chatbot.engage_user("我想创建一个关于太空冒险的视频")
        
        print("✅ ChatbotCore test successful!")
        print(f"📝 Status: {result.get('status')}")
        print(f"📝 Response: {result.get('response')}")
        print(f"📝 Complete: {result.get('is_complete')}")
        print(f"📝 Missing: {result.get('missing_elements')}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ ChatbotCore test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🎬 Qwen API Integration Test")
    print("=" * 30)
    
    # Test API connection
    api_success = test_qwen_connection()
    
    if api_success:
        # Test chatbot core
        chatbot_success = test_chatbot_core()
        
        if chatbot_success:
            print("🎉 All tests passed! Qwen integration is working.")
        else:
            print("⚠️  API works but ChatbotCore has issues.")
    else:
        print("❌ API connection failed. Please check your configuration.")

if __name__ == "__main__":
    main()