"""Search and retrieval functionality for Mem0 memories."""

import os
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from mem0 import MemoryClient
from rich.console import Console
from rich.table import Table
from rich.text import Text
from .config import Config

console = Console()


class MemorySearcher:
    """Handles searching and retrieving memories from Mem0."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the searcher with configuration."""
        self.config = config or Config()
        
        # Validate configuration
        if not self.config.validate():
            raise ValueError("Invalid configuration. Please check your API key.")
        
        # Initialize Mem0 client
        os.environ['MEM0_API_KEY'] = self.config.mem0_api_key
        self.client = MemoryClient()
        
        console.print(f"✅ Initialized Mem0 searcher for user: {self.config.default_user_id}")
    
    def search_by_query(self, 
                       query: str,
                       user_id: Optional[str] = None,
                       limit: Optional[int] = None,
                       filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search memories by semantic query.
        
        Args:
            query: Search query string
            user_id: User ID to search (defaults to config)
            limit: Maximum number of results
            filters: Additional filters for the search
            
        Returns:
            List of matching memories
        """
        user_id = user_id or self.config.default_user_id
        limit = limit or self.config.search_default_limit
        
        try:
            # Build filters
            search_filters = {"AND": [{"user_id": user_id}]}
            if filters:
                search_filters["AND"].append(filters)
            
            # Search using Mem0 v2 API
            results = self.client.search(
                query=query,
                version="v2",
                filters=search_filters,
                limit=limit
            )
            
            console.print(f"🔍 Found {len(results)} memories for query: '{query}'")
            return results
            
        except Exception as e:
            console.print(f"❌ Search failed: {str(e)}")
            raise
    
    def search_by_time_range(self,
                            days_back: Optional[int] = None,
                            start_date: Optional[str] = None,
                            end_date: Optional[str] = None,
                            user_id: Optional[str] = None,
                            query: Optional[str] = None,
                            limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search memories within a time range.
        
        Args:
            days_back: Number of days to look back (alternative to start/end dates)
            start_date: Start date in ISO format (YYYY-MM-DD)
            end_date: End date in ISO format (YYYY-MM-DD)
            user_id: User ID to search
            query: Optional search query within the time range
            limit: Maximum number of results
            
        Returns:
            List of matching memories
        """
        user_id = user_id or self.config.default_user_id
        limit = limit or self.config.search_default_limit
        
        # Calculate date range
        if days_back is not None:
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=days_back)
            start_date = start_dt.strftime('%Y-%m-%d')
            end_date = end_dt.strftime('%Y-%m-%d')
        elif start_date is None or end_date is None:
            raise ValueError("Either 'days_back' or both 'start_date' and 'end_date' must be provided")
        
        try:
            # Build time filters
            time_filter = {
                "AND": [
                    {"user_id": user_id},
                    {"created_at": {"gte": start_date, "lte": end_date}}
                ]
            }
            
            if query:
                # Search with query within time range
                results = self.client.search(
                    query=query,
                    version="v2",
                    filters=time_filter,
                    limit=limit
                )
                console.print(f"🔍 Found {len(results)} memories for '{query}' between {start_date} and {end_date}")
            else:
                # Get all memories in time range
                results = self.client.get_all(
                    version="v2",
                    filters=time_filter,
                    limit=limit
                )
                console.print(f"📅 Found {len(results)} memories between {start_date} and {end_date}")
            
            return results
            
        except Exception as e:
            console.print(f"❌ Time range search failed: {str(e)}")
            raise
    
    def search_weekly_report_data(self, 
                                 weeks_back: int = 1,
                                 user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get data for weekly report generation.
        
        Args:
            weeks_back: Number of weeks to look back (1 = last week)
            user_id: User ID to search
            
        Returns:
            Dictionary with week's memories and related memories
        """
        user_id = user_id or self.config.default_user_id
        
        # Calculate week range
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday() + (7 * weeks_back))
        week_end = week_start + timedelta(days=6)
        
        # Get memories from the target week
        week_memories = self.search_by_time_range(
            start_date=week_start.strftime('%Y-%m-%d'),
            end_date=week_end.strftime('%Y-%m-%d'),
            user_id=user_id,
            limit=self.config.search_max_limit
        )
        
        # Find related memories from history
        related_memories = []
        if week_memories:
            # Extract key topics/themes from week memories
            week_content = " ".join([m.get('memory', '') for m in week_memories[:5]])
            
            # Search for related historical memories
            if week_content.strip():
                related_memories = self.search_by_query(
                    query=week_content[:500],  # Limit query length
                    user_id=user_id,
                    limit=20,
                    filters={"created_at": {"lt": week_start.strftime('%Y-%m-%d')}}
                )
        
        console.print(f"📊 Weekly report data: {len(week_memories)} current week, {len(related_memories)} related")
        
        return {
            "week_start": week_start.strftime('%Y-%m-%d'),
            "week_end": week_end.strftime('%Y-%m-%d'),
            "week_memories": week_memories,
            "related_memories": related_memories,
            "summary": {
                "total_current": len(week_memories),
                "total_related": len(related_memories)
            }
        }
    
    def search_related_to_content(self,
                                 content: str,
                                 user_id: Optional[str] = None,
                                 exclude_time_range: Optional[Dict[str, str]] = None,
                                 limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search for memories related to given content.
        
        Args:
            content: Reference content to find related memories
            user_id: User ID to search
            exclude_time_range: Time range to exclude (e.g., current week)
            limit: Maximum number of results
            
        Returns:
            List of related memories
        """
        user_id = user_id or self.config.default_user_id
        limit = limit or self.config.search_default_limit
        
        try:
            # Build filters
            search_filters = {"AND": [{"user_id": user_id}]}
            
            # Add time exclusion if specified
            if exclude_time_range:
                if "start" in exclude_time_range and "end" in exclude_time_range:
                    search_filters["AND"].append({
                        "NOT": [
                            {"created_at": {
                                "gte": exclude_time_range["start"],
                                "lte": exclude_time_range["end"]
                            }}
                        ]
                    })
            
            # Search for related content
            results = self.client.search(
                query=content[:500],  # Limit query length
                version="v2",
                filters=search_filters,
                limit=limit
            )
            
            console.print(f"🔗 Found {len(results)} memories related to the provided content")
            return results
            
        except Exception as e:
            console.print(f"❌ Related content search failed: {str(e)}")
            raise
    
    def display_search_results(self, results: List[Dict[str, Any]], max_content_length: int = 100):
        """
        Display search results in a formatted table.
        
        Args:
            results: List of memory results from search
            max_content_length: Maximum length of content to display
        """
        if not results:
            console.print("📭 No results found")
            return
        
        table = Table(title="🧠 Memory Search Results")
        table.add_column("ID", style="cyan", width=8)
        table.add_column("Content", style="white", width=50)
        table.add_column("Created", style="green", width=12)
        table.add_column("Source", style="yellow", width=15)
        table.add_column("Score", style="magenta", width=8)
        
        for result in results:
            memory_id = result.get('id', 'N/A')[:8]
            content = result.get('memory', '')
            
            # Truncate content if too long
            if len(content) > max_content_length:
                content = content[:max_content_length] + "..."
            
            created_at = result.get('created_at', 'N/A')
            if created_at != 'N/A':
                try:
                    # Parse and format date
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    created_at = dt.strftime('%Y-%m-%d')
                except:
                    created_at = created_at[:10]  # Just take first 10 chars
            
            metadata = result.get('metadata', {})
            source = metadata.get('source', 'unknown')
            
            score = result.get('score', 0)
            score_str = f"{score:.2f}" if isinstance(score, (int, float)) else str(score)
            
            table.add_row(
                memory_id,
                content,
                created_at,
                source,
                score_str
            )
        
        console.print(table)
    
    def get_user_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics about user's memories.
        
        Args:
            user_id: User ID to get stats for
            
        Returns:
            Dictionary with user statistics
        """
        user_id = user_id or self.config.default_user_id
        
        try:
            # Get all memories for the user
            all_memories = self.client.get_all(
                version="v2",
                filters={"user_id": user_id},
                limit=1000  # Large limit to get comprehensive stats
            )
            
            # Calculate stats
            total_memories = len(all_memories)
            
            # Group by source
            sources = {}
            extract_modes = {}
            
            for memory in all_memories:
                metadata = memory.get('metadata', {})
                source = metadata.get('source', 'unknown')
                extract_mode = metadata.get('extract_mode', 'unknown')
                
                sources[source] = sources.get(source, 0) + 1
                extract_modes[extract_mode] = extract_modes.get(extract_mode, 0) + 1
            
            # Recent activity (last 7 days)
            recent_memories = self.search_by_time_range(
                days_back=7,
                user_id=user_id,
                limit=1000
            )
            
            stats = {
                "user_id": user_id,
                "total_memories": total_memories,
                "recent_memories_7d": len(recent_memories),
                "sources": sources,
                "extract_modes": extract_modes,
                "generated_at": datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            console.print(f"❌ Failed to get user stats: {str(e)}")
            raise 