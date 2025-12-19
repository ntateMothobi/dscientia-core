import streamlit as st
import requests
import logging

# --- Configuration & Initialization ---
API_BASE_URL = "http://127.0.0.1:8000/api/v1"
logging.basicConfig(level=logging.INFO)

# --- FINALIZATION: Auth bypass is permanently disabled ---
DEV_MODE_BYPASS_AUTH = False

st.set_page_config(page_title="ProSi-mini", page_icon="🏠", layout="wide")

def init_session_state():
    """
    Initializes all required keys in st.session_state for the application.
    """
    defaults = {
        "is_authenticated": False,
        "access_token": None,
        "user_role": None,
        "persona": "Founder / Executive",
        "active_page": "Dashboard",
        "dashboard_loaded": False,
        "recommendations_data": None,
        "confidence_data": None,
        "last_error": None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def map_persona_to_role(persona: str) -> str:
    return {
        "Founder / Executive": "founder",
        "Sales Manager": "sales_manager",
        "Operations / CRM Manager": "ops_crm",
        "Viewer": "viewer"
    }.get(persona, "viewer")

def api_request(method, endpoint, **kwargs):
    """Centralized function for making authenticated API requests."""
    headers = kwargs.pop("headers", {})
    if st.session_state.get("access_token"):
        headers["Authorization"] = f"Bearer {st.session_state.access_token}"
    
    url = f"{API_BASE_URL}/{endpoint}"
    try:
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code in [401, 403]:
            st.session_state.last_error = "Authentication failed or forbidden. Please log in again."
            handle_logout()
        else:
            st.session_state.last_error = f"API Error: {e.response.status_code} on {endpoint}"
        return None
    except requests.exceptions.RequestException as e:
        st.session_state.last_error = f"Connection Error: {e}"
        return None

def handle_login():
    persona = st.session_state.persona
    if not persona:
        return
    with st.spinner("Authenticating..."):
        try:
            response = requests.post(f"{API_BASE_URL}/auth/login", json={"persona": persona})
            response.raise_for_status()
            data = response.json()
            if data and "access_token" in data:
                st.session_state.is_authenticated = True
                st.session_state.access_token = data["access_token"]
                st.session_state.user_role = map_persona_to_role(persona)
                st.session_state.dashboard_loaded = False
                st.session_state.last_error = None
                st.rerun()
        except requests.exceptions.RequestException as e:
            st.error(f"Login failed: {e}")

def handle_logout():
    keys_to_reset = list(st.session_state.keys())
    for key in keys_to_reset:
        del st.session_state[key]
    st.cache_data.clear()
    st.cache_resource.clear()
    st.rerun()

def load_dashboard_data():
    st.session_state.recommendations_data = api_request("get", "decisions/recommendations")
    st.session_state.confidence_data = api_request("get", "analytics/confidence")
    if st.session_state.last_error is None:
        st.session_state.dashboard_loaded = True

def render_recommendations(recommendations):
    st.header("Recommended Actions")
    if not recommendations:
        st.info("✅ No critical actions needed at this time.")
        return

    for rec in recommendations:
        with st.container(border=True):
            st.markdown(f"**{rec['title']}**")
            st.caption(f"Confidence: {rec['confidence']}% | Suggested Owner: {rec['suggested_owner']}")
            st.write(rec['recommendation'])

            if rec.get('overridden'):
                override_details = rec.get('override_details', {})
                st.warning(f"Overridden by **{override_details.get('by', 'N/A')}**.", icon="⚠️")
                with st.expander("View Override Details"):
                    st.write(f"**Reason:** {override_details.get('reason', 'No reason provided.')}")
                    st.write(f"**Final Decision:** {rec.get('final_decision', 'N/A')}")
            
            if st.session_state.user_role in ['founder', 'ops_crm'] and not rec.get('overridden'):
                with st.form(key=f"override_form_{rec['id']}"):
                    new_decision = st.text_input("New Decision", key=f"decision_{rec['id']}")
                    reason = st.text_area("Reason for Override", key=f"reason_{rec['id']}")
                    submitted = st.form_submit_button("Submit Override")

                    if submitted and new_decision and reason:
                        with st.spinner("Processing override..."):
                            response = api_request(
                                "post",
                                f"decisions/{rec['id']}/override",
                                params={"new_decision": new_decision, "override_reason": reason}
                            )
                            if response:
                                st.success("Override successful!")
                                st.rerun()
                            else:
                                st.error("Failed to process override.")

def render_trust_confidence(confidence_data):
    st.header("Trust & Confidence")
    if not confidence_data:
        st.warning("Confidence data unavailable.")
        return
    # ... (rest of rendering logic)

def render_navigation():
    PAGES = {"Dashboard": "📊"}
    if st.session_state.user_role in ["founder", "ops_crm"]:
        PAGES["Governance & Audit"] = "⚖️"
    if st.session_state.user_role == "ops_crm":
        PAGES["Ingestion"] = "📥"

    for page, icon in PAGES.items():
        if st.sidebar.button(f"{icon} {page}", use_container_width=True, key=f"nav_{page}"):
            st.session_state.active_page = page
            if page != "Dashboard":
                st.session_state.dashboard_loaded = False
            st.rerun()

def setup_sidebar():
    st.sidebar.title("ProSi-mini")
    if st.session_state.is_authenticated:
        st.sidebar.success(f"Logged in as: **{st.session_state.user_role.replace('_', ' ').title()}**")
        st.sidebar.button("Logout", on_click=handle_logout, use_container_width=True)
        st.sidebar.markdown("---")
        render_navigation()
    else:
        st.sidebar.header("Login")
        st.sidebar.selectbox(
            "Select Your Persona",
            ["Founder / Executive", "Sales Manager", "Operations / CRM Manager", "Viewer"],
            key="persona"
        )
        st.sidebar.button("Login", on_click=handle_login, use_container_width=True)

def main():
    init_session_state()
    setup_sidebar()

    if not st.session_state.is_authenticated:
        st.info("Please log in using the sidebar to continue.")
        st.stop()

    if st.session_state.last_error:
        st.error(f"An error occurred: {st.session_state.last_error}")
        if st.button("Retry"):
            st.session_state.last_error = None
            st.rerun()
        st.stop()

    if st.session_state.active_page == "Dashboard":
        if not st.session_state.dashboard_loaded:
            with st.spinner("Loading dashboard..."):
                load_dashboard_data()
            st.rerun()
        
        st.title("📊 Main Dashboard")
        render_recommendations(st.session_state.recommendations_data)
        st.markdown("---")
        render_trust_confidence(st.session_state.confidence_data)

    elif st.session_state.active_page == "Governance & Audit":
        st.title("⚖️ Governance & Audit")
        st.write("Governance content goes here.")
    elif st.session_state.active_page == "Ingestion":
        st.title("📥 Data Ingestion")
        st.write("Ingestion controls go here.")

if __name__ == "__main__":
    main()
