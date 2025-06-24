import streamlit as st
import random
import time
import os
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime # Ensure datetime is imported
import google.generativeai as genai

from ncc_utils import (
    load_quiz_score_history,
    append_quiz_score_entry
)

from core_utils import (
    clear_quiz_score_history,
    Config, # For accessing paths and API settings
    _is_in_cooldown,
    _cooldown_message
)

from sync_manager import queue_for_sync

# QUIZ_DATA is removed as we will use AI to generate questions.
# If you need a fallback or a static quiz mode, this could be reinstated.

# --- Quiz State Management ---
SS_PREFIX = "quiz_ss_" # Prefix to avoid conflicts with other modules' session state

# --- Quiz Generation Constants (can be moved to a local config if needed) ---
TEMP_QUIZ = 0.5 # Slightly higher for more creative questions
MAX_TOKENS_QUIZ = 2500 # Increased for potentially more questions or detailed explanations


def _initialize_quiz_state(ss):
    """Initializes all quiz-related session state variables if they don't exist."""
    if f"{SS_PREFIX}quiz_active" not in ss:
        # Load persisted score history first, then reset other quiz state
        # Ensure quiz_score_history is initialized before _reset_quiz_state might use it
        if f"{SS_PREFIX}quiz_score_history" not in ss:
            ss[f"{SS_PREFIX}quiz_score_history"] = load_quiz_score_history()
        _reset_quiz_state(ss) # Resets current quiz, uses loaded history for difficulty

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
    # Default difficulty if no history
    if not score_history:
        return "Medium"

    recent_scores_data = score_history[-5:]
    
    # Extract valid, numeric scores from recent history
    valid_numeric_scores_recent = []
    for entry in recent_scores_data:
        score = entry.get('score') # Use .get() for safety against missing key
        if isinstance(score, (int, float)): # Ensure score is numeric
            valid_numeric_scores_recent.append(score)

    if not valid_numeric_scores_recent:
        # If no valid scores in recent history, try to use overall average from all history
        all_valid_numeric_scores = []
        for entry in score_history: # Check all history
            score = entry.get('score')
            if isinstance(score, (int, float)):
                all_valid_numeric_scores.append(score)
        
        if not all_valid_numeric_scores:
            return "Medium" # Default if absolutely no valid scores anywhere
        average_score = sum(all_valid_numeric_scores) / len(all_valid_numeric_scores)
    else:
        average_score = sum(valid_numeric_scores_recent) / len(valid_numeric_scores_recent)

    # Adaptive logic based on average score
    if average_score >= 80:
        return "Hard"
    elif average_score >= 60:
        return "Medium"
    else:
        return "Easy"

def _build_quiz_prompt(topic: str, num_q: int, difficulty: str) -> str:
    """
    Builds an enhanced Gemini prompt for quiz generation.
    """
    difficulty_instructions = {
        "Easy": "focus on basic concepts, definitions, and straightforward facts. Questions should be simple to understand.",
        "Medium": "require understanding of intermediate concepts, some application of knowledge, and ability to differentiate between related ideas. Distractors should be plausible.",
        "Hard": "demand advanced understanding, critical thinking, analysis, or synthesis of information. Questions can be multi-step or scenario-based. Distractors should be very subtle."
    }
    
    prompt = f"""
    You are an expert NCC (National Cadet Corps) instructor. Your task is to generate {num_q} high-quality multiple-choice questions (MCQs) about the NCC topic: "{topic}".
    The target audience is NCC cadets.
    The desired difficulty level is: {difficulty.upper()}. For this difficulty, {difficulty_instructions.get(difficulty, difficulty_instructions['Medium'])}

    For each question, strictly adhere to the following format:

    Q: [Your question text here. Ensure it is clear, unambiguous, and relevant to NCC.]
    A) [Option A - Plausible, but incorrect if not the answer]
    B) [Option B - Plausible, but incorrect if not the answer]
    C) [Option C - Plausible, but incorrect if not the answer]
    D) [Option D - Plausible, but incorrect if not the answer]
    ANSWER: [A single uppercase letter: A, B, C, or D corresponding to the correct option]
    EXPLANATION: [A concise but comprehensive explanation. Clarify why the correct answer is right and, if applicable, why common misconceptions (represented by distractors) are wrong. This should aid learning.]

    ---
    [This '---' separator MUST be on its own line between each complete question block (Q, Options, Answer, Explanation)]

    Important Guidelines:
    1.  Number of Questions: Generate exactly {num_q} questions.
    2.  Format Adherence: The specified format (Q:, A), B), C), D), ANSWER:, EXPLANATION:, ---) is CRITICAL for parsing. Do not deviate.
    3.  Options: Provide exactly four unique options (A, B, C, D). Avoid "All of the above" or "None of the above". Distractors should be relevant to the topic.
    4.  Answer: Clearly indicate the single correct answer using the format "ANSWER: [Letter]".
    5.  Explanation: The explanation is crucial for learning. Make it informative.
    6.  Relevance: All questions, options, and explanations must be directly related to NCC.
    7.  Clarity: Ensure questions are well-phrased and easy to understand for NCC cadets.
    8.  Originality: Generate fresh questions, not just copied from standard texts if possible, while staying true to NCC doctrine.
    """
    return prompt

