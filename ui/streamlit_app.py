import streamlit as st
import requests
import logging

# --- Configuration & Initialization ---
API_BASE_URL = "http://127.0.0.1:8000/api/v1"
logging.basicConfig(level=logging.INFO)

# --- DEV AUTH BYPASS – REMOVE BEFORE PRODUCTION ---
DEV_MODE_BYPASS_AUTH = True
# --- END DEV AUTH BYPASS ---

st.set_page_config(page_title="Property Sales Intelligence", page_icon="🏠", layout="wide")

def map_persona_to_role(persona: str) -> str:
    """Maps the selected persona to a user role string."""
    return {
        "Founder / Executive": "founder",
        "Sales Manager": "sales_manager",
        "Operations / CRM Manager": "ops_crm",
    }.get(persona, "founder")

def initialize_session_state():
    """Initializes session state for authentication and navigation."""
    defaults = {
        "is_authenticated": False,
        "access_token": None,
        "user_role": "founder",
        "persona": "Founder / Executive",
        "active_page": "Dashboard",
        "debug_mode": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
            
    # --- DEV AUTH BYPASS – REMOVE BEFORE PRODUCTION ---
    if DEV_MODE_BYPASS_AUTH:
        st.session_state.is_authenticated = True
        st.session_state.access_token = "dev-token-do-not-use-in-prod"
        # You can change the default role for testing different personas
        st.session_state.user_role = "founder" 
    # --- END DEV AUTH BYPASS ---


# --- API Calls ---
def api_request(method, endpoint, **kwargs):
    """Centralized function for making authenticated API requests."""
    headers = kwargs.pop("headers", {})
    if st.session_state.get("access_token"):
        headers["Authorization"] = f"Bearer {st.session_state.access_token}"
    else:
        headers["X-User-Role"] = st.session_state.get("user_role", "founder")

    url = f"{API_BASE_URL}/{endpoint}"
    try:
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403: st.error("🚫 Access Denied.")
        elif e.response.status_code == 401:
             st.error("🚫 Authentication failed.")
             handle_logout()
        else: st.error(f"API Error: {e.response.status_code}")
        return None
    except requests.exceptions.RequestException:
        st.error("Failed to connect to the API.")
        return None

def handle_login():
    # This function is now bypassed in DEV_MODE
    pass

def handle_logout():
    # This function is now bypassed in DEV_MODE
    pass

# --- UI Components ---
def display_trust_confidence():
    """Fetches and displays the Trust & Confidence score on the dashboard."""
    st.header("Trust & Confidence")
    confidence_data = api_request("get", "analytics/confidence")

    if confidence_data is None:
        st.warning("Could not retrieve confidence score. Some metrics may be unavailable.")
        return

    level = confidence_data.get("confidence_level", "Unknown")
    score = confidence_data.get("confidence_score", 0)
    signals = confidence_data.get("signals", [])

    color_map = {"High": "green", "Medium": "orange", "Low": "red"}
    
    if level == "Low":
        st.warning(f"**Low System Confidence ({score}%)**: Data quality or freshness is poor. Insights may be unreliable.", icon="⚠️")

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Confidence Level", value=level, delta=f"{score}%", delta_color="off")
        st.markdown(f"<span style='color:{color_map.get(level, 'grey')}; font-size: 1.2em;'>●</span> {level}", unsafe_allow_html=True)

    with col2:
        with st.expander("View Confidence Signals"):
            if signals:
                for signal in signals:
                    st.markdown(f"- {signal}")
            else:
                st.info("No specific signals available.")

def setup_sidebar():
    st.sidebar.title("ProSi-mini")
    
    # --- DEV AUTH BYPASS – REMOVE BEFORE PRODUCTION ---
    if DEV_MODE_BYPASS_AUTH:
        st.sidebar.warning("Auth Bypassed (DEV)")
        st.sidebar.info(f"Role: **{st.session_state.user_role.replace('_', ' ').title()}**")
        st.sidebar.markdown("---")
        render_navigation()
        return
    # --- END DEV AUTH BYPASS ---

    if not st.session_state.is_authenticated:
        st.sidebar.header("Login")
        st.sidebar.selectbox("Select Your Persona", ["Founder / Executive", "Sales Manager", "Operations / CRM Manager"], key="persona")
        st.sidebar.button("Login", on_click=handle_login, use_container_width=True)
    else:
        st.sidebar.success(f"Logged in as: **{st.session_state.user_role.replace('_', ' ').title()}**")
        st.sidebar.button("Logout", on_click=handle_logout, use_container_width=True)
        st.sidebar.markdown("---")
        render_navigation()

def render_navigation():
    # ... (existing code remains the same)
    pass

# --- Main Application ---
def main():
    initialize_session_state()
    setup_sidebar()

    if st.session_state.is_authenticated:
        if st.session_state.active_page == "Dashboard":
            st.title("📊 Main Dashboard")
            display_trust_confidence()
            st.markdown("---")
            st.write("Other dashboard components will go here.")
        elif st.session_state.active_page == "Governance & Audit":
            st.title("⚖️ Governance & Audit")
        elif st.session_state.active_page == "Ingestion":
            st.title("📥 Data Ingestion")
    else:
        st.info("Please log in using the sidebar to continue.")

if __name__ == "__main__":
    main()
