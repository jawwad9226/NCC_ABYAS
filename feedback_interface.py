import streamlit as st
import time

def show_feedback_section():
    """Display a user feedback and error reporting section in the sidebar, with image upload."""
    with st.sidebar.expander("💬 Feedback & Error Reporting", expanded=True):
        feedback = st.text_area("Your feedback or error report", key="feedback_text")
        uploaded_files = st.file_uploader("Attach images/screenshots (optional)", type=["png", "jpg", "jpeg", "gif"], accept_multiple_files=True, key="feedback_files")
        max_size_mb = 5
        oversize_files = [file for file in uploaded_files if file.size > max_size_mb * 1024 * 1024]
        if oversize_files:
            st.error(f"Each image must be less than {max_size_mb} MB. Please remove or resize: {[file.name for file in oversize_files]}")
        if st.button("Submit Feedback", key="submit_feedback_btn"):
            if oversize_files:
                st.error(f"Cannot submit. Please remove or resize files over {max_size_mb} MB.")
            elif feedback.strip() or uploaded_files:
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