def _parse_ai_quiz_response(response_text: str) -> List[Dict[str, Any]]:
    """Parse raw quiz response from AI into structured format."""
    parsed_questions = []
    # Split by "---" which should be the primary separator between full question blocks
    question_blocks = response_text.strip().split("\n---\n")

    q_re = re.compile(r'Q:\s*(.*)', re.IGNORECASE) # Removed re.DOTALL
    opt_re = re.compile(r'([A-D])\)\s*(.*)')
    ans_re = re.compile(r'ANSWER:\s*([A-D])', re.IGNORECASE)
    exp_re = re.compile(r'EXPLANATION:\s*(.*)', re.IGNORECASE | re.DOTALL)

    for block in question_blocks:
        block = block.strip()
        if not block:
            continue

        question_data = {"question": "", "options": {}, "answer": "", "explanation": ""}
        
        # Extract question
        q_match = q_re.search(block)
        if q_match:
            question_data["question"] = q_match.group(1).strip()

        # Extract options
        current_options_text = block
        if q_match: # Remove question part to avoid re-matching options in question
            current_options_text = block[q_match.end():]
        
        for opt_match in opt_re.finditer(current_options_text):
            question_data["options"][opt_match.group(1)] = opt_match.group(2).strip()

        # Extract answer
        ans_match = ans_re.search(block)
        if ans_match:
            question_data["answer"] = ans_match.group(1).upper()

        # Extract explanation
        exp_match = exp_re.search(block)
        if exp_match:
            question_data["explanation"] = exp_match.group(1).strip()

        # Validate extracted data for this block
        if (question_data["question"] and
            len(question_data["options"]) == 4 and
            question_data["answer"] in question_data["options"] and # Check if answer key exists in options
            question_data["explanation"]):
            question_data["timestamp"] = datetime.now().isoformat()
            parsed_questions.append(question_data)
        elif question_data["question"]: # Log if we have a question but other parts are missing
            pass # All debug and user message calls removed for dev/prod direction

    if not parsed_questions and response_text:
        pass # All debug and user message calls removed for dev/prod direction
    return parsed_questions


