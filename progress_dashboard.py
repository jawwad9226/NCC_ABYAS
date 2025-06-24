import streamlit as st
from datetime import datetime
import json
try:
    import pandas as pd
except ImportError:
    st.error("Pandas library is not installed. This dashboard cannot function without it. Please install it: `pip install pandas`")
    st.stop()

try:
    import numpy as np
except ImportError:
    st.warning("NumPy library is not installed. Some calculations might be affected if not pulled in by Pandas.")

from sync_manager import queue_for_sync

def display_progress_dashboard(session_state, quiz_history_raw_string: str):
    """Modern, bug-free progress dashboard with improved visuals and error handling."""
    st.markdown("""
        <style>
        .dashboard-header {
            font-size: 2.2rem;
            font-weight: 700;
            color: #4F46E5;
            margin-bottom: 0.5rem;
        }
        .dashboard-sub {
            color: #6366F1;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }
        .stMetric {
            background: linear-gradient(135deg, #6366F1 10%, #A5B4FC 100%);
            border-radius: 1rem;
            color: #fff !important;
            box-shadow: 0 2px 8px rgba(99,102,241,0.08);
            padding: 1.2rem 0.5rem 1.2rem 0.5rem;
        }
        /* Light mode overrides for info/warning/metric/download */
        body[data-theme="light"] .stAlert, 
        body[data-theme="light"] .stDownloadButton button, 
        body[data-theme="light"] .stButton button, 
        body[data-theme="light"] .stMetric {
            color: #222 !important;
            background: #f3f4f6 !important;
            border: 1.5px solid #6366F1 !important;
        }
        body[data-theme="light"] .stAlert {
            background: #fef9c3 !important;
            border-color: #fde047 !important;
        }
        body[data-theme="light"] .stAlert[data-testid="stInfo"] {
            background: #e0e7ff !important;
            border-color: #6366F1 !important;
        }
        body[data-theme="light"] .stAlert[data-testid="stWarning"] {
            background: #fef3c7 !important;
            border-color: #f59e42 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="dashboard-header">📊 Progress Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-sub">Track your quiz performance, trends, and learning progress over time.</div>', unsafe_allow_html=True)

    # Load quiz history
    try:
        history_list = json.loads(quiz_history_raw_string)
        df = pd.DataFrame(history_list)
        if not df.empty:
            df['Timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('Timestamp')
            df['Score (%)'] = df['score']
    except Exception:
        df = pd.DataFrame()

    if df.empty:
        return

    # --- Summary Cards ---
    total_quizzes = len(df)
    average_score_val = df['Score (%)'].mean() if not df.empty else 0
    best_score_val = df['Score (%)'].max() if not df.empty else 0
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Quizzes", value=total_quizzes)
    with col2:
        st.metric(label="Average Score", value=f"{average_score_val:.2f}%")
    with col3:
        st.metric(label="Best Score", value=f"{best_score_val:.2f}%")

    st.markdown("---")

    # --- Score Over Time ---
    st.subheader("📈 Quiz Score Over Time")
    st.line_chart(df.set_index('Timestamp')[['Score (%)']])

    # --- Difficulty Distribution ---
    st.subheader("🏋️ Difficulty Level Distribution")
    if 'Difficulty' in df.columns and not df['Difficulty'].isnull().all():
        difficulty_counts = df['Difficulty'].value_counts().sort_index()
        st.bar_chart(difficulty_counts)

    # --- Topic-Wise Performance ---
    st.subheader("📚 Topic-Wise Performance")
    if 'Topic' in df.columns and not df['Topic'].isnull().all():
        avg_score_per_topic = df.groupby('Topic')['Score (%)'].mean().sort_values(ascending=False)
        st.write("Average Score per Topic (%):")
        st.bar_chart(avg_score_per_topic)
        quizzes_per_topic = df['Topic'].value_counts()
        st.write("Number of Quizzes per Topic:")
        st.bar_chart(quizzes_per_topic)

    # --- Date Filter ---
    st.subheader("📅 Quiz Timeline (Filter by Date)")
    if 'Timestamp' in df.columns and not df['Timestamp'].dropna().empty:
        min_date = df['Timestamp'].min().date()
        max_date = df['Timestamp'].max().date()
        date_filter = st.date_input(
            "Filter by Date Range",
            value=[min_date, max_date],
            min_value=min_date,
            max_value=max_date,
            key="date_filter_range"
        )
        if len(date_filter) == 2:
            start_date_dt, end_date_dt = pd.to_datetime(date_filter[0]), pd.to_datetime(date_filter[1])
            mask = (df['Timestamp'] >= start_date_dt) & (df['Timestamp'] <= end_date_dt + pd.Timedelta(days=1) - pd.Timedelta(seconds=1))
            filtered_df = df.loc[mask]
            if not filtered_df.empty:
                st.line_chart(filtered_df.set_index('Timestamp')[['Score (%)']])
            else:
                st.info("No quizzes in the selected date range.")
        else:
            st.info("Please select a valid date range (start and end date).")
    else:
        st.info("Not enough data to display quiz timeline.")

    # --- Download CSV ---
    if 'Score (%)' in df.columns:
        csv = df.to_csv(index=False)
        st.download_button("⬇️ Download Progress CSV", csv, "quiz_progress.csv", key="download_progress_csv")
    else:
        st.button("⬇️ Download Progress CSV", disabled=True, key="download_progress_csv_disabled")

    # After progress summary update, queue for sync
    progress_summary = {
        # ...fill with actual summary fields...
    }
    queue_for_sync(progress_summary, "progress_summary")
