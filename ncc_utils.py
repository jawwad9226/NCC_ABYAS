# This file was previously utils.py and is now ncc_utils.py
# All shared utility functions and classes are defined here.

import os
import google.generativeai as genai
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any, Union
import re
import streamlit as st
import logging
import json
import csv
from dataclasses import dataclass
from pathlib import Path

# --- Configuration ---
@dataclass
class Config:
    # ...existing code from utils.py Config...
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    LOGS_DIR = os.path.join(BASE_DIR, "logs")
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    QUIZ_SCORE_HISTORY_FILE = os.path.join(DATA_DIR, "quiz_score_history.json")
    APP_LOG_FILE = os.path.join(LOGS_DIR, "app.log")
    LOG_PATHS = {
        'chat': {
            'history': os.path.join(DATA_DIR, "chat_history.json"),
            'transcript': os.path.join(DATA_DIR, "chat_transcript.txt")
        },
        'quiz': {
            'log': os.path.join(DATA_DIR, "quiz_log.json"),
            'scores': os.path.join(DATA_DIR, "quiz_score_history.json"),
            'transcript': os.path.join(DATA_DIR, "quiz_transcript.txt"),
            'bookmarks': os.path.join(DATA_DIR, "quiz_bookmarks.json")
        },
        'bookmark': {
            'data': os.path.join(DATA_DIR, "bookmarks.json")
        },
        'app': {
            'log': os.path.join(LOGS_DIR, "app.log")
        }
    }
    MODEL_NAME = 'gemini-1.5-flash'
    TEMP_CHAT = 0.3
    TEMP_QUIZ = 0.4
    MAX_TOKENS_CHAT = 1000
    MAX_TOKENS_QUIZ = 2000
    API_CALL_COOLDOWN_MINUTES = 2
    QUESTION_COUNTS = {"Easy": 3, "Medium": 5, "Hard": 8}
    @classmethod
    def ensure_data_dir(cls):
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.LOGS_DIR, exist_ok=True)
Config.ensure_data_dir()
API_CALL_COOLDOWN_MINUTES = Config.API_CALL_COOLDOWN_MINUTES

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(Config.LOG_PATHS['app']['log']),
        logging.StreamHandler()
    ]
)

@st.cache_resource
def setup_gemini() -> Tuple[Optional[genai.GenerativeModel], Optional[str]]:
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_api_key_here":
            error_msg = (
                "GEMINI_API_KEY environment variable is not set or is using the default value. "
                "Please set it to your actual Gemini API key."
            )
            logging.error(error_msg)
            return None, error_msg
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(Config.MODEL_NAME)
        return model, None
    except Exception as e:
        error_msg = f"Failed to initialize Gemini model: {str(e)}"
        logging.exception(error_msg)
        return None, "Apologies, we're experiencing technical difficulties. Please try again later."

# --- File Operations, Quiz, Chat, and Helpers ---

def read_json_file(file_path: str) -> Any:
    """Reads a JSON file and returns the content."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_json_file(file_path: str, data: Any) -> None:
    """Writes data to a JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def append_to_json_file(file_path: str, data: Any) -> None:
    """Appends data to a JSON file."""
    current_data = read_json_file(file_path)
    if isinstance(current_data, list):
        current_data.append(data)
    else:
        current_data = [current_data, data]
    write_json_file(file_path, current_data)

def read_csv_file(file_path: str) -> List[Dict[str, str]]:
    """Reads a CSV file and returns the content as a list of dictionaries."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def write_csv_file(file_path: str, data: List[Dict[str, str]]) -> None:
    """Writes data to a CSV file."""
    if not data:
        return
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

def clear_chat_history() -> None:
    """Clears the chat history."""
    open(Config.LOG_PATHS['chat']['history'], 'w').close()
    open(Config.LOG_PATHS['chat']['transcript'], 'w').close()

def clear_quiz_data() -> None:
    """Clears the quiz data."""
    open(Config.LOG_PATHS['quiz']['log'], 'w').close()
    open(Config.LOG_PATHS['quiz']['scores'], 'w').close()
    open(Config.LOG_PATHS['quiz']['transcript'], 'w').close()
    open(Config.LOG_PATHS['quiz']['bookmarks'], 'w').close()

def log_chat_message(role: str, content: str) -> None:
    """Logs a chat message to the history file."""
    timestamp = datetime.now().isoformat()
    log_entry = {"timestamp": timestamp, "role": role, "content": content}
    append_to_json_file(Config.LOG_PATHS['chat']['history'], log_entry)

def log_quiz_event(event_type: str, details: Dict[str, Any]) -> None:
    """Logs a quiz event (e.g., start, end, question, answer) to the log file."""
    timestamp = datetime.now().isoformat()
    log_entry = {"timestamp": timestamp, "event_type": event_type, "details": details}
    append_to_json_file(Config.LOG_PATHS['quiz']['log'], log_entry)

def get_chat_history() -> List[Dict[str, str]]:
    """Retrieves the chat history."""
    return read_json_file(Config.LOG_PATHS['chat']['history'])

def get_quiz_scores() -> List[Dict[str, Union[str, int]]]:
    """Retrieves the quiz scores."""
    return read_json_file(Config.LOG_PATHS['quiz']['scores'])

def get_quiz_log() -> List[Dict[str, Union[str, int]]]:
    """Retrieves the quiz log."""
    return read_json_file(Config.LOG_PATHS['quiz']['log'])

def get_bookmarks() -> List[Dict[str, Union[str, int]]]:
    """Retrieves the bookmarks."""
    return read_json_file(Config.LOG_PATHS['bookmark']['data'])

def add_bookmark(name: str, url: str) -> None:
    """Adds a bookmark."""
    bookmark = {"name": name, "url": url}
    append_to_json_file(Config.LOG_PATHS['bookmark']['data'], bookmark)

def remove_bookmark(url: str) -> None:
    """Removes a bookmark by URL."""
    bookmarks = get_bookmarks()
    bookmarks = [b for b in bookmarks if b['url'] != url]
    write_json_file(Config.LOG_PATHS['bookmark']['data'], bookmarks)

def update_bookmark(old_url: str, new_name: str, new_url: str) -> None:
    """Updates a bookmark's name and URL."""
    bookmarks = get_bookmarks()
    for b in bookmarks:
        if b['url'] == old_url:
            b['name'] = new_name
            b['url'] = new_url
    write_json_file(Config.LOG_PATHS['bookmark']['data'], bookmarks)

