import streamlit as st
import os
import json
import requests
from functools import partial
from typing import Optional
import base64
import subprocess
import socket
import time
from datetime import datetime
# Core streamlit imports
from streamlit_pdf_viewer import pdf_viewer
import streamlit_browser_storage as stbs
from streamlit_browser_storage.local_storage import LocalStorage

# --- Inject sidebar width CSS at the very top for consistency ---
st.markdown("""
<style>
/* Desktop: wider sidebar for readability */
@media (min-width: 600px) {
    section[data-testid="stSidebar"] {
        min-width: 300px !important;
        width: 320px !important;
        max-width: 350px !important;
    }
}
/* Mobile/PWA: allow sidebar to be narrower */
@media (max-width: 599px) {
    section[data-testid="stSidebar"] {
        min-width: 60vw !important;
        width: 70vw !important;
        max-width: 90vw !important;
    }
}
</style>
""", unsafe_allow_html=True)

from core_utils import Config
from utils.logging_utils import log_info, log_warning, log_error
# Local imports
from core_utils import (
    setup_gemini,
    get_ncc_response,
    API_CALL_COOLDOWN_MINUTES,
    clear_history, # Use the centralized clear_history
    read_history
)
from src.utils import ( # type: ignore
    apply_theme,
    get_theme_config
)
from video_guides import show_video_guides
from quiz_interface import quiz_interface
from login_interface import login_interface
from admin_tools import show_admin_dashboard
from profile_interface import show_profile_page
from sidebar import render_sidebar_profile
from syllabus_interface import show_syllabus_viewer
from history_viewer import show_history_viewer_full
from progress_dashboard import display_progress_dashboard
from auth_manager import restore_session
from sync_manager import sync_to_cloud

# Print version info once
if "version_info_printed" not in st.session_state:
    log_info(f"Streamlit version: {st.__version__}")
    log_info(f"Streamlit file: {st.__file__}")
    st.session_state.version_info_printed = True

def get_image_as_base64(image_path):
    """Convert an image (PNG or SVG) to base64 data URL."""
    with open(image_path, "rb") as img_file:
        base64_string = base64.b64encode(img_file.read()).decode('utf-8')
        # Determine MIME type based on file extension
        if image_path.lower().endswith('.png'):
            mime_type = 'image/png'
        elif image_path.lower().endswith('.svg'):
            mime_type = 'image/svg+xml'
        else:
            mime_type = 'image/*' # Generic fallback
        return f"data:{mime_type};base64,{base64_string}"

# --- DEBUG: Show id_token and user_id at the top of the app ---
# --- Restore id_token from localStorage using restore_session() ---
restore_session()
# (Debug prints removed for production)
# --- Token-based session restore: check /verify_session on app load ---
if not st.session_state.get("user_id") and st.session_state.get("id_token"):
    try:
        resp = requests.get(
            "https://nccabyas.up.railway.app/verify_session",
            headers={"Authorization": f"Bearer {st.session_state['id_token']}"},
            timeout=5
        )
        data = resp.json()
        if data.get("success"):
            st.session_state["user_id"] = data.get("uid")
            st.session_state["profile"] = data.get("profile")
            st.session_state["role"] = data.get("profile", {}).get("role", "cadet")
            st.rerun()
    except Exception:
        pass

# Inject PWA manifest and service worker registration
st.markdown(
    '''
    <link rel="manifest" href="/data/manifest.json">
    <script>
      if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/data/service-worker.js');
      }
    </script>
    ''',
    unsafe_allow_html=True
)

API_COOLDOWN_SECONDS = 10

def _check_and_reset_api_cooldown():
    if st.session_state.get("api_cooldown_active", False):
        current_time = datetime.now()
        last_time = st.session_state.get("api_cooldown_last_time")
        if last_time:
            time_diff = (current_time - last_time).total_seconds()
            time_remaining = max(0, API_COOLDOWN_SECONDS - time_diff)
            st.session_state["api_cooldown_time_remaining"] = int(time_remaining)
            if time_remaining <= 0:
                st.session_state["api_cooldown_active"] = False
                st.session_state["api_cooldown_time_remaining"] = 0