def _display_quiz_creation_form(ss, model, model_error):
    """Displays the form to create a new quiz."""
    st.subheader("New Quiz Configuration")

    # Display current suggested difficulty
    st.info(f"Suggested Difficulty based on history: **{ss[f'{SS_PREFIX}current_quiz_difficulty']}**")

    # Difficulty selection with clear label
    selected_difficulty = st.selectbox(
        "Difficulty Level",  # More descriptive label
        options=["Easy", "Medium", "Hard"],
        index=["Easy", "Medium", "Hard"].index(ss[f"{SS_PREFIX}current_quiz_difficulty"]) if ss[f"{SS_PREFIX}current_quiz_difficulty"] in ["Easy", "Medium", "Hard"] else 1,
        key=f"{SS_PREFIX}difficulty_select",
        help="Choose the difficulty level for your quiz",
        label_visibility="visible"
    )

    # Topic selection with clear label
    # TODO: Consider dynamically populating topics from syllabus_manager or a predefined list for AI.
    ai_topics = [
        "NCC General", "National Integration", "Drill", "Weapon Training", 
        "Map Reading", "Field Craft Battle Craft", "Civil Defence", 
        "First Aid", "Leadership", "Social Service"
    ]
    selected_topic = st.selectbox(
        "Study Topic",  # More descriptive label
        options=ai_topics,
        key=f"{SS_PREFIX}topic_select",
        help="Select the topic you want to be quizzed on",
        label_visibility="visible"
    )

    # Number of questions with descriptive label
    # The AI will attempt to generate this many, capped by difficulty settings in utils.py
    num_questions_to_request = st.slider(
        "Number of Questions to Generate",
        min_value=1, # As per utils.py clamping
        max_value=10, # As per utils.py clamping
        value=5,      # Default value
        step=1,
        key=f"{SS_PREFIX}num_questions_slider_ai",
        help="Choose how many questions you want in your quiz",
        disabled=(model_error is not None or _is_in_cooldown(f"{SS_PREFIX}last_quiz_api_call_time")),
        label_visibility="visible"
    )

    if model_error:
        st.error(f"AI Model Error: {model_error}. Quiz generation is unavailable.")

    if st.button("Start AI Generated Quiz", key=f"{SS_PREFIX}start_quiz_button_ai", disabled=(model_error is not None)):
        if _is_in_cooldown(f"{SS_PREFIX}last_quiz_api_call_time"):
            st.warning(_cooldown_message("quiz generation"))
            return

        with st.spinner(f"Generating {num_questions_to_request} questions on '{selected_topic}' (Difficulty: {selected_difficulty})..."):
            questions_to_start, gen_error = _ai_generate_quiz_questions(
                model, model_error, selected_topic, num_questions_to_request, selected_difficulty
            )
        if not questions_to_start:
            st.error(f"Failed to generate quiz: {gen_error or 'No questions returned by AI.'}")
            return
        
        ss[f"{SS_PREFIX}current_quiz_difficulty"] = selected_difficulty # Set chosen difficulty
        ss[f"{SS_PREFIX}current_quiz_topic"] = selected_topic # Store chosen topic
        ss[f"{SS_PREFIX}quiz_questions"] = questions_to_start
        if ss[f"{SS_PREFIX}quiz_questions"]:
            ss[f"{SS_PREFIX}quiz_active"] = True
            ss[f"{SS_PREFIX}current_question_index"] = 0
            ss[f"{SS_PREFIX}user_answers"] = {}
            ss[f"{SS_PREFIX}quiz_start_time"] = datetime.now()
            ss[f"{SS_PREFIX}quiz_submitted"] = False
            ss[f"{SS_PREFIX}quiz_result"] = None
            ss[f"{SS_PREFIX}quiz_bookmarks"] = [] # Ensure bookmarks are clear for new quiz
            st.rerun() # Trigger rerun to display the quiz

def _save_generated_quiz_to_log(topic: str, questions: List[Dict[str, Any]]) -> None:
    """Saves the generated quiz questions to a log file."""
    try:
        quiz_log_path = Config.LOG_PATHS['quiz']['log'] # Uses Config from utils
        history = []
        if os.path.exists(quiz_log_path):
            with open(quiz_log_path, 'r', encoding='utf-8') as f:
                try:
                    history = json.load(f)
                except json.JSONDecodeError:
                    history = [] # Start fresh if file is corrupt
        
        history.append({
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "questions_generated_count": len(questions),
            "questions": questions # Save the actual questions
        })
        with open(quiz_log_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        pass # All debug and user message calls removed for dev/prod direction

def _ai_generate_quiz_questions(
    model: Optional[genai.GenerativeModel],
    model_error: Optional[str],
    topic: str,
    num_questions_requested: int,
    difficulty: str
) -> Tuple[Optional[List[Dict]], Optional[str]]:
    """Internal function to generate quiz questions using the AI model."""
    if model_error or not model:
        return None, f"Model error: {model_error or 'Model not initialized'}"

    # num_questions_requested is already validated by the slider (1-10)
    prompt = _build_quiz_prompt(topic, num_questions_requested, difficulty)

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(temperature=TEMP_QUIZ, max_output_tokens=MAX_TOKENS_QUIZ)
        )
        raw_response_text = response.text
        parsed_questions = _parse_ai_quiz_response(raw_response_text)

        if parsed_questions:
            st.session_state[f"{SS_PREFIX}last_quiz_api_call_time"] = datetime.now()
            _save_generated_quiz_to_log(topic, parsed_questions) # Log the generated questions
            return parsed_questions, None
        return None, "Failed to parse valid quiz questions from AI response. Check logs for raw response. Please try again or rephrase."
    except Exception as e:
        return None, "Apologies, an error occurred while generating the quiz. Please try again."

