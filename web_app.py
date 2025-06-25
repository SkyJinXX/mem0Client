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
from core.web_helpers import (
    perform_search, perform_time_search, generate_weekly_report,
    display_search_results, show_stats, create_advanced_settings_ui,
    create_metadata_ui, process_exclude_presets
)

# Page configuration
st.set_page_config(
    page_title="Mem0 Client",
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

# Load persistent advanced settings from config
if 'advanced_settings_loaded' not in st.session_state:
    # Load from config file first time
    st.session_state.advanced_settings = {
        'custom_instructions': st.session_state.config.advanced_custom_instructions,
        'includes': st.session_state.config.advanced_includes,
        'excludes': st.session_state.config.advanced_excludes,
        'exclude_presets': st.session_state.config.advanced_exclude_presets,
        'infer': st.session_state.config.advanced_infer,
    }
    st.session_state.advanced_settings_loaded = True

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
        
        st.divider()
        
        # Advanced Settings in sidebar
        st.subheader("🎯 Advanced Settings")
        
        # Custom Instructions
        custom_instructions = st.text_area(
            "Custom Instructions",
            value=st.session_state.advanced_settings['custom_instructions'],
            placeholder="Guide AI on how to process and extract memories...",
            help="Custom instructions for AI processing",
            height=80,
            key="sidebar_custom_instructions"
        )
        
        # Includes and Excludes in columns
        col1, col2 = st.columns(2)
        with col1:
            includes = st.text_input(
                "Includes",
                value=st.session_state.advanced_settings['includes'],
                placeholder="tech docs, APIs",
                help="Content types to include",
                key="sidebar_includes"
            )
        
        with col2:
            excludes = st.text_input(
                "Excludes",
                value=st.session_state.advanced_settings['excludes'],
                placeholder="personal info",
                help="Content types to exclude",
                key="sidebar_excludes"
            )
        
        # Exclude presets
        exclude_presets = st.multiselect(
            "Privacy Presets",
            ["Personal Names", "Contact Info", "Address", "Financial", "Passwords", "ID Numbers", "Sensitive Info"],
            default=st.session_state.advanced_settings['exclude_presets'],
            help="Common exclusion presets",
            key="sidebar_exclude_presets"
        )
        
        # Infer setting
        infer = st.checkbox(
            "Infer Memories",
            value=st.session_state.advanced_settings['infer'],
            help="AI intelligent processing vs raw storage",
            key="sidebar_infer"
        )
        
        # Save settings button
        if st.button("💾 Save Settings", type="secondary"):
            # Update session state
            st.session_state.advanced_settings.update({
                'custom_instructions': custom_instructions,
                'includes': includes,
                'excludes': excludes,
                'exclude_presets': exclude_presets,
                'infer': infer
            })
            
            # Save to config file
            st.session_state.config.update_advanced_settings(
                custom_instructions=custom_instructions,
                includes=includes,
                excludes=excludes,
                exclude_presets=exclude_presets,
                infer=infer
            )
            
            st.success("✅ Settings saved!")
        
        st.divider()
        
        # Quick stats
        if st.button("📊 Show Stats"):
            show_stats(st.session_state.searcher, user_id)
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload", "🔍 Search", "📅 Time Search", "📊 Weekly Report"])
    
    with tab1:
        upload_interface(user_id)
    
    with tab2:
        search_interface(user_id)
    
    with tab3:
        time_search_interface(user_id)
    
    with tab4:
        weekly_report_interface(user_id)

def upload_interface(user_id: str):
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
        
        # Metadata input
        metadata = create_metadata_ui()
        
        if st.button("📤 Upload Text", type="primary"):
            if text_content.strip():
                # Get settings from sidebar
                final_excludes = process_exclude_presets(
                    st.session_state.advanced_settings['excludes'], 
                    st.session_state.advanced_settings['exclude_presets']
                )
                
                try:
                    with st.spinner("Uploading..."):
                        result = st.session_state.uploader.upload_text(
                            content=text_content,
                            user_id=user_id,
                            extract_mode="auto",  # Always use auto mode
                            metadata=metadata,
                            custom_instructions=st.session_state.advanced_settings['custom_instructions'].strip() or None,
                            includes=st.session_state.advanced_settings['includes'].strip() or None,
                            excludes=final_excludes.strip() or None,
                            infer=st.session_state.advanced_settings['infer']
                        )
                    st.success("✅ Text uploaded successfully!")
                    
                    # Show applied settings if any are configured
                    applied_settings = []
                    if st.session_state.advanced_settings['custom_instructions'].strip():
                        applied_settings.append(f"**Custom Instructions:** {st.session_state.advanced_settings['custom_instructions'].strip()}")
                    if st.session_state.advanced_settings['includes'].strip():
                        applied_settings.append(f"**Includes:** {st.session_state.advanced_settings['includes'].strip()}")
                    if final_excludes.strip():
                        applied_settings.append(f"**Excludes:** {final_excludes.strip()}")
                    applied_settings.append(f"**Infer Memories:** {st.session_state.advanced_settings['infer']}")
                    
                    if applied_settings:
                        with st.expander("📋 Applied Settings"):
                            for setting in applied_settings:
                                st.write(setting)
                    
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
            
            if st.button("📤 Upload File", type="primary"):
                try:
                    # Get settings from sidebar
                    final_excludes = process_exclude_presets(
                        st.session_state.advanced_settings['excludes'], 
                        st.session_state.advanced_settings['exclude_presets']
                    )
                    
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
                            extract_mode="auto",  # Always use auto mode
                            custom_instructions=st.session_state.advanced_settings['custom_instructions'].strip() or None,
                            includes=st.session_state.advanced_settings['includes'].strip() or None,
                            excludes=final_excludes.strip() or None,
                            infer=st.session_state.advanced_settings['infer']
                        )
                    
                    # Clean up temp file
                    os.unlink(tmp_path)
                    
                    st.success(f"✅ File '{uploaded_file.name}' uploaded successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Upload failed: {str(e)}")
    
    else:
        # Batch Files upload
        st.subheader("📂 Batch Files Upload")
        
        uploaded_files = st.file_uploader(
            "Choose multiple files",
            type=['md', 'txt', 'markdown', 'json'],
            accept_multiple_files=True,
            help="Upload multiple files at once. Supported formats: .md, .txt, .markdown, .json"
        )
        
        if uploaded_files:
            st.info(f"📄 Selected {len(uploaded_files)} files")
            
            # Show file list
            with st.expander("📋 File List", expanded=True):
                for i, file in enumerate(uploaded_files, 1):
                    st.write(f"{i}. {file.name} ({file.size} bytes)")
            
            # Processing options
            col1, col2 = st.columns(2)
            with col1:
                concurrent_upload = st.checkbox(
                    "Concurrent Upload",
                    value=st.session_state.config.concurrent_upload,
                    help="Process files concurrently for faster upload"
                )
            
            with col2:
                if concurrent_upload:
                    max_workers = st.slider(
                        "Max Concurrent Files",
                        min_value=1,
                        max_value=5,
                        value=st.session_state.config.max_concurrent_files,
                        help="Maximum number of files to process simultaneously"
                    )
                else:
                    max_workers = 1
                    st.write("Sequential processing (safer)")
            
            if st.button("📤 Upload All Files", type="primary"):
                try:
                    # Get settings from sidebar
                    final_excludes = process_exclude_presets(
                        st.session_state.advanced_settings['excludes'], 
                        st.session_state.advanced_settings['exclude_presets']
                    )
                    
                    # Save all files temporarily
                    import tempfile
                    import os
                    
                    temp_files = []
                    for uploaded_file in uploaded_files:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            temp_files.append(tmp_file.name)
                    
                    try:
                        with st.spinner(f"Uploading {len(temp_files)} files..."):
                            # Create a placeholder for results
                            results_placeholder = st.empty()
                            
                            # Use the enhanced batch upload function
                            results = st.session_state.uploader.upload_batch(
                                file_paths=temp_files,
                                user_id=user_id,
                                extract_mode="auto",
                                custom_instructions=st.session_state.advanced_settings['custom_instructions'].strip() or None,
                                includes=st.session_state.advanced_settings['includes'].strip() or None,
                                excludes=final_excludes.strip() or None,
                                infer=st.session_state.advanced_settings['infer'],
                                concurrent_upload=concurrent_upload
                            )
                        
                        # Display results
                        success_count = sum(1 for r in results if r["status"] == "success")
                        error_count = len(results) - success_count
                        
                        if success_count > 0:
                            st.success(f"✅ Successfully uploaded {success_count}/{len(uploaded_files)} files!")
                        
                        if error_count > 0:
                            st.error(f"❌ {error_count} files failed to upload")
                        
                        # Detailed results
                        with st.expander("📊 Detailed Results", expanded=error_count > 0):
                            for i, result in enumerate(results):
                                original_filename = uploaded_files[i].name
                                if result["status"] == "success":
                                    attempts = result.get("attempts", 1)
                                    attempt_text = f" (took {attempts} attempts)" if attempts > 1 else ""
                                    st.write(f"✅ {original_filename}{attempt_text}")
                                else:
                                    st.write(f"❌ {original_filename}: {result['error']}")
                    
                    finally:
                        # Clean up temp files
                        for temp_file in temp_files:
                            try:
                                os.unlink(temp_file)
                            except:
                                pass  # Ignore cleanup errors
                    
                except Exception as e:
                    st.error(f"❌ Batch upload failed: {str(e)}")
        
        else:
            st.info("👆 Select multiple files to upload them in batch")

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
                perform_search(st.session_state.searcher, query, user_id)
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
            perform_time_search(st.session_state.searcher, user_id=user_id, days_back=days_back, query=query or None)
    
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
                st.session_state.searcher,
                user_id=user_id,
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                query=query or None
            )

def weekly_report_interface(user_id: str):
    """Weekly report interface."""
    st.header("📊 Weekly Report")
    
    col1, col2 = st.columns(2)
    
    with col1:
        weeks_back = st.number_input("Weeks Back", min_value=1, max_value=10, value=1)
    
    with col2:
        if st.button("📊 Generate Report", type="primary"):
            generate_weekly_report(st.session_state.searcher, weeks_back, user_id)

# Functions moved to core/web_helpers.py

if __name__ == "__main__":
    main() 