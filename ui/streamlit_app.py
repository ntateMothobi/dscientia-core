import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timezone
import json
import logging
import time

# --- Configuration & Initialization ---
API_BASE_URL = "http://127.0.0.1:8000/api/v1"
logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="Property Sales Intelligence", page_icon="🏠", layout="wide")

def initialize_session_state():
    defaults = {
        "persona": "Founder / Executive",
        "active_page": "Dashboard",
        "last_ingestion_summary": None,
        "debug_mode": False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# --- Data Fetching ---
@st.cache_data(ttl=30)
def fetch_health_status():
    """Fetches system health data with graceful failure."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=3)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Health check failed: {e}")
        return {
            "status": "down",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": "unreachable",
            "cache": "unknown",
            "ingestion_services": {},
            "last_ingestion": None
        }

# --- UI Components ---
def display_health_status_panel():
    """Renders the system health panel in the sidebar."""
    st.sidebar.header("System Status")
    health_data = fetch_health_status()

    status = health_data.get("status", "down")
    
    status_map = {
        "healthy": {"color": "green", "icon": "✅", "summary": "All systems operational."},
        "degraded": {"color": "orange", "icon": "⚠️", "summary": "System is running with minor issues."},
        "unhealthy": {"color": "red", "icon": "🔥", "summary": "Critical system failure detected."},
        "down": {"color": "red", "icon": "🔥", "summary": "API is unreachable."}
    }
    
    current_status = status_map.get(status, status_map["down"])

    st.sidebar.markdown(
        f"<span style='color:{current_status['color']};'>**{current_status['icon']} {status.capitalize()}**</span>",
        unsafe_allow_html=True
    )
    st.sidebar.caption(current_status["summary"])

    with st.sidebar.expander("View System Details"):
        details = {
            "Database Status": health_data.get("database", "unknown"),
            "Cache Status": health_data.get("cache", "unknown"),
            "API Status": "online" if status != "down" else "offline"
        }
        st.json(details)

        last_ingestion = health_data.get("last_ingestion")
        if last_ingestion:
            dt = datetime.fromisoformat(last_ingestion)
            now = datetime.now(timezone.utc)
            delta_minutes = (now - dt).total_seconds() / 60
            st.metric("Last Successful Ingestion", f"{delta_minutes:.0f} min ago")
        else:
            st.metric("Last Successful Ingestion", "Never")

        if status == "down":
            if st.button("Retry Health Check", key="retry_health"):
                st.cache_data.clear()
                st.rerun()

def setup_sidebar():
    """Sets up the main sidebar, including the new health panel."""
    display_health_status_panel()
    st.sidebar.markdown("---")
    
    with st.sidebar:
        st.header("Navigation")
        st.radio("Go to", ["Dashboard", "Governance & Audit"], key="active_page")
        # ... (rest of the sidebar)

# --- Main Application ---
def main():
    initialize_session_state()
    setup_sidebar()
    
    # ... (page router logic)

if __name__ == "__main__":
    main()
