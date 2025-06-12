import os
import json
from functools import partial
from typing import Optional

# Core streamlit imports
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer

# Local imports
from utils import (
    setup_gemini,
    get_ncc_response,
    generate_quiz_questions,
    API_CALL_COOLDOWN_MINUTES,
    clear_history,
    read_history
)
from video_guides import video_guides as display_video_guides
from quiz_interface import quiz_interface

# Print version info once
if "version_info_printed" not in st.session_state:
    print(f"Streamlit version: {st.__version__}")
    print(f"Streamlit file: {st.__file__}")
    st.session_state.version_info_printed = True

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
        st.session_state.theme_mode = "Dark"

    # --- Sidebar - Theme Toggle & Info ---
    st.sidebar.header("Settings")

    # Theme Toggle
    theme_options = ["Dark", "Light"]  # Dark first to match default
    current_theme_idx = theme_options.index(st.session_state.theme_mode)
    new_theme = st.sidebar.radio(
        "Choose Theme",
        theme_options,
        index=current_theme_idx,
        key="theme_radio"
    )
    
    # Update theme if changed
    if new_theme != st.session_state.theme_mode:
        st.session_state.theme_mode = new_theme
        st.rerun()

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

    # --- Helper function for PDF embedding ---
    def display_pdf(file_path: str, height: int = 750, page: Optional[int] = None):
        """
        Embeds a PDF file in the Streamlit app with enhanced navigation and cross-browser support.
        Includes fallback options and proper error handling.
        """
        try:
            if not os.path.exists(file_path):
                st.error(f"🚨 PDF Error: File not found at '{file_path}'.")
                return False
            
            if not file_path.endswith('.pdf'):
                st.error("🚨 Invalid file type. Only PDF files are supported.")
                return False

            # Initialize PDF metadata if not already done
            if "pdf_metadata" not in st.session_state:
                import PyPDF2
                with open(file_path, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    st.session_state.pdf_metadata = {
                        "total_pages": len(pdf_reader.pages),
                        "outline": []  # Will store table of contents
                    }
                    
                    # Try to extract table of contents if available
                    try:
                        outline = pdf_reader.outline
                        if outline:
                            st.session_state.pdf_metadata["outline"] = outline
                    except Exception:
                        pass  # Some PDFs may not have an outline/table of contents
                
            # Use pdf_viewer for display
            pdf_viewer(
                file_path,
                height=height,
                width="100%"
            )
            return True
        except ImportError as ie:
            st.error("🚨 PDF viewer component not installed properly. Try reinstalling streamlit-pdf-viewer.")
            return False
        except Exception as e:
            st.error(f"🚨 Error displaying PDF: {str(e)}")
            st.info("💡 Try downloading the PDF to view it locally if the viewer fails.")
            return False

    # --- Module Routing ---
    st.markdown("<h1 style='text-align: center;'>NCC AI Assistant</h1>", unsafe_allow_html=True)

    if app_mode == "💬 Chat Assistant":
        from chat_interface import chat_interface # Lazy import
        chat_func = partial(get_ncc_response, model, model_error)
        chat_interface()

    elif app_mode == "🎯 Knowledge Quiz":
        from quiz_interface import _initialize_quiz_state, quiz_interface # Lazy imports
        _initialize_quiz_state(st.session_state) # Always initialize quiz state first
        if model: # model is from setup_gemini() at the top of main()
            quiz_interface(model, model_error) # Pass model and model_error
        else:
            st.error("Model failed to load, Quiz feature is unavailable.")

    elif app_mode == "📚 Syllabus Viewer":
        st.header("📚 NCC Syllabus")
        ncc_handbook_pdf_path = "Ncc-CadetHandbook.pdf" # Define path once

        from syllabus_manager import load_syllabus_data, get_syllabus_topics, search_syllabus
        syllabus_data = load_syllabus_data()

        # Initialize session state for PDF page navigation
        if 'pdf_current_page' not in st.session_state:
            st.session_state.pdf_current_page = None

        # Tabs for Syllabus Structure and PDF Viewer
        tab1, tab2 = st.tabs(["Syllabus Structure", "View NCC Handbook (PDF)"])

        with tab1:
            st.subheader("Browse Syllabus Content")
            query = st.text_input("🔍 Search Syllabus Topics/Sections", key="syllabus_search_query")

            if syllabus_data:
                if query:
                    search_results = search_syllabus(syllabus_data, query)
                    if search_results:
                        st.write(f"Found {len(search_results)} results for '{query}':")
                        for result in search_results:
                            expander_title = result.get('chapter_title', 'Result')
                            if result.get('section_name'):
                                expander_title += f" - {result['section_name']}"
                            
                            match_type_display = result.get('match_type', 'Match').replace('_', ' ').title()
                            expander_title = f"🔍 ({match_type_display}) {expander_title}"

                            with st.expander(expander_title):
                                st.markdown(result.get('content_preview', 'No preview available.'))
                                page_num = result.get('page_number')
                                if page_num:
                                    button_key = f"goto_pdf_search_{result.get('chapter_title', 'chap')}_{result.get('section_name', 'sec')}_{page_num}"
                                    if st.button(f"View Page {page_num} in PDF", key=button_key):
                                        st.session_state.pdf_current_page = page_num
                                        st.rerun()  # This will switch to the PDF tab and update the viewer
                    else:
                        st.info(f"No results found for '{query}' in the syllabus structure.")
                else:
                    # Display all chapters and sections if no search query
                    if syllabus_data.chapters:
                        for chapter in syllabus_data.chapters:
                            with st.expander(f"📖 {chapter.title}"):
                                if chapter.sections:
                                    for i, section in enumerate(chapter.sections):
                                        st.markdown(f"##### 📄 {section.name}") # Using H5 for section title
                                        st.markdown(section.content if section.content else "_No content available for this section._")
                                        if section.page_number: # Check if Section object has page_number
                                            col1, col2 = st.columns([3, 1])
                                            with col1:
                                                button_key = f"goto_pdf_browse_{chapter.title}_{section.name}_{section.page_number}"
                                                if st.button(f"📖 View Page {section.page_number} in PDF", key=button_key):
                                                    st.session_state.pdf_current_page = section.page_number
                                                    st.session_state.active_tab = "pdf_viewer"  # Mark PDF viewer tab as active
                                                    st.rerun()
                                            with col2:
                                                bookmark_key = f"bookmark_{chapter.title}_{section.name}"
                                                if st.button("🔖 Bookmark", key=bookmark_key):
                                                    if "bookmarks" not in st.session_state:
                                                        st.session_state.bookmarks = []
                                                    bookmark = {
                                                        "title": f"{chapter.title} - {section.name}",
                                                        "page": section.page_number
                                                    }
                                                    if bookmark not in st.session_state.bookmarks:
                                                        st.session_state.bookmarks.append(bookmark)
                                                        st.toast(f"Bookmarked page {section.page_number}!")
                                        if i < len(chapter.sections) - 1: # Add separator if not the last section
                                            st.markdown("---") 
                                else:
                                    st.info("No sections available for this chapter.")
                    else:
                        st.info("No chapters found in the syllabus data.")
            else:
                st.error("Failed to load syllabus data. Please check the 'data/syllabus.json' file and ensure it's correctly formatted.")

        with tab2:
            # Set this tab as active if requested
            if st.session_state.get("active_tab") == "pdf_viewer":
                st.session_state.active_tab = None  # Reset after switching
                
            st.subheader("NCC Cadet Handbook Viewer")
            if os.path.exists(ncc_handbook_pdf_path):
                # Left sidebar for outline and bookmarks
                pdf_sidebar = st.sidebar.container()
                with pdf_sidebar:
                    st.markdown("### 📑 Quick Navigation")
                    navigation_mode = st.radio(
                        "Navigation Mode",
                        ["📖 Table of Contents", "🔖 Bookmarks", "🔍 Search"],
                        key="pdf_nav_mode"
                    )
                    
                    if navigation_mode == "📖 Table of Contents":
                        if st.session_state.get("pdf_metadata", {}).get("outline"):
                            for item in st.session_state.pdf_metadata["outline"]:
                                if st.button(f"📄 {item.title}", use_container_width=True):
                                    st.session_state.pdf_current_page = item.page
                                    st.rerun()
                        else:
                            st.info("No table of contents available in this PDF")
                            
                    elif navigation_mode == "🔖 Bookmarks":
                        if st.session_state.get("bookmarks"):
                            for bookmark in st.session_state.bookmarks:
                                if st.button(f"🔖 {bookmark['title']}", use_container_width=True):
                                    st.session_state.pdf_current_page = bookmark['page']
                                    st.rerun()
                        else:
                            st.info("No bookmarks added yet. Add bookmarks from the syllabus view.")
                            
                    elif navigation_mode == "🔍 Search":
                        search_query = st.text_input("Search in PDF", key="pdf_search")
                        if search_query:
                            st.info("Search functionality coming soon!")
                
                # Main PDF viewer controls
                controls_container = st.container()
                with controls_container:
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    
                    with col1:
                        # Page navigation with total pages display
                        total_pages = 364  # Set to your PDF's actual page count
                        page = st.number_input(
                            f"Go to page (1-{total_pages})",
                            min_value=1,
                            max_value=total_pages,
                            value=st.session_state.pdf_current_page or 1,
                            step=1,
                            key="page_input",
                            help="Enter a page number to jump directly to that page"
                        )

                    with col2:
                        # First/Previous page
                        col2a, col2b = st.columns(2)
                        with col2a:
                            if st.button("⏮️ First", use_container_width=True):
                                st.session_state.pdf_current_page = 1
                                st.rerun()
                        with col2b:
                            if st.button("◀️ Prev", use_container_width=True):
                                page = max(1, (st.session_state.pdf_current_page or 1) - 1)
                                st.session_state.pdf_current_page = page
                                st.rerun()

                    with col3:
                        # Next/Last page
                        col3a, col3b = st.columns(2)
                        with col3a:
                            if st.button("Next ▶️", use_container_width=True):
                                page = min(total_pages, (st.session_state.pdf_current_page or 1) + 1)
                                st.session_state.pdf_current_page = page
                                st.rerun()
                        with col3b:
                            if st.button("Last ⏭️", use_container_width=True):
                                st.session_state.pdf_current_page = total_pages
                                st.rerun()

                    with col4:
                        # Zoom control (future enhancement placeholder)
                        zoom_level = st.selectbox(
                            "Zoom",
                            ["100%", "125%", "150%", "175%", "200%"],
                            index=0,
                            key="pdf_zoom",
                            help="Select zoom level (Note: May not work in all browsers)"
                        )

                    # Quick Bookmarks
                    st.markdown("---")
                    bookmark_cols = st.columns(4)
                    important_pages = {
                        "Contents": 1,
                        "Common Subjects": 50,
                        "Specialized Subjects": 150,
                        "Reference": 300
                    }
                    for i, (label, page_num) in enumerate(important_pages.items()):
                        with bookmark_cols[i]:
                            if st.button(f"📑 {label}", use_container_width=True):
                                st.session_state.pdf_current_page = page_num
                                st.rerun()

                # Update page state if changed
                if page != st.session_state.pdf_current_page:
                    st.session_state.pdf_current_page = page
                    st.rerun()

                # Help text
                st.info("💡 Due to browser limitations, PDF navigation might not work in all browsers. If you can't navigate pages, please use the download option to view the PDF locally.")

                # Display the PDF with current page
                if not display_pdf(ncc_handbook_pdf_path, height=800, page=st.session_state.pdf_current_page):
                    st.warning("Could not display PDF in the browser. You can download it instead:")
                    
                # Always offer download option
                with open(ncc_handbook_pdf_path, "rb") as f:
                    st.download_button(
                        "⬇️ Download NCC Cadet Handbook (PDF)",
                        f.read(),
                        file_name="Ncc-CadetHandbook.pdf",
                        mime="application/pdf",
                        key="download_handbook_syllabus_tab",
                        use_container_width=True
                    )
            else:
                st.warning(f"NCC Cadet Handbook PDF ('{ncc_handbook_pdf_path}') not found in the application's root directory. PDF viewer and download are unavailable.")


    elif app_mode == "🎥 Video Guides":
        from video_guides import video_guides as display_video_guides # Lazy import
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