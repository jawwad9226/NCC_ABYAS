import streamlit as st
import os
from datetime import datetime
import time # For simulating cooldown display
from streamlit_pdf_viewer import pdf_viewer 

# Import functions from your consolidated modules
# Make sure these paths are correct relative to main.py
from chat_interface import chat_interface
from quiz_interface import quiz_interface
from progress_dashboard import progress_dashboard
from video_guides import video_guides
# Corrected import: now import from syllabus_manager
from syllabus_manager import load_syllabus_data, search_syllabus, SyllabusData 

# --- Configuration and Utility Functions (from utils.py, mocked for demonstration) ---
# In a real application, these would be imported from utils.py
# from utils import get_response_func, read_history, append_message, clear_history, initialize_firebase

def get_response_func(chat_type, prompt):
    """Mocks a function that gets a response from a model."""
    # This is a mock; replace with your actual model call logic
    if "last_chat_time" not in st.session_state:
        st.session_state.last_chat_time = time.time()
        st.session_state.cooldown_duration = 5 # seconds

    time_since_last_chat = time.time() - st.session_state.last_chat_time

    if time_since_last_chat < st.session_state.cooldown_duration:
        remaining_time = int(st.session_state.cooldown_duration - time_since_last_chat)
        return f"Please wait {remaining_time} seconds before sending another message."
    else:
        st.session_state.last_chat_time = time.time() # Reset cooldown timer
        # Simulate a response
        if "hello" in prompt.lower():
            return "Hello! How can I assist you with NCC today?"
        elif "syllabus" in prompt.lower():
            return "The NCC syllabus covers topics like drill, weapon training, map reading, and field craft. Would you like more details on a specific topic?"
        elif "cadet" in prompt.lower():
            return "An NCC cadet is a young individual enrolled in the National Cadet Corps, undergoing training in various military and social service activities."
        else:
            return "I am an AI assistant for NCC. Please ask me a question related to NCC."

