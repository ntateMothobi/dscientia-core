import streamlit as st
import requests
import logging
import json

# --- Configuration & Initialization ---
API_BASE_URL = "http://127.0.0.1:8000/api/v1"
logging.basicConfig(level=logging.INFO)

# --- FINALIZATION: Auth bypass is permanently disabled ---
DEV_MODE_BYPASS_AUTH = False

st.set_page_config(page_title="DscienTia Core", page_icon="🧠", layout="wide")

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
        "simulation_result": None,
        "learning_insights": None,
        "pending_reviews": None, # Added for D5.6
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
    st.session_state.learning_insights = api_request("get", "learning/insights")
    if st.session_state.user_role in ["founder", "ops_crm"]:
        st.session_state.pending_reviews = api_request("get", "learning/reviews/pending")
    if st.session_state.last_error is None:
        st.session_state.dashboard_loaded = True

def render_recommendations(recommendations):
    st.header("🧠 Decision Recommendations")
    if not recommendations:
        st.success("✅ No critical decisions needed.")
        return

    for rec in recommendations:
        with st.container(border=True):
            st.markdown(f"**{rec['title']}**")
            st.caption(f"Priority: **{rec['priority']}** | Confidence: **{rec['confidence']}%** | Owner: **{rec['suggested_owner']}**")
            st.write(rec['recommendation'])

            # --- D5.5: Human-in-the-Loop Feedback ---
            col_approve, col_reject = st.columns([1, 1])
            with col_approve:
                if st.button("Approve", key=f"approve_{rec['id']}", use_container_width=True):
                    with st.spinner("Recording approval..."):
                        api_request(
                            "post",
                            "learning/feedback",
                            json={
                                "recommendation_id": str(rec['id']),
                                "recommendation_title": rec['title'],
                                "decision": "approved",
                                "reason": "User approved via dashboard"
                            }
                        )
                        st.success("Approved!")
                        st.rerun()
            
            with col_reject:
                if st.button("Reject", key=f"reject_{rec['id']}", use_container_width=True):
                    with st.spinner("Recording rejection..."):
                        api_request(
                            "post",
                            "learning/feedback",
                            json={
                                "recommendation_id": str(rec['id']),
                                "recommendation_title": rec['title'],
                                "decision": "rejected",
                                "reason": "User rejected via dashboard"
                            }
                        )
                        st.warning("Rejected!")
                        st.rerun()
            # ----------------------------------------

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
            
            # Explainability Section
            if rec.get('explanation'):
                with st.expander("Why am I seeing this?"):
                    st.markdown(f"**Summary:** {rec['explanation'].get('summary')}")
                    if rec['explanation'].get('contributing_factors'):
                        st.markdown("**Contributing Factors:**")
                        for factor in rec['explanation']['contributing_factors']:
                            st.markdown(f"- {factor}")

def render_learning_insights(insights):
    """
    Renders the D5.5 Learning Insights section.
    """
    st.header("📚 Learning Insights (Read-Only)")
    if not insights:
        st.info("No learning data available yet.")
        return

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Rejection Rate", f"{insights.get('rejection_rate', 0)}%")
        st.caption(f"Based on {insights.get('total_decisions', 0)} decisions")

    with col2:
        st.metric("Override Frequency", f"{insights.get('override_frequency', 0)}%")

    with col3:
        # Simple drift logic for display
        rr = insights.get('rejection_rate', 0)
        drift = "LOW" if rr < 20 else "MEDIUM" if rr < 50 else "HIGH"
        color = "green" if drift == "LOW" else "orange" if drift == "MEDIUM" else "red"
        st.markdown(f"**Confidence Drift:** :{color}[{drift}]")
        st.caption("Drift based on rejection frequency")

    with col4:
        # Check for bias
        bias_map = insights.get('approval_rate_by_persona', {})
        # Simple heuristic: if any persona has < 35% approval (meaning > 65% rejection/override)
        biased = [p for p, rate in bias_map.items() if rate < 35]
        if biased:
            st.error("⚠️ Persona Bias Detected!")
            st.caption(f"Potential bias against: {', '.join(biased)}")
        else:
            st.success("✅ No Persona Bias Detected")

def render_learning_reviews(reviews):
    """
    Renders the D5.6 Learning Review Panel.
    """
    st.header("🧐 Learning Review & Approval")
    
    if st.button("Generate New Review Proposal", use_container_width=True):
        with st.spinner("Generating proposal..."):
            api_request("post", "learning/review/generate")
            st.rerun()

    if not reviews:
        st.info("No pending learning reviews.")
        return

    for review in reviews:
        with st.container(border=True):
            st.subheader(f"{review['insight_type']} (ID: {review['id']})")
            st.write(review['summary'])
            
            with st.expander("View Metrics Snapshot"):
                st.json(review['metrics'])
            
            with st.form(key=f"review_form_{review['id']}"):
                notes = st.text_area("Reviewer Notes", placeholder="Enter justification for approval/rejection...")
                col1, col2 = st.columns(2)
                with col1:
                    approve = st.form_submit_button("✅ Approve Insights", use_container_width=True)
                with col2:
                    reject = st.form_submit_button("❌ Reject Insights", use_container_width=True)
                
                if approve:
                    with st.spinner("Approving..."):
                        api_request("post", f"learning/review/{review['id']}/approve", params={"notes": notes})
                        st.success("Review Approved!")
                        st.rerun()
                
                if reject:
                    with st.spinner("Rejecting..."):
                        api_request("post", f"learning/review/{review['id']}/reject", params={"notes": notes})
                        st.warning("Review Rejected!")
                        st.rerun()

