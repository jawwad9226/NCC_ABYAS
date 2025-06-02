"""
NCC Quiz Interface
Handles quiz generation, display, and interaction with topic-based selection.
"""

import streamlit as st
from typing import Dict, List, Optional, Tuple, Any
import random
import json
from pathlib import Path

from utils import setup_gemini
from syllabus import syllabus_manager, DifficultyLevel

# Constants
QUIZ_TYPES = {
    "Multiple Choice": "multiple_choice",
    "True/False": "true_false",
    "Short Answer": "short_answer"
}

DIFFICULTY_LEVELS = {
    "Beginner (JD/JW)": DifficultyLevel.JD_JW,
    "Advanced (SD/SW)": DifficultyLevel.SD_SW,
    "Both": DifficultyLevel.BOTH
}

def initialize_quiz_state():
    """Initialize quiz-related session state variables"""
    if 'quiz_questions' not in st.session_state:
        st.session_state.quiz_questions = []
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}
    if 'quiz_score' not in st.session_state:
        st.session_state.quiz_score = 0
    if 'quiz_complete' not in st.session_state:
        st.session_state.quiz_complete = False
    if 'selected_topics' not in st.session_state:
        st.session_state.selected_topics = []
    if 'quiz_settings' not in st.session_state:
        st.session_state.quiz_settings = {
            'quiz_type': 'multiple_choice',
            'difficulty': DifficultyLevel.BOTH,
            'num_questions': 5,
            'time_limit': 10  # minutes
        }

def display_quiz_settings() -> Dict[str, Any]:
    """Display and handle quiz settings"""
    st.sidebar.header("⚙️ Quiz Settings")
    
    # Quiz type selection
    quiz_type = st.sidebar.selectbox(
        "Quiz Type",
        options=list(QUIZ_TYPES.keys()),
        index=0
    )
    
    # Difficulty level
    difficulty = st.sidebar.selectbox(
        "Difficulty Level",
        options=list(DIFFICULTY_LEVELS.keys()),
        index=2  # Default to 'Both'
    )
    
    # Number of questions
    num_questions = st.sidebar.slider(
        "Number of Questions",
        min_value=1,
        max_value=20,
        value=5
    )
    
    # Time limit (optional)
    time_limit = st.sidebar.number_input(
        "Time Limit (minutes)",
        min_value=1,
        max_value=60,
        value=10
    )
    
    return {
        'quiz_type': QUIZ_TYPES[quiz_type],
        'difficulty': DIFFICULTY_LEVELS[difficulty],
        'num_questions': num_questions,
        'time_limit': time_limit
    }

def display_topic_selector() -> List[str]:
    """Display topic selection interface"""
    st.sidebar.header("📚 Select Topics")
    
    # Get all chapters
    chapters = syllabus_manager.get_chapters()
    selected_topics = []
    
    # Chapter selection
    chapter_titles = [c['title'] for c in chapters]
    selected_chapter_idx = st.sidebar.selectbox(
        "Select Chapter",
        range(len(chapter_titles)),
        format_func=lambda x: chapter_titles[x]
    )
    
    if selected_chapter_idx is not None:
        chapter_id = chapters[selected_chapter_idx]['id']
        
        # Section selection
        sections = syllabus_manager.get_sections(chapter_id)
        if sections:
            section_titles = [s['title'] for s in sections]
            selected_section_idx = st.sidebar.selectbox(
                "Select Section",
                range(len(section_titles)),
                format_func=lambda x: section_titles[x]
            )
            
            if selected_section_idx is not None:
                section_id = sections[selected_section_idx]['id']
                
                # Topic selection
                topics = syllabus_manager.get_topics(
                    chapter_id=chapter_id,
                    section_id=section_id
                )
                
                if topics:
                    topic_options = {t.id: t.title for t in topics}
                    selected_topics = st.sidebar.multiselect(
                        "Select Topics",
                        options=list(topic_options.keys()),
                        format_func=lambda x: topic_options[x],
                        default=st.session_state.get('selected_topics', [])
                    )
    
    return selected_topics

