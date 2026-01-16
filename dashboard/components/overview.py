"""
Overview Component
==================

Dashboard overview tab with summary statistics and charts.
"""

import streamlit as st
import plotly.express as px
import pandas as pd


def render(stats: dict, endpoints: list):
    """Render overview tab."""
    st.header("Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        _render_methods_chart(stats)
    
    with col2:
        _render_top_endpoints_chart(endpoints)
    
    if endpoints:
        _render_recent_table(endpoints)


def _render_methods_chart(stats: dict):
    """Render HTTP methods distribution chart."""
    if not stats.get('methods'):
        st.info("No method data available")
        return
    
    st.subheader("HTTP Methods Distribution")
    
    methods_df = pd.DataFrame([
        {'Method': method, 'Count': count} 
        for method, count in stats['methods'].items()
    ])
    
    fig = px.pie(
        methods_df,
        values='Count',
        names='Method',
        color_discrete_sequence=px.colors.qualitative.Pastel,
        hole=0.3
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, width="stretch")


def _render_top_endpoints_chart(endpoints: list):
    """Render top endpoints bar chart."""
    if not endpoints:
        st.info("No endpoint data available")
        return
    
    st.subheader("Top 5 Endpoints")
    
    top_5 = sorted(endpoints, key=lambda x: x['call_count'], reverse=True)[:5]
    
    top_df = pd.DataFrame([
        {'Endpoint': ep['url'][:40] + '...', 'Calls': ep['call_count']} 
        for ep in top_5
    ])
    
    fig = px.bar(
        top_df,
        x='Calls',
        y='Endpoint',
        orientation='h',
        color='Calls',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, width="stretch")


def _render_recent_table(endpoints: list):
    """Render recently discovered endpoints table."""
    st.subheader("Recently Discovered")
    
    recent = sorted(endpoints, key=lambda x: x['last_seen'], reverse=True)[:10]
    
    df = pd.DataFrame([{
        'Method': ep['method'],
        'URL': ep['url'][:80],
        'Calls': ep['call_count'],
        'Last Seen': ep['last_seen'][:19]
    } for ep in recent])
    
    st.dataframe(df, width="stretch", hide_index=True)
