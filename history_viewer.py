import streamlit as st
from ncc_utils import (
    read_history,
    clear_history
)

def show_history_viewer_full():
    try:
        st.markdown("""
        <style>
        .history-entry {
            border: 1px solid #4A4A4A;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 12px;
            background-color: #1E1E1E;
        }
        .history-entry-light {
            border: 1.5px solid #6366F1;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 12px;
            background-color: #F9F9F9;
            color: #222 !important;
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
        entry_class = "history-entry" if st.session_state.theme_mode == "Dark" else "history-entry-light"
        history_tabs = st.tabs(["💬 Chat History", "📝 Quiz History"])
        with history_tabs[0]:
            st.subheader("Recent Chat Interactions")
            chat_history_data = read_history("chat")
            col1, col2 = st.columns([3,1])
            with col1:
                if st.button(
                    "🧹 Clear Chat History",
                    key="clear_chat_button",
                    help="Delete all saved chat messages",
                    use_container_width=True
                ):
                    st.session_state.confirm_clear_chat = True
            if st.session_state.get("confirm_clear_chat", False):
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("Yes, Clear Chat History", key="confirm_yes_chat_hist"):
                        clear_history("chat")
                        st.session_state.confirm_clear_chat = False
                with col_no:
                    if st.button("No, Keep Chat History", key="confirm_no_chat_hist"):
                        st.session_state.confirm_clear_chat = False
            if chat_history_data:
                for i, entry in enumerate(reversed(chat_history_data)):
                    timestamp = entry.get("timestamp", "Unknown time")
                    prompt = entry.get("prompt", "No prompt text")
                    response = entry.get("response", "No response text")
                    with st.expander(f"[{timestamp}] User: {prompt[:100]}..."):
                        st.markdown(f"**User:** {prompt}")
                        st.markdown(f"**Assistant:** {response}")
            with col2:
                st.download_button(
                    "⬇️ Download History",
                    read_history("chat_transcript"),
                    "chat_history.txt",
                    key="download_chat_hist_main",
                    help="Save a copy of your chat history to your computer"
                )
        with history_tabs[1]:
            st.subheader("Recent Quiz Attempts")
            quiz_history_data = read_history("quiz")
            if st.button(
                "🧹 Clear Quiz History",
                key="clear_quiz_button",
                help="Delete all saved quiz attempts",
                use_container_width=True
            ):
                st.session_state.confirm_clear_quiz = True
            st.download_button(
                "⬇️ Download Quiz History",
                read_history("quiz_log"),
                "quiz_log.json",
                key="download_quiz_hist_main",
                help="Save a copy of your quiz history to your computer"
            )
            if st.session_state.get("confirm_clear_quiz", False):
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Yes, Clear Quiz History", key="confirm_yes_quiz_hist"):
                        clear_history("quiz")
                        st.session_state.confirm_clear_quiz = False
                with col2:
                    if st.button("No, Keep Quiz History", key="confirm_no_quiz"):
                        st.session_state.confirm_clear_quiz = False
            if quiz_history_data:
                for i, quiz_log_entry in enumerate(reversed(quiz_history_data)):
                    timestamp = quiz_log_entry.get("timestamp", "Unknown time")
                    topic = quiz_log_entry.get("topic", "Unknown Topic")
                    difficulty = quiz_log_entry.get("difficulty", "N/A")
                    questions = quiz_log_entry.get("questions", [])
                    expander_title = f"[{timestamp}] Quiz on {topic} ({difficulty}, {len(questions)} Qs)"
                    with st.expander(expander_title):
                        if questions:
                            for q_idx, q_data in enumerate(questions):
                                st.markdown(f"**Q{q_idx + 1}:** {q_data.get('question', 'N/A')}")
                                options = q_data.get('options', {})
                                for opt_key, opt_text in options.items():
                                    st.markdown(f"- {opt_key}) {opt_text}")
                                st.markdown(f"**Correct Answer:** {q_data.get('answer', 'N/A')}")
                                st.markdown(f"**Explanation:** {q_data.get('explanation', 'No explanation provided.')}")
                                if q_idx < len(questions) - 1:
                                    st.markdown("---")
    except Exception:
        pass  # All st.error and debug messages removed for production.
