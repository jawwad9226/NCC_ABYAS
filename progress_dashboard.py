import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta # For date filtering

# Note: matplotlib.pyplot is no longer imported as it's not used.

def progress_dashboard():
    st.title("📊 Your NCC Progress Dashboard")

    # Alias st.session_state for brevity
    ss = st.session_state

    # Initialize quiz_score_history if it doesn't exist (though quiz_interface should handle this)
    if "quiz_score_history" not in ss:
        ss.quiz_score_history = []

    # Check if there's any quiz data
    if not ss.quiz_score_history:
        st.info("No quiz data yet. Take some quizzes to see your progress here!")
        return # Exit the function if no data

    # Convert history to DataFrame for easier manipulation
    df = pd.DataFrame(ss.quiz_score_history)
    df["timestamp"] = pd.to_datetime(df["timestamp"]) # Convert timestamp string to datetime objects

    st.header("Overall Performance")

    # --- Date Filtering ---
    time_filter_option = st.selectbox(
        "Show data for:",
        ["All Time", "Last 7 Days", "Last 30 Days", "Custom Range"],
        key="time_filter_dashboard"
    )

    filtered_df = df.copy()
    if time_filter_option == "Last 7 Days":
        seven_days_ago = datetime.now() - timedelta(days=7)
        filtered_df = df[df["timestamp"] >= seven_days_ago]
    elif time_filter_option == "Last 30 Days":
        thirty_days_ago = datetime.now() - timedelta(days=30)
        filtered_df = df[df["timestamp"] >= thirty_days_ago]
    elif time_filter_option == "Custom Range":
        col_start, col_end = st.columns(2)
        with col_start:
            start_date = st.date_input("Start date", datetime.now() - timedelta(days=30))
        with col_end:
            end_date = st.date_input("End date", datetime.now())
        filtered_df = df[(df["timestamp"].dt.date >= start_date) & (df["timestamp"].dt.date <= end_date)]

    if filtered_df.empty:
        st.warning(f"No quiz data available for the selected '{time_filter_option}' period.")
        return # Exit if no data after filtering

    # --- Average Score Gauge / Metric ---
    avg_score = filtered_df["score"].mean()
    total_quizzes = len(filtered_df)

    # Calculate delta for average score (compare to previous average if enough data)
    delta_value = None
    if total_quizzes > 1:
        previous_avg = filtered_df["score"].iloc[:-1].mean() # Average of all except the latest quiz
        delta_value = avg_score - previous_avg

    st.metric(
        label="🏆 Average Score",
        value=f"{avg_score:.2f}%",
        delta=f"{delta_value:.2f}%" if delta_value is not None else None,
        help="Your average quiz score. Delta shows change from previous average."
    )
    st.write(f"Completed **{total_quizzes}** quizzes in this period.")

    st.markdown("---")

    # --- Scores Over Time (Altair Chart) ---
    st.subheader("📈 Scores Over Time by Difficulty")

    # Ensure 'Quiz' column for sequential display
    filtered_df['Quiz'] = filtered_df.index + 1 # Use DataFrame index as quiz number

    chart = alt.Chart(filtered_df).mark_line(point=True).encode(
        x=alt.X("Quiz:O", title="Quiz Attempt Number"), # :O for ordinal to treat as discrete categories
        y=alt.Y("score", title="Score (%)", scale=alt.Scale(domain=[0, 100])),
        color=alt.Color("difficulty:N", title="Difficulty"), # :N for nominal
        tooltip=["Quiz", "timestamp", "score", "difficulty", "total_questions", "topic"]
    ).properties(
        title="Quiz Scores Over Time"
    ).interactive() # Enable zooming and panning

    st.altair_chart(chart, use_container_width=True)

    st.markdown("---")

    # --- Quizzes by Topic (Bar Chart) ---
    st.subheader("📑 Quizzes by Topic")
    if "topic" in filtered_df.columns and not filtered_df["topic"].isnull().all():
        topic_counts = filtered_df["topic"].value_counts().reset_index()
        topic_counts.columns = ["Topic", "Count"] # Rename columns for clarity

        topic_chart = alt.Chart(topic_counts).mark_bar().encode(
            x=alt.X("Count", title="Number of Quizzes"),
            y=alt.Y("Topic", sort="-x", title="Topic"), # Sort by count descending
            tooltip=["Topic", "Count"]
        ).properties(
            title="Number of Quizzes per Topic"
        )
        st.altair_chart(topic_chart, use_container_width=True)
    else:
        st.info("No topic data available for analysis in this period.")


    st.markdown("---")

    # --- Export Dashboard Data ---
    st.subheader("📊 Export Data")
    if not filtered_df.empty:
        csv_data = filtered_df.to_csv(index=False)
        st.download_button(
            label="⬇️ Download Progress Data (CSV)",
            data=csv_data,
            file_name="ncc_quiz_progress.csv",
            mime="text/csv",
            help="Download your quiz score history as a CSV file."
        )
    else:
        st.button("⬇️ Download Progress Data (CSV)", disabled=True, help="No data to download.")

