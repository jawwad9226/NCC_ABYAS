import streamlit as st
from typing import Callable, Dict, Any, Optional
import os
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent))

# Import modules
from chat_interface import display_chat_interface
from quiz_interface import display_quiz_interface
from progress_dashboard import display_progress_dashboard
from video_guides import display_video_guides
from utils import setup_gemini, clear_history

# Configure page
st.set_page_config(
    page_title="NCC AI Assistant",
    page_icon="🎖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize session state variables"""
    defaults = {
        'page': "Chat",
        'messages': [],
        'quiz_active': False,
        'quiz_questions': [],
        'current_question': 0,
        'user_answers': {},
        'quiz_score': 0,
        'quiz_complete': False,
        'dark_mode': False  # Added for theme toggle
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def reset_application():
    """Reset the application state and clear history files"""
    # Clear all session variables
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    # Clear on-disk logs
    clear_history("chat")
    clear_history("quiz")
    
    # Re-initialize with defaults
    initialize_session_state()
    st.rerun()

# Initialize session state
initialize_session_state()

# Initialize Gemini model
model, model_error = setup_gemini()
if model_error:
    st.error(f"Error initializing AI model: {model_error}")
    st.stop()

# Apply theme
if st.session_state.dark_mode:
    st.markdown("""
        <style>
            .main { background-color: #0E1117; color: #FAFAFA; }
            .stApp { background-color: #0E1117; }
            .stTextInput>div>div>input { color: #FAFAFA; background-color: #1E1E1E; }
            .stTextArea>div>div>textarea { color: #FAFAFA; background-color: #1E1E1E; }
            .stSelectbox>div>div>div { color: #FAFAFA; }
            .stRadio>div>label>div { color: #FAFAFA; }
        </style>
    """, unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.title("NCC AI Assistant")
    
    # Theme Toggle
    if st.button("🌓 Toggle Theme"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
    
    st.markdown("---")
    
    # Navigation
    st.header("Navigation")
    PAGES = {
        "💬 Chat": "Chat",
        "🎯 Quiz": "Quiz",
        "📊 Progress": "Progress",
        "🎥 Video Guides": "Video Guides"
    }
    
    selection = st.radio(
        "Go to", 
        options=list(PAGES.keys()),
        index=list(PAGES.values()).index(st.session_state.page) if st.session_state.page in PAGES.values() else 0
    )
    
    # Update page based on selection
    st.session_state.page = PAGES[selection]
    
    st.markdown("---")
    
    # Reset Button
    if st.button("♻️ Reset All", type="secondary"):
        reset_application()
    
    # Dev Tools Section
    if st.checkbox("🔍 Dev Tools"):
        st.markdown("### Session State")
        st.json({k: str(v) for k, v in st.session_state.items()})
    
    st.markdown("---")
    
    # About Section
    st.markdown("### About")
    st.info(
        "NCC AI Assistant - Your digital companion for NCC training and learning. "
        "Developed to enhance the NCC cadet experience with AI-powered assistance."
    )
    
    # Support Section
    st.markdown("### Support")
    st.markdown("Having issues? [Report a bug](https://github.com/yourusername/ncc_ai_assistant/issues)")
    st.markdown("View on [GitHub](https://github.com/yourusername/ncc_ai_assistant)")

# Display the selected page
if st.session_state.page == "Chat":
    def chat_page():
        """Display the chat interface"""
        def get_response(prompt: str) -> str:
            """Wrapper function to get response from the model"""
            from utils import get_ncc_response
            return get_ncc_response(model, model_error, prompt)
        
        display_chat_interface(get_response, st.session_state)
    
    chat_page()
    
elif st.session_state.page == "Quiz":
    display_quiz_interface(model)
    
elif st.session_state.page == "Progress":
    display_progress_dashboard()
    
elif st.session_state.page == "Video Guides":
    display_video_guides()

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center;'>Made with ❤️ for NCC Cadets | <a href='https://github.com/yourusername/ncc_ai_assistant' target='_blank'>GitHub</a></div>", unsafe_allow_html=True)
