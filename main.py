import streamlit as st
import os
import json
import requests
from functools import partial
import base64
from datetime import datetime
from typing import Optional
import time

# --- Inject sidebar width CSS for consistency ---
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

# Import and inject mobile-first CSS
from mobile_ui import inject_mobile_css
from accessibility import inject_accessibility_css, add_skip_navigation, add_aria_live_region, add_keyboard_navigation_script

inject_mobile_css()
inject_accessibility_css()

from core_utils import Config
from utils.logging_utils import log_info
# Local imports
from core_utils import (
    setup_gemini,
    get_ncc_response,
    API_CALL_COOLDOWN_MINUTES,
    clear_history, # Use the centralized clear_history
    read_history
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

def get_image_as_base64(image_path: str) -> str:
    """
    Convert an image (PNG or SVG) to base64 data URL.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Base64-encoded data URL string
    """
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

# --- Restore id_token from localStorage using restore_session() ---
restore_session()
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

def _check_and_reset_api_cooldown() -> None:
    """
    Check and reset API cooldown status based on time elapsed.
    Updates session state with cooldown status and remaining time.
    """
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

# Performance monitoring utilities
def _init_performance_monitoring() -> None:
    """Initialize performance monitoring in session state."""
    if "perf_metrics" not in st.session_state:
        st.session_state.perf_metrics = {
            "app_start_time": time.time(),
            "page_loads": 0,
            "api_calls": 0,
            "errors": 0
        }

def _track_performance_metric(metric_name: str, value: float = 1) -> None:
    """Track a performance metric."""
    if "perf_metrics" in st.session_state:
        if metric_name in st.session_state.perf_metrics:
            st.session_state.perf_metrics[metric_name] += value
        else:
            st.session_state.perf_metrics[metric_name] = value

# --- Main app logic ---
def main() -> None:
    """
    Main entry point for the NCC ABYAS application.
    Handles overall structure, navigation, theme, and routing to different features.
    """
    # Initialize performance monitoring
    _init_performance_monitoring()
    _track_performance_metric("page_loads")
    
    # Wrap the entire app content in mobile-friendly container
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # Add accessibility features
    add_skip_navigation()
    add_aria_live_region()
    add_keyboard_navigation_script()
    
    # Handle query parameters for chat navigation
    if st.query_params.get("go_chat") or st.query_params.get("open_chat") or st.query_params.get("hash") == ["open_chat"]:
        st.session_state.app_mode = "💬 Chat Assistant"
        st.query_params.clear()
        st.rerun()
    
    # Create a placeholder for the floating button at the top level.
    floating_button_placeholder = st.empty()

    # Initialize app_mode session state if not exists (single state variable for navigation)
    if "app_mode" not in st.session_state:
        st.session_state.app_mode = "🏠 Home"
    
    # Initialize Gemini model first (lazy initialization - only when needed)
    model, model_error = setup_gemini()
    
    # Initialize gamification features (lazy import)
    if "gamification_initialized" not in st.session_state:
        from gamification import award_xp
        from offline_manager import OfflineManager
        
        # Initialize offline functionality
        OfflineManager.init_offline_storage()
        OfflineManager.load_offline_queue_from_file()
        st.session_state["gamification_initialized"] = True
    else:
        # Use cached imports for better performance
        from gamification import award_xp
        from offline_manager import OfflineManager
    
    # Optimize daily login tracking (cache check to avoid repeated processing)
    today = datetime.now().date().isoformat()
    last_login_date = st.session_state.get("last_login_date")
    
    if last_login_date != today and "daily_login_processed" not in st.session_state:
        st.session_state.last_login_date = today
        st.session_state["daily_login_processed"] = True
        award_xp("daily_login", {"date": today})
    
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

    # --- AUTH: Show login/registration before app content if no user_id or id_token ---
    if not st.session_state.get("user_id") or not st.session_state.get("id_token"):
        if st.session_state.get("id_token") and not st.session_state.get("user_id"):
            pass  # Session restore in progress
        else:
            login_interface()
        st.stop()

    # --- Floating Chat Button (fixed at bottom right, above all content, pure Streamlit) ---
    st.markdown("""
    <style>
    .st-float-chat-btn {position: fixed; bottom: 2.2rem; right: 2.2rem; z-index: 99999;}
    </style>
    """, unsafe_allow_html=True)
    float_btn = st.empty()
    float_btn_html = """
    <div class='st-float-chat-btn'>
        <form action="#" method="post">
            <button type="submit" style="font-size:2.1rem;padding:0.7rem 1.2rem;border-radius:50%;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;border:none;box-shadow:0 4px 16px rgba(99,102,241,0.18);cursor:pointer;transition:box-shadow 0.2s;">💬</button>
        </form>
    </div>
    """
    if float_btn.button("💬", key="floating_chat_btn_real", help="Open Chat Assistant"):
        st.session_state.app_mode = "💬 Chat Assistant"
        st.rerun()

    # --- Custom Header (show only after login) ---
    logo_path = os.path.join(Config.DATA_DIR, "logo.svg") # Use SVG logo
    logo_base64_data_url = get_image_as_base64(logo_path)
    col1, col2 = st.columns([8, 1], gap="small")
    with col1:
        st.markdown(
            f'<div style="display: flex; align-items: center; gap: 0.7rem; padding: 1rem 0 1rem 0; border-bottom: 1px solid rgba(128, 128, 128, 0.2); margin-bottom: 2rem;">'
            f'<img src="{logo_base64_data_url}" style="height: 2rem; width: auto;">'
            f'<h1 style="margin:0;font-size:1.25rem;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;display:inline-block;vertical-align:middle;">NCC ABYAS</h1>'
            f'</div>', unsafe_allow_html=True
        )
    with col2:
        if st.button("👤", key="profile_btn_header_fixed", help="Profile"):
            st.session_state.app_mode = "👤 Profile"
            st.rerun()

    # --- Sidebar Profile Icon (Full Header Style) ---
    render_sidebar_profile()

    # --- Navigation Sidebar ---
    navigation_options = [
        "🏠 Home", "👤 Profile", "💬 Chat Assistant", "🎯 Knowledge Quiz", "📚 Syllabus Viewer", "🎥 Video Guides", "📁 History Viewer", "📊 Progress Dashboard", "🎮 Achievements"
    ]
    if st.session_state.get("role") == "admin":
        navigation_options.append("🛡️ Admin Dashboard")
    if st.session_state.get("role") in ["admin", "instructor"]:
        navigation_options.append("👨‍🏫 Instructor Dashboard")
    navigation_options.append("🛠️ Dev Tools")

    # Always set Home as default after login
    if "app_mode" not in st.session_state or st.session_state["app_mode"] not in navigation_options:
        st.session_state["app_mode"] = "🏠 Home"

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
    # Offline status and sync
    from offline_manager import OfflineManager
    with st.sidebar:
        OfflineManager.show_offline_status()
    
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
    if app_mode == "🏠 Home":
        from homepage_interface import show_homepage
        show_homepage()
    elif app_mode == "👤 Profile":
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

    elif app_mode == "🎮 Achievements":
        from gamification import show_gamification_dashboard
        show_gamification_dashboard()

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

    # --- Enhanced Mobile Bottom Navigation Bar (Mobile-First, Pure Streamlit) ---
    # Only render on mobile screens - detected via viewport width
    st.markdown("""
    <style>
    /* Mobile Bottom Navigation - Enhanced for Reliability */
    @media (max-width: 768px) {
      .mobile-nav-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(to top, rgba(255,255,255,0.98) 0%, rgba(255,255,255,0.95) 100%);
        backdrop-filter: blur(10px);
        border-top: 1px solid rgba(99,102,241,0.1);
        box-shadow: 0 -4px 20px rgba(0,0,0,0.08);
        padding: 8px 0 calc(8px + env(safe-area-inset-bottom));
        z-index: 9999;
      }
      
      .mobile-nav-container .stColumns {
        gap: 0 !important;
      }
      
      .mobile-nav-container .stButton > button {
        width: 100% !important;
        height: 48px !important;
        min-height: 48px !important;
        font-size: 1.8rem !important;
        background: transparent !important;
        border: none !important;
        color: #6B7280 !important;
        transition: all 0.2s ease !important;
        border-radius: 12px !important;
        margin: 2px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
      }
      
      .mobile-nav-container .stButton > button:hover {
        background: rgba(99,102,241,0.08) !important;
        color: #6366F1 !important;
        transform: translateY(-1px) !important;
      }
      
      .mobile-nav-container .stButton > button.active-nav {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
        color: white !important;
        box-shadow: 0 2px 8px rgba(99,102,241,0.25) !important;
      }
      
      /* Add padding to main content to prevent overlap */
      .main .block-container {
        padding-bottom: 80px !important;
      }
    }
    
    /* Hide on desktop */
    @media (min-width: 769px) {
      .mobile-nav-container {
        display: none !important;
      }
    }
    </style>
    """, unsafe_allow_html=True)

    # Mobile Navigation Tabs Configuration
    mobile_nav_tabs = [
        ("🏠 Home", "🏠", "Home"),
        ("📚 Syllabus Viewer", "📚", "Syllabus"),
        ("🎯 Knowledge Quiz", "🎯", "Quiz"),
        ("🎥 Video Guides", "🎥", "Videos"),
        ("📊 Progress Dashboard", "📊", "Progress"),
        ("👤 Profile", "👤", "Profile")
    ]
    
    # Render mobile navigation container
    st.markdown('<div class="mobile-nav-container">', unsafe_allow_html=True)
    
    # Create responsive columns for navigation
    nav_cols = st.columns(len(mobile_nav_tabs))
    
    current_mode = st.session_state.get("app_mode", "🏠 Home")
    
    for i, (mode, icon, label) in enumerate(mobile_nav_tabs):
        with nav_cols[i]:
            # Check if this tab is currently active
            is_active = current_mode == mode
            
            # Create unique button key
            button_key = f"mobile_nav_{mode.replace(' ', '_').replace('🏠', 'home').replace('📚', 'syllabus').replace('🎯', 'quiz').replace('🎥', 'videos').replace('📊', 'progress').replace('👤', 'profile')}"
            
            # Render button with accessibility features
            if st.button(
                f"{icon}\n{label}",
                key=button_key,
                help=f"Go to {label} - Keyboard shortcut: Alt+{label[0].lower()}",
                use_container_width=True
            ):
                # Update app mode and sync with sidebar
                st.session_state.app_mode = mode
                # Force rerun to update the interface
                st.rerun()
    
    # Close the main content container
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # Suppress error display for production