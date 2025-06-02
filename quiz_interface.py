import streamlit as st
import random
import time
import os
import json # Import json for reading quiz data
from typing import List, Dict, Any, Optional
from datetime import datetime # Ensure datetime is imported

# --- Mock Utility Functions (as in main.py) ---
# In a real application, these would be imported from utils.py
# from utils import get_response_func, read_history, append_message, clear_history, initialize_firebase

def read_history(history_type):
    """Mocks reading chat history from a file."""
    try:
        # Assuming history files are in a 'history' subdirectory or project root
        # For this context, let's assume quiz_history.json is in the project root
        file_path = f"{history_type}_history.json" 
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                content = f.read()
                return json.loads(content) if content else [] # Load JSON, return empty list if file is empty
        return []
    except (FileNotFoundError, json.JSONDecodeError) as e:
        st.warning(f"Could not load {history_type} history: {e}. Starting fresh.")
        return []

def append_message(history_type, data):
    """Mocks appending data to chat history (now supports JSON for quiz)."""
    file_path = f"{history_type}_history.json"
    history = read_history(history_type) # Read existing history
    history.append(data) # Append new data
    with open(file_path, "w") as f:
        json.dump(history, f, indent=4) # Write back as JSON

def clear_history(history_type):
    """Mocks clearing chat history."""
    file_path = f"{history_type}_history.json"
    try:
        if os.path.exists(file_path):
            os.remove(file_path) # Remove the file
            st.info(f"Cleared {history_type} history.")
    except OSError as e:
        st.error(f"Error clearing {history_type} history: {e}")

# --- End of Mock Utility Functions ---

# --- Quiz Data Loading (Mock) ---
# In a real app, this would load from data/quizzes.json or similar
# For demonstration, we use a simple hardcoded structure
QUIZ_DATA = {
    "easy": [
        {"question": "What does NCC stand for?", "options": ["National Cadet Corps", "National Central Corps", "National Civil Corps", "None of the above"], "answer": "National Cadet Corps", "chapter": "Introduction"},
        {"question": "What is the capital of India?", "options": ["Mumbai", "Delhi", "Kolkata", "Chennai"], "answer": "Delhi", "chapter": "General Knowledge"},
        {"question": "How many states are there in India?", "options": ["28", "29", "30", "27"], "answer": "28", "chapter": "General Knowledge"},
        {"question": "Who is the Father of the Nation?", "options": ["Jawaharlal Nehru", "Sardar Patel", "Mahatma Gandhi", "Subhash Chandra Bose"], "answer": "Mahatma Gandhi", "chapter": "History"},
    ],
    "medium": [
        {"question": "What is the motto of NCC?", "options": ["Unity and Discipline", "Service and Sacrifice", "Leadership and Loyalty", "Duty and Dedication"], "answer": "Unity and Discipline", "chapter": "Introduction"},
        {"question": "Which of the following ranks is specific to the NCC?", "options": ["Lance Naik", "Sergeant", "Company Quartermaster Sergeant", "Cadet Sergeant Major"], "answer": "Cadet Sergeant Major", "chapter": "Ranks"},
        {"question": "When was NCC established?", "options": ["1948", "1950", "1947", "1962"], "answer": "1948", "chapter": "History"},
    ],
    "hard": [
        {"question": "What is the full form of DG NCC?", "options": ["Director General National Cadet Corps", "Directorate General of National Cadet Corps", "Directorate General National Cadet Corps", "Directorate General of NCC"], "answer": "Directorate General National Cadet Corps", "chapter": "Organization"},
        {"question": "What is the role of NCC in nation-building?", "options": ["Providing military training", "Developing youth leadership", "Disaster relief operations", "All of the above"], "answer": "All of the above", "chapter": "Nation Building"},
    ]
}

# --- Quiz State Management ---
SS_PREFIX = "quiz_ss_" # Prefix to avoid conflicts with other modules' session state

def _initialize_quiz_state(ss):
    """Initializes all quiz-related session state variables if they don't exist."""
    if f"{SS_PREFIX}quiz_active" not in ss:
        _reset_quiz_state(ss)
        ss[f"{SS_PREFIX}quiz_score_history"] = read_history("quiz_score") # Persisted history for difficulty calculation

