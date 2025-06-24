#!/usr/bin/env python3
"""
Mem0 Client CLI Tool
A command-line interface for uploading and searching memories with Mem0.
"""

import click
import json
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from core.config import Config
from core.uploader import MemoryUploader
from core.searcher import MemorySearcher

console = Console()

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """🧠 Mem0 Client - Upload and search your memories"""
    pass

@cli.command()
@click.argument('content', type=str)
@click.option('--user-id', '-u', help='User ID for the memory')
@click.option('--extract-mode', '-m', type=click.Choice(['auto', 'raw']), default='auto',
              help='Processing mode: auto (AI processing) or raw (original content)')
@click.option('--metadata', help='Additional metadata as JSON string')
@click.option('--custom-instructions', '--ci', help='Custom instructions for AI processing')
@click.option('--includes', '--inc', help='Content types to specifically include (comma-separated)')
@click.option('--excludes', '--exc', help='Content types to exclude from processing (comma-separated)')
@click.option('--infer/--no-infer', default=None, help='Whether to infer memories (True) or store raw messages (False)')
def upload_text(content: str, user_id: Optional[str], extract_mode: str, metadata: Optional[str],
               custom_instructions: Optional[str], includes: Optional[str], excludes: Optional[str],
               infer: Optional[bool]):
    """Upload text content to Mem0."""
    try:
        config = Config()
        uploader = MemoryUploader(config)
        
        # Parse metadata if provided
        meta_dict = None
        if metadata:
            try:
                meta_dict = json.loads(metadata)
            except json.JSONDecodeError:
                console.print("❌ Invalid JSON format for metadata")
                return
        
        result = uploader.upload_text(
            content=content,
            user_id=user_id,
            extract_mode=extract_mode,
            metadata=meta_dict,
            custom_instructions=custom_instructions,
            includes=includes,
            excludes=excludes,
            infer=infer
        )
        
        console.print(Panel(f"✅ Successfully uploaded text memory", title="Upload Complete"))
        
        # Show applied custom settings
        if custom_instructions or includes or excludes or infer is not None:
            console.print("\n📋 Applied Custom Settings:")
            if custom_instructions:
                console.print(f"  🎯 Custom Instructions: {custom_instructions}")
            if includes:
                console.print(f"  ✅ Includes: {includes}")
            if excludes:
                console.print(f"  ❌ Excludes: {excludes}")
            if infer is not None:
                console.print(f"  🧠 Infer: {infer}")
        
    except Exception as e:
        console.print(f"❌ Upload failed: {str(e)}")

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--user-id', '-u', help='User ID for the memory')
@click.option('--extract-mode', '-m', type=click.Choice(['auto', 'raw']),
              help='Processing mode: auto (AI processing) or raw (original content)')
@click.option('--custom-instructions', '--ci', help='Custom instructions for AI processing')
@click.option('--includes', '--inc', help='Content types to specifically include (comma-separated)')
@click.option('--excludes', '--exc', help='Content types to exclude from processing (comma-separated)')
@click.option('--infer/--no-infer', default=None, help='Whether to infer memories (True) or store raw messages (False)')
def upload_file(file_path: str, user_id: Optional[str], extract_mode: Optional[str],
               custom_instructions: Optional[str], includes: Optional[str], excludes: Optional[str],
               infer: Optional[bool]):
    """Upload a single file to Mem0."""
    try:
        config = Config()
        uploader = MemoryUploader(config)
        
        result = uploader.upload_file(
            file_path=file_path,
            user_id=user_id,
            extract_mode=extract_mode,
            custom_instructions=custom_instructions,
            includes=includes,
            excludes=excludes,
            infer=infer
        )
        
        console.print(Panel(f"✅ Successfully uploaded file: {file_path}", title="Upload Complete"))
        
        # Show applied custom settings
        if custom_instructions or includes or excludes or infer is not None:
            console.print("\n📋 Applied Custom Settings:")
            if custom_instructions:
                console.print(f"  🎯 Custom Instructions: {custom_instructions}")
            if includes:
                console.print(f"  ✅ Includes: {includes}")
            if excludes:
                console.print(f"  ❌ Excludes: {excludes}")
            if infer is not None:
                console.print(f"  🧠 Infer: {infer}")
        
    except Exception as e:
        console.print(f"❌ Upload failed: {str(e)}")

