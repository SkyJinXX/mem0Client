#!/usr/bin/env python3
"""
测试 infer 参数功能
演示 infer=True 和 infer=False 的区别
"""

import os
from core.config import Config
from core.uploader import MemoryUploader

def test_infer_feature():
    """测试 infer 参数功能"""
    
    print("🧪 测试 infer 参数功能")
    print("=" * 50)
    
    # 检查API密钥
    if not os.getenv('MEM0_API_KEY'):
        print("❌ 请先设置 MEM0_API_KEY 环境变量")
        print("💡 获取API密钥：https://app.mem0.ai")
        return
    
    try:
        # 初始化组件
        config = Config()
        uploader = MemoryUploader(config)
        
        user_id = "infer_test_user"
        
        # 测试内容
        test_content = """
        项目状态更新：
        
        完成情况：
        - 用户认证模块：100% ✅
        - 数据库设计：95% 🔄  
        - API接口开发：80% 🔄
        
        下周计划：
        - 完成数据库索引优化
        - 开始前端界面开发
        - 准备用户测试
        
        技术栈：
        - 后端：Python + FastAPI
        - 数据库：PostgreSQL
        - 前端：React + TypeScript
        
        团队信息：
        - 项目经理：张三 (zhangsan@company.com)
        - 开发：李四, 王五
        - 测试：赵六
        """
        
        # 测试1：启用智能推理 (infer=True)
        print("\n🧠 测试1：启用智能推理 (infer=True)")
        result1 = uploader.upload_text(
            content=test_content,
            user_id=user_id,
            custom_instructions="提取项目进度、技术栈和计划信息，忽略具体的人员联系方式",
            includes="project progress, technology stack, plans, tasks",
            excludes="email addresses, personal contact information",
            infer=True  # 启用智能推理
        )
        print(f"✅ 智能推理模式上传完成，Memory ID: {result1.get('id', 'N/A')}")
        
        # 测试2：关闭智能推理 (infer=False)  
        print("\n📄 测试2：关闭智能推理 (infer=False)")
        result2 = uploader.upload_text(
            content=test_content,
            user_id=user_id,
            custom_instructions="保持原始格式的项目状态记录",
            infer=False  # 关闭智能推理
        )
        print(f"✅ 原始存储模式上传完成，Memory ID: {result2.get('id', 'N/A')}")
        
        # 测试3：默认行为（通常是 infer=True）
        print("\n⚙️ 测试3：默认行为（不指定 infer 参数）")
        result3 = uploader.upload_text(
            content="这是一个简单的测试内容，用于验证默认的 infer 行为。",
            user_id=user_id
        )
        print(f"✅ 默认模式上传完成，Memory ID: {result3.get('id', 'N/A')}")
        
        print("\n" + "="*50)
        print("✨ infer 参数测试完成！")
        print("\n💡 测试总结：")
        print("  📊 测试1 (infer=True): AI会智能分析并提取关键信息")
        print("  📋 测试2 (infer=False): 保存原始内容结构，不进行智能处理") 
        print("  🔧 测试3 (默认): 使用 Mem0 API 的默认行为")
        print("\n🔍 你可以通过搜索功能来对比这三种上传模式的效果！")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

if __name__ == "__main__":
    test_infer_feature() 