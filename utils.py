import os
import google.generativeai as genai
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
import re
import streamlit as st
import logging

# --- Constants ---
GEMINI_MODEL_NAME = 'gemini-1.5-flash'
DEFAULT_TEMPERATURE_CHAT = 0.3
DEFAULT_TEMPERATURE_QUIZ = 0.4
MAX_OUTPUT_TOKENS_CHAT = 1000
MAX_OUTPUT_TOKENS_QUIZ = 2000
API_CALL_COOLDOWN_MINUTES = 1

CHAT_HISTORY_FILE = "chat_history.txt"
QUIZ_LOG_FILE = "quiz_log.txt"

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


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
        model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        return model, None
    except Exception as e:
        error_msg = f"Failed to initialize Gemini model: {str(e)}"
        logging.exception(error_msg)
        return None, error_msg


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
                temperature=DEFAULT_TEMPERATURE_CHAT,
                max_output_tokens=MAX_OUTPUT_TOKENS_CHAT
            )
        )
        st.session_state.last_api_call_time = datetime.now()
        response_text = response.text.strip()
        _save_chat_to_file(prompt, response_text)
        return response_text
    except Exception as e:
        error_msg = f"Error generating response: {str(e)}"
        logging.exception(error_msg)
        return error_msg


# --- Quiz Generator ---
def generate_quiz_questions(model, model_error, st_session_state, topic: str, num_questions: int):
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
    question_count_map = {"Easy": 3, "Medium": 5, "Hard": 8}
    actual_num_questions = min(num_questions, question_count_map[difficulty])

    # Build smart prompt
    prompt = build_prompt(topic, actual_num_questions, difficulty)

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=DEFAULT_TEMPERATURE_QUIZ,
                max_output_tokens=MAX_OUTPUT_TOKENS_QUIZ
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
        error_msg = f"Error generating quiz: {str(e)}"
        logging.exception(error_msg)
        st_session_state.quiz_generation_error = error_msg


# --- Quiz Parser ---
def parse_quiz_response(response_text: str) -> List[Dict[str, Any]]:
    parsed_questions = []
    blocks = response_text.strip().split("---")

    q_re = re.compile(r'Q:\s*(.*)', re.IGNORECASE)
    opt_re = re.compile(r'([A-D])\)\s*(.*)')
    ans_re = re.compile(r'ANSWER:\s*([A-D])')
    exp_re = re.compile(r'EXPLANATION:\s*(.*)')

    for block in blocks:
        question = {"question": "", "options": {}, "answer": "", "explanation": ""}
        lines = block.strip().splitlines()
        section = None

        for line in lines:
            if match := q_re.match(line):
                question["question"] = match.group(1).strip()
            elif match := opt_re.match(line):
                question["options"][match.group(1)] = match.group(2).strip()
            elif match := ans_re.match(line):
                question["answer"] = match.group(1).strip()
            elif match := exp_re.match(line):
                question["explanation"] = match.group(1).strip()

        if (
            question["question"]
            and len(question["options"]) == 4
            and question["answer"] in question["options"]
            and question["explanation"]
        ):
            parsed_questions.append(question)
        else:
            logging.warning(f"Invalid question block skipped:\n{block}")

    return parsed_questions


# --- Cooldown Helpers ---
def _is_in_cooldown(time_key: str) -> bool:
    if time_key in st.session_state:
        elapsed = datetime.now() - st.session_state[time_key]
        return elapsed < timedelta(minutes=API_CALL_COOLDOWN_MINUTES)
    return False

def _cooldown_message(scope: str) -> str:
    return f"🕒 Cooldown active. Please wait before generating another {scope}."


# --- History Saving ---
def _save_chat_to_file(prompt: str, response: str):
    with open(CHAT_HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"\nUser: {prompt}\nAssistant: {response}\n{'-'*50}\n")

def _save_quiz_to_file(topic: str, questions: List[Dict[str, Any]]):
    with open(QUIZ_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n🧠 Quiz Topic: {topic} @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        for idx, q in enumerate(questions, 1):
            f.write(f"Q{idx}: {q['question']}\n")
            for opt in ['A', 'B', 'C', 'D']:
                f.write(f"{opt}) {q['options'][opt]}\n")
            f.write(f"ANSWER: {q['answer']}\nEXPLANATION: {q['explanation']}\n---\n")


# --- Utility Exposed to Other Modules ---
def clear_history(file_type: str = "chat"):
    file_path = CHAT_HISTORY_FILE if file_type == "chat" else QUIZ_LOG_FILE
    if os.path.exists(file_path):
        os.remove(file_path)

def read_history(file_type: str = "chat") -> str:
    file_path = CHAT_HISTORY_FILE if file_type == "chat" else QUIZ_LOG_FILE
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return "No history available."


# --- Adaptive Difficulty & Prompting Helpers ---

def get_difficulty_level(score_history: List[float]) -> str:
    """
    Determines the current difficulty level based on user's score history.
    Returns: 'Easy', 'Medium', or 'Hard'
    """
    if not score_history:
        return "Medium"
    avg = sum(score_history) / len(score_history)
    if avg < 50:
        return "Easy"
    elif avg < 80:
        return "Medium"
    else:
        return "Hard"


def build_prompt(topic: str, num_q: int, difficulty: str) -> str:
    """Builds a Gemini prompt for quiz generation based on difficulty level and topic.
    
    Args:
        topic: The topic for the quiz
        num_q: Number of questions to generate
        difficulty: Difficulty level ('Easy', 'Medium', 'Hard')
        
    Returns:
        Formatted prompt string for the Gemini model
    """
    difficulty_instructions = {
        'Easy': 'suitable for beginners with basic knowledge',
        'Medium': 'moderately challenging for those with some experience',
        'Hard': 'challenging questions that test in-depth understanding'
    }
    
    return f"""Generate {num_q} multiple-choice questions about {topic}.
Difficulty Level: {difficulty} ({difficulty_instructions.get(difficulty, '')})

For each question, follow this format exactly:

Q: [Your question]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
ANSWER: [Correct letter A-D]
EXPLANATION: [Brief explanation of the answer]

Make sure to:
1. Include exactly 4 options (A-D) for each question
2. Mark the correct answer with ANSWER: [letter]
3. Provide a clear explanation for each answer
4. Vary the position of the correct answer randomly
5. Ensure questions are {difficulty.lower()} difficulty
6. Cover different aspects of {topic}

---
"""
