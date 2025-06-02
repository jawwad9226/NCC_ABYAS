import streamlit as st
import random
import json
from datetime import datetime

# Assuming a function to load syllabus topics exists, e.g., in utils.py
# from utils import load_syllabus_topics
# For demonstration, we'll mock it or load from a local JSON if available.

# --- Mock Data/Functions for Demonstration (Replace with actual implementations) ---
def _mock_load_syllabus_topics():
    try:
        with open("data/syllabus.json", "r") as f:
            syllabus_data = json.load(f)
            # Extract main topic names, assuming a structure like {"Topic Name": {"subtopics": [...]}}
            return list(syllabus_data.keys())
    except FileNotFoundError:
        return ["Drill", "Weapon Training", "Map Reading", "Field Craft", "First Aid", "Leadership"]
    except json.JSONDecodeError:
        return ["Drill", "Weapon Training", "Map Reading", "Field Craft", "First Aid", "Leadership"]


def _mock_generate_quiz_questions(topic, difficulty, num_questions):
    """
    Mocks a function to generate quiz questions based on topic, difficulty, and count.
    In a real scenario, this would interact with your syllabus data and possibly a model.
    """
    sample_questions = {
        "Drill": [
            {"question": "What is the command for 'Stand at Ease'?", "options": {"A": "Savdhan!", "B": "Vishram!", "C": "Aaram!", "D": "Dahine Mur!"}, "correct": "B"},
            {"question": "Which foot moves first in 'Quick March'?", "options": {"A": "Right", "B": "Left", "C": "Either", "D": "Both simultaneously"}, "correct": "B"},
            {"question": "What is the purpose of Drill?", "options": {"A": "To look smart", "B": "To instill discipline", "C": "To train for combat", "D": "To avoid falling down"}, "correct": "B"},
            {"question": "How many paces are taken for 'Salute'?", "options": {"A": "1", "B": "2", "C": "3", "D": "No fixed paces"}, "correct": "A"},
            {"question": "In drill, what does 'Savdhan' mean?", "options": {"A": "Attention", "B": "Stand at Ease", "C": "Right Turn", "D": "Left Turn"}, "correct": "A"},
        ],
        "Weapon Training": [
            {"question": "What is the caliber of the INSAS rifle?", "options": {"A": "5.56mm", "B": "7.62mm", "C": "9mm", "D": "0.303 inch"}, "correct": "A"},
            {"question": "What is the full form of LMG?", "options": {"A": "Light Machine Gun", "B": "Long Machine Gun", "C": "Loaded Machine Gun", "D": "Live Military Gun"}, "correct": "A"},
            {"question": "What is the effective range of a .22 rifle?", "options": {"A": "25 yards", "B": "50 yards", "C": "100 yards", "D": "200 yards"}, "correct": "A"},
            {"question": "Which part of the rifle supports the aim?", "options": {"A": "Butt", "B": "Barrel", "C": "Sights", "D": "Trigger"}, "correct": "C"},
        ],
        "General NCC": [
            {"question": "What is the motto of NCC?", "options": {"A": "Unity and Discipline", "B": "Service Before Self", "C": "Knowledge is Power", "D": "Never Give Up"}, "correct": "A"},
            {"question": "When was NCC established?", "options": {"A": "1947", "B": "1948", "C": "1950", "D": "1962"}, "correct": "B"},
        ]
    }

    # Combine topic-specific and general questions
    all_qs = sample_questions.get(topic, []) + sample_questions.get("General NCC", [])
    if not all_qs:
        return []

    # Filter by difficulty (mocking difficulty for simplicity)
    # In a real app, questions would have actual difficulty tags or be generated based on complexity
    if difficulty == "Easy":
        filtered_qs = [q for q in all_qs if len(q["options"]) <= 3] # Example: simpler questions
    elif difficulty == "Hard":
        filtered_qs = [q for q in all_qs if len(q["options"]) == 4] # Example: more complex questions
    else: # Medium
        filtered_qs = all_qs

    if len(filtered_qs) < num_questions:
        st.warning(f"Only {len(filtered_qs)} questions available for '{topic}' at '{difficulty}' difficulty. Generating all available.")
        return filtered_qs
    return random.sample(filtered_qs, min(num_questions, len(filtered_qs)))
# --- End of Mock Functions ---