def generate_quiz_prompt(settings: Dict[str, Any], topic_ids: List[str]) -> str:
    """Generate a prompt for the AI to create quiz questions"""
    if not topic_ids:
        return ""
    
    # Get topic details
    topics_info = []
    for topic_id in topic_ids:
        context = syllabus_manager.get_topic_context(topic_id)
        if context:
            topics_info.append({
                'chapter': context['chapter']['title'],
                'section': context['section']['title'],
                'topic': context['topic']['title'],
                'content': context['topic']['content'],
                'learning_objectives': context['topic'].get('learning_objectives', [])
            })
    
    # Build the prompt
    prompt = f"""Generate {settings['num_questions']} {settings['quiz_type']} questions 
    based on the following NCC syllabus topics. Ensure questions are appropriate for 
    {settings['difficulty'].value} level cadets.
    
    Topics:"""
    
    for topic in topics_info:
        prompt += f"\n\nChapter: {topic['chapter']}"
        prompt += f"\nSection: {topic['section']}"
        prompt += f"\nTopic: {topic['topic']}"
        if topic['content']:
            prompt += f"\nContent: {topic['content']}"
        if topic['learning_objectives']:
            prompt += "\nLearning Objectives:"
            for obj in topic['learning_objectives']:
                prompt += f"\n- {obj}"
    
    prompt += """
    
    For each question, provide:
    1. The question text
    2. Multiple choice options (if applicable)
    3. The correct answer
    4. A brief explanation
    
    Format the response as a JSON array of question objects.
    """
    
    return prompt

def parse_quiz_questions(response: str) -> List[Dict[str, Any]]:
    """Parse the AI response into quiz questions"""
    try:
        # Try to parse the response as JSON
        questions = json.loads(response)
        if not isinstance(questions, list):
            questions = [questions]
        return questions
    except json.JSONDecodeError:
        st.error("Failed to parse quiz questions. Please try again.")
        return []

def display_question(question: Dict[str, Any], question_num: int) -> Optional[str]:
    """Display a single quiz question and return the user's answer.
    
    Args:
        question: Dictionary containing question data
        question_num: Current question number (0-based index)
        
    Returns:
        User's answer or None if question format is invalid
    """
    if not question or not isinstance(question, dict):
        st.error("Invalid question format.")
        return None
        
    st.subheader(f"Question {question_num + 1}")
    
    # Display question text if available
    if 'question' not in question:
        st.error("Question text is missing.")
        return None
        
    st.write(question['question'])
    
    question_type = question.get('type', 'multiple_choice')
    
    try:
        if question_type == 'multiple_choice':
            if 'options' not in question or not question['options']:
                st.error("No options provided for multiple choice question.")
                return None
                
            options = question['options']
            if not isinstance(options, (list, dict)) or not options:
                st.error("Invalid options format for multiple choice question.")
                return None
                
            # Handle both list and dict formats for options
            if isinstance(options, list):
                options = {chr(65 + i): opt for i, opt in enumerate(options)}
            
            # Display options as radio buttons
            answer = st.radio(
                "Select an answer:",
                options=list(options.keys()),
                format_func=lambda x: f"{x}) {options.get(x, '')}",
                key=f"q{question_num}",
                index=None
            )
            return answer
            
        elif question_type == 'true_false':
            answer = st.radio(
                "True or False:",
                options=["True", "False"],
                key=f"q{question_num}",
                index=None
            )
            return answer
            
        else:  # short_answer or unknown type
            answer = st.text_area(
                "Your answer:",
                key=f"q{question_num}",
                height=100
            )
            return answer.strip()
            
    except Exception as e:
        st.error(f"Error displaying question: {str(e)}")
        logging.exception(f"Error in display_question: {str(e)}")
        return None


