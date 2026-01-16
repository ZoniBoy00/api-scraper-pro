"""
Analytics Component
===================

Charts and analytics visualizations.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def render(endpoints: list):
    """Render analytics tab."""
    st.header("Analytics & Insights")
    
    if not endpoints:
        st.info("No data available for analytics yet.")
        return
    
    _render_timeline(endpoints)
    
    col1, col2 = st.columns(2)
    
    with col1:
        _render_size_distribution(endpoints)
    
    with col2:
        _render_call_distribution(endpoints)


def _render_timeline(endpoints: list):
    """Render discovery timeline chart."""
    st.subheader("Discovery Timeline")
    
    df = pd.DataFrame([
        {'Timestamp': ep['first_seen'], 'Count': 1} 
        for ep in endpoints
    ])
    
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    timeline = df.groupby(df['Timestamp'].dt.floor('h')).size().reset_index()
    timeline.columns = ['Time', 'Endpoints']
    
    fig = px.line(
        timeline,
        x='Time',
        y='Endpoints',
        title='Endpoints Discovered Over Time',
        markers=True
    )
    
    fig.update_traces(line_color='#1f77b4', line_width=3)
    st.plotly_chart(fig, width="stretch")


def _render_size_distribution(endpoints: list):
    """Render response size distribution."""
    st.subheader("Response Sizes")
    
    sizes = [
        (ep.get('avg_response_size') or 0) / 1024 
        for ep in endpoints 
        if ep.get('avg_response_size')
    ]
    
    if sizes:
        fig = go.Figure(data=[go.Histogram(x=sizes, nbinsx=30, marker_color='#17a2b8')])
        fig.update_layout(xaxis_title='Size (KB)', yaxis_title='Count')
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("No size data available")


def _render_call_distribution(endpoints: list):
    """Render call distribution."""
    st.subheader("Call Distribution")
    
    calls = [ep['call_count'] for ep in endpoints]
    
    fig = go.Figure(data=[go.Histogram(x=calls, nbinsx=20, marker_color='#28a745')])
    fig.update_layout(xaxis_title='Calls per Endpoint', yaxis_title='Count')
    st.plotly_chart(fig, width="stretch")
