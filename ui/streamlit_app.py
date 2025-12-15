import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timezone

# --- Configuration ---
API_BASE_URL = "http://127.0.0.1:8000/api/v1"

st.set_page_config(
    page_title="Property Sales Intelligence (Mini)",
    page_icon="🏠",
    layout="wide"
)

# --- Data Fetching ---
@st.cache_data(ttl=60)
def fetch_dashboard_analytics():
    """Fetches aggregate analytics data from the backend API."""
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/dashboard")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Error fetching dashboard data: {e}")
        return None

@st.cache_data(ttl=60)
def fetch_all_leads():
    """Fetches all individual lead records for detailed analysis."""
    try:
        response = requests.get(f"{API_BASE_URL}/leads/")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Error fetching lead details: {e}")
        return []

# --- Filtering Logic ---
def filter_leads_data(data, status_filter):
    if not data: return {}
    if status_filter == "All": return data
    by_status = data.get("by_status", {})
    count = by_status.get(status_filter, 0)
    return {"total_leads": count, "by_status": {status_filter: count}}

def filter_followups_data(data, status_filter):
    if not data: return {}
    if status_filter == "All": return data
    by_status = data.get("by_status", {})
    count = by_status.get(status_filter, 0)
    return {"total_followups": count, "by_status": {status_filter: count}}

# --- UI Components ---
def setup_sidebar(leads_data, followups_data):
    with st.sidebar:
        st.header("Controls")
        if st.button("🔄 Refresh Data", key="refresh_btn"):
            st.cache_data.clear()
            st.rerun()
        st.header("Filters")
        lead_statuses = list(leads_data.get("by_status", {}).keys())
        lead_status_filter = st.selectbox("Filter Leads by Status", ["All"] + lead_statuses, key="lead_filter")
        followup_statuses = list(followups_data.get("by_status", {}).keys())
        followup_status_filter = st.selectbox("Filter Follow-ups by Status", ["All"] + followup_statuses, key="followup_filter")
    return lead_status_filter, followup_status_filter

def render_status_charts(leads_data, followups_data):
    st.header("📈 Status Overview")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Leads by Status")
        status_data = leads_data.get("by_status", {})
        if not status_data:
            st.info("No lead data to display.")
        else:
            df = pd.DataFrame(list(status_data.items()), columns=['Status', 'Count']).set_index('Status')
            st.bar_chart(df)
    with col2:
        st.subheader("Follow-ups by Status")
        status_data = followups_data.get("by_status", {})
        if not status_data:
            st.info("No follow-up data to display.")
        else:
            df = pd.DataFrame(list(status_data.items()), columns=['Status', 'Count'])
            fig = px.pie(df, values='Count', names='Status', title='Follow-up Distribution')
            st.plotly_chart(fig, use_container_width=True)

def render_lead_aging_analysis(leads_df, status_filter):
    st.header("⏳ Lead Aging Analysis")
    if leads_df.empty:
        st.info("No lead data available for aging analysis.")
        return

    if status_filter != "All":
        leads_df = leads_df[leads_df['status'] == status_filter]
    if leads_df.empty:
        st.info(f"No leads with status '{status_filter}'.")
        return

    # FIX: Ensure created_at is timezone-aware (UTC) to match datetime.now(timezone.utc)
    leads_df['created_at'] = pd.to_datetime(leads_df['created_at'], utc=True)

    leads_df['age_days'] = (datetime.now(timezone.utc) - leads_df['created_at']).dt.days
    avg_age = leads_df['age_days'].mean()

    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric("Average Lead Age (Days)", f"{avg_age:.1f}")
    with col2:
        fig = px.histogram(leads_df, x="age_days", nbins=20, title="Lead Age Distribution")
        st.plotly_chart(fig, use_container_width=True)

def render_source_performance(leads_df, status_filter):
    st.header("🎯 Source Performance Analysis")
    if leads_df.empty:
        st.info("No lead data available for source analysis.")
        return

    if status_filter != "All":
        leads_df = leads_df[leads_df['status'] == status_filter]
    if leads_df.empty:
        st.info(f"No leads with status '{status_filter}'.")
        return

    source_agg = leads_df.groupby('source').agg(
        total_leads=('id', 'count'),
        closed_leads=('status', lambda s: (s == 'closed').sum())
    ).reset_index()
    source_agg['conversion_rate'] = (source_agg['closed_leads'] / source_agg['total_leads'] * 100).fillna(0)
    
    st.subheader("Performance by Source")
    st.dataframe(source_agg.style.format({'conversion_rate': '{:.1f}%'}), use_container_width=True)

# --- Main Application ---
st.title("🏠 Property Sales Intelligence (Mini)")
st.markdown("### Data-driven insights for property sales")
st.markdown("---")

raw_analytics_data = fetch_dashboard_analytics()
all_leads_list = fetch_all_leads()

if raw_analytics_data and all_leads_list is not None:
    raw_leads_data = raw_analytics_data.get("leads", {})
    raw_followups_data = raw_analytics_data.get("followups", {})

    lead_filter, followup_filter = setup_sidebar(raw_leads_data, raw_followups_data)

    filtered_leads_data = filter_leads_data(raw_leads_data, lead_filter)
    filtered_followups_data = filter_followups_data(raw_followups_data, followup_filter)

    st.header("📊 Key Metrics")
    total_leads = filtered_leads_data.get("total_leads", 0)
    total_followups = filtered_followups_data.get("total_followups", 0)
    closed_leads = filtered_leads_data.get("by_status", {}).get("closed", 0)
    conversion_rate = (closed_leads / total_leads * 100) if total_leads > 0 else 0
    followup_intensity = (total_followups / total_leads) if total_leads > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Leads", value=total_leads)
    with col2:
        st.metric(label="Conversion Rate", value=f"{conversion_rate:.1f}%")
    with col3:
        st.metric(label="Avg Follow-ups / Lead", value=f"{followup_intensity:.1f}")
    with col4:
        pending_count = filtered_followups_data.get("by_status", {}).get("pending", 0)
        st.metric(label="Pending Actions", value=pending_count)

    st.markdown("---")
    
    leads_df = pd.DataFrame(all_leads_list)
    render_lead_aging_analysis(leads_df.copy(), lead_filter)
    st.markdown("---")
    render_source_performance(leads_df.copy(), lead_filter)
    st.markdown("---")
    
    render_status_charts(filtered_leads_data, filtered_followups_data)

else:
    st.warning("Could not load dashboard data. Please ensure the backend server is running.")
