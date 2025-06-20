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
    # Base Directories
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    LOGS_DIR = os.path.join(BASE_DIR, "logs")

    # Ensure directories exist
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)

    # Centralized file paths (ensure these are used consistently)
    QUIZ_SCORE_HISTORY_FILE = os.path.join(DATA_DIR, "quiz_score_history.json")
    APP_LOG_FILE = os.path.join(LOGS_DIR, "app.log")
    
    # Centralized file paths mapping
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
    
    # Model Settings (moved to avoid duplication)
    MODEL_NAME = 'gemini-1.5-flash'
    TEMP_CHAT = 0.3
    TEMP_QUIZ = 0.4
    MAX_TOKENS_CHAT = 1000
    MAX_TOKENS_QUIZ = 2000
    API_CALL_COOLDOWN_MINUTES = 2
    
    # Quiz Settings
    QUESTION_COUNTS = {"Easy": 3, "Medium": 5, "Hard": 8}
    
    # Ensure data directory exists
    @classmethod
    def ensure_data_dir(cls):
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.LOGS_DIR, exist_ok=True)
# Initialize data directory
Config.ensure_data_dir()

# Export the constant for backward compatibility
API_CALL_COOLDOWN_MINUTES = Config.API_CALL_COOLDOWN_MINUTES

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(Config.LOG_PATHS['app']['log']),
        logging.StreamHandler()
    ]
)

# --- Gemini API Setup ---
@st.cache_resource
def setup_gemini() -> Tuple[Optional[genai.GenerativeModel], Optional[str]]:
    """Initialize and return the Gemini model.
    
    Returns:
        Tuple containing the model and error message (if any)
    """
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


# --- File Operations ---
def _load_json_file(file_path: str, default: Any = None) -> Any:
    """Safely load JSON data from a file."""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logging.error(f"Error loading {file_path}: {str(e)}")
    return default if default is not None else []

