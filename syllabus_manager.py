import json
import os
import logging
import streamlit as st # Import streamlit for st.error etc.
from dataclasses import dataclass, field
from typing import List, Optional, Dict

# --- Configure logging ---
from streamlit_pdf_viewer import pdf_viewer # For the actual viewer component
# Basic configuration for logging. You might want to adjust this based on your application's needs.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Define the Dataclasses for your Syllabus Structure ---
@dataclass
class Section:
    """Represents a section within a chapter of the NCC syllabus."""
    name: str
    page_number: Optional[int] = None # Added for PDF navigation
    content: Optional[str] = None  # Optional field for more detailed content

@dataclass
class Chapter:
    """Represents a chapter in the NCC syllabus."""
    title: str
    sections: List[Section] = field(default_factory=list)  # List of Section objects

@dataclass
class SyllabusData:
    """Represents the complete NCC syllabus data structure."""
    version: str  # Added for versioning
    chapters: List[Chapter] = field(default_factory=list)  # List of Chapter objects

# --- End of Dataclass Definitions ---

# --- Constants ---
# Try to determine project root more reliably if possible, or assume script is in project root
# For now, BASE_DIR is the directory of syllabus_manager.py
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__)) # Assuming this script is in the project root

# --- PDF Handling Functions ---

def extract_pdf_metadata(pdf_path: str) -> Optional[Dict]:
    """
    Extracts metadata (total pages, outline) from a PDF file.
    """
    try:
        import PyPDF2
        with open(pdf_path, 'rb') as pdf_file_obj:
            pdf_reader = PyPDF2.PdfReader(pdf_file_obj)
            processed_outline = []
            if hasattr(pdf_reader, 'outline') and pdf_reader.outline:
                def extract_outline_items_recursive(outline_items, reader):
                    extracted = []
                    for item in outline_items:
                        if isinstance(item, list): # It's a list of sub-items
                            extracted.extend(extract_outline_items_recursive(item, reader))
                        elif hasattr(item, 'title') and item.title is not None and hasattr(item, 'page') and item.page is not None:
                            # Direct page object reference
                             try:
                                page_number_0_indexed = reader.get_page_number(item.page)
                                extracted.append({"title": str(item.title), "page": page_number_0_indexed + 1})
                             except Exception: # If get_page_number fails for some reason
                                pass # Skip this item
                        elif hasattr(item, 'title') and item.title is not None:
                            # Destination reference (more common for outlines)
                            try:
                                # get_destination_page_number is the correct method for outline items
                                page_number_0_indexed = reader.get_destination_page_number(item)
                                if page_number_0_indexed is not None:
                                    extracted.append({"title": str(item.title), "page": page_number_0_indexed + 1})
                            except Exception: # Skip item if page number can't be resolved
                                pass
                    return extracted
                processed_outline = extract_outline_items_recursive(pdf_reader.outline, pdf_reader)

            return {
                "total_pages": len(pdf_reader.pages),
                "outline": processed_outline
            }
    except ImportError:
        st.error("PyPDF2 library not installed. PDF metadata cannot be extracted. Install with: `pip install PyPDF2`")
        logging.error("PyPDF2 library not installed.")
    except FileNotFoundError:
        st.error(f"PDF file not found for metadata extraction: {pdf_path}")
        logging.error(f"PDF file not found for metadata extraction: {pdf_path}")
    except Exception as e:
        st.error(f"Error reading PDF for metadata: {str(e)}")
        logging.exception(f"Error reading PDF for metadata from {pdf_path}: {e}")
    return None



# --- Syllabus Data Loading and Searching ---

# Assuming the JSON file is in the same directory as this script or a specific path
# If your original script had a more complex way to determine BASE_DIR, replicate that here.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SYLLABUS_FILENAME = os.path.join("data", "syllabus.json") # Default filename