@cli.command()
@click.argument('directory_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--user-id', '-u', help='User ID for the memories')
@click.option('--extract-mode', '-m', type=click.Choice(['auto', 'raw']),
              help='Processing mode: auto (AI processing) or raw (original content)')
@click.option('--recursive/--no-recursive', default=True, help='Search subdirectories recursively')
def upload_directory(directory_path: str, user_id: Optional[str], extract_mode: Optional[str], recursive: bool):
    """Upload all supported files from a directory."""
    try:
        config = Config()
        uploader = MemoryUploader(config)
        
        results = uploader.upload_directory(
            directory_path=directory_path,
            user_id=user_id,
            extract_mode=extract_mode,
            recursive=recursive
        )
        
        # Show summary
        success_count = sum(1 for r in results if r["status"] == "success")
        error_count = len(results) - success_count
        
        if results:
            console.print(Panel(
                f"📊 Upload Summary:\n"
                f"✅ Successful: {success_count}\n"
                f"❌ Failed: {error_count}\n"
                f"📁 Total files: {len(results)}",
                title="Batch Upload Complete"
            ))
            
            # Show errors if any
            if error_count > 0:
                console.print("\n🚨 Errors:")
                for result in results:
                    if result["status"] == "error":
                        console.print(f"  ❌ {result['file']}: {result['error']}")
        else:
            console.print("📭 No supported files found in the directory")
        
    except Exception as e:
        console.print(f"❌ Batch upload failed: {str(e)}")

@cli.command()
@click.argument('query', type=str)
@click.option('--user-id', '-u', help='User ID to search')
@click.option('--limit', '-l', type=int, help='Maximum number of results')
@click.option('--show-full', is_flag=True, help='Show full content instead of truncated')
def search(query: str, user_id: Optional[str], limit: Optional[int], show_full: bool):
    """Search memories by query."""
    try:
        config = Config()
        searcher = MemorySearcher(config)
        
        results = searcher.search_by_query(
            query=query,
            user_id=user_id,
            limit=limit
        )
        
        # Display results
        max_length = None if show_full else 100
        searcher.display_search_results(results, max_content_length=max_length)
        
    except Exception as e:
        console.print(f"❌ Search failed: {str(e)}")

@cli.command()
@click.option('--days', '-d', type=int, help='Number of days to look back')
@click.option('--start-date', help='Start date (YYYY-MM-DD)')
@click.option('--end-date', help='End date (YYYY-MM-DD)')
@click.option('--query', '-q', help='Optional search query within time range')
@click.option('--user-id', '-u', help='User ID to search')
@click.option('--limit', '-l', type=int, help='Maximum number of results')
@click.option('--show-full', is_flag=True, help='Show full content instead of truncated')
def search_time(days: Optional[int], start_date: Optional[str], end_date: Optional[str], 
               query: Optional[str], user_id: Optional[str], limit: Optional[int], show_full: bool):
    """Search memories within a time range."""
    try:
        config = Config()
        searcher = MemorySearcher(config)
        
        results = searcher.search_by_time_range(
            days_back=days,
            start_date=start_date,
            end_date=end_date,
            query=query,
            user_id=user_id,
            limit=limit
        )
        
        # Display results
        max_length = None if show_full else 100
        searcher.display_search_results(results, max_content_length=max_length)
        
    except Exception as e:
        console.print(f"❌ Time range search failed: {str(e)}")

