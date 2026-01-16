"""
API Scraper Pro - Dashboard
============================

Professional web interface for managing and monitoring API scraping.
"""

import streamlit as st
import asyncio
import sys
from pathlib import Path
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import DatabaseManager
from utils.helpers import load_yaml_config, save_yaml_config
from dashboard import utils as dash_utils
from dashboard.components import overview, endpoints, analytics, search, config_editor

# Page configuration
st.set_page_config(
    page_title="API Scraper Pro - Control Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1rem;
        border-radius: 5px;
    }
    .info-box {
        background-color: #d1ecf1;
        border-left: 5px solid #17a2b8;
        padding: 1rem;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Session state
if 'scraping_process' not in st.session_state:
    st.session_state.scraping_process = None
if 'config' not in st.session_state:
    st.session_state.config = None


async def get_database_data(config: dict):
    """Fetch data from database."""
    db_config = config.get('database', {})
    async with DatabaseManager(db_config) as db:
        stats = await db.get_stats()
        all_endpoints = await db.get_all_endpoints()
        return stats, all_endpoints


def render_sidebar(config: dict, is_scraping: bool):
    """Render sidebar with controls."""
    with st.sidebar:
        st.header("Control Panel")
        
        tabs = st.tabs(["Run", "Settings", "Status"])
        
        # Run tab
        with tabs[0]:
            _render_run_tab(config, is_scraping)
        
        # Settings tab
        with tabs[1]:
            _render_settings_tab(config)
        
        # Status tab
        with tabs[2]:
            _render_status_tab(is_scraping)
        
        st.markdown("---")
        
        # Quick actions
        _render_quick_actions()


def _render_run_tab(config: dict, is_scraping: bool):
    """Render run tab."""
    st.subheader("Start Scraping")
    
    target_url = st.text_input(
        "Target URL",
        "https://jsonplaceholder.typicode.com",
        key="url_input"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        max_depth = st.number_input(
            "Max Depth",
            1, 10,
            config.get('scraping', {}).get('max_depth', 3)
        )
    with col2:
        headless = st.checkbox(
            "Headless",
            config.get('scraping', {}).get('headless', True)
        )
    
    st.info("Scraping runs in separate console window")
    
    if st.button("Start Scraping", disabled=is_scraping, width="stretch", type="primary"):
        config['scraping']['max_depth'] = max_depth
        config['scraping']['headless'] = headless
        save_yaml_config(config)
        
        process = dash_utils.start_scraping_process(target_url, config, max_depth, headless)
        if process:
            st.session_state.scraping_process = process
            st.success("Scraping started!")
            st.info("Check console window")
            time.sleep(1)
            st.rerun()
    
    if st.button("Stop", disabled=not is_scraping, width="stretch"):
        if st.session_state.scraping_process:
            st.session_state.scraping_process.terminate()
            st.session_state.scraping_process = None
            st.warning("Stopped")
            st.rerun()


def _render_settings_tab(config: dict):
    """Render settings tab."""
    st.subheader("Quick Settings")
    
    with st.expander("⚙ Crawling", expanded=True):
        config['scraping']['timeout'] = st.number_input(
            "Timeout (ms)",
            value=config.get('scraping', {}).get('timeout', 30000)
        )
        config['scraping']['page_delay'] = st.number_input(
            "Page Delay (ms)",
            value=config.get('scraping', {}).get('page_delay', 2000)
        )
    
    with st.expander("🛡 Stealth"):
        config['stealth']['enabled'] = st.checkbox(
            "Enable Stealth",
            value=config.get('stealth', {}).get('enabled', True)
        )
    
    with st.expander("🔒 Compliance"):
        config['compliance']['respect_robots_txt'] = st.checkbox(
            "Respect robots.txt",
            value=config.get('compliance', {}).get('respect_robots_txt', True)
        )
    
    if st.button("💾 Save Settings", width="stretch", type="primary"):
        if save_yaml_config(config):
            st.session_state.config = config
            st.success("Settings saved!")
            st.rerun()


def _render_status_tab(is_scraping: bool):
    """Render status tab."""
    st.subheader("Status")
    
    if is_scraping:
        st.markdown(
            '<div class="success-box"><b>● ACTIVE</b><br>Scraping in progress</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="info-box"><b>○ IDLE</b><br>Ready to start</div>',
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    if st.button("🔄 Refresh Data", width="stretch"):
        st.rerun()


def _render_quick_actions():
    """Render quick action buttons."""
    st.subheader("Quick Actions")
    
    if st.button("🔄 Refresh Dashboard", width="stretch", type="primary"):
        st.rerun()
    
    st.markdown("---")
    st.caption("Export Data:")
    
    if st.button("📥 Export JSON", width="stretch"):
        if dash_utils.export_data("json"):
            st.success("Export started! Check exports/ folder")
    
    if st.button("📄 Export CSV", width="stretch"):
        if dash_utils.export_data("csv"):
            st.success("Export started! Check exports/ folder")
    
    st.markdown("---")
    st.caption("⚠️ Danger Zone:")
    
    if 'confirm_clear' not in st.session_state:
        st.session_state.confirm_clear = False
    
    if not st.session_state.confirm_clear:
        if st.button("🗑️ Clear All Data", width="stretch", help="Delete all endpoints and API calls"):
            st.session_state.confirm_clear = True
            st.rerun()
    else:
        st.warning("⚠️ This will delete ALL data!")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Confirm", width="stretch", type="primary"):
                if dash_utils.clear_database():
                    st.session_state.confirm_clear = False
                    st.success("All data cleared!")
                    time.sleep(1)
                    st.rerun()
        with col2:
            if st.button("❌ Cancel", width="stretch"):
                st.session_state.confirm_clear = False
                st.rerun()


def render_metrics(stats: dict):
    """Render metrics row."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Endpoints", stats['total_endpoints'])
    
    with col2:
        st.metric("API Calls", stats['total_calls'])
    
    with col3:
        st.metric("Database Size", f"{stats['database_size_mb']} MB")
    
    with col4:
        avg = (stats['total_calls'] / stats['total_endpoints']) if stats['total_endpoints'] > 0 else 0
        st.metric("Avg Calls", f"{avg:.1f}")


def main():
    """Main application."""
    # Header
    st.markdown(
        '<h1 class="main-header">API Scraper Pro - Control Center</h1>',
        unsafe_allow_html=True
    )
    st.markdown("---")
    
    # Load configuration
    if st.session_state.config is None:
        st.session_state.config = load_yaml_config()
    
    config = st.session_state.config
    
    # Check process status
    if st.session_state.scraping_process is not None:
        if st.session_state.scraping_process.poll() is not None:
            st.session_state.scraping_process = None
    
    is_scraping = st.session_state.scraping_process is not None
    
    # Sidebar
    render_sidebar(config, is_scraping)
    
    # Main content
    try:
        stats, all_endpoints = asyncio.run(get_database_data(config))
    except Exception as e:
        st.error(f"❌ Database Error: {e}")
        st.info("💡 Run scraping first to see data")
        
        with st.expander("📖 Getting Started"):
            st.code("""
# Option 1: Use Dashboard
Click 'Start Scraping' in the sidebar

# Option 2: Use CLI
python main.py scrape https://jsonplaceholder.typicode.com
            """)
        return
    
    # Metrics
    render_metrics(stats)
    st.markdown("---")
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Overview",
        "Endpoints",
        "Analytics",
        "Search",
        "Configuration"
    ])
    
    with tab1:
        overview.render(stats, all_endpoints)
    
    with tab2:
        endpoints.render(all_endpoints)
    
    with tab3:
        analytics.render(all_endpoints)
    
    with tab4:
        search.render(all_endpoints)
    
    with tab5:
        config_editor.render(config)


if __name__ == "__main__":
    main()