def quiz_interface():
    st.title("🧠 NCC Quiz Challenge")

    # Alias st.session_state for brevity
    ss = st.session_state

    # Initialize session state variables if not already present
    if "quiz_questions" not in ss:
        ss.quiz_questions = []
    if "user_answers" not in ss:
        ss.user_answers = {}
    if "quiz_submitted" not in ss:
        ss.quiz_submitted = False
    if "quiz_score_history" not in ss:
        ss.quiz_score_history = []
    if "current_quiz_difficulty" not in ss:
        ss.current_quiz_difficulty = "Medium" # Default difficulty
    if "quiz_bookmarks" not in ss:
        ss.quiz_bookmarks = []
    if "current_q_index" not in ss: # For pagination
        ss.current_q_index = 0
    if "syllabus_topics" not in ss: # For topic selection dropdown
        ss.syllabus_topics = _mock_load_syllabus_topics() # Load topics only once

    # --- Quiz Generation Form ---
    st.header("Generate New Quiz")
    with st.form(key="quiz_generation_form"):
        topic_input = st.text_input("Enter a specific topic (e.g., 'Drill', 'Map Reading'):", key="quiz_topic_input")
        # Explain "No Topic Provided" with dropdown
        selected_topic_from_dropdown = st.selectbox(
            "Or choose from common NCC topics:",
            [""] + ss.syllabus_topics, # Add an empty option
            key="quiz_topic_select",
            help="Select a predefined NCC topic for your quiz."
        )

        difficulty_level = st.radio(
            "Select Difficulty:",
            ["Easy", "Medium", "Hard"],
            horizontal=True,
            key="quiz_difficulty_radio",
            index=1 # Default to Medium
        )
        num_questions = st.slider("Number of Questions:", min_value=1, max_value=10, value=5, key="quiz_num_questions")

        generate_quiz_button = st.form_submit_button("🚀 Generate Quiz")

        if generate_quiz_button:
            # Determine actual topic to use
            actual_topic = topic_input.strip() if topic_input.strip() else selected_topic_from_dropdown

            if not actual_topic:
                st.warning("Please enter a topic or select one from the dropdown to generate a quiz.")
            else:
                ss.quiz_questions = _mock_generate_quiz_questions(actual_topic, difficulty_level, num_questions)
                if ss.quiz_questions:
                    ss.user_answers = {}
                    ss.quiz_submitted = False
                    ss.current_quiz_difficulty = difficulty_level # Store chosen difficulty
                    ss.current_q_index = 0 # Reset for new quiz
                    st.success(f"Generated a {len(ss.quiz_questions)} question quiz on '{actual_topic}' ({difficulty_level}).")
                    st.experimental_rerun() # Rerun to display quiz
                else:
                    st.warning(f"Could not generate questions for topic '{actual_topic}' at '{difficulty_level}' difficulty. Please try another topic or difficulty.")

    st.markdown("---")

    # --- Display Active Quiz or Results ---
    if ss.quiz_questions:
        if not ss.quiz_submitted:
            _display_active_quiz(ss)
        else:
            _display_quiz_results(ss)
    else:
        st.info("Generate a quiz above to get started with your NCC knowledge challenge!")

    st.markdown("---")

    # --- History and Bookmarks ---
    col_hist, col_book = st.columns(2)
    with col_hist:
        _display_quiz_history(ss)
    with col_book:
        _display_bookmarked_questions(ss)


def _display_active_quiz(ss):
    """Displays the current question of the active quiz with navigation."""
    st.header("Active Quiz")

    total_questions = len(ss.quiz_questions)
    current_q_data = ss.quiz_questions[ss.current_q_index]
    q_index = ss.current_q_index

    # Progress Bar
    st.progress((q_index + 1) / total_questions, text=f"Question {q_index + 1} of {total_questions}")

    # Difficulty-based Visual Cues
    color_map = {"Easy": "#A3E635", "Medium": "#60A5FA", "Hard": "#EF4444"}
    diff = ss.current_quiz_difficulty
    st.markdown(f"<span style='background:{color_map[diff]};padding:4px 8px;border-radius:4px;color:#fff;font-weight:bold;'>{diff}</span>", unsafe_allow_html=True)


    st.markdown(f"### Q{q_index + 1}: {current_q_data['question']}")

    # Radio buttons for options
    options_keys = sorted(current_q_data["options"].keys())
    # Ensure consistent string key for user_answers
    selected_option = st.radio(
        "Select your answer:",
        options=[f"{k}) {current_q_data['options'][k]}" for k in options_keys],
        key=f"q_{q_index}_option",
        index=options_keys.index(ss.user_answers.get(str(q_index), "")) if ss.user_answers.get(str(q_index)) else None # Pre-select if answer exists
    )

    if selected_option:
        # Extract just the option key (e.g., 'A', 'B')
        selected_answer_key = selected_option[0]
        # Store using string key
        ss.user_answers[str(q_index)] = selected_answer_key

    # Bookmark Button
    if st.button(f"⭐ Bookmark Q{q_index+1}", key=f"bookmark_{q_index}", help="Bookmark this question for later review."):
        if current_q_data not in ss.quiz_bookmarks: # Avoid duplicates
            ss.quiz_bookmarks.append(current_q_data)
            st.success(f"Question {q_index+1} bookmarked!")
        else:
            st.info(f"Question {q_index+1} is already bookmarked.")


    # --- Navigation Buttons ---
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("⬅️ Previous", key="prev_q_btn", disabled=(q_index == 0)):
            ss.current_q_index -= 1
            st.rerun()
    with col2:
        if q_index == total_questions - 1:
            if st.button("✅ Submit Quiz", key="submit_quiz_btn", type="primary"):
                ss.quiz_submitted = True
                st.rerun()
        else:
            if st.button("➡️ Next", key="next_q_btn"):
                ss.current_q_index += 1
                st.rerun()
    with col3:
        pass # Placeholder for alignment


