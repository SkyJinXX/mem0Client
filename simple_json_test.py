#!/usr/bin/env python3
"""
Simple JSON conversation test to identify the issue
"""

import tempfile
import json
import os
from core.uploader import MemoryUploader
from core.config import Config

def test_simple_json():
    """测试简单的JSON对话"""
    
    print("🧪 Testing simple JSON conversation...")
    
    # 1. 单条消息测试
    simple_conversation = {
        "title": "Simple Test",
        "messages": [
            {
                "role": "user",
                "content": "Hello, how are you?"
            }
        ]
    }
    
    test_conversation("Single message", simple_conversation)
    
    # 2. 两条短消息测试
    short_conversation = {
        "title": "Short Conversation", 
        "messages": [
            {
                "role": "user",
                "content": "What is Python?"
            },
            {
                "role": "assistant",
                "content": "Python is a programming language."
            }
        ]
    }
    
    test_conversation("Short conversation", short_conversation)
    
    # 3. 测试以assistant开头
    assistant_first = {
        "title": "Assistant First",
        "messages": [
            {
                "role": "assistant", 
                "content": "Hello! How can I help you today?"
            },
            {
                "role": "user",
                "content": "I want to learn programming."
            }
        ]
    }
    
    test_conversation("Assistant first", assistant_first)

def test_conversation(test_name, conversation_data):
    """测试单个对话"""
    print(f"\n📝 {test_name}:")
    
    # 保存到临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(conversation_data, f, ensure_ascii=False, indent=2)
        temp_file = f.name
    
    try:
        config = Config()
        uploader = MemoryUploader(config)
        
        result = uploader.upload_file(
            file_path=temp_file,
            extract_mode="auto"
        )
        
        print(f"   ✅ Success! Memory ID: {result.get('id', 'Unknown')}")
        
    except Exception as e:
        print(f"   ❌ Failed: {str(e)}")
    
    finally:
        # 清理
        try:
            os.unlink(temp_file)
        except:
            pass

if __name__ == "__main__":
    test_simple_json() 