import streamlit as st
import time
from utils.logging_utils import log_info, log_warning, log_error

def show_feedback_section():
    """Display a user feedback and error reporting section in the sidebar."""
    with st.sidebar.expander("💬 Feedback & Error Reporting", expanded=False):
        st.write("Help us improve! Share your feedback or report an issue.")
        feedback = st.text_area("Your feedback or error report", key="feedback_text")
        if st.button("Submit Feedback", key="submit_feedback_btn"):
            if feedback.strip():
                # Save feedback to a file or send to backend (here: append to local file)
                with open("data/user_feedback.txt", "a") as f:
                    f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ")
                    f.write(feedback.strip() + "\n---\n")
                st.success("Thank you for your feedback!")
                log_info(f"User feedback submitted: {feedback.strip()[:100]}")
                st.session_state["feedback_text"] = ""
            else:
                st.warning("Please enter your feedback before submitting.")
                log_warning("Feedback submission attempted with empty text.")