def _display_active_quiz(ss):
    """Displays the active quiz questions."""
    st.subheader(f"Quiz (Difficulty: {ss[f'{SS_PREFIX}current_quiz_difficulty']})")
    
    questions = ss.get(f"{SS_PREFIX}quiz_questions", [])
    current_q_index = ss.get(f"{SS_PREFIX}current_question_index", 0)
    num_questions = len(questions)

    if not questions or not (0 <= current_q_index < num_questions):
        st.error("Quiz error: No questions loaded or invalid question index.")
        if st.button("Return to Quiz Setup", key="error_return_to_setup"):
            _reset_quiz_state(ss)
            st.rerun()
        st.warning("No questions available for this quiz. Please go back and select a different configuration.")
        if st.button("Back to Quiz Setup", key="back_to_setup_no_q"):
            _reset_quiz_state(ss)
            st.rerun()
        return

    # Progress bar
    progress_percent = (current_q_index / num_questions) if num_questions > 0 else 0
    st.progress(progress_percent, text=f"Question {current_q_index + 1} of {num_questions}")

    question = questions[current_q_index] # Get current question

    # Display current question and bookmark button in columns
    col_q_text, col_bookmark_btn = st.columns([4, 1]) # Adjust ratio as needed
    with col_q_text:
        st.markdown(f"**Q{current_q_index + 1}: {question['question']}**")
    with col_bookmark_btn:
        # Bookmark button - MOVED OUTSIDE THE FORM & ENHANCED
        is_bookmarked = question in ss.get(f"{SS_PREFIX}quiz_bookmarks", [])
        bookmark_icon = "🌟" if is_bookmarked else "⭐"
        bookmark_text = "Bookmarked" if is_bookmarked else "Bookmark"
        if st.button(f"{bookmark_icon} {bookmark_text}", 
                       key=f"bookmark_toggle_{current_q_index}", # Unique key for toggle
                       help="Bookmark/Unbookmark this question for later review",
                       use_container_width=True):
            bookmarks = ss.get(f"{SS_PREFIX}quiz_bookmarks", [])
            if not is_bookmarked:
                bookmarks.append(question)
                st.toast(f"Question {current_q_index+1} bookmarked!")
            else:
                bookmarks.remove(question) # Ensure removal works
                st.toast(f"Question {current_q_index+1} unbookmarked.")
            ss[f"{SS_PREFIX}quiz_bookmarks"] = bookmarks # Update session state
            st.rerun()

    # Prepare options for st.radio
    # question['options'] is expected to be like {'A': 'Text A', 'B': 'Text B', ...}
    # question['answer'] is the key, e.g., 'A'
    # ss[f"{SS_PREFIX}user_answers"][str(current_q_index)] stores the key, e.g., 'A'
    
    options_dict = question.get('options', {})
    if not options_dict or not all(isinstance(opt_text, str) for opt_text in options_dict.values()) or len(options_dict) < 2 : # Basic check for valid options
        st.error(f"Question {current_q_index + 1} data is malformed: Options are missing, not strings, or incomplete. Please report this issue or try generating a new quiz.")
        if st.button("Return to Quiz Setup", key=f"malformed_q_return_{current_q_index}"):
            _reset_quiz_state(ss)
            st.rerun()
        return
        
    options_display_list = list(options_dict.values()) # List of option texts for display
    
    # Determine the index for st.radio if an answer was previously selected
    selected_option_index = None
    previous_answer_key = ss[f"{SS_PREFIX}user_answers"].get(str(current_q_index))
    if previous_answer_key and previous_answer_key in options_dict:
        previous_answer_text = options_dict[previous_answer_key]
        if previous_answer_text in options_display_list:
            selected_option_index = options_display_list.index(previous_answer_text)
    
    # Use a form to capture user's answer
    with st.form(key=f"question_form_{current_q_index}"):
        # User answer selection with proper label
        user_selected_text = st.radio(
            "Answer Options",  # More descriptive than "Select your answer:"
            options=options_display_list,
            key=f"q_{current_q_index}_option",
            index=selected_option_index,
            help="Select the correct answer from the options below",
            label_visibility="visible" 
        )
        
        # Navigation buttons with clear labels
        col_next_btn, col_abandon_btn = st.columns(2)
        with col_next_btn:
            submit_button = st.form_submit_button(
                "Next Question ▶️",
                use_container_width=True,
                help="Save your answer and move to the next question"
            )
        with col_abandon_btn:
            if st.form_submit_button(
                "🗑️ End Quiz",  # Changed from "Abandon Quiz" for clarity
                use_container_width=True,
                type="secondary",
                help="Stop the current quiz without completing it"
            ):
                _reset_quiz_state(ss) # Reset current quiz, do not clear all history
                st.info("Quiz abandoned. Your overall score history is preserved.")
                st.rerun()

    # The bookmark button is now outside the form, handled above.

    # Handle the "Next Question" button click (if it was the one pressed)
    if submit_button:
        # Find the key ('A', 'B', 'C', 'D') corresponding to the selected text
        user_choice_key = None
        for opt_key, opt_val in options_dict.items():
            if opt_val == user_selected_text:
                user_choice_key = opt_key
                break
        
        if user_choice_key:
            ss[f"{SS_PREFIX}user_answers"][str(current_q_index)] = user_choice_key
        else:
            st.warning(f"Could not map selected answer '{user_selected_text}' back to an option key for Q{current_q_index+1}. This might indicate an issue with question data. Storing raw text.")
            ss[f"{SS_PREFIX}user_answers"][str(current_q_index)] = user_selected_text # Fallback, though this might affect scoring if not a key
        ss[f"{SS_PREFIX}current_question_index"] += 1
        # If all questions answered, go to results
        if ss[f"{SS_PREFIX}current_question_index"] >= num_questions:
            ss[f"{SS_PREFIX}quiz_end_time"] = datetime.now() # Set end time BEFORE calculating results
            _calculate_results(ss)
            ss[f"{SS_PREFIX}quiz_submitted"] = True
        st.rerun() # Rerun to display next question or results

