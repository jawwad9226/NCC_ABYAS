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
from utils import setup_gemini

# Configure page
st.set_page_config(
    page_title="NCC AI Assistant",
    page_icon="🎖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize session state variables"""
    if 'page' not in st.session_state:
        st.session_state.page = "Chat"
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'quiz_active' not in st.session_state:
        st.session_state.quiz_active = False
    if 'quiz_questions' not in st.session_state:
        st.session_state.quiz_questions = []
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}
    if 'quiz_score' not in st.session_state:
        st.session_state.quiz_score = 0
    if 'quiz_complete' not in st.session_state:
        st.session_state.quiz_complete = False

# Initialize session state
initialize_session_state()

# Initialize Gemini model
model, error = setup_gemini()
if error:
    st.error(f"Error initializing AI model: {error}")
    st.stop()

# Sidebar navigation
st.sidebar.title("NCC AI Assistant")
st.sidebar.markdown("---")

# Navigation options
PAGES = {
    "💬 Chat": "Chat",
    "🎯 Quiz": "Quiz",
    "📊 Progress": "Progress",
    "🎥 Video Guides": "Video Guides"
}

# Display navigation
st.sidebar.header("Navigation")
selection = st.sidebar.radio(
    "Go to", 
    options=list(PAGES.keys()),
    index=list(PAGES.values()).index(st.session_state.page) if st.session_state.page in PAGES.values() else 0
)

# Update page based on selection
st.session_state.page = PAGES[selection]

def chat_page():
    """Display the chat interface"""
    def get_response(prompt: str) -> str:
        """Wrapper function to get response from the model"""
        from utils import get_ncc_response
        return get_ncc_response(model, error, prompt)
    
    display_chat_interface(get_response, st.session_state)

def quiz_page():
    """Display the quiz interface"""
    display_quiz_interface(model)

# Display the selected page
if st.session_state.page == "Chat":
    chat_page()
elif st.session_state.page == "Quiz":
    quiz_page()
elif st.session_state.page == "Progress":
    display_progress_dashboard()
elif st.session_state.page == "Video Guides":
    display_video_guides()

# Add some styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .stTextInput>div>div>input {
        border-radius: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Add footer
st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "NCC AI Assistant - Your digital companion for NCC training and learning. "
    "Developed to enhance the NCC cadet experience with AI-powered assistance."
)
st.sidebar.markdown("---")
st.sidebar.markdown("### Support")
st.sidebar.markdown(
    "Having issues? Contact support at [support@nccai.com](mailto:support@nccai.com)"
)