def read_history(history_type):
    """Mocks reading chat history from a file."""
    try:
        with open(f"{history_type}_history.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""

def append_message(history_type, message):
    """Mocks appending a message to chat history."""
    with open(f"{history_type}_history.txt", "a") as f:
        f.write(message + "\n")

def clear_history(history_type):
    """Mocks clearing chat history."""
    try:
        open(f"{history_type}_history.txt", "w").close()
    except FileNotFoundError:
        pass # File doesn't exist, nothing to clear

# --- End of Mock Utility Functions ---

# --- Page Configuration ---
st.set_page_config(
    page_title="NCC AI Assistant",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS (Removed nth-child overrides as st.chat_message handles roles) ---
st.markdown("""
<style>
    .stApp {
        background-color: #f0f2f6; /* Light background */
    }
    .stSidebar {
        background-color: #ffffff; /* White sidebar */
        padding-top: 20px;
    }
    .stButton>button {
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .stRadio > label > div {
        padding: 5px 0;
    }
    .stExpander {
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    .stExpander > div > div > p {
        font-weight: bold;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)


# --- Sidebar Navigation ---
st.sidebar.title("NCC AI Assistant")
st.sidebar.markdown("Your comprehensive guide for NCC.")

# Navigation options
app_mode = st.sidebar.radio(
    "Go to",
    ["💬 Chat with AI", "🧠 Take a Quiz", "📊 Progress Dashboard", "🎥 Video Guides", "📚 Syllabus Viewer", "📖 View Cadet Handbook"],
    key="app_mode_radio"
)

st.sidebar.markdown("---")

# --- Syllabus Viewer in Sidebar ---
st.sidebar.header("📚 Syllabus Viewer")
# Pass the correct filename to load_syllabus_data
# Assuming 'syllabus.json' is in the 'data' directory relative to main.py
SYLLABUS_JSON_PATH = os.path.join("data", "syllabus.json")
syllabus_data: Optional[SyllabusData] = load_syllabus_data(file_name=SYLLABUS_JSON_PATH) 

if syllabus_data: # Check if syllabus_data object was successfully loaded
    st.sidebar.markdown(f"Syllabus Version: **{syllabus_data.version}**") # Display version
    
    syllabus_search_query = st.sidebar.text_input(
        "Search Syllabus:",
        placeholder="e.g., 'Drill', 'First Aid', 'Map Reading'",
        key="syllabus_search_input",
        help="Search for chapters or sections in the NCC syllabus."
    ).lower()

    if syllabus_search_query:
        search_results = search_syllabus(syllabus_data, syllabus_search_query)
        if search_results:
            st.sidebar.subheader("Search Results:")
            for result in search_results:
                # Access attributes or dict keys based on what search_syllabus returns
                if result["match_type"] == "chapter":
                    st.sidebar.markdown(f"**Chapter:** {result['chapter_title']}")
                elif result["match_type"] == "section":
                    st.sidebar.markdown(f"**Section:** {result['section_name']} (in {result['chapter_title']})")
                elif result["match_type"] == "section_content":
                    st.sidebar.markdown(f"**Content in Section:** {result['section_name']} (in {result['chapter_title']})")
            st.sidebar.markdown("---") # Separator for search results
        else:
            st.sidebar.info("No matching chapters or sections found.")
            st.sidebar.markdown("---")
    
    # Display full syllabus if no search query or after search results
    # Access .chapters attribute
    if syllabus_data.chapters: 
        st.sidebar.subheader("Full Syllabus:")
        for chapter in syllabus_data.chapters: # Iterate over Chapter objects
            # Only display if not filtered by search, or if it was a chapter match
            # Access .title attribute
            if not syllabus_search_query or any(res.get("chapter_title") == chapter.title for res in search_results): 
                # Access .title attribute
                with st.sidebar.expander(chapter.title, expanded=False): 
                    # Access .sections attribute
                    for section in chapter.sections: # Iterate over Section objects
                        # Only display section if not filtered by search, or if it was a section match
                        # Access .name and .title attributes
                        if not syllabus_search_query or any(res.get("section_name") == section.name and res.get("chapter_title") == chapter.title for res in search_results): 
                            # Access .name attribute
                            st.write(f"- {section.name}") 
    else:
        st.sidebar.warning("Syllabus data is missing 'chapters' key or is malformed.")
else:
    st.sidebar.info("Syllabus data could not be loaded. Please check data/syllabus.json.")

st.sidebar.markdown("---")

# --- Download Syllabus PDF (Remains as a convenient option) ---
# Ensure this path is correct. If Ncc-CadetHandbook.pdf is in the project root, this is correct.
PDF_PATH = os.path.join(os.path.dirname(__file__), "Ncc-CadetHandbook.pdf")
try:
    with open(PDF_PATH, "rb") as pdf_file:
        st.sidebar.download_button(
            label="⬇️ Download Cadet Handbook (PDF)",
            data=pdf_file,
            file_name="Ncc-CadetHandbook.pdf",
            mime="application/pdf",
            key="sidebar_download_pdf",
            help="Download the complete NCC Cadet Handbook in PDF format."
        )
except FileNotFoundError:
    st.sidebar.warning("NCC Cadet Handbook PDF not found. Please ensure 'Ncc-CadetHandbook.pdf' is in the main directory.")


# --- Main Content Area ---
if app_mode == "💬 Chat with AI":
    chat_interface()
elif app_mode == "🧠 Take a Quiz":
    quiz_interface()
elif app_mode == "📊 Progress Dashboard":
    progress_dashboard()
elif app_mode == "🎥 Video Guides":
    video_guides()
elif app_mode == "📚 Syllabus Viewer":
    st.header("NCC Syllabus Details")
    st.info("The full syllabus content is available in the sidebar. Use the search bar to find specific topics or navigate below to view the full Cadet Handbook.")
    st.write("This section could be used for more detailed interactive syllabus exploration if needed.")
elif app_mode == "📖 View Cadet Handbook":
    st.header("📖 NCC Cadet Handbook")
    
    # Load PDF data
    try:
        with open(PDF_PATH, "rb") as pdf_file:
            PDFbyte = pdf_file.read()
        
        # Display the PDF viewer
        pdf_viewer(PDFbyte)
        
        # Also offer download button in main area
        st.download_button(
            label="⬇️ Download Handbook (Main Area)",
            data=PDFbyte,
            file_name="Ncc-CadetHandbook.pdf",
            mime="application/pdf",
            key="main_download_pdf",
            help="Download the complete NCC Cadet Handbook in PDF format."
        )

    except FileNotFoundError:
        st.error("NCC Cadet Handbook PDF not found. Cannot display viewer. Please ensure 'Ncc-CadetHandbook.pdf' is in the main directory.")
    except Exception as e:
        st.error(f"An error occurred while loading or displaying the PDF: {e}")

