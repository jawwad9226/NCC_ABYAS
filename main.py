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
from src.utils import (
    apply_theme,
    get_theme_config
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
    st.set_page_config(
        page_title="NCC AI Assistant",
        page_icon="🎓",
        layout="wide"
    )
    
    # --- App Header ---
    st.sidebar.title("NCC AI Assistant")


    # --- Gemini Model Initialization & Error Handling ---
    # This should be the very first thing to ensure the model is ready or an error is displayed early.
    model, model_error = setup_gemini()


    if model_error:
        st.error(f"🚨 Critical Error: {model_error}")
        st.stop() # Halts execution, preventing any further UI elements from rendering

    # Initialize session state for theme if not already set
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "Dark"

    # --- Sidebar - Settings & Theme ---
    st.sidebar.header("Settings")
    
    # Modern Theme Toggle with icon tooltips
    st.sidebar.markdown("""
        <div class="theme-toggle">
            <label class="toggle-switch">
                <input type="checkbox" 
                    onchange="handleThemeChange(this.checked)"
                    {}
                >
                <span class="toggle-slider"></span>
            </label>
            <span>🌙 Dark Mode</span>
        </div>
        <script>
        function handleThemeChange(isDark) {{
            const event = new CustomEvent('theme-change', {{ detail: {{ isDark }} }});
            window.dispatchEvent(event);
        }}
        </script>
    """.format('checked' if st.session_state.theme_mode == "Dark" else ''),
    unsafe_allow_html=True)
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

    # Apply theme
    apply_theme(st.session_state.theme_mode)

    st.sidebar.markdown("---") # Separator

    # Sidebar Navigation
    app_mode = st.sidebar.radio( # This will be the primary navigation
        "Navigation",
        ["💬 Chat Assistant", "🎯 Knowledge Quiz", "📚 Syllabus Viewer", "🎥 Video Guides", "📁 History Viewer", "📊 Progress Dashboard"],
        key="app_mode_radio_primary" # Changed key for clarity
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

    # --- Dev Tools Link ---
    if st.sidebar.button("🛠️ Open Dev Tools", key="open_dev_tools"):
        js = f'''
            <script>
            window.open("http://localhost:8501/dev_tools", "_blank");
            </script>
        '''
        st.markdown(js, unsafe_allow_html=True)
        
    # Handle dev tools route
    if st.query_params.get("page") == ["dev_tools"]:
        from dev_tools import dev_tools
        dev_tools()

    # --- Helper function for PDF viewer component ---
    def display_pdf_viewer(file_path: str, height: int = 750):
        """
        Embeds a PDF file in the Streamlit app using streamlit_pdf_viewer.
        Features a modern control bar with icon-only buttons and tooltips.
        """
        try:
            if not os.path.exists(file_path):
                st.error(f"🚨 PDF Error: File not found at '{file_path}'.")
                return False
            if not file_path.endswith('.pdf'):
                st.error("🚨 Invalid file type. Only PDF files are supported.")
                return False

            # Modern control bar
            st.markdown("""
                <div class="pdf-control-bar">
                    <div class="pdf-controls left">
                        <button class="pdf-btn" data-tooltip="Previous Page">◀️</button>
                        <input type="number" class="page-input" min="1" value="1">
                        <button class="pdf-btn" data-tooltip="Next Page">▶️</button>
                    </div>
                    <div class="pdf-controls center">
                        <button class="pdf-btn" data-tooltip="Zoom Out">🔍-</button>
                        <select class="zoom-select">
                            <option value="0.5">50%</option>
                            <option value="1" selected>100%</option>
                            <option value="1.5">150%</option>
                            <option value="2">200%</option>
                        </select>
                        <button class="pdf-btn" data-tooltip="Zoom In">🔍+</button>
                    </div>
                    <div class="pdf-controls right">
                        <button class="pdf-btn" data-tooltip="Toggle Outline">📑</button>
                        <button class="pdf-btn" data-tooltip="Search">🔎</button>
                        <button class="pdf-btn" data-tooltip="Download">⬇️</button>
                    </div>
                </div>
                <style>
                .pdf-control-bar {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    background: #f8f9fa;
                    padding: 8px;
                    border-radius: 8px;
                    margin-bottom: 1rem;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                }
                .pdf-controls {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }
                .pdf-btn {
                    padding: 6px 12px;
                    border: none;
                    background: transparent;
                    border-radius: 4px;
                    cursor: pointer;
                    transition: all 0.2s;
                }
                .pdf-btn:hover {
                    background: #e9ecef;
                }
                .page-input {
                    width: 50px;
                    text-align: center;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    padding: 4px;
                }
                .zoom-select {
                    padding: 4px;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    background: white;
                }
                [data-tooltip]:hover:before {
                    content: attr(data-tooltip);
                    position: absolute;
                    top: -24px;
                    left: 50%;
                    transform: translateX(-50%);
                    padding: 4px 8px;
                    background: rgba(0,0,0,0.8);
                    color: white;
                    font-size: 12px;
                    border-radius: 4px;
                    white-space: nowrap;
                }
                </style>
            """, unsafe_allow_html=True)

            # The PDF viewer component
            pdf_viewer(
                file_path,
                height=height,
                width="100%"
            )
            return True
            
        except ImportError:
            st.error("🚨 PDF viewer component (streamlit-pdf-viewer) not installed properly.")
            return False
        except Exception as e:
            st.error(f"🚨 Error displaying PDF: {str(e)}")
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

        from syllabus_manager import load_syllabus_data, search_syllabus
        syllabus_data = load_syllabus_data()

        # Initialize session state for PDF page navigation
        if 'pdf_current_page' not in st.session_state:
            st.session_state.pdf_current_page = 1 # Default to page 1
        
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
                                    if st.button(f"📖 View Page {page_num} in PDF", key=button_key):
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
                                                button_key = f"goto_pdf_browse_{chapter.title.replace(' ','_')}_{section.name.replace(' ','_')}_{section.page_number}"
                                                if st.button(f"📖 View Page {section.page_number} in PDF", key=button_key):
                                                    st.session_state.pdf_current_page = section.page_number
                                                    st.session_state.active_tab = "pdf_viewer"  # Mark PDF viewer tab as active
                                                    st.rerun()
                                            with col2:
                                                bookmark_key = f"bookmark_{chapter.title}_{section.name}"
                                                if st.button("🔖 Bookmark", key=bookmark_key):
                                                    if "bookmarks" not in st.session_state or not isinstance(st.session_state.bookmarks, list):
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
                # --- PDF Metadata Initialization (once per PDF load) ---
                if "pdf_metadata" not in st.session_state or \
                   st.session_state.get("pdf_metadata_path") != ncc_handbook_pdf_path:
                    try:
                        import PyPDF2
                        with open(ncc_handbook_pdf_path, 'rb') as pdf_file_obj:
                            pdf_reader = PyPDF2.PdfReader(pdf_file_obj)
                            processed_outline = []
                            if hasattr(pdf_reader, 'outline') and pdf_reader.outline:
                                def extract_outline_items(outline_items, reader):
                                    extracted = []
                                    for item in outline_items:
                                        if isinstance(item, list):
                                            extracted.extend(extract_outline_items(item, reader)) # Recurse
                                        elif hasattr(item, 'title') and item.title is not None:
                                            try:
                                                page_number_0_indexed = reader.get_destination_page_number(item)
                                                if page_number_0_indexed is not None:
                                                    extracted.append({"title": str(item.title), "page": page_number_0_indexed + 1})
                                            except Exception: # Skip item if page number can't be resolved
                                                pass 
                                    return extracted
                                processed_outline = extract_outline_items(pdf_reader.outline, pdf_reader)

                            st.session_state.pdf_metadata = {
                                "total_pages": len(pdf_reader.pages),
                                "outline": processed_outline
                            }
                            st.session_state.pdf_metadata_path = ncc_handbook_pdf_path
                    except ImportError:
                        st.error("PyPDF2 library not installed. PDF metadata cannot be extracted. Install with: `pip install PyPDF2`")
                        st.session_state.pdf_metadata = {"total_pages": 1, "outline": []} # Fallback
                        st.session_state.pdf_metadata_path = ncc_handbook_pdf_path
                    except Exception as e:
                        st.error(f"Error reading PDF for metadata: {str(e)}. Using default values.")
                        st.session_state.pdf_metadata = {"total_pages": 1, "outline": []} # Fallback
                        st.session_state.pdf_metadata_path = ncc_handbook_pdf_path

                total_pages = st.session_state.get("pdf_metadata", {}).get("total_pages", 1)
                pdf_outline = st.session_state.get("pdf_metadata", {}).get("outline", [])

                # PDF Sidebar Navigation (conditionally shown in global sidebar)
                with st.sidebar:
                    if app_mode == "📚 Syllabus Viewer": # Only show for this app_mode
                        st.markdown("### 📑 PDF Quick Navigation")
                        navigation_mode = st.radio(
                            "Navigate Handbook",
                            ["📖 Table of Contents", "🔖 Bookmarks", "🔍 Search PDF"],
                            key="pdf_nav_mode_syllabus"
                        )
                        
                        if navigation_mode == "📖 Table of Contents":
                            if pdf_outline:
                                for item_dict in pdf_outline:
                                    button_label = f"📄 {item_dict['title']} (p. {item_dict['page']})"
                                    button_key = f"toc_btn_{item_dict['title'].replace(' ','_').replace('/','_')}_{item_dict['page']}"
                                    if st.button(button_label, use_container_width=True, key=button_key):
                                        st.session_state.pdf_current_page = item_dict['page']
                                        st.rerun()
                            else:
                                st.info("No table of contents extracted or available.")
                                
                        elif navigation_mode == "🔖 Bookmarks":
                            if "bookmarks" in st.session_state and st.session_state.bookmarks:
                                for bookmark in st.session_state.bookmarks:
                                    if st.button(f"🔖 {bookmark['title']} (p. {bookmark['page']})", use_container_width=True, key=f"pdf_bookmark_{bookmark['title']}"):
                                        st.session_state.pdf_current_page = bookmark['page']
                                        st.rerun()
                            else:
                                st.info("No bookmarks added yet. Add bookmarks from the syllabus structure view.")
                                
                        elif navigation_mode == "🔍 Search PDF":
                            search_query_pdf = st.text_input("Search text in PDF", key="pdf_text_search")
                            if search_query_pdf:
                                st.info("PDF text search functionality is coming soon!")
                        else:
                            st.info("Enter text to search within the PDF content (feature coming soon).")
                
                # Main PDF viewer controls
                controls_container = st.container()
                with controls_container:
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    
                    with col1:
                        # Page navigation with total pages display
                        page = st.number_input(
                            f"Go to page (1-{total_pages})",
                            min_value=1,
                            max_value=total_pages,
                            value=st.session_state.get('pdf_current_page', 1),
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
                                page = max(1, (st.session_state.get('pdf_current_page', 1)) - 1)
                                st.session_state.pdf_current_page = page
                                st.rerun()

                    with col3:
                        # Next/Last page
                        col3a, col3b = st.columns(2)
                        with col3a:
                            if st.button("Next ▶️", use_container_width=True):
                                page = min(total_pages, (st.session_state.get('pdf_current_page', 1)) + 1)
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
                if page != st.session_state.get('pdf_current_page', 1):
                    st.session_state.pdf_current_page = page
                    st.rerun()

                # Help text
                st.info("💡 Due to browser limitations, PDF navigation might not work in all browsers. If you can't navigate pages, please use the download option to view the PDF locally.")

                # Display the PDF
                if not display_pdf_viewer(ncc_handbook_pdf_path, height=800):
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
        st.header("📁 View Your Interaction History")
        
        # Styling for history entries
        st.markdown("""
        <style>
        .history-entry {
            border: 1px solid #4A4A4A; /* Darker border for dark theme */
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 12px;
            background-color: #1E1E1E; /* Dark theme entry background */
        }
        .history-entry-light {
            border: 1px solid #DCDCDC; /* Lighter border for light theme */
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 12px;
            background-color: #F9F9F9; /* Light theme entry background */
        }
        </style>
        """, unsafe_allow_html=True)
        entry_class = "history-entry" if st.session_state.theme_mode == "Dark" else "history-entry-light"
        history_tabs = st.tabs(["💬 Chat History", "📝 Quiz History"])
        with history_tabs[0]:
            st.subheader("Recent Chat Interactions")
            chat_history_content = read_history("chat")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button("🧹 Clear Chat History", key="clear_chat_button"):
                    st.session_state.confirm_clear_chat = True
            with col2:
                if st.download_button(
                    "⬇️ Download Full Transcript",
                    chat_history_content,
                    file_name="chat_transcript.txt",
                    mime="text/plain",
                    key="download_full_chat"
                ):
                    st.success("Chat transcript downloaded!")
            
            if st.session_state.get("confirm_clear_chat", False):
                with st.form(key="confirm_clear_chat_form"):
                    st.warning("⚠️ Are you sure you want to clear the chat history?")
                    st.error("This action cannot be undone!")
                    col1, col2 = st.columns(2)
                    with col1:
                        confirm = st.form_submit_button("Yes, Clear History", type="primary")
                        if confirm:
                            clear_history("chat")
                            st.session_state.confirm_clear_chat = False
                            st.success("Chat history cleared!")
                            st.rerun()
                    with col2:
                        cancel = st.form_submit_button("No, Keep History")
                        if cancel:
                            st.session_state.confirm_clear_chat = False
                            st.info("Operation cancelled. Chat history preserved.")

            if chat_history_content:
                lines = chat_history_content.strip().splitlines()
                display_limit = 25 
                
                st.markdown(f"Showing last {min(len(lines), display_limit)} chat entries (newest first):")

                for line in reversed(lines[-display_limit:]):
                    if line.strip():
                        if ": " in line:
                            try:
                                speaker, message = line.split(": ", 1)
                                if speaker.lower() == "user":
                                    with st.chat_message("user"):
                                        st.markdown(message)
                                elif speaker.lower() in ["ai", "assistant", "bot", "gemini", "ncc_ai_assistant"]:
                                    with st.chat_message("assistant"):
                                        st.markdown(message)
                                else:
                                    st.markdown(f"<div class='{entry_class}'>{line}</div>", unsafe_allow_html=True)
                            except ValueError:
                                st.markdown(f"<div class='{entry_class}'>{line}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div class='{entry_class}'>{line}</div>", unsafe_allow_html=True)
                
                if len(lines) > display_limit:
                    st.caption(f"Older entries hidden. Download full history to view all {len(lines)} entries.")
                
                if st.download_button("⬇️ Download Full Chat History", chat_history_content, "chat_history.txt", key="download_chat_hist_main"):
                    st.success("Chat history downloaded!")
            else:
                st.info("No chat history found yet.")
        with history_tabs[1]:
            st.subheader("Recent Quiz Attempts")
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
                entries = quiz_history_content.strip().splitlines()
                display_limit = 25

                st.markdown(f"Showing last {min(len(entries), display_limit)} quiz records (newest first):")

                for i, entry_text in enumerate(reversed(entries[-display_limit:])):
                    if entry_text.strip():
                        try:
                            quiz_data = json.loads(entry_text)
                            # Display JSON nicely, perhaps in an expander
                            timestamp = quiz_data.get('timestamp', f"Record {len(entries) - i}")
                            score = quiz_data.get('score_percentage', quiz_data.get('score'))
                            expander_title = f"Quiz: {timestamp}"
                            if score is not None:
                                expander_title += f" - Score: {score}%" if isinstance(score, (int, float)) else f" - Score: {score}"
                            
                            with st.expander(expander_title):
                                st.json(quiz_data)
                        except json.JSONDecodeError:
                            st.markdown(f"<div class='{entry_class}'>{entry_text}</div>", unsafe_allow_html=True)
                
                if len(entries) > display_limit:
                    st.caption(f"Older records hidden. Download full history to view all {len(entries)} records.")

                if st.download_button("⬇️ Download Full Quiz History", quiz_history_content, "quiz_history.txt", key="download_quiz_hist_main"):
                    st.success("Quiz history downloaded!")
            else:
                st.info("No quiz history found yet. Take a quiz to start.")

    elif app_mode == "📊 Progress Dashboard":
        st.header("📊 Your Learning Progress")
        try:
            from progress_dashboard import display_progress_dashboard
            quiz_history_raw = read_history("quiz") # Pass data to the dashboard
            display_progress_dashboard(st.session_state, quiz_history_raw)
        except ImportError:
            st.info(
                "The Progress Dashboard is under development! "
                "It will soon visualize your performance and learning journey based on your quiz history and interactions. "
                "Keep taking quizzes to see your progress here!"
            )
            st.markdown("---")
            st.markdown("#### What to expect soon:")
            st.markdown("- 📈 Track your quiz scores over time.\n- 🎯 Identify strengths and weaknesses by topic.\n- 💡 See your overall engagement and learning patterns.")
            
            if st.checkbox("Show example dashboard elements (developer preview)", key="dev_dashboard_preview"):
                st.subheader("Example: Quiz Score Trend (Dummy Data)")
                try:
                    import pandas as pd
                    import numpy as np
                    chart_data = pd.DataFrame(
                        np.random.randint(50, 100, size=(8, 3)),
                        columns=['Common Subjects', 'Specialized Subjects', 'Overall Average']
                    )
                    st.line_chart(chart_data)

                    st.subheader("Example: Performance by Syllabus Section (Dummy Data)")
                    data = {'Section': ['Drill', 'Weapon Training', 'Map Reading', 'FC & BC', 'Leadership'],
                            'Average Score (%)': [85, 78, 92, 81, 88]}
                    df_bar = pd.DataFrame(data)
                    st.bar_chart(df_bar.set_index('Section'))
                except ImportError:
                    st.caption("Pandas and NumPy would be needed for this preview.")

    def render_syllabus_section():
        """Render the syllabus viewer section with modern navigation."""
        # Load syllabus data
        from syllabus_manager import load_syllabus_data, search_syllabus
        syllabus_data = load_syllabus_data()
        
        # Determine PDF file path
        ncc_handbook_pdf_path = os.path.join(os.path.dirname(__file__), "Ncc-CadetHandbook.pdf")

        # Add syllabus navigation options to sidebar
        st.sidebar.markdown(
            """
            <div class="syllabus-nav">
                <h3>📚 Syllabus Navigation</h3>
                <div class="nav-options">
                    <button class="nav-btn active" data-section="structure">
                        <span>🔍</span>Browse Structure
                    </button>
                    <button class="nav-btn" data-section="handbook">
                        <span>📖</span>View Handbook
                    </button>
                    <button class="nav-btn" data-section="bookmarks">
                        <span>🔖</span>Bookmarks
                    </button>
                </div>
            </div>
            <style>
            .syllabus-nav {
                padding: 1rem 0;
            }
            .syllabus-nav h3 {
                margin-bottom: 1rem;
                font-size: 1.1rem;
            }
            .nav-options {
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            }
            .nav-btn {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.5rem 1rem;
                border: none;
                background: transparent;
                border-radius: 4px;
                cursor: pointer;
                transition: all 0.2s;
                text-align: left;
                width: 100%;
            }
            .nav-btn:hover {
                background: rgba(255,255,255,0.1);
            }
            .nav-btn.active {
                background: rgba(255,255,255,0.15);
            }
            .nav-btn span {
                font-size: 1.2rem;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Initialize view state if not exists
        if "syllabus_view" not in st.session_state:
            st.session_state.syllabus_view = "structure"

        # Handle navigation clicks via query params
        params = st.query_params
        if "view" in params:
            st.session_state.syllabus_view = params["view"][0]

        # Render content based on selected view
        if st.session_state.syllabus_view == "structure":
            st.header("📚 Browse Syllabus")
            query = st.text_input("🔍 Search Topics", key="syllabus_search")
            
            if syllabus_data:
                if query:
                    search_results = search_syllabus(syllabus_data, query)
                    if search_results:
                        for result in search_results:
                            with st.expander(f"📎 {result['title']}", expanded=True):
                                st.write(result['content'])
                    else:
                        st.info(f"No results found for '{query}'")
                else:
                    for chapter in syllabus_data.chapters:
                        with st.expander(f"📘 {chapter.title}", expanded=False):
                            for section in chapter.sections:
                                st.markdown(f"### {section.title}")
                                st.write(section.content)
            else:
                st.error("Failed to load syllabus data")

        elif st.session_state.syllabus_view == "handbook":
            st.header("📖 NCC Handbook")
            # Modern PDF controls are already implemented
            if not display_pdf_viewer(ncc_handbook_pdf_path, height=800):
                st.error("Failed to load PDF viewer")

        else:  # bookmarks view
            st.header("🔖 Bookmarked Content")
            if "syllabus_bookmarks" not in st.session_state:
                st.session_state.syllabus_bookmarks = []
            
            if not st.session_state.syllabus_bookmarks:
                st.info("No bookmarks yet! Click the 🔖 icon next to any topic to bookmark it.")
            else:
                for bookmark in st.session_state.syllabus_bookmarks:
                    with st.expander(f"📎 {bookmark['title']}", expanded=True):
                        st.write(bookmark['content'])
                        if st.button("🗑️", key=f"remove_{bookmark['id']}"):
                            st.session_state.syllabus_bookmarks.remove(bookmark)
                            st.rerun()

def render_video_card(video, show_tags=False):
    """Render a video card with modern styling and hidden tags."""
    st.markdown(f"""
        <div class="video-card">
            <img src="{video.thumbnail}" class="thumbnail" alt="Video thumbnail">
            <div class="video-info">
                <h3>{video.title}</h3>
                <p class="description">{video.description[:150]}...</p>
                <div class="video-meta">
                    <span class="duration">⏱️ {video.duration}</span>
                    <span class="category">📂 {video.category}</span>
                </div>
                {'<div class="tags">' + ' '.join([f'<span class="tag">{tag}</span>' for tag in video.tags]) + '</div>' if show_tags else ''}
                <a href="{video.url}" target="_blank" class="watch-btn">Watch Now</a>
            </div>
        </div>
        <style>
        .video-card {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
            margin: 1rem 0;
            transition: transform 0.2s;
        }}
        .video-card:hover {{
            transform: translateY(-2px);
        }}
        .thumbnail {{
            width: 100%;
            height: 200px;
            object-fit: cover;
        }}
        .video-info {{
            padding: 1rem;
        }}
        .video-info h3 {{
            margin: 0 0 0.5rem 0;
            font-size: 1.1rem;
        }}
        .description {{
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }}
        .video-meta {{
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
            font-size: 0.9rem;
            color: #666;
        }}
        .watch-btn {{
            display: inline-block;
            padding: 0.5rem 1rem;
            background: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            transition: background 0.2s;
        }}
        .watch-btn:hover {{
            background: #0056b3;
        }}
        .tags {{
            display: none; /* Hide tags visually */
        }}
        </style>
    """, unsafe_allow_html=True)

def display_video_guides():
    """Display video guides with modern styling."""
    st.title("🎥 NCC Video Guides")

    # Load videos from data file
    if hasattr(st.session_state, 'video_data'):
        videos = st.session_state.video_data
    else:
        try:
            with open('data/videos.json', 'r') as f:
                videos = json.load(f)
            st.session_state.video_data = videos
        except Exception as e:
            st.error(f"Failed to load video data: {e}")
            return

    # Search functionality (includes hidden tags)
    search_query = st.text_input("🔍 Search videos by title, description, or topic", key="video_search")
    
    if search_query:
        filtered_videos = []
        for video in videos:
            # Search in title, description, category, and tags
            searchable_text = f"{video['title']} {video['description']} {video['category']} {' '.join(video['tags'])}".lower()
            if search_query.lower() in searchable_text:
                filtered_videos.append(video)
    else:
        filtered_videos = videos

    # Display videos in a grid
    cols = st.columns(2)
    for idx, video in enumerate(filtered_videos):
        with cols[idx % 2]:
            render_video_card(video)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.exception(e)