def _reset_quiz_state(ss):
    """Resets the quiz to its initial state, clearing current quiz data."""
    ss[f"{SS_PREFIX}quiz_active"] = False
    ss[f"{SS_PREFIX}current_question_index"] = 0
    ss[f"{SS_PREFIX}quiz_questions"] = []
    ss[f"{SS_PREFIX}user_answers"] = {}
    ss[f"{SS_PREFIX}quiz_start_time"] = None
    ss[f"{SS_PREFIX}quiz_end_time"] = None
    ss[f"{SS_PREFIX}quiz_submitted"] = False
    ss[f"{SS_PREFIX}quiz_result"] = None
    ss[f"{SS_PREFIX}quiz_bookmarks"] = [] # Clear bookmarks on new quiz
    ss[f"{SS_PREFIX}current_quiz_topic"] = "General Knowledge" # Default topic for new quizzes

    # FIX: Resetting Difficulty on "New Quiz" - Recalc from history instead of hard-coding "Medium"
    if f"{SS_PREFIX}quiz_score_history" in ss and ss[f"{SS_PREFIX}quiz_score_history"]:
        ss[f"{SS_PREFIX}current_quiz_difficulty"] = get_difficulty_level(ss[f"{SS_PREFIX}quiz_score_history"])
    else:
        ss[f"{SS_PREFIX}current_quiz_difficulty"] = "Medium" # Default if no history


def get_difficulty_level(score_history: List[Dict[str, Any]]) -> str:
    """
    Determines the next quiz difficulty based on recent quiz scores.
    Args:
        score_history: List of dictionaries, each with 'score' (percentage) and 'difficulty'.
    Returns:
        str: 'easy', 'medium', or 'hard'.
    """
    if not score_history:
        return "Medium" # Default difficulty if no history

    # Consider last 3-5 quizzes for adaptive difficulty
    recent_scores = score_history[-5:]
    
    # Calculate average score for the recent quizzes
    total_score = sum(entry['score'] for entry in recent_scores if 'score' in entry)
    average_score = total_score / len(recent_scores) if recent_scores else 0

    # Basic adaptive logic
    if average_score >= 80:
        return "Hard"
    elif average_score >= 60:
        return "Medium"
    else:
        return "Easy"

def _generate_quiz_questions(num_questions: int, difficulty: str, topic: str) -> List[Dict[str, Any]]:
    """Generates a list of quiz questions for the selected difficulty and topic."""
    # Filter questions by topic first (mocking based on 'chapter' field in QUIZ_DATA)
    topic_filtered_questions = [
        q for q in QUIZ_DATA.get(difficulty.lower(), [])
        if topic.lower() in q.get("chapter", "").lower() or topic.lower() == "general knowledge" # Allow 'General Knowledge' to match all
    ]
    
    if not topic_filtered_questions:
        st.warning(f"No questions found for topic: '{topic}' at difficulty: {difficulty}. Falling back to general questions for this difficulty.")
        available_questions = QUIZ_DATA.get(difficulty.lower(), []) # Fallback to all questions for difficulty
    else:
        available_questions = topic_filtered_questions

    if not available_questions:
        st.warning(f"No questions found for difficulty: {difficulty}. Please choose another difficulty.")
        return []
    
    # Ensure we don't try to pick more questions than available
    num_to_pick = min(num_questions, len(available_questions))
    
    return random.sample(available_questions, num_to_pick)

