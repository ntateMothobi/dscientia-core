import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# --- Configuration ---
API_URL = "http://127.0.0.1:8000/api/v1/analytics/dashboard"

st.set_page_config(
    page_title="Property Sales Intelligence (Mini)",
    page_icon="🏠",
    layout="wide"
)

# --- Data Fetching ---
@st.cache_data(ttl=60)
def fetch_dashboard_analytics():
    """Fetches analytics data from the backend API."""
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Error connecting to backend: {e}")
        return None

# --- Chart Rendering Functions ---
def render_leads_chart(leads_data):
    """Renders a bar chart for leads by status."""
    st.subheader("Leads by Status")
    lead_status_data = leads_data.get("by_status", {})
    
    if not lead_status_data:
        st.info("No lead data available to display a chart.")
        return
        
    # Convert to DataFrame for charting
    df = pd.DataFrame(list(lead_status_data.items()), columns=['Status', 'Count']).set_index('Status')
    st.bar_chart(df)

def render_followups_chart(followups_data):
    """Renders a pie chart for follow-ups by status."""
    st.subheader("Follow-ups by Status")
    followup_status_data = followups_data.get("by_status", {})

    if not followup_status_data:
        st.info("No follow-up data available to display a chart.")
        return

    # Use Plotly for a better pie chart
    df = pd.DataFrame(list(followup_status_data.items()), columns=['Status', 'Count'])
    fig = px.pie(df, values='Count', names='Status', title='Follow-up Distribution')
    st.plotly_chart(fig, use_container_width=True)

# --- Main Application ---
st.title("🏠 Property Sales Intelligence (Mini)")
st.markdown("### Data-driven insights for property sales")
st.markdown("---")

analytics_data = fetch_dashboard_analytics()

if analytics_data:
    leads_data = analytics_data.get("leads", {})
    followups_data = analytics_data.get("followups", {})

    # --- Key Metrics Section ---
    st.header("📊 Key Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Leads", value=leads_data.get("total_leads", 0))
    with col2:
        st.metric(label="Total Follow-ups", value=followups_data.get("total_followups", 0))
    with col3:
        pending_count = followups_data.get("by_status", {}).get("pending", 0)
        st.metric(label="Pending Actions", value=pending_count)

    st.markdown("---")

    # --- Visualizations Section ---
    col1, col2 = st.columns(2)
    with col1:
        render_leads_chart(leads_data)
    with col2:
        render_followups_chart(followups_data)

else:
    st.warning("Could not load dashboard data. Please ensure the backend server is running.")
