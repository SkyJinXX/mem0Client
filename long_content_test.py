#!/usr/bin/env python3
"""
Test long content and special characters
"""

import tempfile
import json
import os
from core.uploader import MemoryUploader
from core.config import Config

def test_long_content():
    """测试长内容"""
    
    print("🧪 Testing long content...")
    
    # 测试长内容 - 使用真实的长消息但稍微缩短
    long_conversation = {
        "title": "Memory Management Test",
        "messages": [
            {
                "role": "assistant",
                "content": "**结论先行**\n\n- **仅 60 %～65 % '使用率'并不是危险信号**。\n- 真正该担心的是 **'Available / 可用'长时间低于 1–2 GB**。\n- Windows 自带的内存管理够用；如果你体感流畅，就没必要机械地关标签或 IDE。"
            },
            {
                "role": "user", 
                "content": "所以我什么时候需要焦虑？我之前内存占用大概90多，因为太多标签页了。"
            }
        ]
    }
    
    test_conversation("Long content (shortened)", long_conversation)
    
    # 测试非常长的内容
    very_long_conversation = {
        "title": "Very Long Test",
        "messages": [
            {
                "role": "assistant",
                "content": "**结论先行**\n\n- **仅 60 %～65 % '使用率'并不是危险信号**。\n- 真正该担心的是 **'Available / 可用'长时间低于 1–2 GB**、或者 **硬缺页 (Hard faults/sec) 持续攀升** 并伴随卡顿。\n- Windows 自带的内存管理（回收 Standby cache、压缩、换出到 pagefile 等）在大多数场景够用；如果你体感流畅，就没必要机械地关标签或 IDE。\n\n### 1. 读懂 Resource Monitor 里的几个关键字段\n\n| 字段 | 含义 | 可否立刻回收 |\n|------|------|--------------|\n| **In Use** | 进程当前占用的物理页（工作集），包括前台应用、后台常驻服务 | ❌（除非进程自行释放，或系统主动把其中部分换出） |\n| **Modified** | 已被进程改写但尚未写回磁盘的页 | ⚠️（需先写回才能回收） |\n| **Standby** | 文件缓存／曾被用过的数据，**可随时抢占** | ✅ |\n| **Free** | 完全空闲 | ✅ |"
            }
        ]
    }
    
    test_conversation("Very long content", very_long_conversation)

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
        
        print(f"   ✅ Success! Memory created")
        
    except Exception as e:
        print(f"   ❌ Failed: {str(e)}")
        # 打印更多错误信息
        if "Bad request" in str(e):
            print(f"   💡 This might be due to content length or special characters")
    
    finally:
        # 清理
        try:
            os.unlink(temp_file)
        except:
            pass

if __name__ == "__main__":
    test_long_content() 