def _display_quiz_creation_form(ss):
    """Displays the form to create a new quiz."""
    st.subheader("New Quiz Configuration")

    # Display current suggested difficulty
    st.info(f"Suggested Difficulty based on history: **{ss[f'{SS_PREFIX}current_quiz_difficulty']}**")

    # Difficulty selection
    selected_difficulty = st.selectbox(
        "Select Difficulty",
        ["Easy", "Medium", "Hard"],
        index=["Easy", "Medium", "Hard"].index(ss[f"{SS_PREFIX}current_quiz_difficulty"]) if ss[f"{SS_PREFIX}current_quiz_difficulty"] in ["Easy", "Medium", "Hard"] else 1,
        key=f"{SS_PREFIX}difficulty_select"
    )

    # Topic selection (mocked list of topics)
    # In a real app, this would come from syllabus_manager.get_syllabus_topics()
    mock_topics = ["General Knowledge", "Introduction", "History", "Ranks", "Organization", "Nation Building"]
    selected_topic = st.selectbox(
        "Select Topic",
        mock_topics,
        key=f"{SS_PREFIX}topic_select"
    )

    # Number of questions selection
    num_questions = st.slider(
        "Number of Questions",
        min_value=5,
        max_value=len(QUIZ_DATA.get(selected_difficulty.lower(), [])) or 10, # Max available or 10 if none
        value=min(10, len(QUIZ_DATA.get(selected_difficulty.lower(), [])) or 10),
        step=1,
        key=f"{SS_PREFIX}num_questions_slider"
    )

    if st.button("Start Quiz", key=f"{SS_PREFIX}start_quiz_button"):
        ss[f"{SS_PREFIX}current_quiz_difficulty"] = selected_difficulty # Set chosen difficulty
        ss[f"{SS_PREFIX}current_quiz_topic"] = selected_topic # Store chosen topic
        ss[f"{SS_PREFIX}quiz_questions"] = _generate_quiz_questions(num_questions, selected_difficulty, selected_topic)
        if ss[f"{SS_PREFIX}quiz_questions"]:
            ss[f"{SS_PREFIX}quiz_active"] = True
            ss[f"{SS_PREFIX}current_question_index"] = 0
            ss[f"{SS_PREFIX}user_answers"] = {}
            ss[f"{SS_PREFIX}quiz_start_time"] = datetime.now()
            ss[f"{SS_PREFIX}quiz_submitted"] = False
            ss[f"{SS_PREFIX}quiz_result"] = None
            ss[f"{SS_PREFIX}quiz_bookmarks"] = [] # Ensure bookmarks are clear for new quiz
            st.rerun() # Trigger rerun to display the quiz

def _display_active_quiz(ss):
    """Displays the active quiz questions."""
    st.subheader(f"Quiz (Difficulty: {ss[f'{SS_PREFIX}current_quiz_difficulty']})")
    
    current_q_index = ss[f"{SS_PREFIX}current_question_index"]
    questions = ss[f"{SS_PREFIX}quiz_questions"]
    num_questions = len(questions)

    if not questions:
        st.warning("No questions available for this quiz. Please go back and select a different configuration.")
        if st.button("Back to Quiz Setup", key="back_to_setup_no_q"):
            _reset_quiz_state(ss)
            st.rerun()
        return

    # Progress bar
    progress_percent = (current_q_index / num_questions) if num_questions > 0 else 0
    st.progress(progress_percent, text=f"Question {current_q_index + 1} of {num_questions}")

    # Display current question
    question = questions[current_q_index]
    st.markdown(f"**Q{current_q_index + 1}: {question['question']}**")

    # Use a form to capture user's answer
    with st.form(key=f"question_form_{current_q_index}"):
        user_choice = st.radio(
            "Select your answer:",
            options=question['options'],
            key=f"q_{current_q_index}_option",
            index=question['options'].index(ss[f"{SS_PREFIX}user_answers"].get(str(current_q_index))) if str(current_q_index) in ss[f"{SS_PREFIX}user_answers"] else None
        )
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            submit_button = st.form_submit_button("Next Question ▶️")
        with col2:
            # FIX: Avoid Duplicate Bookmarks
            if st.form_submit_button(f"⭐ Bookmark Q{current_q_index+1}", key=f"bookmark_{current_q_index}"):
                if question not in ss[f"{SS_PREFIX}quiz_bookmarks"]:
                    ss[f"{SS_PREFIX}quiz_bookmarks"].append(question)
                    st.toast(f"Question {current_q_index+1} bookmarked!")
                else:
                    st.toast(f"Question {current_q_index+1} already bookmarked.")
        with col3:
            if st.form_submit_button("🗑️ Abandon Quiz", key=f"abandon_quiz_{current_q_index}"):
                # FIX: "Abandon Quiz" vs History - Clear persisted history if desired
                _reset_quiz_state(ss)
                clear_history("quiz_score") # Clear score history on abandon
                st.rerun()

    if submit_button:
        ss[f"{SS_PREFIX}user_answers"][str(current_q_index)] = user_choice
        ss[f"{SS_PREFIX}current_question_index"] += 1
        # If all questions answered, go to results
        if ss[f"{SS_PREFIX}current_question_index"] >= num_questions:
            _calculate_results(ss)
            ss[f"{SS_PREFIX}quiz_submitted"] = True
            ss[f"{SS_PREFIX}quiz_end_time"] = datetime.now()
        st.rerun() # Rerun to display next question or results