def _calculate_results(ss):
    """Calculates and stores quiz results."""
    correct_answers = 0
    wrong_questions = []
    
    for i, question in enumerate(ss[f"{SS_PREFIX}quiz_questions"]):
        user_ans_key = ss[f"{SS_PREFIX}user_answers"].get(str(i)) # This should be the key 'A', 'B', etc.
        correct_ans_key = question.get('answer')

        if user_ans_key == correct_ans_key:
            correct_answers += 1
        else:
            wrong_questions.append({
                "index": i,
                "question": question,
                "user_answer_key": user_ans_key, # Store the key of user's answer
                "correct_answer_key": correct_ans_key # Store the key of correct answer
            })
    
    total_questions = len(ss[f"{SS_PREFIX}quiz_questions"])
    score_percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0

    duration_str = "N/A"
    if ss[f"{SS_PREFIX}quiz_start_time"] and ss[f"{SS_PREFIX}quiz_end_time"]:
        duration = ss[f"{SS_PREFIX}quiz_end_time"] - ss[f"{SS_PREFIX}quiz_start_time"]
        total_seconds = duration.total_seconds()
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)

        if minutes > 0:
            duration_str = f"{minutes} min {seconds} sec"
        elif seconds > 0:
            duration_str = f"{seconds} sec"
        else: # Less than a second
            duration_str = f"{total_seconds:.2f} sec"

    ss[f"{SS_PREFIX}quiz_result"] = {
        "score": score_percentage,
        "correct": correct_answers,
        "wrong": len(wrong_questions),
        "total": total_questions,
        "wrong_questions": wrong_questions,
        "duration": duration_str,
        "timestamp": datetime.now().isoformat(),
        "difficulty": ss[f"{SS_PREFIX}current_quiz_difficulty"],
        "topic": ss[f"{SS_PREFIX}current_quiz_topic"] # Include topic in result
    }
    
    # Append result to persisted history
    # This uses the new dedicated function from utils.py
    append_quiz_score_entry({
        "timestamp": datetime.now().isoformat(),
        "score": score_percentage,
        "difficulty": ss[f"{SS_PREFIX}current_quiz_difficulty"],
        "topic": ss[f"{SS_PREFIX}current_quiz_topic"]
    })

    # After quiz completion, queue summary for sync
    quiz_metadata = {
        "topic": ss[f"{SS_PREFIX}current_quiz_topic"],
        "score": score_percentage,
        "difficulty": ss[f"{SS_PREFIX}current_quiz_difficulty"],
        "timestamp": datetime.now().isoformat(),
    }
    queue_for_sync(quiz_metadata, "quiz_metadata")

