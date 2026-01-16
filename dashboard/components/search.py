"""
Search Component
================

Advanced endpoint search.
"""

import streamlit as st


def render(endpoints: list):
    """Render search tab."""
    st.header("Advanced Search")
    
    # Search inputs
    search_query = st.text_input("Search by URL:", placeholder="e.g., /api/users")
    
    col1, col2 = st.columns(2)
    with col1:
        min_calls = st.number_input("Min Calls", 0, value=0)
    with col2:
        max_calls = st.number_input("Max Calls", 0, value=1000000)
    
    # Perform search
    if search_query or (min_calls > 0 or max_calls < 1000000):
        results = _search_endpoints(endpoints, search_query, min_calls, max_calls)
        _display_results(results)


def _search_endpoints(endpoints: list, query: str, min_calls: int, max_calls: int) -> list:
    """Search and filter endpoints."""
    results = endpoints
    
    if query:
        results = [ep for ep in results if query.lower() in ep['url'].lower()]
    
    results = [ep for ep in results if min_calls <= ep['call_count'] <= max_calls]
    
    return results


def _display_results(results: list):
    """Display search results."""
    st.subheader(f"Found {len(results)} results")
    
    for ep in results[:20]:
        with st.expander(f"{ep['method']} {ep['url']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Details:**")
                st.write(f"ID: {ep['id']}")
                st.write(f"Calls: {ep['call_count']}")
                st.write(f"Size: {round((ep.get('avg_response_size') or 0) / 1024, 2)} KB")
                st.write(f"First: {ep['first_seen']}")
                st.write(f"Last: {ep['last_seen']}")
            
            with col2:
                st.markdown("**Schema:**")
                if ep.get('schema'):
                    st.json(ep['schema'])
                else:
                    st.info("No schema available")
    
    if len(results) > 20:
        st.info(f"Showing first 20 of {len(results)} results")
