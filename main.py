import os
import json
from functools import partial
from typing import Optional
import base64
# Core streamlit imports
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer

from utils import Config # Import Config to get DATA_DIR
# Local imports
from utils import (
    setup_gemini,
    get_ncc_response,
    API_CALL_COOLDOWN_MINUTES,
    clear_history, # Use the centralized clear_history
    read_history
)
from src.utils import ( # type: ignore
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

def get_image_as_base64(image_path):
    """Convert an image (PNG or SVG) to base64 data URL."""
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

def main():
    """    
    Main entry point for the NCC ABYAS application.
    Handles overall structure, navigation, theme, and routing to different features.
    """
    st.set_page_config(
        page_title="NCC ABYAS",
        page_icon=os.path.join(Config.DATA_DIR, "logo.svg"), # Use SVG for page icon
        layout="wide"
    )
    
    # Handle query parameters for chat navigation
    if st.query_params.get("go_chat"):
        st.session_state.app_mode = "💬 Chat Assistant"
        # Clear the query parameter
        st.query_params.clear()
        st.rerun()
    
    # Create a placeholder for the floating button at the top level.
    floating_button_placeholder = st.empty()

    # Initialize app_mode session state if not exists (single state variable for navigation)
    if "app_mode" not in st.session_state:
        st.session_state.app_mode = "🎯 Knowledge Quiz"
    
    # Initialize Gemini model first
    model, model_error = setup_gemini()
    
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

    # --- Custom Header ---
    header_col1, header_col2, header_col3 = st.columns([4, 1, 1])
    
    with header_col1:
        # Get logo as base64
        logo_path = os.path.join(Config.DATA_DIR, "logo.svg") # Use SVG logo
        logo_base64_data_url = get_image_as_base64(logo_path)
        
        # Create header with logo
        header_html = f'''
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <img src="{logo_base64_data_url}" style="height: 2rem; width: auto;">
                <h1 style="margin:0;font-size:1.25rem">NCC ABYAS</h1>
            </div>
        '''
        st.markdown(header_html, unsafe_allow_html=True)

    with header_col3:
        # Theme toggle button
        if "theme_mode" not in st.session_state:
            st.session_state.theme_mode = "Dark"
        
        current_theme = st.session_state.get("theme_mode", "Dark")
        theme_icon = "☀️" if current_theme == "Dark" else "🌙"
        theme_tooltip = "Switch to Light Theme" if current_theme == "Dark" else "Switch to Dark Theme"
        
        if st.button(theme_icon, help=theme_tooltip, key="theme_toggle", type="secondary"):
            st.session_state.theme_mode = "Light" if current_theme == "Dark" else "Dark"
            st.rerun()

    # Apply theme
    apply_theme(st.session_state.theme_mode)

    # --- Floating Chat Button (SVG Version) ---
    # Only show floating button when not in chat mode
    if st.session_state.app_mode != "💬 Chat Assistant":
        # Get chat icon as base64
        chat_icon_path = os.path.join(Config.DATA_DIR, "chat-icon.svg")
        chat_icon_base64 = get_image_as_base64(chat_icon_path)
        
        # We will render the button inside the placeholder we created earlier
        with floating_button_placeholder.container():
            # Create a clickable area that will use URL query parameters
            # Add target="_self" to ensure it opens in the same tab
            st.markdown(f"""
                <a href="?go_chat=1" id="floating-chat-button" aria-label="Open Chat Assistant" target="_self">
                    <img src="data:image/svg+xml;base64,{chat_icon_base64.split(',')[1]}" alt="Chat">
                </a>
            """, unsafe_allow_html=True)

        # Inject CSS for the floating button with SVG icon
        st.markdown(f"""
            <style>
                @keyframes pulse {{
                    0% {{ box-shadow: 0 4px 20px rgba(99, 102, 241, 0.3); }}
                    50% {{ box-shadow: 0 4px 25px rgba(99, 102, 241, 0.5); }}
                    100% {{ box-shadow: 0 4px 20px rgba(99, 102, 241, 0.3); }}
                }}
                
                /* Floating chat button styling */
                #floating-chat-button {{
                    position: fixed;
                    bottom: 2rem;
                    right: 2rem;
                    z-index: 9999;
                    width: 3.75rem;
                    height: 3.75rem;
                    border-radius: 50%;
                    background: linear-gradient(135deg, #6366F1, #8B5CF6);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    box-shadow: 0 4px 20px rgba(99, 102, 241, 0.3);
                    animation: pulse 2s infinite;
                    transition: all 0.3s ease;
                    cursor: pointer;
                    text-decoration: none;
                }}
                
                #floating-chat-button:hover {{
                    transform: translateY(-0.2rem);
                    box-shadow: 0 6px 25px rgba(99, 102, 241, 0.4);
                    background: linear-gradient(135deg, #5856EC, #7C3AED);
                }}
                
                #floating-chat-button img {{
                    width: 60%;
                    height: 60%;
                }}
            </style>
        """, unsafe_allow_html=True)
    else:
        # When in chat mode, clear the placeholder to remove the button
        floating_button_placeholder.empty()

    # --- Sidebar Navigation ---
    # NOTE: Only the default Streamlit sidebar toggle (top-left hamburger) is used. No custom close/hide button is implemented.
    st.sidebar.header("Navigation")

    # Chat Assistant is always available in sidebar regardless of mode
    navigation_options = ["💬 Chat Assistant", "🎯 Knowledge Quiz", "📚 Syllabus Viewer", 
                         "🎥 Video Guides", "📁 History Viewer", "📊 Progress Dashboard"]
    
    # Find the index of the current app_mode in navigation_options, default to 0 if not found
    try:
        current_index = navigation_options.index(st.session_state.app_mode)
    except ValueError:
        current_index = 0
        st.session_state.app_mode = navigation_options[0]
    
    app_mode = st.sidebar.radio(
        label="Navigation Menu",  # Add proper label for accessibility
        options=navigation_options,
        index=current_index,  # Select current mode with safe index
        key="app_mode_radio_primary",
        label_visibility="hidden"  # Hide the label since we have the header
    )
    
    # Update session state app_mode if changed
    if app_mode != st.session_state.app_mode:
        st.session_state.app_mode = app_mode
        st.rerun()

    st.sidebar.markdown("---")

    # API cooldown info
    st.sidebar.info(f"API Cooldown: Please wait ~{API_CALL_COOLDOWN_MINUTES} min. if you hit rate limits.")

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
        
    # Add a back button only when in Chat Assistant mode
    if st.session_state.app_mode == "💬 Chat Assistant":
        # Get the most recently used non-chat mode or default to Knowledge Quiz
        previous_modes = [mode for mode in st.session_state.get('previous_modes', ["🎯 Knowledge Quiz"]) if mode != "💬 Chat Assistant"]
        previous_mode = previous_modes[0] if previous_modes else "🎯 Knowledge Quiz"
        
        # Add a back button for returning from chat
        if st.button(f"← Back to {previous_mode.split(' ', 1)[1]}", key="back_from_chat"):
            st.session_state.app_mode = previous_mode
            st.rerun()
        
        st.markdown("---")
    
    # Store navigation history (last 3 non-duplicate modes)
    if "previous_modes" not in st.session_state:
        st.session_state.previous_modes = [st.session_state.app_mode]
    elif st.session_state.app_mode != st.session_state.previous_modes[0]:
        # Add current mode to front of list if it's different
        st.session_state.previous_modes = [st.session_state.app_mode] + [
            mode for mode in st.session_state.previous_modes 
            if mode != st.session_state.app_mode
        ][:2]  # Keep only last 2 previous modes for a total of 3

    # Handle dev tools route
    if st.query_params.get("page") == ["dev_tools"]:
        # Lazy import dev_tools only when the route is accessed
        from dev_tools import dev_tools as display_dev_tools
        display_dev_tools()
        return # Stop further rendering of main page if dev_tools is active

    # --- Module Routing ---
    if st.session_state.app_mode == "💬 Chat Assistant":
        from chat_interface import chat_interface # Lazy import
        chat_func = partial(get_ncc_response, model, model_error)
        chat_interface()

    elif st.session_state.app_mode == "🎯 Knowledge Quiz":
        from quiz_interface import _initialize_quiz_state, quiz_interface # Lazy imports
        _initialize_quiz_state(st.session_state) # Always initialize quiz state first
        if model: # model is from setup_gemini() at the top of main()
            quiz_interface(model, model_error) # Pass model and model_error
        else:
            st.error("Model failed to load, Quiz feature is unavailable.")

    elif st.session_state.app_mode == "📚 Syllabus Viewer":
        ncc_handbook_pdf_path = "Ncc-CadetHandbook.pdf" # Define path once

        # Import necessary functions from syllabus_manager
        from syllabus_manager import load_syllabus_data, search_syllabus, extract_pdf_metadata, display_pdf_viewer_component
        syllabus_data = load_syllabus_data()

        
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
                                        st.toast(f"PDF target set to page {page_num}. Switch to the 'View NCC Handbook (PDF)' tab.", icon="📄")
                                        st.rerun()
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
                                                    st.toast(f"PDF target set to page {section.page_number}. Switch to the 'View NCC Handbook (PDF)' tab.", icon="📄")
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
            st.subheader("NCC Cadet Handbook Viewer")
            
            # Initialize session state for PDF page navigation if not already done
            if 'pdf_current_page' not in st.session_state:
                st.session_state.pdf_current_page = 1

            if os.path.exists(ncc_handbook_pdf_path):
                # --- PDF Metadata Initialization (once per PDF load) ---
                if "pdf_metadata" not in st.session_state or \
                   st.session_state.get("pdf_metadata_path") != ncc_handbook_pdf_path:
                    metadata = extract_pdf_metadata(ncc_handbook_pdf_path)
                    if metadata:
                        st.session_state.pdf_metadata = metadata
                        st.session_state.pdf_metadata_path = ncc_handbook_pdf_path
                    else:
                        # Fallback if metadata extraction fails
                        st.session_state.pdf_metadata = {"total_pages": 1, "outline": [], "error": "Failed to extract metadata."}
                        st.session_state.pdf_metadata_path = ncc_handbook_pdf_path

                total_pages = st.session_state.get("pdf_metadata", {}).get("total_pages", 1)
                pdf_outline = st.session_state.get("pdf_metadata", {}).get("outline", [])

                # PDF Sidebar Navigation is MOVED to the main content area of this tab.
                # The 'with st.sidebar:' block that previously contained these controls is now empty for this app_mode.
                
                # --- PDF Navigation Controls MOVED HERE (Inside Tab2, above viewer) ---
                with st.container(): # Group controls
                    # Removed markdown heading for "PDF Quick Navigation"
                    navigation_mode_main = st.radio(
                        "Navigate Handbook By:",
                        ["📖 Table of Contents", "🔖 Bookmarks", "🔍 Search PDF (soon)"],
                        key="pdf_nav_mode_main_area", 
                        horizontal=True,
                        help="Select a method to navigate the PDF document."
                    )
                    
                    if navigation_mode_main == "📖 Table of Contents":
                        if pdf_outline:
                            for i, item_dict in enumerate(pdf_outline):
                                # Use a single column for linearity
                                button_label = f"📄 {item_dict['title']} (p. {item_dict['page']})" # Use full title + page number
                                button_key = f"toc_btn_main_{item_dict['title'].replace(' ','_').replace('/','_')}_{item_dict['page']}"
                                if st.button(button_label, use_container_width=True, key=button_key, help=f"{item_dict['title']} (p. {item_dict['page']})"):
                                        st.session_state.pdf_current_page = item_dict['page']
                                        st.rerun()
                        else:
                            st.info("No table of contents extracted or available.")
                            
                    elif navigation_mode_main == "🔖 Bookmarks":
                        if "bookmarks" in st.session_state and st.session_state.bookmarks:
                            for i, bookmark in enumerate(st.session_state.bookmarks):
                                # Use a single column for linearity
                                if st.button(f"🔖 {bookmark['title']} (p. {bookmark['page']})", use_container_width=True, key=f"pdf_bookmark_main_{bookmark['title'].replace(' ','_')}_{bookmark['page']}", help=f"{bookmark['title']} (p. {bookmark['page']})"):
                                        st.session_state.pdf_current_page = bookmark['page']
                                        st.rerun()
                        else:
                            st.info("No bookmarks added yet. Add bookmarks from the syllabus structure view.")
                    
                    elif navigation_mode_main == "🔍 Search PDF (soon)":
                        search_query_pdf_main = st.text_input("Search text in PDF (coming soon)", key="pdf_text_search_main", disabled=True)
                        if search_query_pdf_main: # This block won't run due to disabled=True
                            st.info("PDF text search functionality is under development!")

                    # Removed markdown separator and heading for "Page Controls"
                    # The page controls will now appear directly after the TOC/Bookmarks/Search section
                    
                    page_controls_cols = st.columns([2,1,1,1,1]) 
                    with page_controls_cols[0]:
                        current_page_for_input_main = st.session_state.get('pdf_current_page', 1)
                        target_page_main = st.number_input(
                            f"Go to Page (1-{total_pages})", 
                            min_value=1, 
                            max_value=total_pages, 
                            value=current_page_for_input_main, 
                            step=1, 
                            key="pdf_page_selector_main_area", 
                            help="Enter page number and press Enter"
                        )
                        if target_page_main != current_page_for_input_main:
                            st.session_state.pdf_current_page = target_page_main
                            st.rerun()
                    
                    with page_controls_cols[1]:
                        if st.button("⏮️", use_container_width=True, help="First Page", key="pdf_first_main"):
                            st.session_state.pdf_current_page = 1
                            st.rerun()
                    with page_controls_cols[2]:
                        if st.button("◀️", use_container_width=True, help="Previous Page", key="pdf_prev_main"):
                            st.session_state.pdf_current_page = max(1, st.session_state.get('pdf_current_page', 1) - 1)
                            st.rerun()
                    with page_controls_cols[3]:
                        if st.button("▶️", use_container_width=True, help="Next Page", key="pdf_next_main"):
                            st.session_state.pdf_current_page = min(total_pages, st.session_state.get('pdf_current_page', 1) + 1)
                            st.rerun()
                    with page_controls_cols[4]:
                        if st.button("⏭️", use_container_width=True, help="Last Page", key="pdf_last_main"):
                            st.session_state.pdf_current_page = total_pages
                            st.rerun()
                    st.markdown("---") 
                # End of MOVED PDF Navigation Controls

                st.info("💡 PDF navigation is available through the controls above and the viewer's built-in controls. If you experience any issues, you can download the PDF to view it locally.", icon="ℹ️")

                # Display the PDF
                # Use the new display_pdf_viewer_component from syllabus_manager
                if not display_pdf_viewer_component(
                    ncc_handbook_pdf_path, 
                    height=800, 
                    page_number=st.session_state.get('pdf_current_page', 1)
                ):
                    st.warning("Could not display PDF in the browser. You can download it instead:")
                    
                # Offer download option in the main area as well
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
    



    elif st.session_state.app_mode == "🎥 Video Guides":
        from video_guides import video_guides as display_video_guides # Lazy import
        display_video_guides()

    elif st.session_state.app_mode == "📁 History Viewer":
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

        # --- Chat History Tab ---
        with history_tabs[0]:
            st.subheader("Recent Chat Interactions")
            chat_history_data = read_history("chat") # Read raw data (list of dicts)
            col1, col2 = st.columns([3,1]) # Define col1 and col2 here
            with col1:
                if st.button(
                    "🧹 Clear Chat History",
                    key="clear_chat_button",
                    help="Delete all saved chat messages",
                    use_container_width=True
                ):
                    st.session_state.confirm_clear_chat = True

            # Confirmation dialog for clearing chat history
            if st.session_state.get("confirm_clear_chat", False):
                st.warning("Are you sure you want to clear the chat history? This cannot be undone.")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("Yes, Clear Chat History", key="confirm_yes_chat_hist"):
                        clear_history("chat") # Use the centralized clear_history
                        st.session_state.confirm_clear_chat = False
                        st.success("Chat history cleared!")
                        st.rerun()
                with col_no:
                    if st.button("No, Keep Chat History", key="confirm_no_chat_hist"):
                        st.session_state.confirm_clear_chat = False
                        st.info("Chat history not cleared.")

            # Display chat history entries
            if chat_history_data:
                # Display newest first
                for i, entry in enumerate(reversed(chat_history_data)):
                    timestamp = entry.get("timestamp", "Unknown time")
                    prompt = entry.get("prompt", "No prompt text")
                    response = entry.get("response", "No response text")

                    # Use expander for each conversation
                    with st.expander(f"[{timestamp}] User: {prompt[:100]}..."):
                        st.markdown(f"**User:** {prompt}")
                        st.markdown(f"**Assistant:** {response}")
                        # Optional: Add a separator between entries within the expander if needed
                        # st.markdown("---")
            else:
                st.info("No chat history found yet. Start a conversation in the Chat Assistant tab.")

            with col2:
                st.download_button(
                    "⬇️ Download History",
                    read_history("chat_transcript"), # Download the transcript for readability
                    "chat_history.txt",
                    key="download_chat_hist_main",
                    help="Save a copy of your chat history to your computer"
                )

        with history_tabs[1]:
            st.subheader("Recent Quiz Attempts")
            quiz_history_data = read_history("quiz") # Read raw data (list of dicts)

            if st.button(
                "🧹 Clear Quiz History",
                key="clear_quiz_button",
                help="Delete all saved quiz attempts",
                use_container_width=True
            ):
                st.session_state.confirm_clear_quiz = True

            # Download button for quiz log (full questions/answers)
            st.download_button(
                "⬇️ Download Quiz History",
                read_history("quiz_log"), # Use the raw log data
                "quiz_log.json", # Save as JSON
                key="download_quiz_hist_main",
                help="Save a copy of your quiz history to your computer"
            )
            
            if st.session_state.get("confirm_clear_quiz", False):
                st.warning("Are you sure you want to clear the quiz history? This cannot be undone.")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Yes, Clear Quiz History", key="confirm_yes_quiz_hist"):
                        clear_history("quiz")
                        st.session_state.confirm_clear_quiz = False
                        st.success("Quiz history cleared!")
                        st.rerun()
                with col2:
                    if st.button("No, Keep Quiz History", key="confirm_no_quiz"):
                        st.session_state.confirm_clear_quiz = False
                        st.info("Quiz history not cleared.") # This info message might disappear on rerun

            # Display quiz history entries
            if quiz_history_data:
                # Display newest first
                for i, quiz_log_entry in enumerate(reversed(quiz_history_data)):
                    timestamp = quiz_log_entry.get("timestamp", "Unknown time")
                    topic = quiz_log_entry.get("topic", "Unknown Topic")
                    difficulty = quiz_log_entry.get("difficulty", "N/A")
                    questions = quiz_log_entry.get("questions", [])

                    expander_title = f"[{timestamp}] Quiz on {topic} ({difficulty}, {len(questions)} Qs)"

                    with st.expander(expander_title):
                        if questions:
                            for q_idx, q_data in enumerate(questions):
                                st.markdown(f"**Q{q_idx + 1}:** {q_data.get('question', 'N/A')}")
                                options = q_data.get('options', {})
                                for opt_key, opt_text in options.items():
                                    st.markdown(f"- {opt_key}) {opt_text}")
                                st.markdown(f"**Correct Answer:** {q_data.get('answer', 'N/A')}")
                                st.markdown(f"**Explanation:** {q_data.get('explanation', 'No explanation provided.')}")
                                if q_idx < len(questions) - 1:
                                    st.markdown("---") # Separator between questions
            else:
                st.info("No quiz history found yet. Take a quiz to start.")

    elif st.session_state.app_mode == "📊 Progress Dashboard":
        try:
            from progress_dashboard import display_progress_dashboard
            # Pass quiz score history to the dashboard, not the quiz log
            quiz_history_raw = read_history("quiz_score") 
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

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.exception(e)