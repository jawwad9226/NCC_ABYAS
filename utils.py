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

    # Legacy file paths (for backward compatibility)
    CHAT_HISTORY_FILE = os.path.join(DATA_DIR, "chat_history.json")
    QUIZ_LOG_FILE = os.path.join(DATA_DIR, "quiz_log.json")
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

def append_message(role: str, content: str) -> None:
    """
    Appends a chat message to the session state and saves the chat interaction to a file.
    This function is primarily for chat messages (user/assistant).
    """
    st.session_state.setdefault("messages", []) # Assuming 'messages' is used by chat_interface
    st.session_state["messages"].append({"role": role, "content": content})
    
    # For saving to disk, _save_chat_to_file expects prompt and response.
    # This append_message is more for UI state. Actual saving might be handled differently.
    # If this is the primary save mechanism, it needs to be adapted or called appropriately.
    # For now, let's assume _save_chat_to_file is called separately with prompt/response pairs.
    pass # See _save_chat_to_file for actual disk saving logic for chat.


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

def _save_chat_to_file(user_prompt: str, assistant_response: str) -> None:
    """Save chat interaction to history file and transcript."""
    try:
        # Save to JSON history
        history_path = Config.LOG_PATHS['chat']['history']
        history = _load_json_file(history_path, [])
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
        except Exception as e:
            logging.error(f"Failed to append to chat transcript: {str(e)}")
            
    except Exception as e:
        logging.error(f"Failed to save chat history: {str(e)}")
        logging.debug(f"Failed chat data: Prompt='{user_prompt}', Response='{assistant_response}'")

def _save_quiz_to_file(topic: str, questions: List[Dict[str, Any]]) -> None:
    """Save quiz questions to history file."""
    try:
        history = _load_json_file(Config.QUIZ_LOG_FILE, [])
        history.append({
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "questions": questions
        })
        _save_json_file(Config.QUIZ_LOG_FILE, history)
    except Exception as e:
        logging.error(f"Failed to save quiz: {str(e)}")

# --- Quiz Score History Functions ---
def load_quiz_score_history() -> List[Dict[str, Any]]:
    """Loads quiz score history from its dedicated JSON file."""
    return _load_json_file(Config.LOG_PATHS['quiz']['scores'], [])

def append_quiz_score_entry(entry: Dict[str, Any]) -> None:
    """Appends a quiz score entry to the history and saves it to file."""
    try:
        history = load_quiz_score_history()
        history.append(entry)
        _save_json_file(Config.QUIZ_SCORE_HISTORY_FILE, history)
    except Exception as e:
        logging.error(f"Failed to save quiz score entry: {str(e)}")
        logging.debug(f"Failed quiz score data: {entry}")

def clear_quiz_score_history() -> bool:
    """Clears the quiz score history file."""
    try:
        scores_path = Config.LOG_PATHS['quiz']['scores']
        if os.path.exists(scores_path):
            os.remove(scores_path)
        return True
    except Exception as e:
        logging.error(f"Failed to clear quiz score history: {str(e)}")
        return False
