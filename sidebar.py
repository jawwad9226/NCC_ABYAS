import streamlit as st
from base64 import b64encode
from core_utils import Config
from config import PROFILE_ICON
import os

def render_sidebar_profile():
    profile = st.session_state.get("profile", {})
    profile_icon_path = PROFILE_ICON
    with open(profile_icon_path, "rb") as f:
        profile_icon_b64 = b64encode(f.read()).decode()

    st.sidebar.markdown("""
    <style>
    header[data-testid="stSidebarNav"] { display: none; }
    section[data-testid="stSidebar"] > div { padding-top: 0 !important; }
    .profile-container { display: flex; flex-direction: column; align-items: center; padding: 1.5rem 1rem 1rem 1rem; margin: -1rem -1rem 1rem -1rem; border-bottom: 1px solid rgba(99, 102, 241, 0.2); background: rgba(99, 102, 241, 0.05); }
    .profile-icon { position: relative; width: 80px; height: 80px; border-radius: 50%; border: 3px solid #6366F1; background: #EEF2FF; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25); margin-bottom: 0.8rem; overflow: hidden; transition: transform 0.2s ease, box-shadow 0.2s ease; display: flex; align-items: center; justify-content: center; }
    .profile-icon img { width: 100%; height: 100%; object-fit: cover; }
    .profile-name { font-weight: 600; font-size: 1.2rem; line-height: 1.2; text-align: center; }
    .profile-role { font-size: 1rem; color: #6366F1; margin-top: 0.2rem; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

    st.sidebar.markdown(f'''
        <div class="profile-container">
            <div class="profile-icon">
                <img src="data:image/svg+xml;base64,{profile_icon_b64}" alt="Profile">
            </div>
            <div class="profile-name">{profile.get('name','Cadet')}</div>
            <div class="profile-role">{profile.get('role','cadet').capitalize()}</div>
        </div>
    ''', unsafe_allow_html=True)