# --- Main app logic ---
def main():
    """
    Main entry point for the NCC ABYAS application.
    Handles overall structure, navigation, theme, and routing to different features.
    """
    # --- Apply theme at the very top ---
    apply_theme(st.session_state.get("theme_mode", "Dark"))

    # Handle query parameters for chat navigation
    if st.query_params.get("go_chat") or st.query_params.get("open_chat") or st.query_params.get("hash") == ["open_chat"]:
        st.session_state.app_mode = "💬 Chat Assistant"
        st.query_params.clear()
        st.rerun()
    
    # Create a placeholder for the floating button at the top level.
    floating_button_placeholder = st.empty()

    # Initialize app_mode session state if not exists (single state variable for navigation)
    if "app_mode" not in st.session_state:
        st.session_state.app_mode = "🎯 Knowledge Quiz"
    
    # Initialize Gemini model first
    model, model_error = setup_gemini()
    
    # Apply custom header spacing
    st.markdown("""
        <style>
        .app-header {
            padding: 1rem 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(128, 128, 128, 0.2);
            margin-bottom: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- Custom Header ---
    # Prepare logo and theme variables for header
    logo_path = os.path.join(Config.DATA_DIR, "logo.svg") # Use SVG logo
    logo_base64_data_url = get_image_as_base64(logo_path)
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "Dark"
    current_theme = st.session_state.get("theme_mode", "Dark")
    theme_icon = "☀️" if current_theme == "Dark" else "🌙"
    theme_tooltip = "Switch to Light Theme" if current_theme == "Dark" else "Switch to Dark Theme"
    st.markdown("""
        <style>
        .app-header-flex {
            display: flex;
            align-items: center;
            justify-content: space-between;
            width: 100%;
            gap: 1rem;
        }
        @media (max-width: 600px) {
            .app-header-flex h1 {
                font-size: 1.1rem !important;
            }
            .app-header-flex img {
                height: 1.5rem !important;
            }
        }
        </style>
    """, unsafe_allow_html=True)
    # Use Streamlit columns to place the theme toggle button in the header
    header_col1, header_col2 = st.columns([8, 1])
    with header_col1:
        st.markdown(
            f'''
            <div class="app-header-flex">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <img src="{logo_base64_data_url}" style="height: 2rem; width: auto;">
                    <h1 style="margin:0;font-size:1.25rem">NCC ABYAS</h1>
                </div>
            </div>
            ''', unsafe_allow_html=True
        )
    with header_col2:
        if st.button(theme_icon, key="theme_toggle_btn", help=theme_tooltip):
            st.session_state.theme_mode = "Light" if current_theme == "Dark" else "Dark"
            st.rerun()

    # --- AUTH: Show login/registration before app content if no user_id or id_token ---
    if not st.session_state.get("user_id") or not st.session_state.get("id_token"):
        if st.session_state.get("id_token") and not st.session_state.get("user_id"):
            pass  # Session restore in progress
        else:
            login_interface()
        st.stop()

    # --- Sidebar Profile Icon (Full Header Style) ---
    render_sidebar_profile()

    # --- Navigation Sidebar ---
    navigation_options = [
        "👤 Profile", "💬 Chat Assistant", "🎯 Knowledge Quiz", "📚 Syllabus Viewer", "🎥 Video Guides", "📁 History Viewer", "📊 Progress Dashboard"
    ]
    if st.session_state.get("role") == "admin":
        navigation_options.append("🛡️ Admin Dashboard")
    if st.session_state.get("role") in ["admin", "instructor"]:
        navigation_options.append("👨‍🏫 Instructor Dashboard")
    navigation_options.append("🛠️ Dev Tools")

    # On first load, set session state for app_mode
    if "app_mode" not in st.session_state:
        st.session_state.app_mode = "🎯 Knowledge Quiz"

    try:
        current_index = navigation_options.index(st.session_state.app_mode)
    except ValueError:
        current_index = 0

    app_mode = st.sidebar.radio(
        label="Navigation Menu",  # Add proper label for accessibility
        options=navigation_options,
        index=current_index,  # Select current mode with safe index
        key="app_mode_radio_primary",
    )

    st.sidebar.markdown("---")
    st.sidebar.info(f"API Cooldown: Please wait ~{API_CALL_COOLDOWN_MINUTES} min. if you hit rate limits.")
    st.sidebar.markdown("---") # Separator
    # Feedback button and form directly after API cooldown info
    if st.sidebar.button("💬 Feedback / Error Report", key="sidebar_feedback_btn"):
        st.session_state["show_feedback_tab"] = True
    if st.session_state.get("show_feedback_tab"):
        from feedback_interface import show_feedback_section
        st.sidebar.markdown("---")
        show_feedback_section()
        st.session_state["show_feedback_tab"] = False
    # Remove all navigation buttons (reset, dev tools, back, etc.)
    st.sidebar.markdown("<small>By using this app, you agree to our <a href='https://yourdomain.com/privacy' target='_blank'>Privacy Policy</a> and <a href='https://yourdomain.com/terms' target='_blank'>Terms of Service</a>." , unsafe_allow_html=True)

    # --- On login/app start, sync any queued data ---
    sync_to_cloud()

    # --- Module Routing ---
    if app_mode == "👤 Profile":
        show_profile_page()
        return
    elif app_mode == "🛡️ Admin Dashboard":
        show_admin_dashboard()
    elif app_mode == "📊 Progress Dashboard":
        # Show own progress for all users, including admins
        user_id = st.session_state.get("user_id")
        from ncc_utils import read_history
        quiz_score_history = read_history("quiz_score")
        if not isinstance(quiz_score_history, list):
            quiz_score_history = []
        quiz_history_raw_string = json.dumps(quiz_score_history)
        display_progress_dashboard(st.session_state, quiz_history_raw_string)
    elif app_mode == "💬 Chat Assistant":
        from chat_interface import chat_interface # Lazy import
        chat_func = partial(get_ncc_response, model, model_error)
        chat_interface()

    elif app_mode == "🎯 Knowledge Quiz":
        from quiz_interface import _initialize_quiz_state, quiz_interface # Lazy imports
        _initialize_quiz_state(st.session_state) # Always initialize quiz state first
        if model: # model is from setup_gemini() at the top of main()
            quiz_interface(model, model_error) # Pass model and model_error

    elif app_mode == "📚 Syllabus Viewer":
        show_syllabus_viewer()

    elif app_mode == "🎥 Video Guides":
        show_video_guides()

    elif app_mode == "📁 History Viewer":
        show_history_viewer_full()

    elif app_mode == "📊 Progress Dashboard":
        quiz_history_raw = read_history("quiz_score")
        display_progress_dashboard(st.session_state, quiz_history_raw)
    elif app_mode == "🛠️ Dev Tools":
        from dev_tools import dev_tools as display_dev_tools
        display_dev_tools()
        return
    elif app_mode == "👨‍🏫 Instructor Dashboard":
        if st.session_state.get("role") in ["admin", "instructor"]:
            from instructor_tools import show_instructor_dashboard
            show_instructor_dashboard()
    else:
        pass  # Unknown app mode, do nothing for production

    # --- API Request Flow Example ---
    # Before making an API request (e.g., in quiz_interface, main, or any API call):
    _check_and_reset_api_cooldown()
    if st.session_state.get("api_cooldown_active", False):
        st.warning(f"⏳ API Cooldown active: {st.session_state['api_cooldown_time_remaining']} seconds remaining before you can make another request.")
    else:
        # ...existing code for making API request...
        st.session_state["api_cooldown_active"] = True
        st.session_state["api_cooldown_last_time"] = datetime.now()

if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # Suppress error display for production