def load_syllabus_data(file_name: str = DEFAULT_SYLLABUS_FILENAME) -> Optional[SyllabusData]:
    """
    Loads syllabus data from a JSON file, validates its structure,
    and converts it into SyllabusData dataclass objects.

    Args:
        file_name (str): The name of the syllabus JSON file.
                         It's expected to be in the data directory,
                         or an absolute path can be provided.

    Returns:
        Optional[SyllabusData]: A SyllabusData object if successful, None otherwise.
    """
    # Construct the full path to the syllabus file
    if not os.path.isabs(file_name):
        # If relative path, assume it's relative to the script directory
        # BASE_DIR is the directory of syllabus_manager.py.
        file_path = os.path.join(BASE_DIR, file_name)
    else:
        file_path = file_name

    # More robust check for file existence before opening
    if not os.path.exists(file_path):
        logging.error(f"Syllabus file not found at path: {file_path}")
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Validate the basic structure
        if 'version' not in data or 'chapters' not in data:
            logging.error("Invalid syllabus format: missing 'version' or 'chapters' field")
            return None
            
        syllabus = SyllabusData(version=data['version'])
        
        # Process chapters
        if isinstance(data['chapters'], list): # Expecting a list of chapter dicts
            for chapter_data_item in data['chapters']:
                if not isinstance(chapter_data_item, dict):
                    logging.warning(f"Skipping non-dictionary item in chapters list: {chapter_data_item}")
                    continue
                
                # Assuming chapter title is a key like "title" or use a default
                chapter_title = chapter_data_item.get('title', 'Untitled Chapter')
                chapter = Chapter(title=chapter_title)
                
                # Process sections if they exist and are a list of dicts
                if 'sections' in chapter_data_item and isinstance(chapter_data_item['sections'], list):
                    for section_data_item in chapter_data_item['sections']:
                        if not isinstance(section_data_item, dict):
                            logging.warning(f"Skipping non-dictionary item in sections list for chapter '{chapter_title}': {section_data_item}")
                            continue
                        
                        section = Section(
                            name=section_data_item.get('name', 'Untitled Section'), # Assuming section name key is 'name'
                            content=section_data_item.get('content', ''), # Assuming section content key is 'content'
                            page_number=section_data_item.get('page_number') # Get page number
                        )
                        chapter.sections.append(section)
                syllabus.chapters.append(chapter)
        else:
            logging.error("Invalid syllabus format: 'chapters' field is not a list.")
            return None
        return syllabus
        
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing syllabus JSON: {e}")
    except FileNotFoundError:
        logging.error(f"Syllabus file not found at '{file_path}'. Please ensure it exists and the path is correct.")
        # st.error(f"Syllabus file not found at '{file_path}'.") # Cannot use st.error here
    except Exception as e:
        logging.error(f"Error loading syllabus: {e}")
        
    return None

def get_syllabus_topics(syllabus_data: Optional[SyllabusData]) -> List[str]:
    """
    Extracts a list of main topics (chapter titles) from the syllabus data.

    Args:
        syllabus_data (Optional[SyllabusData]): The loaded syllabus data (dataclass object)
                                               or None if loading failed.

    Returns:
        List[str]: A list of main topic strings. Returns an empty list if input is None
                   or contains no chapters.
    """
    topics: List[str] = []
    if syllabus_data and syllabus_data.chapters:
        for chapter in syllabus_data.chapters:
            # Ensure chapter.title is a string, though dataclass definition should enforce this.
            if isinstance(chapter.title, str):
                 topics.append(chapter.title)
    return topics

