import streamlit as st
from video_guides import show_video_admin_tab

def show_instructor_dashboard():
    st.title("Instructor Dashboard")
    st.markdown("---")
    st.subheader("Video Management")
    show_video_admin_tab()
    # Future: Add more instructor tools as new tabs/sections here