def search_bookmarks(query: str) -> List[Dict[str, Union[str, int]]]:
    """Searches bookmarks by name or URL."""
    bookmarks = get_bookmarks()
    query = query.lower()
    return [b for b in bookmarks if query in b['name'].lower() or query in b['url'].lower()]

def generate_quiz(questions: List[str], model: genai.GenerativeModel) -> List[Dict[str, str]]:
    """Generates a quiz based on the provided questions using the Gemini model."""
    # ...existing code for generating quiz...
    pass

def grade_quiz(user_answers: List[str], correct_answers: List[str]) -> int:
    """Grades the quiz and returns the score."""
    # ...existing code for grading quiz...
    pass

def format_chat_history_for_display(history: List[Dict[str, str]]) -> str:
    """Formats the chat history for display in the app."""
    # ...existing code for formatting chat history...
    pass

def format_quiz_results_for_display(results: List[Dict[str, Union[str, int]]]) -> str:
    """Formats the quiz results for display in the app."""
    # ...existing code for formatting quiz results...
    pass

def get_time_until_next_api_call() -> str:
    """Calculates the time until the next API call is allowed."""
    # ...existing code for calculating time until next API call...
    pass

def is_api_call_due(last_call_time: Optional[datetime]) -> bool:
    """Checks if an API call is due based on the last call time."""
    # ...existing code for checking if API call is due...
    pass

def get_ncc_response(model: genai.GenerativeModel, model_error: Optional[str], prompt: str) -> str:
    """Generate a response from the Gemini model.
    Args:
        model: Initialized Gemini model instance
        model_error: Error message if model initialization failed
        prompt: User's input prompt
    Returns:
        Generated response or error message
    """
    if not model or model_error:
        return f"Error: {model_error or 'Model not initialized'}"

    if not prompt or not prompt.strip():
        return "Please provide a valid question or prompt."

    # Cooldown logic (if needed, implement your own or use session state)
    # if _is_in_cooldown("last_api_call_time"):
    #     return _cooldown_message("chat")

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=Config.TEMP_CHAT,
                max_output_tokens=Config.MAX_TOKENS_CHAT
            )
        )
        # Optionally update last_api_call_time here
        response_text = response.text.strip()
        # Save the chat interaction to file if needed
        # if prompt and response_text:
        #     save_chat_to_file(user_prompt=prompt, assistant_response=response_text)
        return response_text
    except Exception as e:
        error_msg = "Apologies, I'm having trouble processing your request. Please try again in a moment."
        logging.exception(f"Error in get_ncc_response: {str(e)}")
        return error_msg

def clear_history(file_type: str = "chat") -> bool:
    """Clear history files for the specified type.
    Args:
        file_type: Type of history to clear ('chat' or 'quiz')
    Returns:
        bool: True if successful, False otherwise. Note: This clears files, not session state.
    """
    try:
        paths_to_clear = []
        if file_type == "chat":
            paths_to_clear = [
                Config.LOG_PATHS['chat']['history'],
                Config.LOG_PATHS['chat']['transcript']
            ]
        elif file_type == "quiz":
            paths_to_clear = [
                Config.LOG_PATHS['quiz']['log'],
                Config.LOG_PATHS['quiz']['transcript'],
                Config.LOG_PATHS['quiz']['bookmarks']
            ]
        if not paths_to_clear:
            return False
        success = True
        for path in paths_to_clear:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    logging.error(f"Failed to clear {path}: {str(e)}")
                    success = False
        return success
    except Exception as e:
        logging.error(f"Failed to clear {file_type} history: {str(e)}")
        return False