def search_syllabus(syllabus_data: Optional[SyllabusData], query: str) -> List[Dict]:
    """
    Searches the syllabus data for chapters or sections matching the query.

    Args:
        syllabus_data (Optional[SyllabusData]): The loaded syllabus data (dataclass object)
                                               or None if loading failed.
        query (str): The search query (case-insensitive).

    Returns:
        List[Dict]: A list of dictionaries, each representing a matching chapter/section.
                    (Returning dicts here for easier consumption, e.g., in Streamlit's st.write,
                    but could also return custom search result dataclasses).
                    Returns an empty list if input is None or no matches are found.
    """
    if not syllabus_data or not syllabus_data.chapters:
        logging.info(f"Search query '{query}' attempted on empty or invalid syllabus data.")
        return []

    if not query or not isinstance(query, str): # Basic validation for query
        logging.warning("Search query is empty or not a string.")
        return []

    query_lower = query.lower()
    results: List[Dict] = []

    for chapter in syllabus_data.chapters:
        # Ensure chapter.title is a string
        if not isinstance(chapter.title, str):
            logging.warning(f"Skipping chapter in search due to non-string title: {chapter}")
            continue
        
        chapter_title_lower = chapter.title.lower()
        
        # Check if chapter title matches
        if query_lower in chapter_title_lower:
            results.append({
                "chapter_title": chapter.title,
                "match_type": "chapter",
                "content_preview": f"Chapter: {chapter.title}" # Added for clarity
            })
        
        # Iterate over section objects
        for section in chapter.sections:
            # Ensure section.name is a string
            if not isinstance(section.name, str):
                logging.warning(f"Skipping section in chapter '{chapter.title}' due to non-string name: {section}")
                continue

            section_name_lower = section.name.lower()
            if query_lower in section_name_lower:
                match_info = {
                    "chapter_title": chapter.title,
                    "section_name": section.name,
                    "match_type": "section",
                    "page_number": section.page_number, # Add page number to search results
                    # Provide section content if available, otherwise just the name
                    "content_preview": f"Section: {section.name}" + (f" - Content: {section.content[:50]}..." if section.content else "")
                }
                results.append(match_info)
            
            # Optionally, search within section.content as well
            if section.content and isinstance(section.content, str):
                if query_lower in section.content.lower():
                    # Avoid duplicate if name already matched
                    is_already_added = any(
                        r.get("chapter_title") == chapter.title and 
                        r.get("section_name") == section.name and
                        r.get("match_type") == "section_content" # or section
                        for r in results
                    ) # Basic check, might need refinement for exact duplicates
                    if not is_already_added: # Add only if not already added as a section name match
                         results.append({
                            "chapter_title": chapter.title,
                            "section_name": section.name,
                            "match_type": "section_content",
                            "page_number": section.page_number, # Add page number
                            "content_preview": f"Content in section '{section.name}': ...{section.content[max(0, section.content.lower().find(query_lower)-20) : section.content.lower().find(query_lower)+len(query_lower)+20]}..."
                        })


    if not results:
        logging.info(f"No results found for query: '{query}'")
    else:
        logging.info(f"Found {len(results)} results for query: '{query}'")
    return results