def render_trust_confidence(confidence_data):
    st.header("Trust & Confidence")
    if not confidence_data:
        st.warning("Confidence data unavailable.")
        return

    level = confidence_data.get("level", "Unknown")
    score = confidence_data.get("score", 0)
    guidance = confidence_data.get("decision_guidance", "Guidance unavailable.")
    icon_map = {"HIGH": "✅", "MEDIUM": "⚠️", "LOW": "⛔️"}
    
    st.metric(label="Confidence Level", value=level, delta=f"{score}%", delta_color="off")
    st.write(f"**{icon_map.get(level, '⚪️')} {guidance}**")

    with st.expander("Why am I seeing this?"):
        summary = confidence_data.get("explanation_summary")
        details = confidence_data.get("explanation_details", [])
        if summary:
            st.markdown(f"**Summary:** {summary}")
            if details:
                st.markdown("---")
                st.markdown("**Key Drivers:**")
                for bullet in details:
                    st.markdown(f"- {bullet}")
        else:
            st.info("Detailed explanation is currently unavailable.")

def render_scenario_simulator():
    st.header("🔮 What-If Scenario Simulator")
    
    with st.container(border=True):
        st.subheader("Adjust Metrics")
        col1, col2 = st.columns(2)
        with col1:
            sla_delta = st.slider("SLA Breach Improvement (%)", -50, 50, 0, 5, key="sim_sla")
        with col2:
            rt_delta = st.slider("Response Time Improvement (%)", -50, 50, 0, 5, key="sim_rt")

        if st.button("Run Simulation", use_container_width=True, type="primary"):
            payload = {
                "overrides": {
                    "duplicate_rate": sla_delta / 100,
                    "avg_response_time": rt_delta / 100
                }
            }
            with st.spinner("Calculating impact..."):
                st.session_state.simulation_result = api_request("post", "analytics/simulate", json=payload)

    with st.container():
        if not st.session_state.simulation_result:
            st.info("Run simulation to see results.")
        else:
            res = st.session_state.simulation_result
            st.subheader("Simulation Impact")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("##### Baseline")
                st.metric(label=f"Risk Score ({res['baseline']['decision']})", value=res['baseline']['risk_score'])
            with col2:
                st.markdown("##### Simulated")
                st.metric(label=f"Risk Score ({res['simulated']['decision']})", value=res['simulated']['risk_score'], delta=res['impact']['risk_delta'], delta_color="inverse")
            if res['impact']['decision_changed']:
                st.success(f"✅ Decision level improved from **{res['baseline']['decision']}** to **{res['simulated']['decision']}**.")
            else:
                st.info("No change in overall decision level.")

def render_navigation():
    PAGES = {"Dashboard": "📊"}
    if st.session_state.user_role in ["founder", "ops_crm"]:
        PAGES["Governance & Audit"] = "⚖️"
        PAGES["Learning Review"] = "🧐" # Added for D5.6
    if st.session_state.user_role == "ops_crm":
        PAGES["Ingestion"] = "📥"

    for page, icon in PAGES.items():
        if st.sidebar.button(f"{icon} {page}", use_container_width=True, key=f"nav_{page}"):
            st.session_state.active_page = page
            if page != "Dashboard":
                st.session_state.dashboard_loaded = False
            st.rerun()

def setup_sidebar():
    st.sidebar.title("DscienTia Core")
    st.sidebar.caption("Decision Intelligence Core Platform")
    st.sidebar.caption("Property Sales as First Vertical")
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
        
        st.title("🧠 DscienTia Core")
        st.caption("Decision Intelligence Core Platform · Property Sales as First Vertical")
        render_recommendations(st.session_state.recommendations_data)
        st.markdown("---")
        render_learning_insights(st.session_state.learning_insights)
        st.markdown("---")
        render_trust_confidence(st.session_state.confidence_data)
        st.markdown("---")
        if st.session_state.user_role in ["founder", "ops_crm"]:
             render_scenario_simulator()

    elif st.session_state.active_page == "Learning Review":
        if not st.session_state.dashboard_loaded:
             with st.spinner("Loading reviews..."):
                 load_dashboard_data()
             st.rerun()
        render_learning_reviews(st.session_state.pending_reviews)

    elif st.session_state.active_page == "Governance & Audit":
        st.title("⚖️ Governance & Audit")
        st.write("Governance content goes here.")
    elif st.session_state.active_page == "Ingestion":
        st.title("📥 Data Ingestion")
        st.write("Ingestion controls go here.")

if __name__ == "__main__":
    main()
