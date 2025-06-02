import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

def display_progress_dashboard(ss):
    st.header("📊 Progress Dashboard")

    if not ss.get("quiz_score_history"):
        st.info("No quiz data yet. Take a quiz to see your progress here.")
        return

    score_history = ss.quiz_score_history
    quiz_numbers = list(range(1, len(score_history) + 1))

    # Score Chart
    st.subheader("📈 Score Over Time")
    df = pd.DataFrame({
        'Quiz': quiz_numbers,
        'Score (%)': score_history
    })
    st.line_chart(df.set_index('Quiz'))

    # Difficulty Trend (based on score)
    def get_difficulty(score):
        if score < 50:
            return "Easy"
        elif score < 80:
            return "Medium"
        else:
            return "Hard"

    difficulty_trend = [get_difficulty(score) for score in score_history]
    difficulty_counts = pd.Series(difficulty_trend).value_counts()

    st.subheader("📶 Difficulty Level Distribution")
    st.bar_chart(difficulty_counts)

    # Stats Summary
    st.subheader("📋 Summary")
    st.markdown(f"**Total Quizzes Taken:** {len(score_history)}")
    st.markdown(f"**Average Score:** {round(sum(score_history) / len(score_history), 2)}%")
    st.markdown(f"**Best Score:** {max(score_history)}%")
    st.markdown(f"**Latest Difficulty:** {ss.get('current_quiz_difficulty', 'Unknown')}")

    # Future: Topic analysis (stub)
    st.subheader("📚 Topic Performance (Coming Soon)")
    st.info("Topic-wise performance tracking will be added once quiz topics are stored per session.")