@cli.command()
@click.option('--weeks-back', '-w', type=int, default=1, help='Number of weeks to look back (default: 1)')
@click.option('--user-id', '-u', help='User ID to search')
@click.option('--output', '-o', type=click.Path(), help='Save report data to JSON file')
def weekly_report(weeks_back: int, user_id: Optional[str], output: Optional[str]):
    """Generate data for weekly report."""
    try:
        config = Config()
        searcher = MemorySearcher(config)
        
        report_data = searcher.search_weekly_report_data(
            weeks_back=weeks_back,
            user_id=user_id
        )
        
        # Display summary
        console.print(Panel(
            f"📅 Week: {report_data['week_start']} to {report_data['week_end']}\n"
            f"📝 Current week memories: {report_data['summary']['total_current']}\n"
            f"🔗 Related historical memories: {report_data['summary']['total_related']}",
            title=f"Weekly Report Data (Week {weeks_back} ago)"
        ))
        
        # Show current week memories
        if report_data['week_memories']:
            console.print("\n📅 Current Week Memories:")
            searcher.display_search_results(report_data['week_memories'][:10])
        
        # Show related memories
        if report_data['related_memories']:
            console.print("\n🔗 Related Historical Memories:")
            searcher.display_search_results(report_data['related_memories'][:5])
        
        # Save to file if requested
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            console.print(f"\n💾 Report data saved to: {output}")
        
    except Exception as e:
        console.print(f"❌ Weekly report generation failed: {str(e)}")

@cli.command()
@click.argument('content', type=str)
@click.option('--user-id', '-u', help='User ID to search')
@click.option('--limit', '-l', type=int, help='Maximum number of results')
@click.option('--exclude-days', type=int, help='Exclude recent days from results')
def search_related(content: str, user_id: Optional[str], limit: Optional[int], exclude_days: Optional[int]):
    """Search for memories related to given content."""
    try:
        config = Config()
        searcher = MemorySearcher(config)
        
        # Build exclusion filter if specified
        exclude_range = None
        if exclude_days:
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=exclude_days)
            exclude_range = {
                "start": start_date.strftime('%Y-%m-%d'),
                "end": end_date.strftime('%Y-%m-%d')
            }
        
        results = searcher.search_related_to_content(
            content=content,
            user_id=user_id,
            exclude_time_range=exclude_range,
            limit=limit
        )
        
        # Display results
        searcher.display_search_results(results)
        
    except Exception as e:
        console.print(f"❌ Related content search failed: {str(e)}")

@cli.command()
@click.option('--user-id', '-u', help='User ID to get stats for')
def stats(user_id: Optional[str]):
    """Show user memory statistics."""
    try:
        config = Config()
        searcher = MemorySearcher(config)
        
        stats_data = searcher.get_user_stats(user_id)
        
        # Create stats table
        table = Table(title="📊 Memory Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("User ID", stats_data["user_id"])
        table.add_row("Total Memories", str(stats_data["total_memories"]))
        table.add_row("Recent (7 days)", str(stats_data["recent_memories_7d"]))
        
        console.print(table)
        
        # Sources breakdown
        if stats_data["sources"]:
            console.print("\n📋 Sources:")
            for source, count in stats_data["sources"].items():
                console.print(f"  • {source}: {count}")
        
        # Extract modes breakdown
        if stats_data["extract_modes"]:
            console.print("\n⚙️  Extract Modes:")
            for mode, count in stats_data["extract_modes"].items():
                console.print(f"  • {mode}: {count}")
        
    except Exception as e:
        console.print(f"❌ Stats retrieval failed: {str(e)}")

@cli.command()
def config_check():
    """Check configuration and API connectivity."""
    try:
        config = Config()
        
        console.print("🔧 Configuration Check:")
        console.print(f"  • API Key: {'✅ Set' if config.mem0_api_key else '❌ Missing'}")
        console.print(f"  • Default User ID: {config.default_user_id}")
        console.print(f"  • Extract Mode: {config.default_extract_mode}")
        console.print(f"  • Supported Formats: {', '.join(config.supported_formats)}")
        
        # Test API connectivity
        if config.mem0_api_key:
            from core.uploader import MemoryUploader
            uploader = MemoryUploader(config)
            console.print("  • API Connection: ✅ Connected")
        else:
            console.print("  • API Connection: ❌ No API key")
            console.print("\n💡 Please set MEM0_API_KEY environment variable")
        
    except Exception as e:
        console.print(f"❌ Configuration check failed: {str(e)}")

if __name__ == '__main__':
    cli() 