import streamlit as st
from syllabus_manager import load_syllabus_data, search_syllabus, extract_pdf_metadata, display_pdf_viewer_component
from config import NCC_HANDBOOK_PDF
import os

# Custom CSS for light mode
st.markdown("""
        <style>
        /* Light mode overrides for info/warning/metric/download */
        body[data-theme="light"] .stAlert, 
        body[data-theme="light"] .stDownloadButton button, 
        body[data-theme="light"] .stButton button, 
        body[data-theme="light"] .stMetric {
            color: #222 !important;
            background: #f3f4f6 !important;
            border: 1.5px solid #6366F1 !important;
        }
        body[data-theme="light"] .stAlert {
            background: #fef9c3 !important;
            border-color: #fde047 !important;
        }
        body[data-theme="light"] .stAlert[data-testid="stInfo"] {
            background: #e0e7ff !important;
            border-color: #6366F1 !important;
        }
        body[data-theme="light"] .stAlert[data-testid="stWarning"] {
            background: #fef3c7 !important;
            border-color: #f59e42 !important;
        }
        </style>
        """, unsafe_allow_html=True)

def show_syllabus_viewer():
    try:
        ncc_handbook_pdf_path = NCC_HANDBOOK_PDF
        syllabus_data = load_syllabus_data()
        tab1, tab2 = st.tabs(["Syllabus Structure", "View NCC Handbook (PDF)"])
        with tab1:
            st.subheader("Browse Syllabus Content")
            query = st.text_input("🔍 Search Syllabus Topics/Sections", key="syllabus_search_query")
            if syllabus_data:
                if query:
                    search_results = search_syllabus(syllabus_data, query)
                    if search_results:
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
                    if syllabus_data.chapters:
                        for chapter in syllabus_data.chapters:
                            with st.expander(f"📖 {chapter.title}"):
                                if chapter.sections:
                                    for i, section in enumerate(chapter.sections):
                                        st.markdown(f"##### 📄 {section.name}")
                                        st.markdown(section.content if section.content else "_No content available for this section._")
                                        if section.page_number:
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
                                        if i < len(chapter.sections) - 1:
                                            st.markdown("---")
                                else:
                                    st.info("No sections available for this chapter.")
                    else:
                        st.info("No chapters found in the syllabus data.")
            else:
                st.error("Failed to load syllabus data. Please check the 'data/syllabus.json' file and ensure it's correctly formatted.")
        with tab2:
            st.subheader("NCC Cadet Handbook Viewer")
            if 'pdf_current_page' not in st.session_state:
                st.session_state.pdf_current_page = 1
            if os.path.exists(ncc_handbook_pdf_path):
                try:
                    if "pdf_metadata" not in st.session_state or st.session_state.get("pdf_metadata_path") != ncc_handbook_pdf_path:
                        metadata = extract_pdf_metadata(ncc_handbook_pdf_path)
                        if metadata:
                            st.session_state.pdf_metadata = metadata
                            st.session_state.pdf_metadata_path = ncc_handbook_pdf_path
                        else:
                            st.session_state.pdf_metadata = {"total_pages": 1, "outline": [], "error": "Failed to extract metadata."}
                            st.session_state.pdf_metadata_path = ncc_handbook_pdf_path
                    total_pages = st.session_state.get("pdf_metadata", {}).get("total_pages", 1)
                    pdf_outline = st.session_state.get("pdf_metadata", {}).get("outline", [])
                    with st.container():
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
                                    button_label = f"📄 {item_dict['title']} (p. {item_dict['page']})"
                                    button_key = f"toc_btn_main_{item_dict['title'].replace(' ','_').replace('/','_')}_{item_dict['page']}"
                                    if st.button(button_label, use_container_width=True, key=button_key, help=f"{item_dict['title']} (p. {item_dict['page']})"):
                                        st.session_state.pdf_current_page = item_dict['page']
                                        st.rerun()
                            else:
                                st.info("No table of contents extracted or available.")
                        elif navigation_mode_main == "🔖 Bookmarks":
                            if "bookmarks" in st.session_state and st.session_state.bookmarks:
                                for i, bookmark in enumerate(st.session_state.bookmarks):
                                    if st.button(f"🔖 {bookmark['title']} (p. {bookmark['page']})", use_container_width=True, key=f"pdf_bookmark_main_{bookmark['title'].replace(' ','_')}_{bookmark['page']}", help=f"{bookmark['title']} (p. {bookmark['page']})"):
                                        st.session_state.pdf_current_page = bookmark['page']
                                        st.rerun()
                            else:
                                st.info("No bookmarks added yet. Add bookmarks from the syllabus structure view.")
                        elif navigation_mode_main == "🔍 Search PDF (soon)":
                            search_query_pdf_main = st.text_input("Search text in PDF (coming soon)", key="pdf_text_search_main", disabled=True)
                            if search_query_pdf_main:
                                st.info("PDF text search functionality is under development!")
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
                    if not display_pdf_viewer_component(
                        ncc_handbook_pdf_path, 
                        height=800, 
                        page_number=st.session_state.get('pdf_current_page', 1)
                    ):
                        st.warning("Could not display PDF in the browser. You can download it instead:")
                    with open(ncc_handbook_pdf_path, "rb") as f:
                        st.download_button(
                            "⬇️ Download NCC Cadet Handbook (PDF)",
                            f.read(),
                            file_name="Ncc-CadetHandbook.pdf",
                            mime="application/pdf",
                            key="download_handbook_syllabus_tab",
                            use_container_width=True
                        )
                except Exception as pdf_err:
                    st.error(f"An error occurred while displaying the PDF: {pdf_err}")
            else:
                st.warning(f"NCC Cadet Handbook PDF ('{ncc_handbook_pdf_path}') not found in the application's root directory. PDF viewer and download are unavailable.")
    except Exception as e:
        st.error(f"An error occurred in the syllabus viewer: {e}")