def _display_quiz_results(ss):
    """Displays the quiz results."""
    result = ss[f"{SS_PREFIX}quiz_result"]
    if not result:
        st.error("No quiz results available.")
        return

    st.subheader("📊 Quiz Results")

    # Use columns for key metrics for a cleaner look
    res_col1, res_col2, res_col3 = st.columns(3)
    with res_col1:
        st.metric(label="Score", value=f"{result['score']:.2f}%")
    with res_col2:
        st.metric(label="Correct Answers", value=result['correct'])
    with res_col3:
        st.metric(label="Wrong Answers", value=result['wrong'])
    
    # Display other relevant information
    st.write(f"Total Questions: {result['total']}")
    st.write(f"⏱️ Duration: {result['duration']}")
    st.write(f"🏋️ Difficulty: {result['difficulty']}")
    st.write(f"📚 Topic: {ss.get(f'{SS_PREFIX}current_quiz_topic', 'N/A')}")
    st.markdown("---") # Visual separator

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
            # Maintain the original topic and difficulty for the retry session
            ss[f"{SS_PREFIX}current_quiz_topic"] = result.get('topic', 'General Knowledge')
            ss[f"{SS_PREFIX}current_quiz_difficulty"] = result.get('difficulty', 'Medium')
            st.rerun()

    if st.button("Start New Quiz", key="new_quiz_from_results"):
        _reset_quiz_state(ss)
        st.rerun()

    if wrong_questions_count > 0:
        st.markdown("---")
        st.subheader("Review Wrong Answers")
        for wrong_q_info in result['wrong_questions']:
            q_data = wrong_q_info['question'] # Full question dict
            q_index = wrong_q_info['index'] # 0-based index from the original quiz
            user_answered_key = wrong_q_info['user_answer_key'] 
            correct_answer_key = wrong_q_info['correct_answer_key']

            st.markdown(f"**Q{q_index + 1}: {q_data.get('question', 'N/A')}**")

            options_in_q = q_data.get('options', {})
            st.markdown("**Options:**")
            for opt_key, opt_text in options_in_q.items():
                if opt_key == correct_answer_key:
                    st.success(f"- {opt_key}) {opt_text} (Correct Answer)")
                elif opt_key == user_answered_key:
                    st.error(f"- {opt_key}) {opt_text} (Your Answer)")
                else:
                    st.markdown(f"- {opt_key}) {opt_text}")
            
            # Explicitly state the user's answer if it was wrong, for clarity,
            # especially if it wasn't highlighted in the list (e.g., if user_answered_key was None or unexpected).
            if user_answered_key != correct_answer_key:
                user_answer_display_text = "Not answered"
                if user_answered_key is not None:
                    if user_answered_key in options_in_q:
                        user_answer_display_text = f"{user_answered_key}) {options_in_q[user_answered_key]}"
                    else:
                        user_answer_display_text = str(user_answered_key) # Display the raw recorded answer if not a valid key
                # The loop above already highlights the user's choice if it's a valid option.
                # This explicit message can be redundant but ensures clarity if highlighting failed or answer was unusual.
                # To avoid redundancy if already highlighted:
                # if not (user_answered_key in options_in_q): # Only show this if not already highlighted in the list
                #    st.error(f"Your recorded answer: {user_answer_display_text}")
                # For now, the highlighting in the loop is the primary indicator.
                pass # The highlighting within the option list should cover displaying the user's wrong answer.
 
            explanation = q_data.get('explanation', 'No explanation available for this question.')
            with st.expander("View Explanation", expanded=True): # Show explanation by default
                st.info(explanation if explanation else "_No explanation provided._")
            st.markdown("---")

    if ss[f"{SS_PREFIX}quiz_bookmarks"]:
        st.markdown("---")
        st.subheader("Bookmarked Questions")
        for i, b_q in enumerate(ss[f"{SS_PREFIX}quiz_bookmarks"]):
            st.markdown(f"**Bookmarked Q: {b_q.get('question', 'N/A')}**")
            options_in_bookmark = b_q.get('options', {})
            correct_answer_key_bookmark = b_q.get('answer')
            st.markdown("**Options:**")
            for opt_key, opt_text in options_in_bookmark.items():
                if opt_key == correct_answer_key_bookmark:
                    st.success(f"- {opt_key}) {opt_text} (Correct Answer)")
                else:
                    st.markdown(f"- {opt_key}) {opt_text}")

            explanation = b_q.get('explanation', 'No explanation available.')
            with st.expander("View Explanation", expanded=True): # Show explanation by default
                 st.info(explanation if explanation else "_No explanation provided._")
            if b_q.get("chapter"): # This field might not be present for AI generated questions
                st.caption(f"Chapter: {b_q['chapter']}")
            st.markdown("---")

