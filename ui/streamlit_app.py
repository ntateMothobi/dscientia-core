import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json
import logging

# --- Configuration ---
API_BASE_URL = "http://127.0.0.1:8000/api/v1"
logging.basicConfig(level=logging.ERROR)

st.set_page_config(
    page_title="Property Sales Intelligence",
    page_icon="🏠",
    layout="wide"
)

# --- State Initialization ---
if 'persona' not in st.session_state:
    st.session_state.persona = 'Founder / Executive'
if 'active_page' not in st.session_state:
    st.session_state.active_page = 'Dashboard'

# --- Data Fetching ---
@st.cache_data(ttl=30)
def fetch_all_data():
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/risk_profile")
        response.raise_for_status()
        df = pd.DataFrame(response.json())
        # Ensure required columns exist to prevent downstream errors
        for col in ['confidence_score', 'explainability_coverage', 'risk_level', 'sla_breached']:
            if col not in df.columns:
                df[col] = 0
        return df
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching risk profile data: {e}")
        st.error("⚠️ Unable to connect to the analytics service.")
        return pd.DataFrame()

@st.cache_data(ttl=30)
def fetch_trust_metrics():
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/data_freshness")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching trust metrics: {e}")
        return {}

@st.cache_data(ttl=30)
def fetch_audit_logs(params=None):
    try:
        response = requests.get(f"{API_BASE_URL}/governance/audit_logs", params=params)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching audit logs: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=30)
def fetch_persona_insight(persona: str) -> str:
    persona_map = {"Founder / Executive": "founder", "Sales Manager": "sales", "Operations / CRM Manager": "ops"}
    api_persona = persona_map.get(persona, "founder")
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/persona_insights?persona={api_persona}")
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching insights: {e}")
        return "⚠️ Insights currently unavailable."

@st.cache_data(ttl=30)
def fetch_alerts(persona: str) -> list:
    persona_map = {"Founder / Executive": "founder", "Sales Manager": "sales", "Operations / CRM Manager": "ops"}
    api_persona = persona_map.get(persona, "sales")
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/alerts?persona={api_persona}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching alerts: {e}")
        return []

# --- Page Implementations ---

def render_main_dashboard_page(master_df):
    try:
        st.title("🏠 Property Sales Intelligence Dashboard")
        
        if master_df.empty:
            st.info("👋 Welcome! No lead data is currently available.")
            st.markdown("Once leads are added to the system, analytics will appear here.")
            return

        status_filter, risk_filter = get_dashboard_filters(master_df)

        filtered_df = master_df.copy()
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df['status'] == status_filter]
        if risk_filter != "All":
            filtered_df = filtered_df[filtered_df['risk_level'] == risk_filter]

        if filtered_df.empty:
            st.warning("No leads match the selected filters.")
            st.markdown(f"👉 **Try adjusting the filters:**\n- Status: `{status_filter}`\n- Risk Level: `{risk_filter}`")
            return

        render_executive_summary(filtered_df, st.session_state.persona)
        render_risk_sla_dashboard(filtered_df)

    except Exception as e:
        logging.error(f"Error rendering dashboard: {e}")
        st.error("An unexpected error occurred while loading the dashboard. Please try refreshing the page.")

def render_governance_audit_page():
    try:
        st.title("🔐 Governance & Audit Trail")
        st.markdown("This section provides a traceable log of key system decisions and AI-driven outputs.")

        with st.spinner("Retrieving governance records..."):
            logs_df = fetch_audit_logs()

        if logs_df.empty:
            st.info("No audit logs found.")
            st.markdown("System events (risk calculations, alerts) will appear here once they occur.")
            return

        display_df = logs_df[['timestamp', 'event_type', 'entity_type', 'entity_id', 'persona', 'decision', 'confidence']].copy()
        display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        display_df['decision_summary'] = display_df['decision'].apply(lambda d: json.dumps(d, indent=2)[:100] + '...' if isinstance(d, dict) else str(d)[:100])
        
        st.dataframe(
            display_df[['timestamp', 'event_type', 'entity_type', 'entity_id', 'persona', 'decision_summary', 'confidence']], 
            use_container_width=True,
            column_config={
                "timestamp": "Time (UTC)",
                "event_type": "Event",
                "entity_type": "Entity",
                "entity_id": "ID",
                "persona": "Persona Context",
                "decision_summary": "Decision Output",
                "confidence": st.column_config.NumberColumn(
                    "Confidence",
                    help="System confidence score (0.0 - 1.0) for this decision.",
                    format="%.2f"
                )
            }
        )

        st.subheader("Log Details")
        selected_index = st.selectbox("Select a log entry to inspect:", logs_df.index, key="audit_log_selector")
        if selected_index is not None:
            selected_log = logs_df.loc[selected_index]
            st.json(selected_log.to_json(), expanded=True)

    except Exception as e:
        logging.error(f"Error rendering audit page: {e}")
        st.error("Unable to load audit logs. Please check the system logs.")

# --- UI Components ---

def setup_sidebar():
    with st.sidebar:
        st.header("Navigation")
        st.session_state.active_page = st.radio(
            "Go to", 
            ["Dashboard", "Governance & Audit"], 
            key="nav_selector"
        )
        st.markdown("---")

        st.header("Dashboard Controls")
        st.session_state.persona = st.radio(
            "View as", 
            ["Founder / Executive", "Sales Manager", "Operations / CRM Manager"], 
            key="persona_selector"
        )
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
    
    render_alerts_panel(st.session_state.persona)

