import json
import os
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict

# --- Configure logging ---
# Basic configuration for logging. You might want to adjust this based on your application's needs.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Define the Dataclasses for your Syllabus Structure ---
@dataclass
class Section:
    """Represents a section within a chapter of the NCC syllabus."""
    name: str
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
# Assuming the JSON file is in the same directory as this script or a specific path
# If your original script had a more complex way to determine BASE_DIR, replicate that here.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SYLLABUS_FILENAME = "ncc_syllabus.json" # Default filename

def load_syllabus_data(file_name: str = DEFAULT_SYLLABUS_FILENAME) -> Optional[SyllabusData]:
    """
    Loads syllabus data from a JSON file, validates its structure,
    and converts it into SyllabusData dataclass objects.

    Args:
        file_name (str): The name of the syllabus JSON file.
                         It's expected to be in the same directory as this script,
                         or an absolute path can be provided.

    Returns:
        Optional[SyllabusData]: A SyllabusData object if successful, None otherwise.
    """
    # Construct the full path to the syllabus file
    if os.path.isabs(file_name):
        full_path = file_name
    else:
        full_path = os.path.join(BASE_DIR, file_name)

    logging.info(f"Attempting to load syllabus data from '{full_path}'")

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            raw_syllabus_dict = json.load(f)
            logging.info(f"Successfully loaded raw syllabus data from '{full_path}'.")

        if not raw_syllabus_dict:
            logging.warning(f"Syllabus data file '{full_path}' is empty.")
            return None

        # --- NEW: Convert raw dict to dataclass objects ---
        syllabus_version = raw_syllabus_dict.get("version", "unknown") # Expects 'version' key
        chapters_data = raw_syllabus_dict.get("chapters", [])
        
        parsed_chapters: List[Chapter] = []
        if not isinstance(chapters_data, list):
            logging.error(f"'chapters' field is not a list in '{full_path}'. Found: {type(chapters_data)}")
            return None

        for chapter_dict in chapters_data:
            if not isinstance(chapter_dict, dict):
                logging.warning(f"Skipping chapter item as it's not a dictionary: {chapter_dict}")
                continue
            
            chapter_title = chapter_dict.get("title")
            if not chapter_title:
                logging.warning(f"Skipping chapter due to missing title: {chapter_dict}")
                continue

            parsed_sections: List[Section] = []
            sections_data = chapter_dict.get("sections", [])
            if not isinstance(sections_data, list):
                logging.warning(f"Skipping sections in chapter '{chapter_title}' as 'sections' is not a list. Found: {type(sections_data)}")
            else:
                for section_dict in sections_data:
                    if not isinstance(section_dict, dict):
                        logging.warning(f"Skipping section item in chapter '{chapter_title}' as it's not a dictionary: {section_dict}")
                        continue

                    section_name = section_dict.get("name")
                    if not section_name:
                        logging.warning(f"Skipping section due to missing name in chapter '{chapter_title}': {section_dict}")
                        continue
                    parsed_sections.append(Section(name=section_name, content=section_dict.get("content")))
            
            parsed_chapters.append(Chapter(title=chapter_title, sections=parsed_sections))
        
        syllabus_obj = SyllabusData(version=syllabus_version, chapters=parsed_chapters)
        logging.info("Syllabus data successfully converted to dataclass objects.")
        return syllabus_obj

    except FileNotFoundError:
        logging.error(f"Syllabus file not found at '{full_path}'. Please ensure it exists.")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from '{full_path}': {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred while loading syllabus data: {e}", exc_info=True)
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
            else:
                logging.warning(f"Found a chapter with a non-string title: {chapter}")
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
                    {"name": "Aims of NCC", "content": "To develop character, comradeship, discipline, leadership..."},
                    {"name": "Organization of NCC", "content": "Details about NCC organization structure."},
                    {"name": "NCC Song", "content": "Hum Sab Bharatiya Hain..."}
                ]
            },
            {
                "title": "National Integration",
                "sections": [
                    {"name": "Importance of National Integration", "content": "Unity in diversity..."},
                    {"name": "Role of NCC in Nation Building", "content": "Contributions of NCC cadets."}
                ]
            },
            {
                "title": "Drill",
                "sections": [
                    {"name": "Foot Drill", "content": "Commands like Savdhan, Vishram..."},
                    {"name": "Arms Drill", "content": "Handling of rifles..."}
                ]
            }
        ]
    }
    # Create the dummy JSON file in the same directory as the script
    dummy_file_path = os.path.join(BASE_DIR, DEFAULT_SYLLABUS_FILENAME)
    try:
        with open(dummy_file_path, "w", encoding="utf-8") as f:
            json.dump(dummy_syllabus_content, f, indent=4)
        logging.info(f"Created dummy syllabus file at '{dummy_file_path}' for testing.")
    except IOError as e:
        logging.error(f"Failed to create dummy syllabus file: {e}")


    # Test loading the syllabus
    syllabus_data_obj = load_syllabus_data() # Uses DEFAULT_SYLLABUS_FILENAME

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