# --- Public API ---
def clear_history(file_type: str = "chat") -> bool:
    """Clear history for the specified type.
    
    Args:
        file_type: Type of history to clear ('chat' or 'quiz')
    
    Returns:
        bool: True if successful, False otherwise
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
                Config.LOG_PATHS['quiz']['log'],
                Config.LOG_PATHS['quiz']['transcript']
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

def read_history(file_type: str = "chat") -> str:
    """Read history for the specified type and return as formatted string.
    
    Args:
        file_type: Type of history to read ('chat' or 'quiz')
    
    Returns:
        Formatted string of history items
    """
    # Special case for quiz scores
    if file_type == "quiz_score":
        score_history = load_quiz_score_history()
        return json.dumps(score_history, indent=2)
        
    # Get the appropriate path from LOG_PATHS
    file_path = None
    if file_type == "chat":
        file_path = Config.LOG_PATHS['chat']['history']
    elif file_type == "quiz":
        file_path = Config.LOG_PATHS['quiz']['log']
    
    if not file_path:
        return ""
        
    history_data = _load_json_file(file_path, [])
    if not history_data:
        return ""
    
    # Format history as readable text
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
            topic = item.get("topic", "Unknown topic")
            questions = item.get("questions", [])
            formatted_lines.append(f"[{timestamp}] QUIZ: {topic} ({len(questions)} questions)")
            for i, q in enumerate(questions, 1):
                formatted_lines.append(f"  Q{i}: {q.get('question', 'No question')}")
                formatted_lines.append(f"  Answer: {q.get('answer', 'No answer')}")
            formatted_lines.append("")  # Empty line between quizzes
    
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
            _save_chat_to_file(user_prompt=prompt, assistant_response=response_text)
        return response_text
    except Exception as e:
        error_msg = "Apologies, I'm having trouble processing your request. Please try again in a moment."
        logging.exception(f"Error in get_ncc_response: {str(e)}")
        return error_msg

# --- Quiz Generator ---
def generate_quiz_questions(model: genai.GenerativeModel, model_error: Optional[str], 
                            topic: str, num_questions_requested: int, difficulty: str
                           ) -> Tuple[Optional[List[Dict]], Optional[str]]:
    """Generate quiz questions using the Gemini model.
    
    Args:
        model: Initialized Gemini model instance
        model_error: Error message if model initialization failed
        topic: Topic for the quiz
        num_questions_requested: Number of questions requested by the user.
        difficulty: Difficulty level ('Easy', 'Medium', 'Hard').
        
    Returns:
        A tuple containing (list of parsed questions, error message string or None).
    """
    if model_error or not model:
        return None, f"Model error: {model_error or 'Model not initialized'}"

    # Validate number of questions
    try:
        num_questions = int(num_questions_requested)
        num_questions = max(1, min(10, num_questions))  # Clamp between 1 and 10 as per prompt design
    except (TypeError, ValueError):
        return None, "Invalid number of questions specified."

    if _is_in_cooldown("last_quiz_api_call_time"):
        return None, _cooldown_message("quiz generation")

    # Adjust number of questions based on difficulty
    actual_num_questions = min(num_questions, Config.QUESTION_COUNTS[difficulty])
    prompt = build_prompt(topic, actual_num_questions, difficulty)

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=Config.TEMP_QUIZ,
                max_output_tokens=Config.MAX_TOKENS_QUIZ
            )
        )
        raw = response.text
        parsed = parse_quiz_response(raw)

        if parsed:
            st.session_state.last_quiz_api_call_time = datetime.now()
            _save_quiz_to_file(topic, parsed)
            return parsed, None
        else:
            logging.error(f"Failed to parse quiz response: {raw}")
            return None, "Failed to parse valid quiz questions from AI response. Please try again."
    except Exception as e:
        error_msg = "Apologies, we're having trouble generating your quiz. Please try again in a moment."
        logging.exception(f"Error in generate_quiz_questions: {str(e)}")
        return None, error_msg

# --- Quiz Parser ---
def parse_quiz_response(response_text: str) -> List[Dict[str, Any]]:
    """Parse raw quiz response into structured format.
    
    Args:
        response_text: Raw text response from the model
        
    Returns:
        List of parsed question dictionaries
    """
    parsed_questions = []
    blocks = response_text.strip().split("---")

    q_re = re.compile(r'Q:\s*(.*)', re.IGNORECASE)
    opt_re = re.compile(r'([A-D])\)\s*(.*)')
    ans_re = re.compile(r'ANSWER:\s*([A-D])')
    exp_re = re.compile(r'EXPLANATION:\s*(.*)')

    for block in blocks:
        question = {
            "question": "", 
            "options": {}, 
            "answer": "", 
            "explanation": "",
            "timestamp": datetime.now().isoformat()
        }
        lines = block.strip().splitlines()

        for line in lines:
            if match := q_re.match(line):
                question["question"] = match.group(1).strip()
            elif match := opt_re.match(line):
                question["options"][match.group(1)] = match.group(2).strip()
            elif match := ans_re.match(line):
                question["answer"] = match.group(1).strip()
            elif match := exp_re.match(line):
                question["explanation"] = match.group(1).strip()

        if (question["question"] and 
            len(question["options"]) == 4 and 
            question["answer"] in question["options"] and 
            question["explanation"]):
            parsed_questions.append(question)
        elif question["question"]:  # Only log if we have at least a question
            logging.warning(f"Invalid question block skipped: {question}")

    return parsed_questions

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

# --- Adaptive Difficulty & Prompting Helpers ---

def get_difficulty_level(score_history: List[float]) -> str:
    """
    Determines the current difficulty level based on user's score history.
    
    Args:
        score_history: List of previous quiz scores (0-1)
        
    Returns:
        str: 'Easy', 'Medium', or 'Hard'
    """
    if not score_history:
        return "Medium"
        
    avg_score = sum(score_history) / len(score_history)
    
    if avg_score < 0.4:
        return "Easy"
    elif avg_score > 0.7:
        return "Hard"
    return "Medium"

def build_prompt(topic: str, num_q: int, difficulty: str) -> str:
    """
    Builds a Gemini prompt for quiz generation based on difficulty level and topic.
    
    Args:
        topic: The topic for the quiz
        num_q: Number of questions to generate
        difficulty: Difficulty level ('Easy', 'Medium', 'Hard')
        
    Returns:
        Formatted prompt string for the Gemini model
    """
    difficulty_map = {
        "Easy": "basic concepts and definitions",
        "Medium": "intermediate concepts with some application",
        "Hard": "advanced concepts requiring analysis and critical thinking"
    }
    
    return f"""Generate {num_q} multiple-choice questions about {topic}.
    Difficulty: {difficulty_map.get(difficulty, 'Medium')}
    
    For each question, follow this exact format:
    
    Q: [Your question here]
    A) [Option A]
    B) [Option B]
    C) [Option C]
    D) [Option D]
    ANSWER: [Correct letter A-D]
    EXPLANATION: [Brief explanation of the answer]
    
    ---
    
    Important:
    - Each question must be separated by '---' on a new line
    - Include exactly 4 options (A-D) for each question
    - Only one correct answer per question
    - Keep explanations concise but informative
    - Questions should test {difficulty_map.get(difficulty, 'a good understanding')} of {topic}
    - Avoid using 'All of the above' or 'None of the above' as options
    - Ensure questions are clear and unambiguous
    """