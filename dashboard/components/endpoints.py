"""
Endpoints Component
===================

Endpoints browser with filtering and export.
"""

import streamlit as st
import pandas as pd
import json


def render(endpoints: list):
    """Render endpoints tab."""
    st.header("All Endpoints")
    
    if not endpoints:
        st.info("No endpoints yet. Start scraping to populate data.")
        return
    
    # Filters
    filtered = _apply_filters(endpoints)
    
    # Display
    _render_table(filtered, total=len(endpoints))
    
    # Export
    _render_export_buttons(filtered)


def _apply_filters(endpoints: list) -> list:
    """Apply filters to endpoints list."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        methods = ['All'] + sorted(set(ep['method'] for ep in endpoints))
        selected_method = st.selectbox("Filter by Method:", methods)
    
    with col2:
        sort_options = ["Calls (Most)", "Calls (Least)", "URL (A-Z)", "Last Seen"]
        sort_by = st.selectbox("Sort by:", sort_options)
    
    with col3:
        search_term = st.text_input("Search URL:", placeholder="e.g., /api/users")
    
    # Filter
    filtered = endpoints
    
    if selected_method != 'All':
        filtered = [ep for ep in filtered if ep['method'] == selected_method]
    
    if search_term:
        filtered = [ep for ep in filtered if search_term.lower() in ep['url'].lower()]
    
    # Sort
    if sort_by == "Calls (Most)":
        filtered = sorted(filtered, key=lambda x: x['call_count'], reverse=True)
    elif sort_by == "Calls (Least)":
        filtered = sorted(filtered, key=lambda x: x['call_count'])
    elif sort_by == "URL (A-Z)":
        filtered = sorted(filtered, key=lambda x: x['url'])
    elif sort_by == "Last Seen":
        filtered = sorted(filtered, key=lambda x: x['last_seen'], reverse=True)
    
    return filtered


def _render_table(filtered: list, total: int):
    """Render endpoints table."""
    st.info(f"Showing {len(filtered)} of {total} endpoints")
    
    df = pd.DataFrame([{
        'ID': ep['id'],
        'Method': ep['method'],
        'URL': ep['url'],
        'Calls': ep['call_count'],
        'Size (KB)': round((ep.get('avg_response_size') or 0) / 1024, 2),
        'First Seen': ep['first_seen'][:19],
        'Last Seen': ep['last_seen'][:19],
    } for ep in filtered])
    
    st.dataframe(df, width="stretch", hide_index=True)


def _render_export_buttons(filtered: list):
    """Render export buttons."""
    col1, col2 = st.columns(2)
    
    with col1:
        df = pd.DataFrame(filtered)
        csv = df.to_csv(index=False)
        st.download_button(
            "Download CSV",
            csv,
            "endpoints.csv",
            "text/csv",
            width="stretch"
        )
    
    with col2:
        json_data = json.dumps(filtered, indent=2)
        st.download_button(
            "Download JSON",
            json_data,
            "endpoints.json",
            "application/json",
            width="stretch"
        )
