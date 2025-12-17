import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timezone
import time

# --- Configuration ---
API_BASE_URL = "http://127.0.0.1:8000/api/v1"

st.set_page_config(page_title="Property Sales Intelligence", page_icon="🏠", layout="wide")

# --- State Initialization ---
# ... (existing state init)

# --- Data Fetching ---
@st.cache_data(ttl=30)
def fetch_system_health():
    try:
        response = requests.get(f"{API_BASE_URL}/system/health")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return {"status": "unhealthy", "reason": "API is unreachable."}

@st.cache_data(ttl=60)
def fetch_system_metrics():
    try:
        response = requests.get(f"{API_BASE_URL}/system/metrics")
        response.raise_for_status()
        return response.json()
    except: return None

@st.cache_data(ttl=60)
def fetch_ingestion_status():
    try:
        response = requests.get(f"{API_BASE_URL}/system/ingestion_status")
        response.raise_for_status()
        return response.json()
    except: return None

# --- UI Components ---
def display_system_health_panel():
    health_data = fetch_system_health()
    status = health_data.get("status", "unhealthy")
    
    color_map = {"healthy": "green", "degraded": "orange", "unhealthy": "red"}
    icon_map = {"healthy": "🟢", "degraded": "🟡", "unhealthy": "🔴"}
    
    col1, col2, col3, col4 = st.columns([3, 2, 2, 3])
    
    with col1:
        st.markdown(f"**System Status:** <span style='color:{color_map[status]};'>{icon_map[status]} {status.upper()}</span>", unsafe_allow_html=True)
    
    metrics = fetch_system_metrics()
    if metrics:
        last_ingestion_at = metrics.get("last_ingestion_at")
        if last_ingestion_at:
            dt = datetime.fromisoformat(last_ingestion_at)
            now = datetime.now(timezone.utc)
            delta_hours = (now - dt).total_seconds() / 3600
            col2.metric("Last Ingestion", f"{delta_hours:.1f}h ago")
        else:
            col2.metric("Last Ingestion", "N/A")
        
        col3.metric("Failed Ingestions (24h)", metrics.get("failed_ingestions_last_24h", "N/A"))

    with col4:
        with st.expander("View System Details"):
            st.write(f"**Reason:** {health_data.get('reason', 'No details available.')}")
            if metrics:
                st.dataframe(pd.DataFrame([metrics]))
            
            ingestion_status = fetch_ingestion_status()
            if ingestion_status:
                st.subheader("Last Ingestion Run")
                st.json(ingestion_status)

def main():
    st.title("🏠 Property Sales Intelligence")
    
    # Render the health panel at the top
    display_system_health_panel()
    st.markdown("---")
    
    # ... (rest of the main app logic, sidebar, and page routing)

if __name__ == "__main__":
    main()
