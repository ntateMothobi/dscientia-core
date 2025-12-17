import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# --- Configuration ---
API_BASE_URL = "http://127.0.0.1:8000/api/v1"

st.set_page_config(
    page_title="Property Sales Intelligence",
    page_icon="🏠",
    layout="wide"
)

# --- State Initialization ---
if 'persona' not in st.session_state:
    st.session_state.persona = 'Founder / Executive'

# --- Data Fetching (Cached) ---
@st.cache_data(ttl=30)
def fetch_all_data():
    """Fetches lead and risk profile data."""
    try:
        risk_response = requests.get(f"{API_BASE_URL}/analytics/risk_profile")
        risk_response.raise_for_status()
        return pd.DataFrame(risk_response.json())
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Error fetching dashboard data: {e}")
        return None

@st.cache_data(ttl=30)
def fetch_persona_insight(persona: str) -> str:
    """Fetches formatted insights for a specific persona."""
    persona_map = {
        "Founder / Executive": "founder",
        "Sales Manager": "sales",
        "Operations / CRM Manager": "ops"
    }
    api_persona = persona_map.get(persona, "founder")
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/persona_insights?persona={api_persona}")
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return f"⚠️ Error fetching insights: {e}"

@st.cache_data(ttl=30)
def fetch_alerts(persona: str) -> list:
    """Fetches proactive alerts for a specific persona."""
    persona_map = {
        "Founder / Executive": "founder",
        "Sales Manager": "sales",
        "Operations / CRM Manager": "ops"
    }
    api_persona = persona_map.get(persona, "sales")
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/alerts?persona={api_persona}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return []

# --- UI Components ---
def render_alerts_panel(persona: str):
    """Renders the alerts and notifications panel in the sidebar."""
    alerts = fetch_alerts(persona)
    if not alerts:
        return

    with st.sidebar:
        with st.expander("🚨 Alerts & Notifications", expanded=True):
            for alert in sorted(alerts, key=lambda x: x['severity'], reverse=True):
                icon = alert.get('icon', '⚠️')
                st.markdown(f"**{icon} {alert['title']}**")
                st.caption(alert['message'])
                if 'action_hint' in alert:
                    st.markdown(f"<small>_Action: {alert['action_hint']}_</small>", unsafe_allow_html=True)
                st.markdown("---")

def setup_sidebar(df):
    """Sets up the sidebar with controls and filters."""
    with st.sidebar:
        st.header("Dashboard Controls")
        persona_options = ["Founder / Executive", "Sales Manager", "Operations / CRM Manager"]
        st.session_state.persona = st.radio("View as", persona_options, key="persona_selector")
        
        st.markdown("---")
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
    
    render_alerts_panel(st.session_state.persona) # Render alerts after persona is set

    with st.sidebar:
        st.header("Filters")
        status_options = ["All"] + df['status'].unique().tolist()
        status_filter = st.selectbox("Filter by Status", status_options)

        risk_options = ["All"] + df['risk_level'].unique().tolist()
        risk_filter = st.selectbox("Filter by Risk Level", risk_options)

    return status_filter, risk_filter

def render_executive_summary(df, persona):
    """Renders the high-level executive summary view."""
    st.header("Executive Snapshot")
    
    total_leads = len(df)
    high_risk_leads = len(df[df['risk_level'] == 'High'])
    sla_breached_count = df['sla_breached'].sum()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Active Leads", total_leads)
    col2.metric("High-Risk Leads", high_risk_leads)
    col3.metric("SLA Breaches", sla_breached_count)

    st.markdown("---")
    
    st.subheader(f"Insights for: {persona}")
    insight_text = fetch_persona_insight(persona)
    st.info(insight_text)

def render_risk_sla_dashboard(df):
    """Renders the risk and SLA breach analysis view."""
    st.header("Risk & SLA Analysis")
    st.dataframe(df[["name", "status", "age_days", "risk_score", "risk_level", "sla_breached"]], use_container_width=True)

# --- Main Application ---
st.title("🏠 Property Sales Intelligence")

master_df = fetch_all_data()

if master_df is not None and not master_df.empty:
    status_filter, risk_filter = setup_sidebar(master_df)

    filtered_df = master_df.copy()
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    if risk_filter != "All":
        filtered_df = filtered_df[filtered_df['risk_level'] == risk_filter]

    render_executive_summary(filtered_df, st.session_state.persona)
    render_risk_sla_dashboard(filtered_df)
else:
    st.warning("Could not load dashboard data. Ensure the backend is running.")
