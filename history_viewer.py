import streamlit as st
from ncc_utils import (
    read_history,
    clear_history
)
import logging

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
            border: 1px solid #DCDCDC;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 12px;
            background-color: #F9F9F9;
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
                st.warning("Are you sure you want to clear the chat history? This cannot be undone.")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("Yes, Clear Chat History", key="confirm_yes_chat_hist"):
                        clear_history("chat")
                        st.session_state.confirm_clear_chat = False
                        st.success("Chat history cleared!")
                        st.rerun()
                with col_no:
                    if st.button("No, Keep Chat History", key="confirm_no_chat_hist"):
                        st.session_state.confirm_clear_chat = False
                        st.info("Chat history not cleared.")
            if chat_history_data:
                for i, entry in enumerate(reversed(chat_history_data)):
                    timestamp = entry.get("timestamp", "Unknown time")
                    prompt = entry.get("prompt", "No prompt text")
                    response = entry.get("response", "No response text")
                    with st.expander(f"[{timestamp}] User: {prompt[:100]}..."):
                        st.markdown(f"**User:** {prompt}")
                        st.markdown(f"**Assistant:** {response}")
            else:
                st.info("No chat history found yet. Start a conversation in the Chat Assistant tab.")
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
                st.warning("Are you sure you want to clear the quiz history? This cannot be undone.")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Yes, Clear Quiz History", key="confirm_yes_quiz_hist"):
                        clear_history("quiz")
                        st.session_state.confirm_clear_quiz = False
                        st.success("Quiz history cleared!")
                        st.rerun()
                with col2:
                    if st.button("No, Keep Quiz History", key="confirm_no_quiz"):
                        st.session_state.confirm_clear_quiz = False
                        st.info("Quiz history not cleared.")
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
            else:
                st.info("No quiz history found yet. Take a quiz to start.")
    except Exception as e:
        logging.exception("History viewer error:")
        st.error(f"An error occurred in the history viewer: {e}")
