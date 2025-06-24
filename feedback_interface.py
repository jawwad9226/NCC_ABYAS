import streamlit as st
import time

def show_feedback_section():
    """Display a user feedback and error reporting section in the sidebar, with image upload."""
    with st.sidebar.expander("💬 Feedback & Error Reporting", expanded=True):
        feedback = st.text_area("Your feedback or error report", key="feedback_text")
        uploaded_files = st.file_uploader("Attach images/screenshots (optional)", type=["png", "jpg", "jpeg", "gif"], accept_multiple_files=True, key="feedback_files")
        if st.button("Submit Feedback", key="submit_feedback_btn"):
            if feedback.strip() or uploaded_files:
                # Save feedback to a file or send to backend (here: append to local file)
                with open("data/user_feedback.txt", "a") as f:
                    import time
                    f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ")
                    f.write(feedback.strip() + "\n")
                    if uploaded_files:
                        f.write(f"Attachments: {[file.name for file in uploaded_files]}\n")
                    f.write("---\n")
                # Save images
                for file in uploaded_files:
                    file_path = f"data/feedback_{int(time.time())}_{file.name}"
                    with open(file_path, "wb") as out:
                        out.write(file.getbuffer())
                st.session_state["feedback_text"] = ""
            else:
                from utils.logging_utils import log_warning
                log_warning("Feedback submission attempted with empty text and no files.")