def _calculate_results(ss):
    """Calculates and stores quiz results."""
    correct_answers = 0
    wrong_questions = []
    
    for i, question in enumerate(ss[f"{SS_PREFIX}quiz_questions"]):
        user_ans = ss[f"{SS_PREFIX}user_answers"].get(str(i)) # FIX: Consistent Key Types for user_answers (already str(i))
        if user_ans == question['answer']:
            correct_answers += 1
        else:
            wrong_questions.append({
                "index": i,
                "question": question,
                "user_answer": user_ans,
                "correct_answer": question['answer']
            })
    
    total_questions = len(ss[f"{SS_PREFIX}quiz_questions"])
    score_percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0

    duration = None
    if ss[f"{SS_PREFIX}quiz_start_time"] and ss[f"{SS_PREFIX}quiz_end_time"]:
        duration = ss[f"{SS_PREFIX}quiz_end_time"] - ss[f"{SS_PREFIX}quiz_start_time"]

    ss[f"{SS_PREFIX}quiz_result"] = {
        "score": score_percentage,
        "correct": correct_answers,
        "wrong": len(wrong_questions),
        "total": total_questions,
        "wrong_questions": wrong_questions,
        "duration": str(duration) if duration else "N/A",
        "timestamp": datetime.now().isoformat(),
        "difficulty": ss[f"{SS_PREFIX}current_quiz_difficulty"]
    }
    
    # Append result to persisted history
    append_message("quiz_score", {
        "timestamp": datetime.now().isoformat(),
        "score": score_percentage,
        "difficulty": ss[f"{SS_PREFIX}current_quiz_difficulty"],
        "topic": ss[f"{SS_PREFIX}current_quiz_topic"] # NEW: Include the quiz topic
    })

def _display_quiz_results(ss):
    """Displays the quiz results."""
    result = ss[f"{SS_PREFIX}quiz_result"]
    if not result:
        st.error("No quiz results available.")
        return

    st.subheader("Quiz Results")
    st.markdown(f"**Score: {result['score']:.2f}%**")
    st.info(f"Correct: {result['correct']} | Wrong: {result['wrong']} | Total: {result['total']}")
    st.write(f"Duration: {result['duration']}")
    st.write(f"Difficulty: {result['difficulty']}")
    st.write(f"Topic: {result.get('topic', 'N/A')}") # Display topic

    # FIX: "Retry Wrong Questions" When None Wrong - Disable or hide button
    wrong_questions_count = result['wrong']
    if wrong_questions_count == 0:
        st.success("🎉 Congratulations! You answered all questions correctly!")
        st.info("No wrong questions to retry.")
    else:
        if st.button("🔁 Retry Wrong Questions", key="retry_wrong_q_button"):
            # Set up a new quiz with only the wrong questions
            ss[f"{SS_PREFIX}quiz_active"] = True
            ss[f"{SS_PREFIX}current_question_index"] = 0
            ss[f"{SS_PREFIX}user_answers"] = {}
            ss[f"{SS_PREFIX}quiz_start_time"] = datetime.now()
            ss[f"{SS_PREFIX}quiz_end_time"] = None
            ss[f"{SS_PREFIX}quiz_submitted"] = False
            ss[f"{SS_PREFIX}quiz_result"] = None
            ss[f"{SS_PREFIX}quiz_questions"] = [q['question'] for q in result['wrong_questions']]
            ss[f"{SS_PREFIX}quiz_bookmarks"] = [] # Clear bookmarks when retrying wrong questions
            # When retrying wrong questions, maintain the original topic and difficulty
            ss[f"{SS_PREFIX}current_quiz_topic"] = result.get('topic', 'General Knowledge')
            ss[f"{SS_PREFIX}current_quiz_difficulty"] = result.get('difficulty', 'Medium')
            st.rerun()

    if st.button("Start New Quiz", key="new_quiz_from_results"):
        _reset_quiz_state(ss)
        st.rerun()

    if wrong_questions_count > 0:
        st.markdown("---")
        st.subheader("Review Wrong Answers")
        for wrong_q in result['wrong_questions']:
            q_data = wrong_q['question']
            q_index = wrong_q['index']
            st.markdown(f"**Q{q_index + 1}: {q_data['question']}**")
            st.error(f"Your answer: {wrong_q['user_answer']}")
            st.success(f"Correct answer: {wrong_q['correct_answer']}")
            st.markdown(f"Options: {', '.join(q_data['options'])}")
            st.markdown("---")

    if ss[f"{SS_PREFIX}quiz_bookmarks"]:
        st.markdown("---")
        st.subheader("Bookmarked Questions")
        for i, b_q in enumerate(ss[f"{SS_PREFIX}quiz_bookmarks"]):
            st.markdown(f"**Q{i+1}: {b_q['question']}**")
            st.write(f"Options: {', '.join(b_q['options'])}")
            st.info(f"Correct Answer: {b_q['answer']}")
            if b_q.get("chapter"):
                st.caption(f"Chapter: {b_q['chapter']}")
            st.markdown("---")


