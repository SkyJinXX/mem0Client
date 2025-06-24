#!/usr/bin/env python3
"""
Mem0 Client - Advanced Features Example
演示 Custom Instructions、Includes 和 Excludes 功能的使用

这个脚本展示了如何使用新增的高级配置功能来控制AI如何处理和提取记忆内容。
"""

from core.config import Config
from core.uploader import MemoryUploader

def main():
    """示例：使用高级配置功能上传内容."""
    
    print("🎯 Mem0 Client - Advanced Features Example")
    print("=" * 50)
    
    # 初始化配置和上传器
    config = Config()
    uploader = MemoryUploader(config)
    
    # 示例1：技术文档上传 - 使用 Custom Instructions
    print("\n📖 示例1：技术文档上传")
    tech_content = """
    # API 文档
    
    ## 用户认证 API
    POST /api/auth/login
    - 用户名：admin
    - 密码：secret123
    - 返回：JWT token
    
    ## 数据查询 API  
    GET /api/data/{id}
    - 需要认证
    - 返回用户数据
    
    ## 注意事项
    - 这是内部测试环境
    - 联系人：张三 (zhangsan@company.com)
    - 服务器IP：192.168.1.100
    """
    
    result1 = uploader.upload_text(
        content=tech_content,
        extract_mode="auto",
        custom_instructions="请专注于提取API接口信息、参数和返回值，忽略具体的认证凭据和服务器信息",
        includes="API endpoints, parameters, return values, authentication methods",
        excludes="passwords, IP addresses, email addresses, specific credentials",
        infer=True  # 智能推理和提取记忆
    )
    print(f"✅ 技术文档上传完成，Memory ID: {result1.get('id', 'N/A')}")
    
    # 示例2：会议记录上传 - 排除个人信息
    print("\n🤝 示例2：会议记录上传")
    meeting_content = """
    # 项目会议记录 - 2024年3月15日
    
    ## 参会人员
    - 张三 (项目经理) - zhang.san@company.com
    - 李四 (开发) - li.si@company.com  
    - 王五 (设计) - wang.wu@company.com
    
    ## 会议内容
    1. 项目进度回顾：
       - 前端开发完成80%
       - 后端API开发完成60%
       - 数据库设计已完成
    
    2. 下周计划：
       - 完成用户认证模块
       - 集成支付接口
       - 开始测试工作
    
    3. 技术决策：
       - 采用React作为前端框架
       - 使用Node.js + Express作为后端
       - 数据库选择MongoDB
    
    ## 问题和风险
    - 第三方API集成可能存在延迟
    - 需要额外的安全审查
    
    ## 下次会议
    - 时间：2024年3月22日 下午2点
    - 地点：会议室B301
    """
    
    result2 = uploader.upload_text(
        content=meeting_content,
        extract_mode="auto",
        custom_instructions="请提取项目相关的技术信息、进度和决策，保护参会人员的个人信息",
        includes="project progress, technical decisions, tasks, risks, technology choices",
        excludes="personal names, email addresses, specific meeting locations, contact information",
        infer=True  # 智能推理和提取记忆
    )
    print(f"✅ 会议记录上传完成，Memory ID: {result2.get('id', 'N/A')}")
    
    # 示例3：研究笔记上传 - 自定义处理
    print("\n📚 示例3：研究笔记上传")
    research_content = """
    # AI模型优化研究笔记
    
    ## 研究背景
    研究如何优化大语言模型的推理速度和准确性
    
    ## 方法探索
    1. 量化技术：
       - 8bit量化：速度提升2x，准确率下降5%
       - 4bit量化：速度提升4x，准确率下降15%
    
    2. 模型剪枝：
       - 结构化剪枝：减少30%参数，速度提升1.5x
       - 非结构化剪枝：减少50%参数，但速度提升有限
    
    ## 实验数据
    - 基准模型：GPT-3.5, 175B参数
    - 测试数据集：CommonSense QA, GLUE
    - 硬件：NVIDIA A100 GPU
    
    ## 个人感想
    这些技术都有各自的优缺点，需要根据具体应用场景选择。
    下周计划联系李博士讨论进一步的研究方向。
    """
    
    result3 = uploader.upload_text(
        content=research_content,
        extract_mode="auto",
        custom_instructions="专注提取技术方法、实验结果和可操作的见解，过滤个人感想和计划",
        includes="technical methods, experimental results, performance metrics, research findings",
        excludes="personal opinions, meeting plans, contact intentions",
        infer=True  # 智能推理和提取记忆
    )
    print(f"✅ 研究笔记上传完成，Memory ID: {result3.get('id', 'N/A')}")
    
    # 示例4：原始存储模式 - 不进行智能推理
    print("\n📄 示例4：原始存储模式 (infer=False)")
    raw_content = """
    用户反馈：
    - 界面加载太慢
    - 搜索功能不准确  
    - 希望增加暗色主题
    
    解决方案记录：
    1. 优化图片压缩 ✓
    2. 升级搜索算法 (进行中)
    3. 实现主题切换功能 (待开始)
    """
    
    result4 = uploader.upload_text(
        content=raw_content,
        extract_mode="auto",
        infer=False  # 不进行智能推理，保存原始内容结构
    )
    print(f"✅ 原始内容上传完成，Memory ID: {result4.get('id', 'N/A')}")
    
    print("\n" + "="*50)
    print("✨ 所有示例上传完成！")
    print("\n💡 infer 参数说明：")
    print("  • infer=True (默认): AI会智能推理和提取关键记忆")
    print("  • infer=False: 保存原始消息内容，不进行智能处理")
    print("\n🔧 这些功能可以让你精确控制AI如何处理和存储你的内容！")

if __name__ == "__main__":
    main() 