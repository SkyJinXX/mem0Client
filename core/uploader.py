"""Upload and memory management with Mem0 API."""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from mem0 import MemoryClient
from rich.console import Console
from rich.progress import Progress, TaskID
from .config import Config
from .parser import FileParser

console = Console()


class MemoryUploader:
    """Handles uploading and managing memories with Mem0."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the uploader with configuration."""
        self.config = config or Config()
        
        # Validate configuration
        if not self.config.validate():
            raise ValueError("Invalid configuration. Please check your API key.")
        
        # Initialize Mem0 client
        os.environ['MEM0_API_KEY'] = self.config.mem0_api_key
        self.client = MemoryClient()
        
        console.print(f"✅ Initialized Mem0 client for user: {self.config.default_user_id}")
    
    def upload_text(self, 
                   content: str, 
                   user_id: Optional[str] = None,
                   extract_mode: str = "auto",
                   metadata: Optional[Dict[str, Any]] = None,
                   custom_instructions: Optional[str] = None,
                   includes: Optional[str] = None,
                   excludes: Optional[str] = None,
                   infer: Optional[bool] = None) -> Dict[str, Any]:
        """
        Upload text content to Mem0.
        
        Args:
            content: Text content to upload
            user_id: User ID for the memory (defaults to config)
            extract_mode: Processing mode ("auto" or "raw")
            metadata: Additional metadata
            custom_instructions: Custom instructions for AI processing
            includes: Content types to specifically include
            excludes: Content types to exclude from processing
            infer: Whether to infer memories (True) or store raw messages (False)
            
        Returns:
            Upload result from Mem0
        """
        user_id = user_id or self.config.default_user_id
        
        # Parse content
        messages, parsed_metadata = FileParser.parse_plain_text(content, extract_mode)
        
        # Merge metadata
        final_metadata = {
            "upload_time": datetime.now().isoformat(),
            "user_id": user_id,
            "extract_mode": extract_mode,
            **parsed_metadata,
            **(metadata or {})
        }
        
        # Add custom processing configuration to metadata for tracking
        if custom_instructions:
            final_metadata["custom_instructions"] = custom_instructions
        if includes:
            final_metadata["includes"] = includes
        if excludes:
            final_metadata["excludes"] = excludes
        if infer is not None:
            final_metadata["infer"] = infer
        
        try:
            # Prepare additional parameters for Mem0 (using v2 API format)
            add_params = {
                "user_id": user_id,
                "version": "v2"
            }
            
            # Add custom processing parameters if available
            if custom_instructions:
                add_params["custom_instructions"] = custom_instructions
            if includes:
                add_params["includes"] = includes
            if excludes:
                add_params["excludes"] = excludes
            if infer is not None:
                add_params["infer"] = infer
            if final_metadata:
                add_params["metadata"] = final_metadata
            
            # Log the parameters being sent to Mem0 (if debug enabled)
            if self.config.debug_logging:
                console.print("\n🔍 [DEBUG] Mem0.add() 调用参数:")
                console.print(f"  📱 user_id: {user_id}")
                
                # Log messages with truncation
                if messages:
                    for i, msg in enumerate(messages[:3]):  # Show first 3 messages
                        if isinstance(msg, dict) and 'content' in msg:
                            content_preview = msg['content'][:20] + "..." if len(msg['content']) > 20 else msg['content']
                            role = msg.get('role', 'unknown')
                            console.print(f"  💬 messages[{i}]: role='{role}', content='{content_preview}'")
                        elif isinstance(msg, str):
                            content_preview = msg[:20] + "..." if len(msg) > 20 else msg
                            console.print(f"  💬 messages[{i}]: '{content_preview}'")
                    if len(messages) > 3:
                        console.print(f"  💬 ... and {len(messages) - 3} more messages")
                
                # Log custom processing parameters
                if custom_instructions:
                    instr_preview = custom_instructions[:50] + "..." if len(custom_instructions) > 50 else custom_instructions
                    console.print(f"  🎯 custom_instructions: '{instr_preview}'")
                if includes:
                    console.print(f"  ✅ includes: '{includes}'")
                if excludes:
                    console.print(f"  ❌ excludes: '{excludes}'")
                if infer is not None:
                    console.print(f"  🧠 infer: {infer}")
                
                # Log metadata (excluding lengthy fields)
                metadata_summary = {}
                for key, value in final_metadata.items():
                    if key in ['upload_time', 'user_id', 'extract_mode', 'file_name', 'file_type']:
                        metadata_summary[key] = value
                    elif isinstance(value, str) and len(value) > 30:
                        metadata_summary[key] = value[:30] + "..."
                    else:
                        metadata_summary[key] = value
                console.print(f"  📋 metadata: {metadata_summary}")
                console.print("")
            
            # Add to Mem0 (messages as first positional argument)
            result = self.client.add(messages, **add_params)
            
            console.print(f"✅ Uploaded text memory for user: {user_id}")
            if custom_instructions or includes or excludes or infer is not None:
                console.print(f"📋 Applied custom processing settings")
            return result
            
        except Exception as e:
            console.print(f"❌ Failed to upload text: {str(e)}")
            raise
    
    def upload_file(self, 
                   file_path: str,
                   user_id: Optional[str] = None,
                   extract_mode: Optional[str] = None,
                   custom_instructions: Optional[str] = None,
                   includes: Optional[str] = None,
                   excludes: Optional[str] = None,
                   infer: Optional[bool] = None) -> Dict[str, Any]:
        """
        Upload a file to Mem0.
        
        Args:
            file_path: Path to the file
            user_id: User ID for the memory (defaults to config)
            extract_mode: Processing mode (defaults to config)
            custom_instructions: Custom instructions for AI processing
            includes: Content types to specifically include
            excludes: Content types to exclude from processing
            infer: Whether to infer memories (True) or store raw messages (False)
            
        Returns:
            Upload result from Mem0
        """
        user_id = user_id or self.config.default_user_id
        extract_mode = extract_mode or self.config.default_extract_mode
        
        # Validate file
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > self.config.max_file_size_mb:
            raise ValueError(f"File too large: {file_size_mb:.1f}MB > {self.config.max_file_size_mb}MB")
        
        # Parse file
        try:
            messages, metadata = FileParser.parse_file(file_path, extract_mode)
        except Exception as e:
            console.print(f"❌ Failed to parse file {file_path}: {str(e)}")
            raise
        
        # Add upload metadata
        metadata.update({
            "upload_time": datetime.now().isoformat(),
            "user_id": user_id,
            "extract_mode": extract_mode
        })
        
        # Add custom processing configuration to metadata for tracking
        if custom_instructions:
            metadata["custom_instructions"] = custom_instructions
        if includes:
            metadata["includes"] = includes
        if excludes:
            metadata["excludes"] = excludes
        if infer is not None:
            metadata["infer"] = infer
        
        try:
            # Prepare additional parameters for Mem0 (using v2 API format)
            add_params = {
                "user_id": user_id,
                "version": "v2"
            }
            
            # Add custom processing parameters if available
            if custom_instructions:
                add_params["custom_instructions"] = custom_instructions
            if includes:
                add_params["includes"] = includes
            if excludes:
                add_params["excludes"] = excludes
            if infer is not None:
                add_params["infer"] = infer
            if metadata:
                add_params["metadata"] = metadata
            
            # Log the parameters being sent to Mem0 (if debug enabled)
            if self.config.debug_logging:
                console.print(f"\n🔍 [DEBUG] Mem0.add() 调用参数 (文件: {os.path.basename(file_path)}):")
                console.print(f"  📱 user_id: {user_id}")
                
                # Log messages with truncation
                if messages:
                    for i, msg in enumerate(messages[:3]):  # Show first 3 messages
                        if isinstance(msg, dict) and 'content' in msg:
                            content_preview = msg['content'][:20] + "..." if len(msg['content']) > 20 else msg['content']
                            role = msg.get('role', 'unknown')
                            console.print(f"  💬 messages[{i}]: role='{role}', content='{content_preview}'")
                        elif isinstance(msg, str):
                            content_preview = msg[:20] + "..." if len(msg) > 20 else msg
                            console.print(f"  💬 messages[{i}]: '{content_preview}'")
                    if len(messages) > 3:
                        console.print(f"  💬 ... and {len(messages) - 3} more messages")
                
                # Log custom processing parameters
                if custom_instructions:
                    instr_preview = custom_instructions[:50] + "..." if len(custom_instructions) > 50 else custom_instructions
                    console.print(f"  🎯 custom_instructions: '{instr_preview}'")
                if includes:
                    console.print(f"  ✅ includes: '{includes}'")
                if excludes:
                    console.print(f"  ❌ excludes: '{excludes}'")
                if infer is not None:
                    console.print(f"  🧠 infer: {infer}")
                
                # Log metadata (excluding lengthy fields)
                metadata_summary = {}
                for key, value in metadata.items():
                    if key in ['upload_time', 'user_id', 'extract_mode', 'file_name', 'file_type']:
                        metadata_summary[key] = value
                    elif isinstance(value, str) and len(value) > 30:
                        metadata_summary[key] = value[:30] + "..."
                    else:
                        metadata_summary[key] = value
                console.print(f"  📋 metadata: {metadata_summary}")
                console.print("")
            
            # Add to Mem0 (messages as first positional argument)
            try:
                result = self.client.add(messages, **add_params)
                
                console.print(f"✅ Uploaded file: {file_path} for user: {user_id}")
                if custom_instructions or includes or excludes or infer is not None:
                    console.print(f"📋 Applied custom processing settings")
                return result
                
            except Exception as api_error:
                raise api_error
            
        except Exception as e:
            console.print(f"❌ Failed to upload file {file_path}: {str(e)}")
            raise
    
    def upload_batch(self, 
                    file_paths: List[str],
                    user_id: Optional[str] = None,
                    extract_mode: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Upload multiple files in batch.
        
        Args:
            file_paths: List of file paths
            user_id: User ID for the memories
            extract_mode: Processing mode
            
        Returns:
            List of upload results
        """
        results = []
        
        with Progress() as progress:
            task = progress.add_task("Uploading files...", total=len(file_paths))
            
            for file_path in file_paths:
                try:
                    result = self.upload_file(file_path, user_id, extract_mode)
                    results.append({"file": file_path, "status": "success", "result": result})
                except Exception as e:
                    results.append({"file": file_path, "status": "error", "error": str(e)})
                
                progress.advance(task)
        
        # Summary
        success_count = sum(1 for r in results if r["status"] == "success")
        error_count = len(results) - success_count
        
        console.print(f"📊 Batch upload complete: {success_count} success, {error_count} errors")
        
        return results
    
    def upload_directory(self, 
                        directory_path: str,
                        user_id: Optional[str] = None,
                        extract_mode: Optional[str] = None,
                        recursive: bool = True) -> List[Dict[str, Any]]:
        """
        Upload all supported files from a directory.
        
        Args:
            directory_path: Path to the directory
            user_id: User ID for the memories
            extract_mode: Processing mode
            recursive: Whether to search subdirectories
            
        Returns:
            List of upload results
        """
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        # Find all supported files
        supported_extensions = self.config.supported_formats
        file_paths = []
        
        if recursive:
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in supported_extensions):
                        file_paths.append(os.path.join(root, file))
        else:
            for file in os.listdir(directory_path):
                file_path = os.path.join(directory_path, file)
                if os.path.isfile(file_path) and any(file.lower().endswith(ext) for ext in supported_extensions):
                    file_paths.append(file_path)
        
        if not file_paths:
            console.print(f"⚠️  No supported files found in {directory_path}")
            return []
        
        console.print(f"📁 Found {len(file_paths)} files to upload")
        return self.upload_batch(file_paths, user_id, extract_mode) 