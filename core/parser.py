"""File parsing utilities for different content types."""

import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime


class FileParser:
    """Parser for different file types and content formats."""
    
    @staticmethod
    def parse_json_chat(content: str) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
        """
        Parse JSON chat log into messages format.
        
        Expected format:
        {
            "id": "...",
            "title": "...", 
            "messages": [
                {
                    "id": "...",
                    "role": "user|assistant|system",
                    "content": "...",
                    "timestamp": 1234567890
                }
            ]
        }
        
        Args:
            content: Raw JSON content
            
        Returns:
            Tuple of (messages_list, metadata)
        """
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
        
        messages = []
        metadata = {
            "source": "json_chat",
            "format": "json_conversation",
            "parsed_at": datetime.now().isoformat()
        }
        
        # Extract conversation metadata
        if "title" in data:
            metadata["conversation_title"] = data["title"]
        if "id" in data:
            metadata["conversation_id"] = data["id"]
        if "created" in data:
            try:
                # Convert timestamp to datetime
                created_time = datetime.fromtimestamp(data["created"] / 1000)  # Assuming milliseconds
                metadata["conversation_created"] = created_time.isoformat()
            except (ValueError, TypeError):
                metadata["conversation_created"] = str(data["created"])
        if "updated" in data:
            try:
                updated_time = datetime.fromtimestamp(data["updated"] / 1000)  # Assuming milliseconds
                metadata["conversation_updated"] = updated_time.isoformat()
            except (ValueError, TypeError):
                metadata["conversation_updated"] = str(data["updated"])
        
        # Parse messages
        if "messages" in data and isinstance(data["messages"], list):
            for msg in data["messages"]:
                if not isinstance(msg, dict):
                    continue
                
                # Extract role and content
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                # Skip empty messages
                if not content or not content.strip():
                    continue
                
                # Normalize role
                normalized_role = FileParser._normalize_role(role)
                
                # Skip assistant messages entirely - only keep user messages
                # if normalized_role == "assistant":
                #     continue
                
                # Handle long messages and problematic formatting
                original_content = content.strip()
                
                # Since we only process user messages now, no special cleaning needed
                cleaned_content = original_content
                
                # Handle length after cleaning
                final_content = cleaned_content

                # Build message - only include role and content for API compatibility
                parsed_msg = {
                    "role": normalized_role,
                    "content": final_content
                }
                
                messages.append(parsed_msg)
            
            metadata["message_count"] = len(messages)
            
            # Add conversation stats
            role_counts = {}
            truncated_count = 0
            for msg in messages:
                role = msg["role"]
                role_counts[role] = role_counts.get(role, 0) + 1
                if "[消息已截断" in msg["content"]:
                    truncated_count += 1
            
            metadata["role_distribution"] = role_counts
        
        else:
            raise ValueError("JSON must contain a 'messages' array")
        
        if not messages:
            raise ValueError("No valid messages found in JSON")
        
        return messages, metadata
    
    @staticmethod
    def parse_markdown_chat(content: str) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
        """
        Parse markdown chat log into messages format.
        
        Args:
            content: Raw markdown content
            
        Returns:
            Tuple of (messages_list, metadata)
        """
        messages = []
        metadata = {
            "source": "markdown_chat",
            "format": "conversation",
            "parsed_at": datetime.now().isoformat()
        }
        
        # Common patterns for chat logs
        patterns = [
            # Pattern: **User:** or **Assistant:**
            r'\*\*([^*]+):\*\*\s*(.*?)(?=\*\*[^*]+:\*\*|$)',
            # Pattern: ## User or ## Assistant
            r'^##\s+([^#\n]+)\n(.*?)(?=^##\s+|$)',
            # Pattern: User: or Assistant:
            r'^([^:\n]+):\s*(.*?)(?=^[^:\n]+:|$)',
            # Pattern: [User] or [Assistant]
            r'\[([^\]]+)\]\s*(.*?)(?=\[[^\]]+\]|$)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            if matches:
                for role_raw, message_content in matches:
                    role = FileParser._normalize_role(role_raw.strip())
                    content_clean = message_content.strip()
                    if content_clean:
                        messages.append({
                            "role": role,
                            "content": content_clean
                        })
                break
        
        # If no pattern matches, treat as single message
        if not messages:
            messages.append({
                "role": "user",
                "content": content.strip()
            })
            metadata["format"] = "single_message"
        
        return messages, metadata
    
    @staticmethod
    def _normalize_role(role: str) -> str:
        """Normalize role names to standard format."""
        role_lower = role.lower().strip()
        
        # User aliases
        if any(alias in role_lower for alias in ['user', 'human', 'you', 'me', '用户', '我']):
            return "user"
        
        # Assistant aliases  
        if any(alias in role_lower for alias in ['assistant', 'ai', 'bot', 'gpt', 'claude', 'chatgpt', '助手', '机器人']):
            return "assistant"
        
        # System aliases
        if any(alias in role_lower for alias in ['system', 'sys', '系统']):
            return "system"
            
        # Default to user if unclear
        return "user"
    
    @staticmethod
    def parse_plain_text(content: str, extract_mode: str = "auto") -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
        """
        Parse plain text content.
        
        Args:
            content: Raw text content
            extract_mode: "auto" for AI processing, "raw" for original content
            
        Returns:
            Tuple of (messages_list, metadata)
        """
        metadata = {
            "source": "plain_text",
            "extract_mode": extract_mode,
            "parsed_at": datetime.now().isoformat()
        }
        
        if extract_mode == "raw":
            # Store as-is without AI processing
            messages = [{"role": "user", "content": content.strip()}]
            metadata["format"] = "raw_content"
        else:
            # Let Mem0 AI process and extract
            messages = [{"role": "user", "content": content.strip()}]
            metadata["format"] = "ai_extract"
        
        return messages, metadata
    
    @staticmethod
    def read_file(file_path: str, encoding: str = 'utf-8') -> str:
        """
        Read file content with proper encoding handling.
        
        Args:
            file_path: Path to the file
            encoding: File encoding (default: utf-8)
            
        Returns:
            File content as string
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Try different encodings if utf-8 fails
        encodings = [encoding, 'utf-8', 'gbk', 'gb2312', 'latin1']
        
        for enc in encodings:
            try:
                return path.read_text(encoding=enc)
            except UnicodeDecodeError:
                continue
        
        raise ValueError(f"Unable to decode file {file_path} with any supported encoding")
    
    @staticmethod
    def detect_content_type(content: str, file_extension: str = "") -> str:
        """
        Detect if content looks like a JSON chat, markdown chat, or plain text.
        
        Args:
            content: Text content to analyze
            file_extension: File extension for additional context
            
        Returns:
            Content type: "json_chat", "markdown_chat", or "plain_text"
        """
        # Check if it's JSON first
        if file_extension.lower() == ".json" or content.strip().startswith('{'):
            try:
                data = json.loads(content)
                # Check if it has the conversation structure
                if isinstance(data, dict) and "messages" in data:
                    return "json_chat"
            except json.JSONDecodeError:
                pass
        
        # Look for conversation patterns in markdown/text
        chat_indicators = [
            r'\*\*[^*]+:\*\*',  # **User:** pattern
            r'^##\s+[^#\n]+',   # ## User pattern
            r'^[^:\n]+:\s',     # User: pattern
            r'\[[^\]]+\]',      # [User] pattern
            r'(user|assistant|human|ai|bot|gpt|claude)[\s:：]',  # Role words
        ]
        
        for pattern in chat_indicators:
            if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                return "markdown_chat"
        
        return "plain_text"
    
    @staticmethod
    def parse_file(file_path: str, extract_mode: str = "auto") -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
        """
        Parse any supported file type.
        
        Args:
            file_path: Path to the file
            extract_mode: Processing mode for the content
            
        Returns:
            Tuple of (messages_list, metadata)
        """
        content = FileParser.read_file(file_path)
        
        # Add file metadata
        path = Path(file_path)
        base_metadata = {
            "file_name": path.name,
            "file_path": str(path.absolute()),
            "file_size": path.stat().st_size,
            "file_modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat()
        }
        
        # Detect content type
        content_type = FileParser.detect_content_type(content, path.suffix)
        
        # Special handling: treat .md files as plain text unless they contain simple conversation patterns
        if path.suffix.lower() == ".md":
            # Check if this is a complex markdown document (like exported conversation)
            # If it contains export metadata or is very long, treat as plain text
            if ("Made with Echoes" in content or 
                "This conversation was exported" in content or 
                len(content) > 3000 or
                content.count('\n') > 50):
                content_type = "plain_text"
        
        if content_type == "json_chat":
            messages, metadata = FileParser.parse_json_chat(content)
        elif content_type == "markdown_chat":
            messages, metadata = FileParser.parse_markdown_chat(content)
        else:
            messages, metadata = FileParser.parse_plain_text(content, extract_mode)
        
        # Merge metadata
        metadata.update(base_metadata)
        
        return messages, metadata 