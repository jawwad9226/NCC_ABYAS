import streamlit as st
from datetime import datetime
import json

try:
    import pandas as pd
except ImportError:
    st.error("Pandas library is not installed. This dashboard cannot function without it. Please install it: `pip install pandas`")
    st.stop()

try:
    import numpy as np # For mean calculation if needed, pandas handles it mostly
except ImportError:
    # Numpy is often a dependency of pandas, but good to check.
    st.warning("NumPy library is not installed. Some calculations might be affected if not pulled in by Pandas.")
    # Not stopping, as pandas might still work for basic operations.

def display_progress_dashboard(session_state, quiz_history_raw_string: str):
    st.header("📊 Progress Dashboard")

    if not quiz_history_raw_string:
        st.info("No quiz data yet. Take a quiz to see your progress here.")
        return

    raw_quiz_entries = []
    malformed_entries = 0
    for line in quiz_history_raw_string.strip().splitlines():
        if line.strip():
            try:
                raw_quiz_entries.append(json.loads(line))
            except json.JSONDecodeError:
                malformed_entries += 1
    
    if malformed_entries > 0:
        st.caption(f"ℹ️ Note: {malformed_entries} history entries could not be parsed and were skipped.")

    # Prepare data: Filter for valid entries and parse timestamps
    processed_data = []
    timestamp_parse_errors = 0
    for i, entry in enumerate(raw_quiz_entries):
        score = entry.get('score_percentage', entry.get('score')) # Check for score_percentage first
        timestamp_str = entry.get('timestamp')
        topic = entry.get('topic', 'Unknown Topic') # Get topic, default if missing
        difficulty = entry.get('difficulty', 'Unknown') # Get difficulty
        if isinstance(score, (int, float)) and timestamp_str:
            try:
                dt_obj = datetime.fromisoformat(timestamp_str)
                processed_data.append({
                    'Quiz': i + 1,
                    'Score (%)': score,
                    'Timestamp': dt_obj,
                    'Date': dt_obj.strftime('%Y-%m-%d %H:%M'), # More precise date
                    'Topic': topic,
                    'Difficulty': difficulty
                })
            except ValueError:
                timestamp_parse_errors +=1
    
    if timestamp_parse_errors > 0:
        st.caption(f"ℹ️ Note: {timestamp_parse_errors} entries had issues parsing timestamps and were skipped.")

    
    if not processed_data:
        st.info("No valid quiz data with scores and timestamps found for the dashboard.")
        return

    df = pd.DataFrame(processed_data)
    df['Timestamp'] = pd.to_datetime(df['Timestamp']) # Ensure Timestamp is datetime dtype

    # ─── Score Over Time ─────────────────────────────────────
    st.subheader("📈 Score Over Time")
    if not df.empty:
        st.line_chart(df.set_index('Timestamp')[['Score (%)']])
    else:
        st.info("Not enough data to plot score over time.")


    # ─── Difficulty Trend (Distribution of difficulties attempted) ────────────────────────────────────
    st.subheader("📶 Difficulty Level Distribution (Quizzes Taken)")
    if not df.empty and 'Difficulty' in df.columns:
        difficulty_counts = df['Difficulty'].value_counts().sort_index()
        if not difficulty_counts.empty:
            st.bar_chart(difficulty_counts)
        else:
            st.info("No difficulty data available.")
    else:
        st.info("No difficulty data available.")


    # ─── Stats Summary ────────────────────────────────────────
    st.subheader("📋 Summary")
    total_quizzes = len(df)
    average_score_val = df['Score (%)'].mean() if not df.empty else 0
    best_score_val = df['Score (%)'].max() if not df.empty else 0
    # latest_recorded_diff = df['Difficulty'].iloc[-1] if not df.empty else "N/A"

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Quizzes Taken", value=total_quizzes)
    with col2:
        st.metric(label="Average Score", value=f"{average_score_val:.2f}%")
    with col3:
        st.metric(label="Best Score", value=f"{best_score_val:.2f}%")

    # ─── Download CSV of Progress ─────────────────────────────
    if not df.empty:
        csv = df.to_csv(index=False)
        st.download_button("⬇️ Download Progress CSV", csv, "quiz_progress.csv", key="download_progress_csv")
    else:
        st.button("⬇️ Download Progress CSV", disabled=True, key="download_progress_csv_disabled")


    # ─── Topic‐Wise Performance ──────────────────────────────
    st.subheader("📚 Topic Performance")
    if not df.empty and 'Topic' in df.columns:
        # Average score per topic
        avg_score_per_topic = df.groupby('Topic')['Score (%)'].mean().sort_values(ascending=False)
        st.write("Average Score per Topic (%):")
        if not avg_score_per_topic.empty:
            st.bar_chart(avg_score_per_topic)
        else:
            st.info("No data for average score per topic.")

        # Number of quizzes per topic
        quizzes_per_topic = df['Topic'].value_counts()
        st.write("Number of Quizzes Taken per Topic:")
        if not quizzes_per_topic.empty:
            st.bar_chart(quizzes_per_topic)
        else:
            st.info("No data for quizzes taken per topic.")
    else:
        st.info("Topic performance data is not available or incomplete.")


    # ─── Date Filter (if timestamps exist) ───────────────────
    st.subheader("📆 Quiz Timeline (Filter by Date)")
    if not df.empty and 'Timestamp' in df.columns and not df['Timestamp'].dropna().empty:
        try:
            min_date = df['Timestamp'].min().date()
            max_date = df['Timestamp'].max().date()
            
            date_filter_values = [min_date, max_date]
            # This check might be redundant if min_date and max_date are derived correctly
            # if min_date > max_date: date_filter_values = [max_date, min_date] 

            date_filter = st.date_input(
                "Filter by Date Range",
                value=date_filter_values,
                min_value=min_date,
                max_value=max_date,
                key="date_filter_range"
            )
            if len(date_filter) == 2:
                start_date_dt, end_date_dt = pd.to_datetime(date_filter[0]), pd.to_datetime(date_filter[1])
                mask = (df['Timestamp'] >= start_date_dt) & (df['Timestamp'] <= end_date_dt + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)) # Inclusive end date
                filtered_df = df.loc[mask]
                if not filtered_df.empty:
                    st.line_chart(filtered_df.set_index('Timestamp')[['Score (%)']])
                else:
                    st.info("No quizzes in the selected date range.")
            else:
                st.info("Please select a valid date range (start and end date).")
        except Exception as e:
            st.warning(f"Could not display date filter or timeline: {e}")
    else:
        st.info("Not enough data to display quiz timeline.")
