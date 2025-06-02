import streamlit as st
from datetime import datetime
import time  # For simulating cooldown display
import os
from pathlib import Path

# Import from utils
from utils import (
    get_response_func,
    read_history,
    append_message,
    clear_history,
    setup_gemini,
    Config
)

# Initialize Gemini model
model, model_error = setup_gemini()

def chat_interface():
    st.title("🤖 NCC AI Assistant Chat")

    # Initialize session state for messages and confirmation dialog
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "confirm_clear" not in st.session_state:
        st.session_state.confirm_clear = False
    if "cooldown_active" not in st.session_state:
        st.session_state.cooldown_active = False
    if "cooldown_time_remaining" not in st.session_state:
        st.session_state.cooldown_time_remaining = 0

    # --- Sample Questions ---
    with st.expander("💡 Sample Questions"):
        st.write("Click a question to ask the assistant directly:")
        sample_questions = [
            "What is the NCC?",
            "What are the benefits of joining NCC?",
            "Tell me about the NCC syllabus.",
            "What is drill in NCC?",
            "How can I join the NCC?",
            "What is weapon training in NCC?"
        ]
        cols = st.columns(3)
        for i, q in enumerate(sample_questions):
            with cols[i % 3]:
                if st.button(q, key=f"sample_q_{i}"):
                    # Append user message with timestamp
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state.messages.append({"role": "user", "content": f"{q} *(Sent at {timestamp})*"})
                    append_message("chat", f"User: {q} *(Sent at {timestamp})*")
                    st.rerun()

    # --- Clear Chat Confirmation ---
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("🧹 Clear Chat", help="Erase all chat history from this session and disk."):
            st.session_state.confirm_clear = True

    if st.session_state.confirm_clear:
        st.warning("Are you sure you want to clear the chat history? This cannot be undone.")
        col_yes, col_no = st.columns(2)
        with col_yes:
            if st.button("Yes, clear", key="confirm_yes"):
                st.session_state.messages = []
                clear_history("chat") # Clear on-disk history
                st.session_state.confirm_clear = False
                st.success("Chat history cleared!")
                st.rerun()
        with col_no:
            if st.button("No, keep chat", key="confirm_no"):
                st.session_state.confirm_clear = False
                st.info("Chat clearing cancelled.")
                st.rerun()
    with col2:
        with st.expander("📜 View Chat History", expanded=False, help="Show the last 50 chat messages from disk."):
            history_lines = read_history("chat").splitlines()
            if history_lines:
                for line in history_lines[-50:]:  # Show only last 50 lines
                    st.text(line) # Using st.text to preserve raw line formatting
                if len(history_lines) > 50:
                    st.info(f"...and {len(history_lines)-50} more lines (view full history by downloading).")
            else:
                st.info("No chat history found yet.")
    with col3:
        # Download Full History
        history_content = read_history("chat")
        if history_content:
            st.download_button(
                label="⬇️ Download Full History",
                data=history_content,
                file_name="chat_history.txt",
                mime="text/plain",
                help="Download the complete chat history as a text file."
            )
        else:
            st.button("⬇️ Download Full History", disabled=True, help="No chat history to download yet.")


    st.markdown("---")

    # Display chat messages from session state
    for message in st.session_state.messages:
        with st.chat_message(message["role"]): # Streamlit automatically handles bubble styling based on role
            st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me anything about NCC..."):
        # Prompt Sanitization
        if prompt.strip() == "":
            st.warning("Please enter a valid question.")
            # Clear the chat input if it was just whitespace
            st.stop() # Stop execution to prevent further processing of empty prompt

        # Append user message with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.messages.append({"role": "user", "content": f"{prompt} *(Sent at {timestamp})*"})
        append_message("chat", f"User: {prompt} *(Sent at {timestamp})*")

        # Display user message immediately
        with st.chat_message("user"):
            st.write(f"{prompt} *(Sent at {timestamp})*")

        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_response_func("chat", prompt)

                # Check for cooldown message
                if "Please wait" in response and "seconds" in response:
                    st.session_state.cooldown_active = True
                    # Attempt to parse remaining time
                    try:
                        parts = response.split(" ")
                        time_index = parts.index("wait") + 1
                        st.session_state.cooldown_time_remaining = int(parts[time_index])
                    except (ValueError, IndexError):
                        st.session_state.cooldown_time_remaining = 0 # Fallback
                    st.warning(response) # Display the cooldown message
                    # Do not append to messages or history if it's a cooldown message
                    st.session_state.messages.pop() # Remove the last user message if it was a cooldown
                    append_message("chat", f"Assistant: {response} *(Cooldown)*")
                else:
                    st.session_state.cooldown_active = False
                    st.session_state.cooldown_time_remaining = 0
                    st.write(f"{response} *(Answered at {datetime.now().strftime('%H:%M:%S')})*")
                    st.session_state.messages.append({"role": "assistant", "content": f"{response} *(Answered at {datetime.now().strftime('%H:%M:%S')})*"})
                    append_message("chat", f"Assistant: {response} *(Answered at {datetime.now().strftime('%H:%M:%S')})*")

        # Rerun to update chat display
        st.rerun()

    # Display cooldown timer if active (can be placed near the input field)
    if st.session_state.cooldown_active and st.session_state.cooldown_time_remaining > 0:
        st.info(f"Please wait {st.session_state.cooldown_time_remaining} seconds before sending another message.")
        # You could also disable the input here, but Streamlit's chat_input doesn't directly support `disabled`
        # A more advanced approach would be to use a regular text_input and a button, and control their disabled state.

chat_interface()