def _generate_result_text(quiz_info: Dict[str, Any], correct_count: int, total_count: int) -> str:
    """
    Generates a text summary of the quiz results.
    Args:
        quiz_info (dict): Dictionary containing quiz metadata.
        correct_count (int): Number of correct answers.
        total_count (int): Total number of questions.
    Returns:
        str: A formatted text summary.
    """
    score = (correct_count / total_count) * 100 if total_count > 0 else 0
    duration = quiz_info.get("duration", "N/A")
    difficulty = quiz_info.get("difficulty", "N/A")
    topic = quiz_info.get("topic", "N/A")

    result_text = f"Quiz Completed!\n"
    result_text += f"Score: {score:.2f}%\n"
    result_text += f"Correct Answers: {correct_count}/{total_count}\n"
    result_text += f"Difficulty: {difficulty}\n"
    result_text += f"Topic: {topic}\n" # Include topic in text summary
    result_text += f"Time Taken: {duration}\n\n"
    result_text += "Review your answers below."
    return result_text

# Main function for the quiz interface
def quiz_interface():
    st.title("🧠 NCC Quiz Challenge")
    st.write("Test your knowledge about NCC topics!")

    # Use a common session state object for brevity and clarity
    ss = st.session_state

    # Initialize quiz state if not already done
    _initialize_quiz_state(ss)

    if not ss[f"{SS_PREFIX}quiz_active"]:
        _display_quiz_creation_form(ss)
    elif not ss[f"{SS_PREFIX}quiz_submitted"]:
        _display_active_quiz(ss)
    else:
        _display_quiz_results(ss)

    # Display quiz score history for adaptive difficulty calculation visibility
    st.sidebar.markdown("---")
    st.sidebar.subheader("Quiz Score History")
    score_history = ss.get(f"{SS_PREFIX}quiz_score_history", [])
    if score_history:
        for i, entry in enumerate(reversed(score_history)): # Show most recent first
            timestamp = datetime.fromisoformat(entry['timestamp']).strftime("%Y-%m-%d %H:%M")
            st.sidebar.write(f"**{i+1}.** {timestamp} | Score: {entry['score']:.2f}% | Diff: {entry['difficulty']} | Topic: {entry.get('topic', 'N/A')}") # Display topic
    else:
        st.sidebar.info("No quiz history yet. Take a quiz to build your history!")

    # Option to clear quiz history
    if st.sidebar.button("Clear Quiz History", key="clear_quiz_history_sidebar"):
        clear_history("quiz_score")
        _reset_quiz_state(ss) # Reset quiz state after clearing history
        st.rerun()

