import streamlit as st
import pandas as pd
from datetime import datetime

def display_progress_dashboard(ss):
    st.header("📊 Progress Dashboard")

    # If no quiz history exists
    if not ss.get("quiz_score_history"):
        st.info("No quiz data yet. Take a quiz to see your progress here.")
        return

    # Prepare data
    score_history = ss.quiz_score_history
    quiz_numbers = list(range(1, len(score_history) + 1))

    # Optional: timestamps if stored
    timestamps = ss.get("quiz_timestamps", None)
    
    # Create DataFrame for scores
    df = pd.DataFrame({
        'Quiz': quiz_numbers,
        'Score (%)': score_history
    })

    # If timestamps exist, add them to the DataFrame
    if timestamps and len(timestamps) == len(score_history):
        df['Date'] = [ts.strftime('%Y-%m-%d') for ts in timestamps]
    
    # ─── Score Over Time ─────────────────────────────────────
    st.subheader("📈 Score Over Time")
    # Plot a line chart of Quiz Number vs. Score
    st.line_chart(df.set_index('Quiz')[['Score (%)']])

    # ─── Difficulty Trend ────────────────────────────────────
    def get_difficulty(score):
        if score < 50:
            return "Easy"
        elif score < 80:
            return "Medium"
        else:
            return "Hard"

    difficulty_trend = [get_difficulty(score) for score in score_history]
    diff_counts = pd.Series(difficulty_trend).value_counts().sort_index()

    st.subheader("📶 Difficulty Level Distribution")
    # Plot a bar chart of difficulty counts
    st.bar_chart(diff_counts)

    # ─── Stats Summary ────────────────────────────────────────
    st.subheader("📋 Summary")
    total = len(score_history)
    average = round(sum(score_history) / total, 2)
    best = max(score_history)
    latest_diff = ss.get('current_quiz_difficulty', 'Unknown')

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Total Quizzes Taken:** {total}")
    with col2:
        st.markdown(f"**Average Score:** {average}%")
    with col3:
        st.markdown(f"**Best Score:** {best}%")
    st.markdown(f"**Latest Difficulty:** {latest_diff}")

    # ─── Download CSV of Progress ─────────────────────────────
    csv = df.to_csv(index=False)
    st.download_button("⬇️ Download Progress CSV", csv, "quiz_progress.csv")

    # ─── Topic‐Wise Performance ──────────────────────────────
    if ss.get('quiz_topic_history'):
        topic_counts = pd.Series(ss.quiz_topic_history).value_counts()
        st.subheader("📑 Quizzes by Topic")
        st.bar_chart(topic_counts)
    else:
        st.subheader("📚 Topic Performance (Coming Soon)")
        st.info("Topic-wise performance tracking will be added once quiz topics are stored per session.")

    # ─── Date Filter (if timestamps exist) ───────────────────
    if timestamps:
        st.subheader("📆 Quiz Timeline")
        date_df = df.copy()
        date_df['Date'] = pd.to_datetime(date_df['Date'])
        date_filter = st.date_input(
            "Filter by Date Range",
            [date_df['Date'].min(), date_df['Date'].max()]
        )
        start_date, end_date = date_filter
        mask = (date_df['Date'] >= pd.to_datetime(start_date)) & (date_df['Date'] <= pd.to_datetime(end_date))
        filtered = date_df.loc[mask]
        if not filtered.empty:
            st.line_chart(filtered.set_index('Quiz')[['Score (%)']])
        else:
            st.info("No quizzes in the selected date range.")

    # ─── Placeholder for Future Metrics ───────────────────────
    st.subheader("🔧 Additional Insights")
    st.info("More analytics (e.g., topic weaknesses, pace of improvement) will be available soon.")