# --- Example Usage (Optional - for testing purposes) ---
if __name__ == "__main__":
    # Create a dummy ncc_syllabus.json for testing
    dummy_syllabus_content = {
        "version": "1.0-test",
        "chapters": [
            {
                "title": "The NCC General",
                "sections": [
                    {"name": "Aims of NCC", "page_number": 5, "content": "To develop character, comradeship, discipline, leadership..."},
                    {"name": "Organization of NCC", "page_number": 7, "content": "Details about NCC organization structure."},
                    {"name": "NCC Song", "page_number": 10, "content": "Hum Sab Bharatiya Hain..."}
                ]
            },
            {
                "title": "National Integration",
                "sections": [
                    {"name": "Importance of National Integration", "page_number": 12, "content": "Unity in diversity..."},
                    {"name": "Role of NCC in Nation Building", "page_number": 15, "content": "Contributions of NCC cadets."}
                ]
            },
            {
                "title": "Drill",
                "sections": [
                    {"name": "Foot Drill", "page_number": 20, "content": "Commands like Savdhan, Vishram..."},
                    {"name": "Arms Drill", "page_number": 25, "content": "Handling of rifles..."}
                ]
            }
        ]
    }
    # Create the dummy JSON file in the same directory as the script
    # Ensure the 'data' directory exists for the dummy file
    data_dir_for_dummy = os.path.join(BASE_DIR, "data")
    if not os.path.exists(data_dir_for_dummy):
        os.makedirs(data_dir_for_dummy, exist_ok=True)
    dummy_file_path = os.path.join(data_dir_for_dummy, "syllabus.json") # Assuming DEFAULT_SYLLABUS_FILENAME is "data/syllabus.json"
    try:
        with open(dummy_file_path, "w", encoding="utf-8") as f:
            json.dump(dummy_syllabus_content, f, indent=4)
        logging.info(f"Created dummy syllabus file at '{dummy_file_path}' for testing.")
    except IOError as e:
        logging.error(f"Failed to create dummy syllabus file: {e}")


    # Test loading the syllabus
    syllabus_data_obj = load_syllabus_data(DEFAULT_SYLLABUS_FILENAME) # Explicitly pass filename

    if syllabus_data_obj:
        logging.info(f"Syllabus Version: {syllabus_data_obj.version}")
        
        # Test getting topics
        topics = get_syllabus_topics(syllabus_data_obj)
        logging.info(f"\nSyllabus Topics ({len(topics)}):")
        for i, topic in enumerate(topics):
            logging.info(f"{i+1}. {topic}")

        # Test searching
        logging.info("\n--- Search Results ---")
        search_queries = ["NCC", "drill", "Integration", "nonexistent topic"]
        for q_idx, q in enumerate(search_queries):
            logging.info(f"\nSearching for: '{q}' (Query #{q_idx+1})")
            search_res = search_syllabus(syllabus_data_obj, q)
            if search_res:
                for r_idx, res_item in enumerate(search_res):
                    logging.info(f"  Result {r_idx+1}: Type: {res_item['match_type']}, Chapter: {res_item['chapter_title']}" +
                                 (f", Section: {res_item['section_name']}" if 'section_name' in res_item else "") +
                                 (f", Preview: {res_item.get('content_preview', 'N/A')}" ))
            else:
                logging.info(f"  No results found for '{q}'.")
        
        # Test with None input for robustness
        logging.info("\n--- Testing with None syllabus data ---")
        topics_none = get_syllabus_topics(None)
        logging.info(f"Topics from None: {topics_none} (Expected: [])")
        search_none = search_syllabus(None, "test")
        logging.info(f"Search from None: {search_none} (Expected: [])")

    else:
        logging.error("Failed to load syllabus data for testing.")

    # Clean up the dummy file (optional)
    # try:
    #     if os.path.exists(dummy_file_path):
    #         os.remove(dummy_file_path)
    #         logging.info(f"Cleaned up dummy syllabus file: '{dummy_file_path}'.")
    # except OSError as e:
    #     logging.error(f"Error removing dummy syllabus file: {e}")


def display_pdf_viewer_component(file_path: str, height: int = 750, page_number: int = 1) -> bool:
    """
    Embeds a PDF file in the Streamlit app using streamlit_pdf_viewer.
    This function focuses *only* on rendering the viewer component.
    Controls and download buttons should be handled outside this function.

    Args:
        file_path (str): Absolute path to the PDF file.
        height (int): Height of the PDF viewer.
        page_number (int): Initial page number to display.

    Returns:
        bool: True if PDF displayed successfully, False otherwise.
    """
    try:
        if not os.path.exists(file_path):
            st.error(f"🚨 PDF Error: File not found at '{file_path}'.")
            return False
        if not file_path.endswith('.pdf'):
            st.error("🚨 Invalid file type. Only PDF files are supported.")
            return False

        # The PDF viewer component
        # Using a dynamic key based on page_number to help force re-render if page changes.
        viewer_key = f"pdf_viewer_main_{page_number}_{os.path.basename(file_path)}"
        pdf_viewer(file_path, height=height, width="100%", pages_to_render=[page_number], key=viewer_key)
        return True
    except Exception as e: # Catch any exception from pdf_viewer or os.path
        st.error(f"🚨 Error displaying PDF: {str(e)}")
        logging.error(f"Error in display_pdf_viewer_component for {file_path}: {e}")
        return False