def get_dashboard_filters(df):
    with st.sidebar:
        st.header("Filters")
        status_options = ["All"] + df['status'].unique().tolist()
        status_filter = st.selectbox("Filter by Status", status_options, key="status_filter")
        risk_options = ["All"] + df['risk_level'].unique().tolist()
        risk_filter = st.selectbox("Filter by Risk Level", risk_options, key="risk_filter")
    return status_filter, risk_filter

def render_alerts_panel(persona: str):
    with st.sidebar.expander("🚨 Alerts & Notifications", expanded=True):
        with st.spinner("Checking alerts..."):
            alerts = fetch_alerts(persona)
        
        if not alerts:
            st.success("No active alerts. All clear! ✅")
            return

        for alert in sorted(alerts, key=lambda x: x.get('severity', 'low'), reverse=True):
            st.markdown(f"**{alert.get('icon', '⚠️')} {alert.get('title', 'Alert')}**")
            st.caption(alert.get('message', ''))
            if 'action_hint' in alert:
                st.markdown(f"<small>_Action: {alert['action_hint']}_</small>", unsafe_allow_html=True)
            st.markdown("---")

def render_executive_summary(df, persona):
    st.header("Executive Snapshot")
    total_leads, high_risk_leads, sla_breached_count = len(df), len(df[df['risk_level'] == 'High']), df['sla_breached'].sum()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Active Leads", total_leads, help="Total number of leads currently in the pipeline.")
    col2.metric("High-Risk Leads", high_risk_leads, help="Leads flagged with high risk scores (>75) or critical issues.")
    col3.metric("SLA Breaches", sla_breached_count, help="Leads that have exceeded the allowed time in their current stage.")
    
    render_trust_confidence_section(df)

    st.markdown("---")
    st.subheader(f"Insights for: {persona}")
    with st.spinner(f"Generating insights for {persona}..."):
        st.info(fetch_persona_insight(persona))

def render_trust_confidence_section(df):
    st.subheader("Trust & Confidence Layer")
    trust_metrics = fetch_trust_metrics()
    avg_confidence, avg_coverage = df['confidence_score'].mean(), df['explainability_coverage'].mean()
    
    col1, col2, col3 = st.columns(3)
    freshness_score = trust_metrics.get('freshness_score', 0)
    last_updated_str = trust_metrics.get('last_updated_at', 'N/A')
    if last_updated_str != 'N/A':
        try:
            last_updated_dt = datetime.fromisoformat(last_updated_str)
            last_updated_str = last_updated_dt.strftime('%d %b %Y, %H:%M:%S')
        except (ValueError, TypeError): pass

    col1.metric("Data Freshness", f"{freshness_score}/100", help=f"Score based on recency of data updates. Last update: {last_updated_str}")
    col2.metric("Avg. Confidence", f"{avg_confidence:.2f}", help="Average system confidence (0-1) in the risk assessments based on data completeness.")
    col3.metric("Explainability", f"{avg_coverage:.0%}", help="Percentage of expected risk factors that were successfully identified and explained.")

def render_risk_sla_dashboard(df):
    st.header("Risk & SLA Analysis")
    
    high_risk_df = df[df['risk_level'] == 'High'].sort_values('risk_score', ascending=False)

    if high_risk_df.empty:
        st.success("🎉 No high-risk leads detected!")
        st.markdown("Your pipeline looks healthy. Check 'All Leads Data' below for the full list.")
    else:
        for index, row in high_risk_df.iterrows():
            st.markdown(f"#### {row.get('name', 'N/A')} (Risk Score: {row.get('risk_score', 'N/A')})")
            with st.expander(f"**Why is {row.get('name', 'this lead')} high risk?**"):
                summary, risk_factors, action, disclaimer = row.get('explanation_text'), row.get('risk_factors', []), row.get('recommended_action'), row.get('disclaimer')
                
                st.markdown(f"**Summary:** *{summary or 'No summary available.'}*")
                if risk_factors:
                    st.markdown("**Risk Factors:**")
                    for factor in risk_factors:
                        st.markdown(f"- **{factor.get('type', 'N/A').replace('_', ' ').title()}** ({factor.get('weight', 0)}%): {factor.get('detail', 'N/A')}")
                st.markdown("**Recommended Action:**")
                st.success(f"➡️ {action or 'No action recommended.'}")
                if disclaimer: st.warning(f"*{disclaimer}*")
            st.markdown("---")

    st.subheader("All Leads Data")
    display_cols = ["name", "status", "age_days", "risk_score", "risk_level", "sla_breached", "confidence_level"]
    
    if df.empty:
        st.info("No leads available to display.")
    else:
        st.dataframe(
            df[[col for col in display_cols if col in df.columns]], 
            use_container_width=True,
            column_config={
                "risk_score": st.column_config.NumberColumn("Risk Score", help="0-100 score indicating lead risk."),
                "confidence_level": st.column_config.TextColumn("Confidence", help="System confidence in this assessment.")
            }
        )

# --- Main Application Router ---
def main():
    # Setup sidebar for navigation and global controls
    setup_sidebar()

    # Page routing
    if st.session_state.active_page == 'Dashboard':
        with st.spinner("Analyzing pipeline data..."):
            master_df = fetch_all_data()
        render_main_dashboard_page(master_df)
    elif st.session_state.active_page == 'Governance & Audit':
        render_governance_audit_page()
    else:
        st.switch_page("streamlit_app.py") # Fallback to default

if __name__ == "__main__":
    main()
