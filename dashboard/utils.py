"""
Dashboard Utilities
===================

Helper functions for dashboard operations.
"""

import subprocess
import sys
import os
import streamlit as st


def run_cli_command(command: list, show_window: bool = True):
    """
    Run CLI command in subprocess.
    
    Args:
        command: Command as list [python, main.py, ...]
        show_window: Show console window on Windows
    """
    try:
        if os.name == 'nt' and show_window:
            # Windows - show console window
            subprocess.Popen(
                command,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                cwd=os.getcwd()
            )
        else:
            # Unix or background
            subprocess.Popen(command, cwd=os.getcwd())
        return True
    except Exception as e:
        st.error(f"Command failed: {e}")
        return False


def start_scraping_process(url: str, config: dict, depth: int, headless: bool):
    """
    Start scraping in new process.
    
    Args:
        url: Target URL
        config: Configuration dict
        depth: Max crawl depth
        headless: Run headless browser
        
    Returns:
        Process object or None
    """
    cmd = [sys.executable, "main.py", "scrape", url, "--depth", str(depth)]
    
    if not headless:
        cmd.append("--no-headless")
    
    try:
        if os.name == 'nt':
            process = subprocess.Popen(
                cmd,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                cwd=os.getcwd()
            )
        else:
            process = subprocess.Popen(cmd, cwd=os.getcwd())
        return process
    except Exception as e:
        st.error(f"Failed to start scraping: {e}")
        return None


def export_data(format: str = "json"):
    """
    Export data to file.
    
    Args:
        format: Export format (json or csv)
    """
    output_file = f"exports/export.{format}"
    cmd = [sys.executable, "main.py", "export", "--format", format, "--output", output_file]
    return run_cli_command(cmd, show_window=True)


def clear_database():
    """
    Clear all data from database.
    
    Returns:
        True if successful
    """
    import asyncio
    sys.path.insert(0, str(os.path.dirname(os.path.dirname(__file__))))
    from core.database import DatabaseManager
    from utils.helpers import load_yaml_config
    
    try:
        config = load_yaml_config()
        db_config = config.get('database', {})
        
        async def _clear():
            async with DatabaseManager(db_config) as db:
                return await db.clear_all_data()
        
        result = asyncio.run(_clear())
        return result
    except Exception as e:
        st.error(f"Failed to clear database: {e}")
        return False