def read_history(file_type: str = "chat") -> Union[List[Dict], str]:
    """Read history for the specified type and return raw data.
    Args:
        file_type: Type of history to read ('chat', 'quiz', 'quiz_score', 'bookmark', 'chat_transcript', 'quiz_log')
    Returns:
        List[Dict]: List of history items for 'chat', 'quiz', 'bookmark'.
        str: JSON string for 'quiz_score', or text content for 'chat_transcript', 'quiz_log' (as JSON string).
        Empty list or string if file not found or error occurs.
    """
    if file_type == "chat":
        path = Config.LOG_PATHS['chat']['history']
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    if file_type == "quiz":
        path = Config.LOG_PATHS['quiz']['log']
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    if file_type == "bookmark":
        path = Config.LOG_PATHS['bookmark']['data']
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    if file_type == "chat_transcript":
        path = Config.LOG_PATHS['chat']['transcript']
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    if file_type == "quiz_score":
        path = Config.LOG_PATHS['quiz']['scores']
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    if file_type == "quiz_log":
        path = Config.LOG_PATHS['quiz']['log']
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    return []

# --- Hybrid read_history: merge local and Firestore data for chat/quiz/quiz_score ---
def get_firestore_history(user_id: str, file_type: str) -> list:
    """Fetch history from Firestore for the given user and type."""
    try:
        from firebase_admin import firestore
        firestore_db = firestore.client()
        if file_type == "chat":
            docs = firestore_db.collection("users").document(user_id).collection("chat_history").stream()
            return [doc.to_dict() for doc in docs]
        elif file_type == "quiz":
            docs = firestore_db.collection("users").document(user_id).collection("quiz_history").stream()
            return [doc.to_dict() for doc in docs]
        elif file_type == "quiz_score":
            doc = firestore_db.collection("users").document(user_id).collection("progress").document("summary").get()
            return doc.to_dict() or {}
    except Exception as e:
        logging.warning(f"Could not fetch Firestore {file_type} history: {e}")
        return [] if file_type != "quiz_score" else {}

_original_read_history = read_history

def hybrid_read_history(file_type: str = "chat"):
    user_id = st.session_state.get("user_id")
    local_data = _original_read_history(file_type)
    if user_id:
        cloud_data = get_firestore_history(user_id, file_type)
        if file_type in ("chat", "quiz"):
            # Merge and deduplicate by timestamp if possible
            all_data = local_data + [d for d in cloud_data if d not in local_data]
            all_data.sort(key=lambda x: x.get("timestamp", ""))
            return all_data
        elif file_type == "quiz_score":
            return cloud_data if cloud_data else local_data
    return local_data

globals()["read_history"] = hybrid_read_history

def load_quiz_score_history() -> List[Dict[str, Any]]:
    """Loads quiz score history from its dedicated JSON file."""
    path = Config.LOG_PATHS['quiz']['scores']
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def append_quiz_score_entry(entry: Dict[str, Any]) -> None:
    """Appends a quiz score entry to the history and saves it to file."""
    path = Config.LOG_PATHS['quiz']['scores']
    history = load_quiz_score_history()
    history.append(entry)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def clear_quiz_score_history() -> bool:
    """Clears the quiz score history file."""
    path = Config.LOG_PATHS['quiz']['scores']
    try:
        if os.path.exists(path):
            os.remove(path)
        return True
    except Exception as e:
        logging.error(f"Failed to clear quiz score history: {str(e)}")
        return False

def _is_in_cooldown(time_key: str) -> bool:
    """Check if an action is in cooldown period."""
    if time_key in st.session_state:
        elapsed = datetime.now() - st.session_state[time_key]
        return elapsed < timedelta(minutes=Config.API_CALL_COOLDOWN_MINUTES)
    return False

def _cooldown_message(action: str = "this action") -> str:
    """Return a user-friendly cooldown message for the given action."""
    return f"You are doing {action} too frequently. Please wait a few moments before trying again."

def save_chat_to_file(user_prompt: str, assistant_response: str) -> None:
    """Appends a chat interaction (prompt and response) to the chat history file as a single entry."""
    try:
        if not user_prompt or not user_prompt.strip() or not assistant_response or not assistant_response.strip():
            # Do not save empty prompts or responses
            return
        history_path = Config.LOG_PATHS['chat']['history']
        entry = {
            "timestamp": datetime.now().isoformat(),
            "prompt": user_prompt,
            "response": assistant_response
        }
        # Load existing history or start new
        if os.path.exists(history_path):
            with open(history_path, 'r', encoding='utf-8') as f:
                try:
                    history = json.load(f)
                except Exception:
                    history = []
        else:
            history = []
        history.append(entry)
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logging.error(f"Failed to save chat to file: {e}")

def main():
    """Main entry point of the application."""
    # ...existing code for the main application logic...
    pass

if __name__ == "__main__":
    main()
