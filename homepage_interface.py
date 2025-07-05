import streamlit as st
import os
import base64
from datetime import datetime
from core_utils import Config

# Utility for base64 image
def get_image_as_base64(image_path):
    with open(image_path, "rb") as img_file:
        base64_string = base64.b64encode(img_file.read()).decode('utf-8')
        if image_path.lower().endswith('.png'):
            mime_type = 'image/png'
        elif image_path.lower().endswith('.svg'):
            mime_type = 'image/svg+xml'
        else:
            mime_type = 'image/*'
        return f"data:{mime_type};base64,{base64_string}"

def show_homepage():
    user_role = st.session_state.get("role", "cadet")
    profile = st.session_state.get("profile", {})
    user_name = profile.get('name', 'Cadet')
    profile_pic = profile.get('pic')  # Placeholder for future

    # --- CSS for modern, responsive layout ---
    st.markdown("""
    <style>
    body {background:#f6f7fb;}
    .fixed-header {position:fixed;top:0;left:0;width:100vw;z-index:1000;background:#fff;box-shadow:0 2px 8px rgba(99,102,241,0.08);display:none;}
    .main-title-row {width:100vw;max-width:1200px;margin:0 auto;display:flex;align-items:center;justify-content:flex-start;gap:1.2rem;padding:2.2rem 2vw 0.7rem 2vw;}
    .header-logo {width:48px;height:48px;}
    .header-title {font-size:1.7rem;font-weight:700;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
    .profile-btn-inline {margin-left:0.7rem;width:44px;height:44px;border-radius:50%;border:2px solid #6366F1;display:flex;align-items:center;justify-content:center;cursor:pointer;overflow:hidden;background:#EEF2FF;transition:box-shadow 0.2s;}
    .profile-btn-inline:hover {box-shadow:0 4px 16px rgba(99,102,241,0.18);}
    .notification-bar {width:100vw;background:linear-gradient(90deg,#667eea 0%,#764ba2 100%);color:#fff;padding:0.5rem 2.5vw;font-weight:500;overflow:hidden;white-space:nowrap;box-shadow:0 2px 8px rgba(99,102,241,0.04);}
    .notification-scroll {display:inline-block;animation:scrollText 18s linear infinite;}
    @keyframes scrollText {0%{transform:translateX(100%);}100%{transform:translateX(-100%);}}
    .banner-section {margin:1.2rem auto 0.7rem auto;padding:1.3rem 1.5rem;background:#fff;border-radius:16px;box-shadow:0 2px 12px rgba(99,102,241,0.10);position:relative;display:flex;align-items:center;gap:2.2rem;max-width:900px;min-height:120px;}
    .banner-img {width:100px;height:100px;border-radius:12px;object-fit:cover;box-shadow:0 2px 8px rgba(99,102,241,0.10);background:#eef2ff;}
    .banner-content {flex:1;min-width:0;}
    .banner-title {font-size:1.2rem;font-weight:700;color:#6366F1;margin-bottom:0.3rem;}
    .banner-desc {font-size:1.05rem;color:#333;margin-bottom:0.5rem;}
    .banner-links a {color:#6366F1;font-weight:600;text-decoration:none;margin-right:1.2rem;}
    .banner-links a:hover {text-decoration:underline;}
    .banner-toggle {position:absolute;top:1.1rem;right:1.1rem;cursor:pointer;font-size:1.2rem;background:none;border:none;}
    @media (max-width:900px) {.banner-section{flex-direction:column;gap:1.2rem;padding:1.1rem 0.7rem;}}
    @media (max-width:600px) {.main-title-row{padding:1.2rem 1vw 0.5rem 1vw;}.notification-bar{padding:0.5rem 1vw;}.banner-section{margin:1.1rem 1vw 0.6rem 1vw;}}
    .tab-nav {position:fixed;bottom:0;left:0;width:100vw;display:flex;justify-content:space-around;align-items:center;background:#fff;box-shadow:0 -2px 8px rgba(99,102,241,0.08);padding:0.5rem 0;z-index:1100;}
    .tab-nav-icon {font-size:2.1rem;color:#6366F1;opacity:0.7;transition:opacity 0.2s,color 0.2s;cursor:pointer;position:relative;padding:0.5rem 0.7rem;}
    .tab-nav-icon.active {opacity:1;color:#764ba2;}
    .tab-nav-icon:hover::after {content:attr(data-label);position:absolute;bottom:2.2rem;left:50%;transform:translateX(-50%);background:#6366F1;color:#fff;padding:0.22rem 0.8rem;border-radius:7px;font-size:0.97rem;white-space:nowrap;}
    @media (min-width:900px) {.tab-nav{top:80px;left:0;width:70px;height:calc(100vh - 80px);flex-direction:column;justify-content:flex-start;align-items:center;padding:1.2rem 0;bottom:auto;box-shadow:2px 0 8px rgba(99,102,241,0.08);}.tab-nav-icon{font-size:1.7rem;padding:0.7rem 0;}}
    </style>
    """, unsafe_allow_html=True)

    # --- Notification Bar ---
    notifications = [
        "📢 New video guides added for Drill and Ceremonies",
        "🎯 Weekly quiz challenge is now live!",
        "📚 Updated syllabus for Map Reading available",
        "⭐ Congratulations to top performers this week!"
    ]
    current_notification = notifications[datetime.now().second % len(notifications)]
    st.markdown(f"""
    <div class="notification-bar">
        <span class="notification-scroll">{current_notification}</span>
    </div>
    """, unsafe_allow_html=True)

    # --- Banner Section (collapsible, with image) ---
    logo_path = os.path.join(Config.DATA_DIR, "logo.svg")
    logo_base64 = get_image_as_base64(logo_path)
    show_banner = st.session_state.get("show_banner", True)
    # Always render the toggle button just above the banner, and update state immediately
    toggle_label = "▲ Hide Banner" if show_banner else "▼ Show Banner"
    toggle_clicked = st.button(toggle_label, key="banner_toggle", help="Show/Hide Banner")
    if toggle_clicked:
        st.session_state["show_banner"] = not show_banner
        show_banner = not show_banner
    if show_banner:
        banner_img = logo_base64  # Placeholder, can use event image
        st.markdown(f"""
        <div class="banner-section">
            <img src="{banner_img}" class="banner-img" alt="Event">
            <div class="banner-content">
                <div class="banner-title">🏆 Annual Training Camp 2025</div>
                <div class="banner-desc">Registration deadline: <b>July 15, 2025</b><br>📅 <b>Dates:</b> July 20-30, 2025<br>📍 <b>Location:</b> NCC Training Center</div>
                <div class="banner-links">
                    <a href="#">📥 Download Brochure</a>
                    <a href="#">✍️ Register Now</a>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # --- Features Section (Role-based, responsive two-column layout on all devices) ---
    try:
        import streamlit as stlib
        ctx = stlib.runtime.scriptrunner.script_run_context.get_script_run_ctx()
        user_agent = getattr(getattr(ctx.session_info, 'user_agent', ''), 'lower', lambda: '')()
        is_mobile = 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent
    except Exception:
        is_mobile = False

    # Always use two columns, but adjust spacing for mobile
    col_gap = "1.1rem" if is_mobile else "2.5rem"
    max_width = "98vw" if is_mobile else "900px"
    st.markdown(f'<div class="features-row" style="display:flex;flex-wrap:wrap;gap:{col_gap};max-width:{max_width};margin:2.2rem auto 0 auto;">', unsafe_allow_html=True)
    col1, col2 = st.columns([1.2, 1])
    with col1:
        if user_role == "admin":
            if st.button("👥 User Management", key="btn_user_mgmt"):
                st.session_state.app_mode = "🛡️ Admin Dashboard"
                st.rerun()
            if st.button("🎥 Video Management", key="btn_video_mgmt"):
                st.session_state.app_mode = "🎥 Video Guides"
                st.rerun()
            if st.button("📚 Syllabus Management", key="btn_syllabus_mgmt"):
                st.session_state.app_mode = "📚 Syllabus Viewer"
                st.rerun()
        elif user_role == "instructor":
            if st.button("🎥 Video Guides", key="btn_video_guides_instr"):
                st.session_state.app_mode = "🎥 Video Guides"
                st.rerun()
            if st.button("📚 Syllabus Content", key="btn_syllabus_content_instr"):
                st.session_state.app_mode = "📚 Syllabus Viewer"
                st.rerun()
        if st.button("📖 Syllabus Viewer", key="btn_syllabus_viewer"):
            st.session_state.app_mode = "📚 Syllabus Viewer"
            st.rerun()
        if st.button("🎯 Take Quiz", key="btn_take_quiz"):
            st.session_state.app_mode = "🎯 Knowledge Quiz"
            st.rerun()
    with col2:
        if user_role == "admin":
            if st.button("💬 Feedback Reports", key="btn_feedback_reports"):
                st.session_state.app_mode = "🛡️ Admin Dashboard"
                st.rerun()
            if st.button("📊 Overall Progress", key="btn_overall_progress"):
                st.session_state.app_mode = "📊 Progress Dashboard"
                st.rerun()
            if st.button("📝 Activity Logs", key="btn_activity_logs"):
                st.session_state.app_mode = "🛡️ Admin Dashboard"
                st.rerun()
        elif user_role == "instructor":
            if st.button("📊 Overall Progress", key="btn_overall_progress_instr"):
                st.session_state.app_mode = "📊 Progress Dashboard"
                st.rerun()
        if st.button("🎥 Video Guides", key="btn_video_guides_common"):
            st.session_state.app_mode = "🎥 Video Guides"
            st.rerun()
        if st.button("📊 View Dashboard", key="btn_view_dashboard"):
            st.session_state.app_mode = "📊 Progress Dashboard"
            st.rerun()
        if st.button("🧪 Practice Tests", key="btn_practice_tests"):
            st.session_state.app_mode = "🎯 Knowledge Quiz"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