def display_results():
    """Display quiz results and performance analysis"""
    if not st.session_state.get('quiz_questions'):
        st.error("No quiz data available to display results.")
        return
        
    total_questions = len(st.session_state.quiz_questions)
    if total_questions == 0:
        st.warning("No questions were answered.")
        return
    
    # Calculate score
    correct_answers = 0
    for i, question in enumerate(st.session_state.quiz_questions):
        user_answer = st.session_state.user_answers.get(str(i))
        correct_answer = question.get('correct_answer')
        
        if user_answer and correct_answer and str(user_answer).lower() == str(correct_answer).lower():
            correct_answers += 1
    
    score_percentage = (correct_answers / total_questions) * 100
    
    # Display overall score
    st.title("🎯 Quiz Results")
    st.metric("Your Score", f"{correct_answers}/{total_questions} ({score_percentage:.1f}%)")
    
    # Performance by topic
    if any('topic' in q for q in st.session_state.quiz_questions):
        st.subheader("Performance by Topic")
        topic_scores = {}
        
        for i, question in enumerate(st.session_state.quiz_questions):
            topic = question.get('topic', 'General')
            if topic not in topic_scores:
                topic_scores[topic] = {'correct': 0, 'total': 0}
                
            topic_scores[topic]['total'] += 1
            user_answer = st.session_state.user_answers.get(str(i))
            correct_answer = question.get('correct_answer')
            
            if user_answer and correct_answer and str(user_answer).lower() == str(correct_answer).lower():
                topic_scores[topic]['correct'] += 1
        
        # Display topic-wise performance
        for topic, scores in topic_scores.items():
            if scores['total'] > 0:
                score_pct = (scores['correct'] / scores['total']) * 100
                st.progress(
                    score_pct / 100, 
                    text=f"{topic}: {scores['correct']}/{scores['total']} ({score_pct:.1f}%)"
                )
    
    # Review incorrect answers
    incorrect_questions = [
        (i, q) for i, q in enumerate(st.session_state.quiz_questions)
        if str(st.session_state.user_answers.get(str(i), '')).lower() != str(q.get('correct_answer', '')).lower()
    ]
    
    if incorrect_questions:
        st.subheader("Review Incorrect Answers")
        for idx, question in incorrect_questions:
            user_answer = st.session_state.user_answers.get(str(idx))
            with st.expander(f"Question {idx+1}: {question.get('question', '')}", expanded=False):
                st.write(f"**Your answer:** {user_answer}")
                st.write(f"**Correct answer:** {question.get('correct_answer', '')}")
                if 'explanation' in question:
                    st.write(f"**Explanation:** {question['explanation']}")
    else:
        st.balloons()
        st.success("🎉 Perfect! You got all questions correct!")
    
    # Reset button
    if st.button("Take Another Quiz"):
        for key in ['quiz_questions', 'current_question', 'user_answers', 
                   'quiz_score', 'quiz_complete', 'selected_topics']:
            st.session_state.pop(key, None)
        st.rerun()

def display_quiz_interface(model):
    """Main function to display the quiz interface"""
    st.title("🎯 NCC Knowledge Quiz")
    
    # Initialize session state
    initialize_quiz_state()
    
    # Display quiz settings and topic selection
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if not st.session_state.quiz_questions:
            st.info("Configure your quiz using the sidebar options.")
            
            # Display topic selection
            st.session_state.selected_topics = display_topic_selector()
            
            # Start quiz button
            if st.button("Start Quiz") and st.session_state.selected_topics:
                # Generate quiz questions
                settings = display_quiz_settings()
                prompt = generate_quiz_prompt(settings, st.session_state.selected_topics)
                
                if prompt:
                    with st.spinner("Generating quiz questions..."):
                        response = model.generate_content(prompt)
                        st.session_state.quiz_questions = parse_quiz_questions(response.text)
                        st.session_state.quiz_settings = settings
                        st.rerun()
            
            elif not st.session_state.selected_topics:
                st.warning("Please select at least one topic to start the quiz.")
        
        # Display quiz in progress
        elif not st.session_state.quiz_complete:
            question = st.session_state.quiz_questions[st.session_state.current_question]
            user_answer = display_question(question, st.session_state.current_question)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Submit Answer", disabled=not user_answer):
                    # Check answer
                    is_correct = user_answer.lower() == question['correct_answer'].lower()
                    
                    # Update score
                    if is_correct:
                        st.session_state.quiz_score += 1
                    
                    # Store user's answer
                    st.session_state.user_answers[str(st.session_state.current_question)] = user_answer
                    
                    # Move to next question or finish quiz
                    if st.session_state.current_question < len(st.session_state.quiz_questions) - 1:
                        st.session_state.current_question += 1
                        st.rerun()
                    else:
                        st.session_state.quiz_complete = True
                        st.rerun()
            
            with col2:
                if st.session_state.current_question > 0:
                    if st.button("Previous Question"):
                        st.session_state.current_question -= 1
                        st.rerun()
        
        # Display results
        else:
            display_results()
    
    # Display quiz info in sidebar
    with col2:
        if st.session_state.quiz_questions and not st.session_state.quiz_complete:
            st.subheader("Quiz Progress")
            progress = (st.session_state.current_question / len(st.session_state.quiz_questions))
            st.progress(progress)
            st.write(f"Question {st.session_state.current_question + 1} of {len(st.session_state.quiz_questions)}")
            st.write(f"Score: {st.session_state.quiz_score}")
            
            # Navigation buttons
            st.subheader("Navigation")
            for i in range(len(st.session_state.quiz_questions)):
                status = "✅" if str(i) in st.session_state.user_answers else ""
                if st.button(f"Q{i+1} {status}", key=f"nav_{i}"):
                    st.session_state.current_question = i
                    st.rerun()

if __name__ == "__main__":
    model, _ = setup_gemini()
    display_quiz_interface(model)