def _save_json_file(file_path: str, data: Any) -> bool:
    """Safely save data as JSON to a file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logging.error(f"Error saving to {file_path}: {str(e)}")
        return False

def save_chat_to_file(user_prompt: str, assistant_response: str) -> None:
    """Save chat interaction to history file and transcript."""
    try:
        # Save to JSON history
        history_path = Config.LOG_PATHS['chat']['history']
        # Load existing history, default to empty list if file doesn't exist or is invalid
        history = _load_json_file(history_path, default=[])
        history.append({
            "timestamp": datetime.now().isoformat(),
            "prompt": user_prompt,
            "response": assistant_response
        })
        _save_json_file(history_path, history)

        # Append to transcript file
        transcript_path = Config.LOG_PATHS['chat']['transcript']
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(transcript_path, 'a', encoding='utf-8') as f:
                f.write(f"\n[{timestamp}] USER: {user_prompt}\n")
                f.write(f"[{timestamp}] AI: {assistant_response}\n")
                f.write("-" * 40 + "\n") # Add separator in transcript
        except Exception as e:
            logging.error(f"Failed to append to chat transcript: {str(e)}")
            
    except Exception as e:
        logging.error(f"Failed to save chat history: {str(e)}")
        logging.debug(f"Failed chat data: Prompt='{user_prompt}', Response='{assistant_response}'")

def save_quiz_log_entry(quiz_data: Dict[str, Any]) -> None:
    """Save a completed quiz log entry to file."""
    try:
        log_path = Config.LOG_PATHS['quiz']['log']
        logs = _load_json_file(log_path, default=[])
        logs.append(quiz_data)
        _save_json_file(log_path, logs)
    except Exception as e:
        logging.error(f"Failed to save quiz log entry: {str(e)}")


# --- Quiz Score History Functions ---
def load_quiz_score_history() -> List[Dict[str, Any]]:
    """Loads quiz score history from its dedicated JSON file."""
    return _load_json_file(Config.LOG_PATHS['quiz']['scores'], [])

def append_quiz_score_entry(entry: Dict[str, Any]) -> None:
    """Appends a quiz score entry to the history and saves it to file."""
    try:
        history = load_quiz_score_history() # Load existing history
        history.append(entry) # entry is a dict
        _save_json_file(Config.QUIZ_SCORE_HISTORY_FILE, history)
    except Exception as e:
        logging.error(f"Failed to save quiz score entry: {str(e)}")
        logging.debug(f"Failed quiz score data: {entry}")

def clear_quiz_score_history() -> bool:
    """Clears the quiz score history file."""
    try:
        scores_path = Config.LOG_PATHS['quiz']['scores']
        if os.path.exists(scores_path):
            # Overwrite with empty list instead of deleting, to keep file structure, or remove.
            os.remove(scores_path)
        return True
    except Exception as e:
        logging.error(f"Failed to clear quiz score history: {str(e)}")
        return False
# --- Public API ---
def clear_history(file_type: str = "chat") -> bool:
    """Clear history files for the specified type.
    
    Args:
        file_type: Type of history to clear ('chat' or 'quiz')
    
    Returns:    
        bool: True if successful, False otherwise. Note: This clears files, not session state.
    """
    try:
        # Handle special case for quiz scores first
        if file_type == "quiz_score":
            return clear_quiz_score_history()
        
        # Map file_type to the appropriate path in LOG_PATHS
        paths_to_clear = []
        if file_type == "chat":
            paths_to_clear = [
                Config.LOG_PATHS['chat']['history'],
                Config.LOG_PATHS['chat']['transcript']
            ]
        elif file_type == "quiz":
            paths_to_clear = [
                Config.LOG_PATHS['quiz']['log'], # This contains the full quiz data
                Config.LOG_PATHS['quiz']['transcript'],
                # Config.LOG_PATHS['quiz']['scores'] is handled by clear_quiz_score_history
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
    # Special case for quiz scores
    if file_type == "quiz_score":
        score_history = load_quiz_score_history()
        return json.dumps(score_history, indent=2) # Return as JSON string

    # For chat and quiz logs (full data), return the parsed list of dictionaries
    if file_type in ['chat', 'quiz', 'bookmark']:
        path_key = 'history' if file_type == 'chat' else 'log' if file_type == 'quiz' else 'data'
        file_path = Config.LOG_PATHS.get(file_type, {}).get(path_key)
        if file_path:
            return _load_json_file(file_path, default=[])

    # For transcript files or specific log files that should be read as text/JSON strings
    if file_type == "chat_transcript":
        file_path = Config.LOG_PATHS['chat']['transcript']
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    if file_type == "quiz_log": # This is the detailed quiz log, return as JSON string
        file_path = Config.LOG_PATHS['chat']['history']
        quiz_log_data = _load_json_file(Config.LOG_PATHS['quiz']['log'], default=[])
        return json.dumps(quiz_log_data, indent=2)

    logging.warning(f"read_history called with unknown file_type: {file_type}")
    return [] # Default for unhandled types that expect a list

def export_history_to_text(file_type: str) -> str:
    """Read history for the specified type and return as a formatted text string."""
    history_data = read_history(file_type) # This now returns list of dicts or JSON string

    if file_type == "quiz_score" or file_type == "chat_transcript" or file_type == "quiz_log":
        return history_data if isinstance(history_data, str) else json.dumps(history_data, indent=2)

    if not isinstance(history_data, list):
        logging.error(f"Expected list for {file_type} history export, but got {type(history_data)}")
        return ""

    formatted_lines = []
    for item in history_data:
        timestamp = item.get("timestamp", "Unknown time")
        if file_type == "chat":
            prompt = item.get("prompt", "")
            response = item.get("response", "")
            formatted_lines.append(f"[{timestamp}] USER: {prompt}")
            formatted_lines.append(f"[{timestamp}] AI: {response}")
            formatted_lines.append("")  # Empty line between conversations
        elif file_type == "quiz":
            # This case is for the 'quiz' type which refers to quiz_log.json (list of dicts)
            topic = item.get("topic", "Unknown Topic")
            difficulty = item.get("difficulty", "N/A")
            questions = item.get("questions", [])
            formatted_lines.append(f"[{timestamp}] QUIZ: {topic} ({difficulty}, {len(questions)} questions)")
            for i, q in enumerate(questions, 1):
                formatted_lines.append(f"  Q{i}: {q.get('question', 'No question')}")
                options = q.get('options', {})
                formatted_lines.append(f"    Options: {', '.join([f'{k}) {v}' for k, v in options.items()])}")
                formatted_lines.append(f"    Correct Answer: {q.get('answer', 'N/A')}")
                formatted_lines.append(f"    Explanation: {q.get('explanation', 'N/A')}")
            formatted_lines.append("")
        elif file_type == "bookmark":
            formatted_lines.append(json.dumps(item, indent=2))
    return "\n".join(formatted_lines)

def export_flashcards(questions: List[Dict], format: str = "csv") -> Union[str, bytes]:
    """Export quiz questions as flashcards.
    
    Args:
        questions: List of question dictionaries
        format: Export format ('csv' or 'json')
        
    Returns:
        str or bytes: Exported data in requested format
    """
    try:
        if format.lower() == "json":
            return json.dumps(questions, indent=2, ensure_ascii=False)
            
        # Default to CSV
        output = []
        for i, q in enumerate(questions, 1):
            output.append({"#": i, "Type": "Question", "Content": q["question"]})
            for opt, text in q["options"].items():
                output.append({"#": "", "Type": f"Option {opt}", "Content": text})
            output.append({"#": "", "Type": "Answer", "Content": q["answer"]})
            output.append({"#": "", "Type": "Explanation", "Content": q["explanation"]})
            output.append({})  # Empty row between questions
        
        # Convert to CSV
        if not output:
            return ""
            
        # Remove last empty row if exists
        if not any(output[-1].values()):
            output = output[:-1]
            
        from io import StringIO
        csv_output = StringIO()
        writer = csv.DictWriter(csv_output, fieldnames=["#", "Type", "Content"])
        writer.writeheader()
        writer.writerows(output)
        
        return csv_output.getvalue()
        
    except Exception as e:
        logging.error(f"Failed to export flashcards: {str(e)}")
        return ""

# --- Chat Function ---
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

    if _is_in_cooldown("last_api_call_time"):
        return _cooldown_message("chat")

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=Config.TEMP_CHAT,
                max_output_tokens=Config.MAX_TOKENS_CHAT
            )
        )
        st.session_state.last_api_call_time = datetime.now()
        response_text = response.text.strip()
        # Save the chat interaction to file
        # Assuming 'prompt' is the user's input and 'response_text' is the AI's reply
        if prompt and response_text: # Ensure both are non-empty before saving
            save_chat_to_file(user_prompt=prompt, assistant_response=response_text)
        return response_text
    except Exception as e:
        error_msg = "Apologies, I'm having trouble processing your request. Please try again in a moment."
        logging.exception(f"Error in get_ncc_response: {str(e)}")
        return error_msg

# --- Cooldown Helpers ---
def _is_in_cooldown(time_key: str) -> bool:
    """Check if an action is in cooldown period."""
    if time_key in st.session_state:
        elapsed = datetime.now() - st.session_state[time_key]
        return elapsed < timedelta(minutes=Config.API_CALL_COOLDOWN_MINUTES)
    return False

def _cooldown_message(scope: str) -> str:
    """Generate cooldown message for the given scope."""
    return f"🕒 Cooldown active. Please wait before generating another {scope}."