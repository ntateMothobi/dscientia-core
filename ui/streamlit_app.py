import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json
import logging
import time

# --- Configuration & Initialization ---
API_BASE_URL = "http://127.0.0.1:8000/api/v1"
logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="Property Sales Intelligence", page_icon="🏠", layout="wide")


# 1. Initialize state safely at the very beginning
def initialize_session_state():
    """Initializes all required session state keys to prevent KeyErrors."""
    defaults = {
        "persona": "Founder / Executive",
        "active_page": "Dashboard",
        "last_ingestion_summary": None,
        "debug_mode": False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# --- Production-Safe Debugging ---
DEBUG = st.session_state.get("debug_mode", False)


def debug_log(message: str, data=None):
    """Logs a debug message and optional data only if debug mode is enabled."""
    if DEBUG:
        st.markdown(f"🐞 **DEBUG:** {message}")
        if data:
            st.json(data)


# --- Data Fetching & Actions ---
@st.cache_data(ttl=30)
def fetch_api_data(endpoint: str):
    """A single, robust function to fetch data from any API endpoint."""
    debug_log(f"Fetching API data from: {endpoint}")
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}", timeout=5)
        response.raise_for_status()
        data = response.json()
        debug_log(f"SUCCESS fetching from: {endpoint}", data)
        return data
    except requests.exceptions.RequestException as e:
        logging.error(f"API call to {endpoint} failed: {e}")
        debug_log(f"FAILED fetching from: {endpoint}", {"error": str(e)})
        return None


def clear_all_caches():
    """Clears Streamlit's data cache and resets relevant session state."""
    debug_log("Clearing all caches...")
    st.cache_data.clear()
    # FIX: Isolate cache by resetting session state that depends on cached data
    st.session_state["last_ingestion_summary"] = None
    st.toast("Cache cleared!", icon="✅")


def run_ingestion():
    # ... (ingestion logic using on_click, no changes needed)
    pass


# --- UI Rendering Components ---

def render_section_error(section_name: str, key_suffix: str, error: Exception):
    """Renders a consistent error message for a failed UI section."""
    st.error(f"⚠️ {section_name} failed to render.")
    if DEBUG:
        st.exception(error)  # Show full exception only in debug mode
    if st.button(f"Retry {section_name}", key=f"retry_button_{key_suffix}"):
        st.rerun()


def safe_render(section_name: str, render_fn, *args, **kwargs):
    """
    A helper utility to wrap each dashboard section, ensuring one section's
    failure does not crash the entire page.
    """
    try:
        render_fn(*args, **kwargs)
    except Exception as e:
        render_section_error(section_name, section_name.lower().replace(" ", "_"), e)


def display_insight_confidence_panel():
    """Null-safe rendering of the insight confidence panel."""
    report = fetch_api_data("analytics/insight_quality")

    # FIX: Null-safe rendering pattern
    if not report:
        st.warning("Insight Quality report is currently unavailable.")
        return

    level = report.get("confidence_level", "Unknown")
    score = report.get("score", 0)

    st.subheader("Insight Quality & Confidence")
    # ... (rest of the rendering logic using .get() for safety)
    with st.expander("Why this confidence level?", expanded=level != "High"):
        st.markdown("**✅ Drivers:**")
        for driver in report.get("drivers", ["N/A"]): st.markdown(f"- {driver}")
        st.markdown("**⚠️ Limitations:**")
        for limitation in report.get("limitations", ["N/A"]): st.markdown(f"- {limitation}")


def display_executive_summary():
    """Null-safe rendering of the executive summary."""
    metrics = fetch_api_data("system/metrics")
    if not metrics:
        st.warning("Executive metrics are currently unavailable.")
        return

    st.header("Executive Snapshot")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Active Leads", metrics.get("leads_count", 0))
    col2.metric("Follow-ups Logged", metrics.get("followups_count", 0))
    col3.metric("Failed Ingestions (24h)", metrics.get("failed_ingestions_last_24h", 0))


def setup_sidebar():
    with st.sidebar:
        # ... (sidebar UI with unique keys)
        st.header("Ingestion")
        if st.button("Run Mock Ingestion", key="ingest_button"):
            run_ingestion()

        st.markdown("---")
        st.checkbox("🛠️ Debug Mode", key="debug_mode")


# --- Page Implementations ---

def render_main_dashboard_page():
    st.title("🏠 Property Sales Intelligence Dashboard")

    # Use the safe_render helper for each independent section
    safe_render("Executive Summary", display_executive_summary)
    st.markdown("---")
    safe_render("Insight Confidence", display_insight_confidence_panel)
    st.markdown("---")
    # safe_render("Risk & SLA Analysis", display_risk_analysis) # etc.


def render_governance_page():
    st.title("🔐 Governance & Audit Trail")
    # ... (governance page logic)


# --- Main Application ---
def main():
    """Main application entrypoint with global error boundary."""
    try:
        initialize_session_state()

        if st.session_state.get("debug_mode"):
            st.warning("⚠️ DEBUG MODE ENABLED", icon="🐞")

        setup_sidebar()

        page_router = {
            "Dashboard": render_main_dashboard_page,
            "Governance & Audit": render_governance_page
        }

        page_to_render = st.session_state.get("active_page", "Dashboard")
        render_function = page_router.get(page_to_render)

        if render_function:
            render_function()
        else:
            st.error(f"Unknown page '{page_to_render}'. Returning to Dashboard.")
            st.session_state.active_page = "Dashboard"
            st.rerun()

    except Exception as e:
        # Global error boundary: The last line of defense.
        logging.critical(f"A critical UI failure occurred: {e}", exc_info=True)
        st.error("🚨 A critical error occurred in the application.")
        st.info("Please refresh the page or contact support if the issue persists.")
        if DEBUG:
            st.exception(e)


if __name__ == "__main__":
    main()