# Main function for the quiz interface
def quiz_interface(model, model_error): # Accept model and model_error
    st.write("Test your knowledge about NCC topics!")

    # Use a common session state object for brevity and clarity
    ss = st.session_state

    # Initialize quiz state if not already done
    _initialize_quiz_state(ss)

    if not ss[f"{SS_PREFIX}quiz_active"]:
        _display_quiz_creation_form(ss, model, model_error) # Pass model and model_error
    elif not ss[f"{SS_PREFIX}quiz_submitted"]:
        _display_active_quiz(ss)
    else:
        _display_quiz_results(ss)

    # Removed Quiz Score History display from sidebar as it's in the "History Viewer" tab.
    # # Display quiz score history for adaptive difficulty calculation visibility
    # st.sidebar.markdown("---")
    # st.sidebar.subheader("Quiz Score History")
    # score_history = ss.get(f"{SS_PREFIX}quiz_score_history", [])
    # if score_history:
    #     for i, entry in enumerate(reversed(score_history)): # Show most recent first
    #         try:
    #             timestamp_str = datetime.fromisoformat(entry['timestamp']).strftime("%Y-%m-%d %H:%M")
    #         except (TypeError, ValueError):
    #             timestamp_str = "Unknown Time"
    #         st.sidebar.write(f"**{i+1}.** {timestamp_str} | Score: {entry.get('score', 0):.2f}% | Diff: {entry.get('difficulty', 'N/A')} | Topic: {entry.get('topic', 'N/A')}")
    # else:
    #     st.sidebar.info("No quiz history yet. Take a quiz to build your history!")

    # # Option to clear quiz history
    # if st.sidebar.button("Clear Quiz History", key="clear_quiz_history_sidebar"):
    #     clear_quiz_score_history() # Use new dedicated function
    #     _reset_quiz_state(ss) # Reset quiz state after clearing history
    #     st.rerun()