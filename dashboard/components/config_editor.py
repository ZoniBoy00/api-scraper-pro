"""
Configuration Component
=======================

Configuration editor interface.
"""

import streamlit as st
from utils.helpers import save_yaml_config, load_yaml_config


def render(config: dict):
    """Render configuration editor."""
    st.header("Configuration Editor")
    st.warning("Advanced settings - modify with caution")
    
    tabs = st.tabs(["Scraping", "Stealth", "Database", "Compliance"])
    
    with tabs[0]:
        _render_scraping_config(config)
    
    with tabs[1]:
        _render_stealth_config(config)
    
    with tabs[2]:
        _render_database_config(config)
    
    with tabs[3]:
        _render_compliance_config(config)
    
    st.markdown("---")
    _render_action_buttons(config)


def _render_scraping_config(config: dict):
    """Render scraping configuration."""
    st.subheader("Scraping Configuration")
    
    config['scraping']['max_depth'] = st.slider(
        "Max Crawl Depth",
        1, 10,
        config.get('scraping', {}).get('max_depth', 3)
    )
    
    config['scraping']['timeout'] = st.number_input(
        "Page Timeout (ms)",
        1000, 120000,
        config.get('scraping', {}).get('timeout', 30000)
    )
    
    config['scraping']['page_delay'] = st.number_input(
        "Page Delay (ms)",
        0, 10000,
        config.get('scraping', {}).get('page_delay', 2000)
    )
    
    config['scraping']['headless'] = st.checkbox(
        "Headless Mode",
        config.get('scraping', {}).get('headless', True)
    )


def _render_stealth_config(config: dict):
    """Render stealth configuration."""
    st.subheader("Stealth Configuration")
    
    config['stealth']['enabled'] = st.checkbox(
        "Enable Stealth Mode",
        config.get('stealth', {}).get('enabled', True)
    )
    
    config['stealth']['mouse_movements'] = st.checkbox(
        "Simulate Mouse Movements",
        config.get('stealth', {}).get('mouse_movements', True)
    )


def _render_database_config(config: dict):
    """Render database configuration."""
    st.subheader("Database Configuration")
    
    config['database']['path'] = st.text_input(
        "Database Path",
        config.get('database', {}).get('path', 'data/scraper.db')
    )
    
    config['database']['auto_backup'] = st.checkbox(
        "Auto Backup",
        config.get('database', {}).get('auto_backup', True)
    )


def _render_compliance_config(config: dict):
    """Render compliance configuration."""
    st.subheader("Compliance Configuration")
    
    config['compliance']['respect_robots_txt'] = st.checkbox(
        "Respect robots.txt",
        config.get('compliance', {}).get('respect_robots_txt', True)
    )
    
    config['compliance']['anonymize_pii'] = st.checkbox(
        "Anonymize PII (GDPR)",
        config.get('compliance', {}).get('anonymize_pii', True)
    )


def _render_action_buttons(config: dict):
    """Render configuration action buttons."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Save Configuration", width="stretch", type="primary"):
            if save_yaml_config(config):
                st.session_state.config = config
                st.success("Configuration saved!")
                st.rerun()
    
    with col2:
        if st.button("Reset to Defaults", width="stretch"):
            st.session_state.config = load_yaml_config()
            st.info("Defaults loaded (not saved)")
            st.rerun()
    
    with col3:
        if st.button("View Raw YAML", width="stretch"):
            st.code(str(config), language='yaml')
