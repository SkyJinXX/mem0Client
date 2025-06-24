#!/usr/bin/env python3
"""
Mem0 Client 使用示例
演示如何使用核心功能进行记忆上传和搜索
"""

import os
from datetime import datetime
from core.config import Config
from core.uploader import MemoryUploader
from core.searcher import MemorySearcher

def main():
    """主示例函数"""
    print("🧠 Mem0 Client 使用示例")
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
        searcher = MemorySearcher(config)
        
        user_id = "example_user"
        
        # 示例1：上传文本记忆
        print("\n📤 示例1：上传文本记忆")
        sample_texts = [
            "今天学习了Python的装饰器概念，装饰器可以在不修改原函数的情况下增加功能。",
            "与团队讨论了新项目的架构设计，决定使用微服务架构。",
            "阅读了关于机器学习的文章，了解了监督学习和无监督学习的区别。",
            "参加了AI大会，听到了很多关于大语言模型的最新进展。"
        ]
        
        for i, text in enumerate(sample_texts):
            result = uploader.upload_text(
                content=text,
                user_id=user_id,
                extract_mode="auto",
                metadata={"example": True, "batch": f"sample_{i+1}"}
            )
            print(f"  ✅ 已上传样本 {i+1}")
        
        # 示例2：语义搜索
        print("\n🔍 示例2：语义搜索")
        search_queries = [
            "Python编程",
            "项目架构",
            "机器学习",
            "AI人工智能"
        ]
        
        for query in search_queries:
            results = searcher.search_by_query(
                query=query,
                user_id=user_id,
                limit=3
            )
            print(f"\n🔍 搜索 '{query}':")
            if results:
                for result in results[:2]:  # 只显示前2个结果
                    content = result.get('memory', '')[:80] + "..."
                    score = result.get('score', 0)
                    print(f"  📝 {content} (相似度: {score:.2f})")
            else:
                print("  📭 未找到相关记忆")
        
        # 示例3：时间范围搜索
        print("\n📅 示例3：时间范围搜索（最近1天）")
        time_results = searcher.search_by_time_range(
            days_back=1,
            user_id=user_id,
            limit=10
        )
        
        print(f"找到 {len(time_results)} 条最近的记忆")
        for result in time_results[:3]:
            content = result.get('memory', '')[:60] + "..."
            created_at = result.get('created_at', 'N/A')
            print(f"  📅 {content} ({created_at[:10]})")
        
        # 示例4：统计信息
        print("\n📊 示例4：用户统计")
        stats = searcher.get_user_stats(user_id)
        print(f"  👤 用户ID: {stats['user_id']}")
        print(f"  📝 总记忆数: {stats['total_memories']}")
        print(f"  🕐 最近7天: {stats['recent_memories_7d']}")
        
        if stats['sources']:
            print("  📋 记忆来源:")
            for source, count in stats['sources'].items():
                print(f"    • {source}: {count}")
        
        # 示例5：相关记忆搜索
        print("\n🔗 示例5：相关记忆搜索")
        reference_content = "机器学习是人工智能的一个重要分支"
        related_results = searcher.search_related_to_content(
            content=reference_content,
            user_id=user_id,
            limit=3
        )
        
        print(f"与 '{reference_content[:30]}...' 相关的记忆:")
        for result in related_results:
            content = result.get('memory', '')[:70] + "..."
            score = result.get('score', 0)
            print(f"  🔗 {content} (相关度: {score:.2f})")
        
        print("\n✅ 示例演示完成！")
        print("\n💡 提示：")
        print("  • 使用 'python cli.py --help' 查看所有CLI命令")
        print("  • 使用 'streamlit run web_app.py' 启动Web界面")
        print("  • 查看 README.md 了解更多使用方法")
        
    except Exception as e:
        print(f"❌ 示例执行失败: {str(e)}")
        print("💡 请检查API密钥是否正确设置")

if __name__ == "__main__":
    main() 