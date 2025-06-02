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
    # File Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CHAT_HISTORY_FILE = os.path.join(BASE_DIR, "data", "chat_history.json")
    QUIZ_LOG_FILE = os.path.join(BASE_DIR, "data", "quiz_log.json")
    
    # Model Settings
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
        os.makedirs(os.path.join(cls.BASE_DIR, "data"), exist_ok=True)

# Initialize data directory
Config.ensure_data_dir()

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(Config.BASE_DIR, "app.log")),
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

def _save_chat_to_file(prompt: str, response: str) -> None:
    """Save chat interaction to history file."""
    try:
        history = _load_json_file(Config.CHAT_HISTORY_FILE, [])
        history.append({
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "response": response
        })
        _save_json_file(Config.CHAT_HISTORY_FILE, history)
    except Exception as e:
        logging.error(f"Failed to save chat history: {str(e)}")

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

# --- Public API ---
def clear_history(file_type: str = "chat") -> bool:
    """Clear history for the specified type.
    
    Args:
        file_type: Type of history to clear ('chat' or 'quiz')
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        file_path = {
            "chat": Config.CHAT_HISTORY_FILE,
            "quiz": Config.QUIZ_LOG_FILE
        }.get(file_type)
        
        if not file_path:
            return False
            
        if os.path.exists(file_path):
            os.remove(file_path)
        return True
    except Exception as e:
        logging.error(f"Failed to clear {file_type} history: {str(e)}")
        return False

def read_history(file_type: str = "chat") -> List[Dict]:
    """Read history for the specified type.
    
    Args:
        file_type: Type of history to read ('chat' or 'quiz')
    
    Returns:
        List of history items
    """
    file_path = {
        "chat": Config.CHAT_HISTORY_FILE,
        "quiz": Config.QUIZ_LOG_FILE
    }.get(file_type)
    
    if not file_path:
        return []
        
    return _load_json_file(file_path, [])

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
            
        csv_output = []
        writer = csv.DictWriter(csv_output, fieldnames=["#", "Type", "Content"])
        writer.writeheader()
        writer.writerows(output)
        
        return "\n".join(csv_output)
        
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
        _save_chat_to_file(prompt, response_text)
        return response_text
    except Exception as e:
        error_msg = "Apologies, I'm having trouble processing your request. Please try again in a moment."
        logging.exception(f"Error in get_ncc_response: {str(e)}")
        return error_msg

# --- Quiz Generator ---
def generate_quiz_questions(model, model_error, st_session_state, topic: str, num_questions: int) -> None:
    """Generate quiz questions using the Gemini model.
    
    Args:
        model: Initialized Gemini model instance
        model_error: Error message if model initialization failed
        st_session_state: Streamlit session state
        topic: Topic for the quiz
        num_questions: Number of questions to generate (1-10)
    """
    if not model or model_error:
        st_session_state.quiz_generation_error = f"Model error: {model_error or 'Model not initialized'}"
        return

    # Validate number of questions
    try:
        num_questions = int(num_questions)
        num_questions = max(1, min(10, num_questions))  # Clamp between 1 and 10
    except (TypeError, ValueError):
        num_questions = 5  # Default value

    if _is_in_cooldown("last_quiz_api_call_time"):
        st_session_state.quiz_generation_error = _cooldown_message("quiz")
        return

    # Determine difficulty level from session (or default)
    score_history = st_session_state.get("quiz_score_history", [])
    difficulty = get_difficulty_level(score_history)
    st_session_state.current_quiz_difficulty = difficulty

    # Adjust number of questions based on difficulty
    actual_num_questions = min(num_questions, Config.QUESTION_COUNTS[difficulty])

    # Build smart prompt
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
            st_session_state.quiz_questions = parsed
            st.session_state.last_quiz_api_call_time = datetime.now()
            _save_quiz_to_file(topic, parsed)
            st_session_state.quiz_generation_error = None
        else:
            st_session_state.quiz_generation_error = "Failed to generate valid quiz questions. Please try again."
            logging.error(f"Failed to parse quiz response: {raw}")
    except Exception as e:
        error_msg = "Apologies, we're having trouble generating your quiz. Please try again in a moment."
        logging.exception(f"Error in generate_quiz_questions: {str(e)}")
        st_session_state.quiz_generation_error = error_msg

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
        return elapsed < timedelta(minutes=Config.COOLDOWN_MIN)
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
