"""
Mem0 Client Web Interface
A Streamlit-based web interface for uploading and searching memories.
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from core.config import Config
from core.uploader import MemoryUploader
from core.searcher import MemorySearcher

# Page configuration
st.set_page_config(
    page_title="🧠 Mem0 Client",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'config' not in st.session_state:
    try:
        st.session_state.config = Config()
        st.session_state.uploader = MemoryUploader(st.session_state.config)
        st.session_state.searcher = MemorySearcher(st.session_state.config)
        st.session_state.initialized = True
    except Exception as e:
        st.session_state.initialized = False
        st.session_state.init_error = str(e)

# Initialize Advanced Settings persistence
if 'advanced_settings' not in st.session_state:
    st.session_state.advanced_settings = {
        'text_custom_instructions': '',
        'text_includes': '',
        'text_excludes': '',
        'text_exclude_presets': [],
        'text_infer': True,
        'file_custom_instructions': '',
        'file_includes': '',
        'file_excludes': '',
        'file_exclude_presets': [],
        'file_infer': True,
        'advanced_settings_expanded': False
    }

def main():
    """Main application function."""
    st.title("🧠 Mem0 Client")
    st.markdown("Upload and search your memories with AI-powered processing")
    
    # Check initialization
    if not st.session_state.get('initialized', False):
        st.error(f"❌ Initialization failed: {st.session_state.get('init_error', 'Unknown error')}")
        st.info("💡 Please make sure MEM0_API_KEY environment variable is set")
        return
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # User ID input
        user_id = st.text_input(
            "User ID",
            value=st.session_state.config.default_user_id,
            help="Identifier for your memories"
        )
        
        # Extract mode selection
        extract_mode = st.selectbox(
            "Extract Mode",
            options=["auto", "raw"],
            index=0 if st.session_state.config.default_extract_mode == "auto" else 1,
            help="auto: AI processing, raw: original content"
        )
        
        st.divider()
        
        # Quick stats
        if st.button("📊 Show Stats"):
            show_stats(user_id)
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload", "🔍 Search", "📅 Time Search", "📊 Weekly Report"])
    
    with tab1:
        upload_interface(user_id, extract_mode)
    
    with tab2:
        search_interface(user_id)
    
    with tab3:
        time_search_interface(user_id)
    
    with tab4:
        weekly_report_interface(user_id)

def upload_interface(user_id: str, extract_mode: str):
    """Upload interface."""
    st.header("📤 Upload Memories")
    
    # Upload method selection
    upload_method = st.radio(
        "Upload Method",
        options=["Text", "File", "Batch Files"],
        horizontal=True
    )
    
    if upload_method == "Text":
        # Text upload
        st.subheader("📝 Upload Text")
        
        text_content = st.text_area(
            "Text Content",
            height=200,
            placeholder="Enter your text content here..."
        )
        
        # Advanced Settings
        with st.expander("⚙️ Advanced Settings", expanded=st.session_state.advanced_settings.get('advanced_settings_expanded', False)):
            col1, col2 = st.columns(2)
            
            with col1:
                custom_instructions = st.text_area(
                    "自定义指令 (Custom Instructions)",
                    value=st.session_state.advanced_settings.get('text_custom_instructions', ''),
                    placeholder="例如：请专注于提取技术相关的信息，忽略日常闲聊内容...",
                    help="指导AI如何处理和提取记忆内容的自定义指令",
                    height=80,
                    key="text_custom_instructions_input"
                )
                
                includes = st.text_input(
                    "包含内容 (Includes)",
                    value=st.session_state.advanced_settings.get('text_includes', ''),
                    placeholder="例如：技术知识, 工作经验, 项目信息",
                    help="指定要特别包含的信息类型，用逗号分隔",
                    key="text_includes_input"
                )
                
                # Infer setting
                infer = st.checkbox(
                    "推理记忆 (Infer Memories)",
                    value=st.session_state.advanced_settings.get('text_infer', True),
                    help="True: AI会智能推理和提取记忆；False: 存储原始消息内容",
                    key="text_infer_input"
                )
            
            with col2:
                excludes = st.text_input(
                    "排除内容 (Excludes)",
                    value=st.session_state.advanced_settings.get('text_excludes', ''),
                    placeholder="例如：个人信息, 敏感数据, 隐私内容",
                    help="指定要排除的信息类型，用逗号分隔",
                    key="text_excludes_input"
                )
                
                # 预设的排除选项
                exclude_presets = st.multiselect(
                    "常用排除选项",
                    ["个人姓名", "联系方式", "地址信息", "财务信息", "密码/秘钥", "身份证号", "其他敏感信息"],
                    default=st.session_state.advanced_settings.get('text_exclude_presets', []),
                    help="选择常用的排除类型，会自动添加到排除内容中",
                    key="text_exclude_presets_input"
                )
            
            # Update session state when values change
            st.session_state.advanced_settings.update({
                'text_custom_instructions': custom_instructions,
                'text_includes': includes,
                'text_excludes': excludes,
                'text_exclude_presets': exclude_presets,
                'text_infer': infer,
                'advanced_settings_expanded': True  # Mark as expanded since user is using it
            })
        
        # Metadata
        with st.expander("🏷️ Additional Metadata (Optional)"):
            col1, col2 = st.columns(2)
            with col1:
                source_tag = st.text_input("Source", placeholder="e.g., meeting, idea, note")
            with col2:
                category_tag = st.text_input("Category", placeholder="e.g., work, personal, research")
        
        if st.button("📤 Upload Text", type="primary"):
            if text_content.strip():
                metadata = {}
                if source_tag:
                    metadata['source_tag'] = source_tag
                if category_tag:
                    metadata['category_tag'] = category_tag
                
                # 处理排除选项
                final_excludes = excludes
                if exclude_presets:
                    preset_mapping = {
                        "个人姓名": "personal names, individual names",
                        "联系方式": "contact information, phone numbers, email addresses",
                        "地址信息": "addresses, location information",
                        "财务信息": "financial information, bank details, payment information", 
                        "密码/秘钥": "passwords, secret keys, credentials",
                        "身份证号": "ID numbers, identification numbers",
                        "其他敏感信息": "other sensitive information, private data"
                    }
                    preset_excludes = [preset_mapping[preset] for preset in exclude_presets]
                    if final_excludes:
                        final_excludes = final_excludes + ", " + ", ".join(preset_excludes)
                    else:
                        final_excludes = ", ".join(preset_excludes)
                
                try:
                    with st.spinner("Uploading..."):
                        result = st.session_state.uploader.upload_text(
                            content=text_content,
                            user_id=user_id,
                            extract_mode=extract_mode,
                            metadata=metadata,
                            custom_instructions=custom_instructions.strip() if custom_instructions.strip() else None,
                            includes=includes.strip() if includes.strip() else None,
                            excludes=final_excludes.strip() if final_excludes.strip() else None,
                            infer=infer
                        )
                    st.success("✅ Text uploaded successfully!")
                    
                    # 显示使用的配置
                    if custom_instructions.strip() or includes.strip() or final_excludes.strip() or infer is not None:
                        with st.expander("📋 Applied Settings"):
                            if custom_instructions.strip():
                                st.write("**Custom Instructions:**", custom_instructions.strip())
                            if includes.strip():
                                st.write("**Includes:**", includes.strip())
                            if final_excludes.strip():
                                st.write("**Excludes:**", final_excludes.strip())
                            st.write("**Infer Memories:**", infer)
                    
                except Exception as e:
                    st.error(f"❌ Upload failed: {str(e)}")
            else:
                st.warning("⚠️ Please enter some text content")
    
    elif upload_method == "File":
        # Single file upload
        st.subheader("📁 Upload File")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['md', 'txt', 'markdown', 'json'],
            help="Supported formats: .md, .txt, .markdown, .json (conversation files)"
        )
        
        if uploaded_file is not None:
            # Show file info
            st.info(f"📄 File: {uploaded_file.name} ({uploaded_file.size} bytes)")
            
            # Preview content
            if st.checkbox("👀 Preview content"):
                try:
                    content = str(uploaded_file.read(), "utf-8")
                    st.text_area("Content Preview", content[:1000] + "..." if len(content) > 1000 else content, height=200)
                    uploaded_file.seek(0)  # Reset file pointer
                except Exception as e:
                    st.error(f"❌ Cannot preview file: {str(e)}")
            
            # Advanced Settings for file upload
            with st.expander("⚙️ Advanced Settings", expanded=st.session_state.advanced_settings.get('advanced_settings_expanded', False)):
                col1, col2 = st.columns(2)
                
                with col1:
                    file_custom_instructions = st.text_area(
                        "自定义指令 (Custom Instructions)",
                        value=st.session_state.advanced_settings.get('file_custom_instructions', ''),
                        placeholder="例如：这是技术文档，请重点提取架构和API信息...",
                        help="指导AI如何处理和提取记忆内容的自定义指令",
                        height=80,
                        key="file_custom_instructions"
                    )
                    
                    file_includes = st.text_input(
                        "包含内容 (Includes)",
                        value=st.session_state.advanced_settings.get('file_includes', ''),
                        placeholder="例如：技术文档, API接口, 架构设计",
                        help="指定要特别包含的信息类型，用逗号分隔",
                        key="file_includes"
                    )
                    
                    # Infer setting for file upload
                    file_infer = st.checkbox(
                        "推理记忆 (Infer Memories)",
                        value=st.session_state.advanced_settings.get('file_infer', True),
                        help="True: AI会智能推理和提取记忆；False: 存储原始消息内容",
                        key="file_infer_input"
                    )
                
                with col2:
                    file_excludes = st.text_input(
                        "排除内容 (Excludes)",
                        value=st.session_state.advanced_settings.get('file_excludes', ''),
                        placeholder="例如：个人信息, 临时备注, 调试信息",
                        help="指定要排除的信息类型，用逗号分隔",
                        key="file_excludes"
                    )
                    
                    # 预设的排除选项
                    file_exclude_presets = st.multiselect(
                        "常用排除选项",
                        ["个人姓名", "联系方式", "地址信息", "财务信息", "密码/秘钥", "身份证号", "其他敏感信息"],
                        default=st.session_state.advanced_settings.get('file_exclude_presets', []),
                        help="选择常用的排除类型，会自动添加到排除内容中",
                        key="file_exclude_presets"
                    )
                
                # Update session state when values change
                st.session_state.advanced_settings.update({
                    'file_custom_instructions': file_custom_instructions,
                    'file_includes': file_includes,
                    'file_excludes': file_excludes,
                    'file_exclude_presets': file_exclude_presets,
                    'file_infer': file_infer,
                    'advanced_settings_expanded': True  # Mark as expanded since user is using it
                })
            
            if st.button("📤 Upload File", type="primary"):
                try:
                    # 处理排除选项
                    final_file_excludes = file_excludes
                    if file_exclude_presets:
                        preset_mapping = {
                            "个人姓名": "personal names, individual names",
                            "联系方式": "contact information, phone numbers, email addresses",
                            "地址信息": "addresses, location information",
                            "财务信息": "financial information, bank details, payment information", 
                            "密码/秘钥": "passwords, secret keys, credentials",
                            "身份证号": "ID numbers, identification numbers",
                            "其他敏感信息": "other sensitive information, private data"
                        }
                        preset_excludes = [preset_mapping[preset] for preset in file_exclude_presets]
                        if final_file_excludes:
                            final_file_excludes = final_file_excludes + ", " + ", ".join(preset_excludes)
                        else:
                            final_file_excludes = ", ".join(preset_excludes)
                    
                    # Save uploaded file temporarily
                    import tempfile
                    import os
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name
                    
                    with st.spinner("Uploading..."):
                        result = st.session_state.uploader.upload_file(
                            file_path=tmp_path,
                            user_id=user_id,
                            extract_mode=extract_mode,
                            custom_instructions=file_custom_instructions.strip() if file_custom_instructions.strip() else None,
                            includes=file_includes.strip() if file_includes.strip() else None,
                            excludes=final_file_excludes.strip() if final_file_excludes.strip() else None,
                            infer=file_infer
                        )
                    
                    # Clean up temp file
                    os.unlink(tmp_path)
                    
                    st.success(f"✅ File '{uploaded_file.name}' uploaded successfully!")
                    
                    # 显示使用的配置
                    if file_custom_instructions.strip() or file_includes.strip() or final_file_excludes.strip() or file_infer is not None:
                        with st.expander("📋 Applied Settings"):
                            if file_custom_instructions.strip():
                                st.write("**Custom Instructions:**", file_custom_instructions.strip())
                            if file_includes.strip():
                                st.write("**Includes:**", file_includes.strip())
                            if final_file_excludes.strip():
                                st.write("**Excludes:**", final_file_excludes.strip())
                            st.write("**Infer Memories:**", file_infer)
                    
                except Exception as e:
                    st.error(f"❌ Upload failed: {str(e)}")
    
    else:
        # Batch upload
        st.subheader("📂 Batch Upload")
        st.info("Use the CLI tool for batch uploading files from a directory")
        st.code("python cli.py upload-directory /path/to/directory --user-id your_user_id")

def search_interface(user_id: str):
    """Search interface."""
    st.header("🔍 Search Memories")
    
    # Search input
    query = st.text_input(
        "Search Query",
        placeholder="What are you looking for?",
        help="Enter keywords or a natural language query"
    )
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button("🔍 Search", type="primary"):
            if query.strip():
                perform_search(query, user_id)
            else:
                st.warning("⚠️ Please enter a search query")
    
    with col2:
        limit = st.number_input("Max Results", min_value=1, max_value=100, value=10)
    
    with col3:
        show_full = st.checkbox("Show Full Content")

def time_search_interface(user_id: str):
    """Time-based search interface."""
    st.header("📅 Time-based Search")
    
    # Time range selection
    time_method = st.radio(
        "Time Range Method",
        options=["Days Back", "Date Range"],
        horizontal=True
    )
    
    if time_method == "Days Back":
        col1, col2 = st.columns(2)
        with col1:
            days_back = st.number_input("Days to Look Back", min_value=1, value=7)
        with col2:
            query = st.text_input("Optional Query", placeholder="Search within time range")
        
        if st.button("📅 Search by Days", type="primary"):
            perform_time_search(days_back=days_back, query=query or None, user_id=user_id)
    
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=7))
        with col2:
            end_date = st.date_input("End Date", value=datetime.now())
        with col3:
            query = st.text_input("Optional Query", placeholder="Search within date range")
        
        if st.button("📅 Search by Date Range", type="primary"):
            perform_time_search(
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                query=query or None,
                user_id=user_id
            )

def weekly_report_interface(user_id: str):
    """Weekly report interface."""
    st.header("📊 Weekly Report")
    
    col1, col2 = st.columns(2)
    
    with col1:
        weeks_back = st.number_input("Weeks Back", min_value=1, max_value=10, value=1)
    
    with col2:
        if st.button("📊 Generate Report", type="primary"):
            generate_weekly_report(weeks_back, user_id)

def perform_search(query: str, user_id: str, limit: int = 10):
    """Perform a search and display results."""
    try:
        with st.spinner("Searching..."):
            results = st.session_state.searcher.search_by_query(
                query=query,
                user_id=user_id,
                limit=limit
            )
        
        display_search_results(results, f"🔍 Search Results for: '{query}'")
        
    except Exception as e:
        st.error(f"❌ Search failed: {str(e)}")

def perform_time_search(user_id: str, days_back: Optional[int] = None, 
                       start_date: Optional[str] = None, end_date: Optional[str] = None,
                       query: Optional[str] = None):
    """Perform time-based search and display results."""
    try:
        with st.spinner("Searching..."):
            results = st.session_state.searcher.search_by_time_range(
                days_back=days_back,
                start_date=start_date,
                end_date=end_date,
                query=query,
                user_id=user_id
            )
        
        time_desc = f"{days_back} days ago" if days_back else f"{start_date} to {end_date}"
        title = f"📅 Time Search Results: {time_desc}"
        if query:
            title += f" (Query: '{query}')"
        
        display_search_results(results, title)
        
    except Exception as e:
        st.error(f"❌ Time search failed: {str(e)}")

def generate_weekly_report(weeks_back: int, user_id: str):
    """Generate and display weekly report."""
    try:
        with st.spinner("Generating report..."):
            report_data = st.session_state.searcher.search_weekly_report_data(
                weeks_back=weeks_back,
                user_id=user_id
            )
        
        # Report summary
        st.subheader(f"📊 Weekly Report (Week {weeks_back} ago)")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Week Period", f"{report_data['week_start']} to {report_data['week_end']}")
        with col2:
            st.metric("Current Week Memories", report_data['summary']['total_current'])
        with col3:
            st.metric("Related Historical", report_data['summary']['total_related'])
        
        # Current week memories
        if report_data['week_memories']:
            st.subheader("📅 Current Week Memories")
            display_search_results(report_data['week_memories'][:10], "")
        
        # Related memories
        if report_data['related_memories']:
            st.subheader("🔗 Related Historical Memories")
            display_search_results(report_data['related_memories'][:5], "")
        
        # Download report data
        if st.button("💾 Download Report Data"):
            st.download_button(
                label="📄 Download JSON",
                data=json.dumps(report_data, indent=2, ensure_ascii=False),
                file_name=f"weekly_report_{report_data['week_start']}.json",
                mime="application/json"
            )
        
    except Exception as e:
        st.error(f"❌ Report generation failed: {str(e)}")

def display_search_results(results: List[Dict[str, Any]], title: str):
    """Display search results in a table."""
    if not results:
        st.info("📭 No results found")
        return
    
    if title:
        st.subheader(title)
    
    # Convert to DataFrame for better display
    data = []
    for result in results:
        data.append({
            "ID": result.get('id', 'N/A')[:8],
            "Content": result.get('memory', '')[:100] + "..." if len(result.get('memory', '')) > 100 else result.get('memory', ''),
            "Created": format_date(result.get('created_at')),
            "Source": result.get('metadata', {}).get('source', 'unknown'),
            "Score": f"{result.get('score', 0):.2f}" if isinstance(result.get('score'), (int, float)) else str(result.get('score', 'N/A'))
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
    
    # Detailed view
    if st.checkbox("📋 Show Detailed View"):
        for i, result in enumerate(results[:5]):  # Limit to first 5 for performance
            with st.expander(f"Memory {i+1}: {result.get('id', 'N/A')[:8]}"):
                st.text_area("Content", result.get('memory', ''), height=100, key=f"content_{i}")
                
                metadata = result.get('metadata', {})
                if metadata:
                    st.json(metadata)

def show_stats(user_id: str):
    """Show user statistics."""
    try:
        with st.spinner("Loading stats..."):
            stats = st.session_state.searcher.get_user_stats(user_id)
        
        st.subheader("📊 User Statistics")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Memories", stats['total_memories'])
        with col2:
            st.metric("Recent (7 days)", stats['recent_memories_7d'])
        with col3:
            st.metric("User ID", stats['user_id'])
        
        # Sources chart
        if stats['sources']:
            st.subheader("📋 Sources Breakdown")
            source_df = pd.DataFrame(list(stats['sources'].items()), columns=['Source', 'Count'])
            st.bar_chart(source_df.set_index('Source'))
        
        # Extract modes
        if stats['extract_modes']:
            st.subheader("⚙️ Extract Modes")
            mode_df = pd.DataFrame(list(stats['extract_modes'].items()), columns=['Mode', 'Count'])
            st.bar_chart(mode_df.set_index('Mode'))
        
    except Exception as e:
        st.error(f"❌ Failed to load stats: {str(e)}")

def format_date(date_str: str) -> str:
    """Format date string for display."""
    if not date_str or date_str == 'N/A':
        return 'N/A'
    
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d')
    except:
        return date_str[:10] if len(date_str) >= 10 else date_str

if __name__ == "__main__":
    main() 