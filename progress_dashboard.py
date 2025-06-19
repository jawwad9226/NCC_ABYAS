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
    """Display and manage the user's learning progress dashboard."""
    
    # Developer preview toggle with clear label
    if st.checkbox(
        "Show Dashboard Preview",
        key="dev_dashboard_preview",
        help="View example charts and statistics (for development)",
        value=False,
        label_visibility="visible"
    ):
        st.subheader("Example: Quiz Performance Trends")
        try:
            import pandas as pd
            import numpy as np

            # Visualization controls with proper labels
            chart_type = st.selectbox(
                "Chart Type",
                ["Line Chart", "Bar Chart", "Area Chart"],
                key="chart_type_select",
                help="Choose how to visualize your quiz scores",
                label_visibility="visible"
            )

            time_range = st.selectbox(
                "Time Period",
                ["Last Week", "Last Month", "Last 3 Months", "All Time"],
                key="time_range_select",
                help="Select the time period to analyze",
                label_visibility="visible"
            )

            # Sample data generation for preview
            now = pd.Timestamp.now()
            date_range = pd.date_range(end=now, periods=30)
            sample_data = {
                "Timestamp": date_range,
                "Score (%)": np.random.randint(50, 100, size=len(date_range)),
                "Difficulty": np.random.choice(["Easy", "Medium", "Hard"], size=len(date_range)),
                "Topic": np.random.choice(["Math", "Science", "History"], size=len(date_range))
            }
            sample_df = pd.DataFrame(sample_data)

            # Filtering sample data based on time range selection
            if time_range == "Last Week":
                filtered_df = sample_df[sample_df['Timestamp'] >= now - pd.Timedelta(weeks=1)]
            elif time_range == "Last Month":
                filtered_df = sample_df[sample_df['Timestamp'] >= now - pd.Timedelta(days=30)]
            elif time_range == "Last 3 Months":
                filtered_df = sample_df[sample_df['Timestamp'] >= now - pd.Timedelta(days=90)]
            else:  # "All Time"
                filtered_df = sample_df

            # Chart type selection
            if chart_type == "Line Chart":
                st.line_chart(filtered_df.set_index('Timestamp')[['Score (%)']])
            elif chart_type == "Bar Chart":
                st.bar_chart(filtered_df.set_index('Timestamp')[['Score (%)']])
            else:  # "Area Chart"
                st.area_chart(filtered_df.set_index('Timestamp')[['Score (%)']])

            st.success("This is how your performance trends could look like!")

        except Exception as e:
            st.error(f"Error displaying preview: {e}")
            st.stop()

    # Set up the dataframe for visualization
    try:
        df = pd.DataFrame([json.loads(line) for line in quiz_history_raw_string.strip().splitlines() if line.strip()])
        if not df.empty:
            df['Timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('Timestamp')
    except (json.JSONDecodeError, pd.errors.EmptyDataError):
        df = pd.DataFrame()  # Create empty DataFrame if no valid data

    if df.empty:
        st.info("No quiz data yet. Take a quiz to see your progress here.")
        return

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
