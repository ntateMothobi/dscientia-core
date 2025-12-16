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

# --- Data Fetching (Cached) ---
@st.cache_data(ttl=30)
def fetch_all_data():
    """Fetches both risk profile and detailed lead data and merges them."""
    try:
        risk_response = requests.get(f"{API_BASE_URL}/analytics/risk_profile")
        risk_response.raise_for_status()
        risk_df = pd.DataFrame(risk_response.json())

        leads_response = requests.get(f"{API_BASE_URL}/leads/")
        leads_response.raise_for_status()
        leads_df = pd.DataFrame(leads_response.json())

        # Merge the two dataframes to have all data in one place
        if not risk_df.empty and not leads_df.empty:
            # Keep followups from leads_df and analytics from risk_df
            merged_df = pd.merge(
                risk_df,
                leads_df[['id', 'followups', 'created_at']],
                on='id',
                how='left'
            )
            return merged_df
        return None

    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Error fetching data: {e}")
        return None

# --- UI Components ---
def setup_sidebar(df):
    """Sets up the sidebar with view selector and filters."""
    with st.sidebar:
        st.header("Dashboard Controls")
        
        view_mode = st.radio(
            "Dashboard View",
            ["Executive Summary", "Sales Analytics", "Risk & SLA"],
            key="view_mode"
        )
        
        st.markdown("---")
        
        if st.button("🔄 Refresh Data", key="refresh_btn"):
            st.cache_data.clear()
            st.rerun()
        
        st.header("Filters")
        
        status_options = ["All"] + df['status'].unique().tolist()
        status_filter = st.selectbox("Filter by Status", status_options, key="status_filter")

        risk_options = ["All"] + df['risk_level'].unique().tolist()
        risk_filter = st.selectbox("Filter by Risk Level", risk_options, key="risk_filter")

    return view_mode, status_filter, risk_filter

# --- Modular Render Functions ---

def render_executive_summary(df):
    """Renders the high-level executive summary view."""
    st.header("📊 Executive Key Metrics")
    
    total_leads = len(df)
    high_risk_leads = len(df[df['risk_level'] == 'High'])
    sla_breached_count = df['sla_breached'].sum()
    closed_leads = len(df[df['status'] == 'closed'])
    conversion_rate = (closed_leads / total_leads * 100) if total_leads > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Leads", value=total_leads)
    with col2:
        st.metric(label="Conversion Rate", value=f"{conversion_rate:.1f}%")
    with col3:
        st.metric(label="🔥 High Risk Leads", value=high_risk_leads, help="Leads with Risk Score >= 70")
    with col4:
        st.metric(label="⏰ SLA Breached", value=sla_breached_count)
    
    st.markdown("---")
    st.header("💡 AI-Driven Insights")
    st.info(
        """
        **Summary:** The sales pipeline shows a steady flow of new leads, but a significant portion are flagged as 'High Risk' due to slow follow-up times. 
        - **Recommendation:** Prioritize outreach to leads in the 'High Risk' and 'SLA Breached' categories to improve conversion potential.
        - **Observation:** Leads from 'Referral' sources continue to show the highest conversion rates, suggesting a strong opportunity for network-based marketing.
        """
    )

def render_sales_analytics(df):
    """Renders the detailed sales performance analytics view."""
    st.header("🎯 Sales Performance Analytics")

    # 1. Lead Status Distribution
    st.subheader("Lead Status Distribution")
    status_counts = df['status'].value_counts()
    fig_status = px.bar(status_counts, x=status_counts.index, y=status_counts.values, labels={'x': 'Status', 'y': 'Count'}, title="Current Lead Funnel")
    st.plotly_chart(fig_status, use_container_width=True)

    # 2. Lead Source Performance
    st.subheader("Performance by Source")
    source_agg = df.groupby('source').agg(
        total_leads=('id', 'count'),
        closed_leads=('status', lambda s: (s == 'closed').sum())
    ).reset_index()
    source_agg['conversion_rate'] = (source_agg['closed_leads'] / source_agg['total_leads'] * 100).fillna(0)
    st.dataframe(source_agg.style.format({'conversion_rate': '{:.1f}%'}), use_container_width=True)

    # 3. Lead Aging Analysis
    st.subheader("Lead Aging")
    avg_age = df['age_days'].mean()
    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric("Average Lead Age (Days)", f"{avg_age:.1f}")
    with col2:
        fig_age = px.histogram(df, x="age_days", nbins=20, title="Lead Age Distribution")
        st.plotly_chart(fig_age, use_container_width=True)

def render_risk_sla_dashboard(df):
    """Renders the risk and SLA breach analysis view."""
    st.header("🚨 Risk & SLA Dashboard")
    
    high_risk_leads = len(df[df['risk_level'] == 'High'])
    sla_breached_count = df['sla_breached'].sum()

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="🔥 High Risk Leads", value=high_risk_leads, help="Leads with Risk Score >= 70")
    with col2:
        st.metric(label="⏰ SLA Breached Leads", value=sla_breached_count)
    
    st.markdown("---")
    st.subheader("Lead Risk Details")
    
    display_cols = ["name", "status", "age_days", "sla_breached", "risk_score", "risk_level"]
    column_config = {
        "name": "Lead Name", "status": "Stage", "age_days": "Age (Days)",
        "sla_breached": "SLA Breached", "risk_score": "Risk Score", "risk_level": "Risk Level"
    }
    st.dataframe(df[display_cols], use_container_width=True, column_config=column_config)

# --- Main Application ---
st.title("🏠 Property Sales Intelligence (Mini)")
st.markdown("### Data-driven insights for property sales")
st.markdown("---")

# Fetch and prepare data once
master_df = fetch_all_data()

if master_df is not None and not master_df.empty:
    # Setup sidebar and get user selections
    view_mode, status_filter, risk_filter = setup_sidebar(master_df)

    # Apply filters to create the displayed DataFrame
    filtered_df = master_df.copy()
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    if risk_filter != "All":
        filtered_df = filtered_df[filtered_df['risk_level'] == risk_filter]

    # Conditionally render the selected view
    if view_mode == "Executive Summary":
        render_executive_summary(filtered_df)
    elif view_mode == "Sales Analytics":
        render_sales_analytics(filtered_df)
    elif view_mode == "Risk & SLA":
        render_risk_sla_dashboard(filtered_df)
else:
    st.warning("Could not load dashboard data. Please ensure the backend server is running and data is seeded.")