def _display_quiz_results(ss):
    """Displays the results of the submitted quiz."""
    st.header("Quiz Results")

    total_questions = len(ss.quiz_questions)
    correct_answers = 0
    wrong_questions = []

    # Iterate through questions to calculate score and identify wrong answers
    for i, q in enumerate(ss.quiz_questions):
        user_ans = ss.user_answers.get(str(i)) # Ensure string key
        correct_ans = q["correct"]

        if user_ans == correct_ans:
            correct_answers += 1
        else:
            wrong_questions.append(q)

    score_percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0

    st.write(f"You answered {correct_answers} out of {total_questions} questions correctly.")
    st.write(f"Your score: **{score_percentage:.2f}%**")

    # Add score to history only if it's an initial submission (not a retry of wrong questions)
    # The assumption here is that 'Retry Wrong Questions' does not add to history.
    # If a new full quiz is generated, quiz_submitted will be reset to False, allowing a new history entry.
    if not ss.get('is_retry_quiz', False):
        ss.quiz_score_history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "score": score_percentage,
            "total_questions": total_questions,
            "difficulty": ss.current_quiz_difficulty,
            "topic": ss.quiz_questions[0].get("topic", "N/A") # Assuming first question has topic
        })
    # Reset is_retry_quiz flag
    ss.is_retry_quiz = False


    st.subheader("Review Answers:")
    for i, q in enumerate(ss.quiz_questions):
        user_ans = ss.user_answers.get(str(i)) # Ensure string key
        correct_ans = q["correct"]
        is_correct = (user_ans == correct_ans)

        with st.expander(f"Q{i+1}: {q['question']}", expanded=False):
            st.write(f"**Your Answer:** {user_ans}) {q['options'].get(user_ans, 'No Answer')}" if user_ans else "**No Answer Provided**")
            st.write(f"**Correct Answer:** {correct_ans}) {q['options'].get(correct_ans, 'N/A')}")
            if is_correct:
                st.success("Correct!")
            else:
                st.error("Incorrect!")

            # Display options with correct/incorrect highlighting
            for k in ['A', 'B', 'C', 'D']: # Fixed typo here ['A', ' 'B', 'C', 'D']
                if k in q['options']:
                    option_text = f"{k}) {q['options'][k]}"
                    if ss.quiz_submitted: # Only show highlighting after submission
                        if k == correct_ans:
                            st.markdown(f"<span style='background-color:#d4edda;color:#155724;padding:3px;border-radius:3px;'>{option_text} (Correct)</span>", unsafe_allow_html=True)
                        elif k == user_ans and not is_correct:
                            st.markdown(f"<span style='background-color:#f8d7da;color:#721c24;padding:3px;border-radius:3px;'>{option_text} (Your Answer)</span>", unsafe_allow_html=True)
                        else:
                            st.write(option_text)
                    else:
                        st.write(option_text) # Show without highlighting if not submitted

    # Retry Wrong Questions button
    if correct_answers == total_questions:
        st.info("Congratulations! You got everything correct—no wrong questions to retry.")
        st.button("🔁 Retry Wrong Questions", disabled=True, help="You answered all questions correctly.")
    elif wrong_questions:
        if st.button("🔁 Retry Wrong Questions", help="Generate a new quiz with only the questions you got wrong."):
            ss.quiz_questions = wrong_questions
            ss.user_answers = {}
            ss.quiz_submitted = False
            ss.current_q_index = 0
            ss.is_retry_quiz = True # Set flag to prevent double counting in history
            st.success(f"Retrying {len(wrong_questions)} wrong questions.")
            st.experimental_rerun()
    else:
        st.info("No questions to retry (perhaps all questions were answered correctly or the quiz was empty).")


def _display_quiz_history(ss):
    """Displays the user's quiz score history."""
    st.subheader("Quiz Score History")
    if ss.quiz_score_history:
        for i, entry in enumerate(reversed(ss.quiz_score_history)): # Show most recent first
            st.markdown(f"**Attempt {len(ss.quiz_score_history) - i}:** "
                        f"{entry['timestamp']} - {entry['score']:.2f}% "
                        f"({entry['difficulty']} on {entry['topic']})")
    else:
        st.info("No quiz history yet. Take a quiz to see your scores here!")


def _display_bookmarked_questions(ss):
    """Displays bookmarked questions and allows removal."""
    st.subheader("Bookmarked Questions")
    if ss.quiz_bookmarks:
        for i, q in enumerate(ss.quiz_bookmarks):
            st.markdown(f"**{i+1}. {q['question']}**")
            if st.button(f"❌ Remove Bookmark {i+1}", key=f"remove_bookmark_{i}", help="Remove this question from your bookmarks."):
                ss.quiz_bookmarks.pop(i)
                st.success(f"Bookmark {i+1} removed.")
                st.experimental_rerun() # Rerun to update the list
    else:
        st.info("No questions bookmarked yet. Click the ⭐ button on a question to bookmark it.")

