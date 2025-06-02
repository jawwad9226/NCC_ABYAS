import streamlit as st
import os
from functools import partial
import json
from utils import setup_gemini, get_ncc_response, generate_quiz_questions, API_CALL_COOLDOWN_MINUTES, clear_history, read_history
from video_guides import display_video_guides
from quiz_interface import display_quiz_interface, initialize_quiz_state

def main():
    """
    Main entry point for the NCC AI Assistant Streamlit application.
    Handles overall structure, navigation, theme, and routing to different features.
    """

    # --- Gemini Model Initialization & Error Handling ---
    # This should be the very first thing to ensure the model is ready or an error is displayed early.
    model, model_error = setup_gemini()

    if model_error:
        st.error(f"🚨 Critical Error: {model_error}")
        st.stop() # Halts execution, preventing any further UI elements from rendering

    # Initialize session state for theme if not already set
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "Light"

    # --- Sidebar - Theme Toggle & Info ---
    # Move these below the model error check to ensure they don't appear if the app is stopped
    st.sidebar.header("Settings")

    # Theme Toggle
    st.session_state.theme_mode = st.sidebar.radio(
        "Choose Theme",
        ["Light", "Dark"],
        index=0 if st.session_state.theme_mode == "Light" else 1,
        key="theme_radio"
    )

    # Apply Custom CSS for Theme
    if st.session_state.theme_mode == "Dark":
        st.markdown(
            """
            <style>
            body {
                background-color: #0e1117;
                color: #fafafa;
            }
            .stApp {
                background-color: #0e1117;
            }
            .stButton>button {
                background-color: #262730;
                color: #fafafa;
                border: 1px solid #262730;
            }
            .stButton>button:hover {
                border: 1px solid #0068c9;
                color: #0068c9;
            }
            .stTextInput>div>div>input {
                background-color: #262730;
                color: #fafafa;
                border: 1px solid #31333F;
            }
            .stSelectbox>div>div>div {
                background-color: #262730;
                color: #fafafa;
                border: 1px solid #31333F;
            }
            .stExpander {
                background-color: #262730;
                border: 1px solid #31333F;
                border-radius: 0.25rem;
            }
            .stExpander>div>div>p {
                color: #fafafa !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <style>
            body {
                background-color: #ffffff;
                color: #333333;
            }
            .stApp {
                background-color: #ffffff;
            }
            .stButton>button {
                background-color: #f0f2f6;
                color: #333333;
                border: 1px solid #f0f2f6;
            }
            .stButton>button:hover {
                border: 1px solid #0068c9;
                color: #0068c9;
            }
            .stTextInput>div>div>input {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #e0e0e0;
            }
            .stSelectbox>div>div>div {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #e0e0e0;
            }
            .stExpander {
                background-color: #f0f2f6;
                border: 1px solid #e0e0e0;
                border-radius: 0.25rem;
            }
            .stExpander>div>div>p {
                color: #333333 !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

    st.sidebar.markdown("---") # Separator

    # Sidebar Navigation
    app_mode = st.sidebar.radio(
        "Go to",
        ["💬 Chat Assistant", "🎯 Knowledge Quiz", "📚 Syllabus Viewer", "🎥 Video Guides", "📁 History Viewer", "📊 Progress Dashboard"],
        key="app_mode_radio"
    )

    st.sidebar.markdown("---") # Separator

    st.sidebar.info(f"API Cooldown: Please wait ~{API_CALL_COOLDOWN_MINUTES} minutes between questions if you hit rate limits.")

    st.sidebar.markdown("---") # Separator

    # Reset All State Button
    if st.sidebar.button("♻️ Reset All"):
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        # Clear on-disk logs
        clear_history("chat")
        clear_history("quiz")
        clear_history("bookmark") # Assuming you might add this later
        st.rerun()

    # Optional Dev Tools
    if st.sidebar.checkbox("🔍 Dev Tools"):
        st.sidebar.write("### Session State Dump")
        st.sidebar.json(st.session_state)

    # --- Module Routing ---
    st.markdown("<h1 style='text-align: center;'>NCC AI Assistant</h1>", unsafe_allow_html=True)

    if app_mode == "💬 Chat Assistant":
        from chat_interface import chat_interface # Lazy import
        chat_func = partial(get_ncc_response, model, model_error)
        chat_interface()

    elif app_mode == "🎯 Knowledge Quiz":
        from quiz_interface import initialize_quiz_state, display_quiz_interface # Lazy imports
        initialize_quiz_state(st.session_state) # Always initialize quiz state first
        if model:
            quiz_func = partial(generate_quiz_questions, model, model_error, st.session_state)
            display_quiz_interface(quiz_func, st.session_state)
        else:
            st.error("Model failed to load, Quiz feature is unavailable.")

    elif app_mode == "📚 Syllabus Viewer":
        st.header("📚 NCC Syllabus")
        syllabus_json_path = os.path.join("data", "syllabus.json")
        ncc_handbook_pdf_path = "Ncc-CadetHandbook.pdf"

        # Display syllabus from JSON
        if os.path.exists(syllabus_json_path):
            with open(syllabus_json_path, "r") as f:
                syllabus_data = json.load(f)

            query = st.text_input("🔍 Search Syllabus", key="syllabus_search_query")
            
            st.markdown("---")

            found_results = False
            if "chapters" in syllabus_data:
                for chapter_key, chapter in syllabus_data["chapters"].items():
                    chapter_title = chapter.get("title", "Untitled Chapter")
                    sections = chapter.get("sections", {}).values() if isinstance(chapter.get("sections", {}), dict) else chapter.get("sections", [])

                    # Filter based on search query
                    if query.lower() in chapter_title.lower() or \
                       any(query.lower() in sec.get("name", "").lower() for sec in sections):
                        
                        found_results = True
                        with st.expander(chapter_title):
                            for section in sections:
                                section_name = section.get("name", "Untitled Section")
                                if query.lower() in section_name.lower():
                                    st.write(f"- {section_name}")
                            if not sections:
                                st.info("No sections found for this chapter.")
            else:
                st.warning("Syllabus JSON format invalid: 'chapters' key not found.")
            
            if query and not found_results:
                st.info(f"No results found for '{query}' in the syllabus.")
            elif not query and not found_results:
                 st.info("Syllabus content could not be displayed. Please check the `data/syllabus.json` file.")

        else:
            st.warning("Syllabus JSON file not found. Please ensure 'data/syllabus.json' exists.")
        
        st.markdown("---")

        # Offer PDF download
        if os.path.exists(ncc_handbook_pdf_path):
            with open(ncc_handbook_pdf_path, "rb") as f:
                pdf_bytes = f.read()
            st.download_button(
                label="⬇️ Download NCC Cadet Handbook (PDF)",
                data=pdf_bytes,
                file_name="Ncc-CadetHandbook.pdf",
                mime="application/pdf"
            )
        else:
            st.info("NCC Cadet Handbook PDF not found. Please ensure 'Ncc-CadetHandbook.pdf' is in the main directory.")

    elif app_mode == "🎥 Video Guides":
        from video_guides import display_video_guides # Lazy import
        display_video_guides()

    elif app_mode == "📁 History Viewer":
        st.header("📁 History Viewer")
        history_tab = st.tabs(["Chat History", "Quiz History"])

        with history_tab[0]:
            st.subheader("Chat History")
            chat_history_content = read_history("chat")
            
            if st.button("🧹 Clear Chat History", key="clear_chat_button"):
                st.session_state.confirm_clear_chat = True
            
            if st.session_state.get("confirm_clear_chat", False):
                st.warning("Are you sure you want to clear the chat history? This cannot be undone.")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Yes, Clear Chat History", key="confirm_yes_chat"):
                        clear_history("chat")
                        st.session_state.confirm_clear_chat = False
                        st.success("Chat history cleared!")
                        st.rerun()
                with col2:
                    if st.button("No, Keep Chat History", key="confirm_no_chat"):
                        st.session_state.confirm_clear_chat = False
                        st.info("Chat history not cleared.")

            if chat_history_content:
                lines = chat_history_content.splitlines()
                display_limit = 50 # Limit display to last 50 lines
                
                for line in lines[-display_limit:]:
                    st.text(line)
                
                if len(lines) > display_limit:
                    st.info(f"...and {len(lines) - display_limit} earlier lines are hidden. Download full history to view all.")
                
                if st.download_button("⬇️ Download Full Chat History", chat_history_content, "chat_history.txt"):
                    st.success("Chat history downloaded!")
            else:
                st.info("No chat history found yet.")

        with history_tab[1]:
            st.subheader("Quiz History")
            quiz_history_content = read_history("quiz")
            
            if st.button("🧹 Clear Quiz History", key="clear_quiz_button"):
                st.session_state.confirm_clear_quiz = True

            if st.session_state.get("confirm_clear_quiz", False):
                st.warning("Are you sure you want to clear the quiz history? This cannot be undone.")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Yes, Clear Quiz History", key="confirm_yes_quiz"):
                        clear_history("quiz")
                        st.session_state.confirm_clear_quiz = False
                        st.success("Quiz history cleared!")
                        st.rerun()
                with col2:
                    if st.button("No, Keep Quiz History", key="confirm_no_quiz"):
                        st.session_state.confirm_clear_quiz = False
                        st.info("Quiz history not cleared.")
            
            if quiz_history_content:
                lines = quiz_history_content.splitlines()
                display_limit = 50 # Limit display to last 50 lines

                for line in lines[-display_limit:]:
                    st.text(line)
                
                if len(lines) > display_limit:
                    st.info(f"...and {len(lines) - display_limit} earlier lines are hidden. Download full history to view all.")

                if st.download_button("⬇️ Download Full Quiz History", quiz_history_content, "quiz_history.txt"):
                    st.success("Quiz history downloaded!")
            else:
                st.info("No quiz history found yet. Take a quiz to start.")

    elif app_mode == "📊 Progress Dashboard":
        # Placeholder for the Progress Dashboard
        # Lazy import only if the file exists and is meant to be used
        try:
            from progress_dashboard import display_progress_dashboard
            display_progress_dashboard(st.session_state)
        except ImportError:
            st.info("📊 Progress Dashboard coming soon! Take quizzes to populate your data here.")


if __name__ == "__main__":
    main()