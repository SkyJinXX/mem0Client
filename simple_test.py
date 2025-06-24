#!/usr/bin/env python3
"""
Simple test to verify correct Mem0 API format
"""

import os
from mem0 import MemoryClient

def test_simple_api():
    # Initialize client
    client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))
    
    # Test different API formats
    messages = [
        {"role": "user", "content": "Hello, I want to learn Python"},
        {"role": "assistant", "content": "Great! Python is an excellent programming language to start with."}
    ]
    
    print("🧪 Testing different Mem0 API formats...")
    
    # Format 1: Basic v2 format
    try:
        print("\n1️⃣ Testing: client.add(messages, user_id='test', version='v2')")
        result = client.add(messages, user_id="test-user", version="v2")
        print("✅ Success with basic v2 format!")
        print(f"Result: {result}")
        return
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
    
    # Format 2: Without version parameter
    try:
        print("\n2️⃣ Testing: client.add(messages, user_id='test')")
        result = client.add(messages, user_id="test-user")
        print("✅ Success without version!")
        print(f"Result: {result}")
        return
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
    
    # Format 3: Single message
    try:
        print("\n3️⃣ Testing: client.add('Hello', user_id='test')")
        result = client.add("Hello, I want to learn Python", user_id="test-user")
        print("✅ Success with single message!")
        print(f"Result: {result}")
        return
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
    
    # Format 4: With minimal metadata
    try:
        print("\n4️⃣ Testing: client.add(messages, user_id='test', metadata={})")
        result = client.add(messages, user_id="test-user", metadata={"source": "test"})
        print("✅ Success with metadata!")
        print(f"Result: {result}")
        return
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
    
    print("\n❌ All formats failed!")

if __name__ == "__main__":
    test_simple_api() 