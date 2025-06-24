import streamlit as st
from base64 import b64encode
from ncc_utils import Config, read_history
from history_viewer import show_history_viewer_full
import os
from config import DATA_DIR, PROFILE_ICON, LOGO_SVG, CHAT_ICON, NCC_HANDBOOK_PDF
import logging

def show_profile_page():
    try:
        profile = st.session_state.get("profile", {})
        icon_path = PROFILE_ICON
        with open(icon_path, "rb") as f:
            icon_b64 = b64encode(f.read()).decode()
        st.markdown("""
            <style>
            .profile-header {
                display: flex;
                align-items: center;
                gap: 1rem;
                margin-bottom: 1.5rem;
            }
            .profile-header img {
                height: 3rem;
                width: 3rem;
                border-radius: 50%;
                border: 2px solid #6366F1;
                background: #EEF2FF;
            }
            .profile-header .profile-name {
                font-size: 1.3rem;
                font-weight: 600;
            }
            </style>
        """, unsafe_allow_html=True)
        st.markdown(f'''<div class="profile-header">
            <img src="data:image/svg+xml;base64,{icon_b64}" alt="Profile">
            <span class="profile-name">{profile.get('name', 'Cadet')}</span>
        </div>''', unsafe_allow_html=True)
        tabs = st.tabs(["Personal Information", "History Viewer", "Progress Dashboard"])
        with tabs[0]:
            st.subheader("Personal Information")
            st.write(f"**Name:** {profile.get('name', 'N/A')}")
            st.write(f"**Email:** {profile.get('email', 'N/A')}")
            st.write(f"**Regimental No.:** {profile.get('reg_no', 'N/A')}")
            st.write(f"**Mobile:** {profile.get('mobile', 'N/A')}")
            st.write(f"**Role:** {profile.get('role', 'cadet')}")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Logout", key="profile_logout_btn"):
                from login_interface import logout
                logout()
        with tabs[1]:
            try:
                show_history_viewer_full()
            except Exception as hist_err:
                logging.exception("Profile history viewer error:")
                st.error(f"An error occurred in the history viewer: {hist_err}")
        with tabs[2]:
            try:
                from progress_dashboard import display_progress_dashboard
                quiz_history_raw = read_history("quiz_score")
                import json
                display_progress_dashboard(st.session_state, json.dumps(quiz_history_raw))
            except Exception as dash_err:
                logging.exception("Profile progress dashboard error:")
                st.error(f"An error occurred in the progress dashboard: {dash_err}")
        # Show sync status indicator
        from sync_manager import show_sync_status
        show_sync_status()
        # Debug: Show current navigation state and profile
        nav_state = st.session_state.get("app_mode_radio_primary", st.session_state.get("app_mode"))
        st.write("[DEBUG] navigation state:", nav_state)
        st.write("[DEBUG] profile:", profile)
    except Exception as e:
        logging.exception("Profile page error:")
        st.error(f"An error occurred in the profile page: {e}")
