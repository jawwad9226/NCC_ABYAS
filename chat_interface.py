import streamlit as st
from datetime import datetime
import time  # For simulating cooldown display
import os
from pathlib import Path
import uuid

# Import from utils
from utils import (
    read_history,
    append_message,
    clear_history,
    setup_gemini,
    get_ncc_response,
    Config
)

# Initialize Gemini model
model, model_error = setup_gemini()

def chat_interface():
    """Main chat interface function with proper widget key management"""
    # Initialize session state for widget keys if they don't exist
    if "widget_keys" not in st.session_state:
        st.session_state.widget_keys = {
            "clear_chat": str(uuid.uuid4()),
            "confirm_yes": str(uuid.uuid4()),
            "confirm_no": str(uuid.uuid4()),
            "chat_input": str(uuid.uuid4())
        }
    
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
                # Use a UUID to guarantee uniqueness
                # Use a stable key based on question content but unique per session
                safe_key = f"sample_q_{i}_{q[:20]}_{st.session_state.widget_keys.get('clear_chat', '')}"
                if st.button(q, key=safe_key):
                    # Append user message with timestamp
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state.messages.append({"role": "user", "content": f"{q} *(Sent at {timestamp})*"})
                    append_message("chat", f"User: {q} *(Sent at {timestamp})*")
                    st.rerun()

    # --- Clear Chat Confirmation ---
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        # Add uuid to the key to ensure it's unique on reruns
        clear_chat_key = f"clear_chat_btn_{st.session_state.widget_keys['clear_chat']}"
        if st.button("🧹 Clear Chat", key=clear_chat_key, help="Erase all chat history from this session and disk."):
            st.session_state.confirm_clear = True

    if st.session_state.confirm_clear:
        st.warning("Are you sure you want to clear the chat history? This cannot be undone.")
        col_yes, col_no = st.columns(2)
        with col_yes:
            if st.button("Yes, clear", key=f"confirm_yes_{st.session_state.widget_keys['confirm_yes']}"):
                st.session_state.messages = []
                clear_history("chat") # Clear on-disk history
                st.session_state.confirm_clear = False
                st.success("Chat history cleared!")
                st.rerun()
        with col_no:
            if st.button("No, keep chat", key=f"confirm_no_{st.session_state.widget_keys['confirm_no']}"):
                st.session_state.confirm_clear = False
                st.info("Chat clearing cancelled.")
                st.rerun()
    with col2:
        with st.expander("📜 View Chat History", expanded=True):
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
                key=f"download_chat_history_btn_{uuid.uuid4()}",
                help="Download the complete chat history as a text file."
            )
        else:
            st.button("⬇️ Download Full History", key=f"download_chat_history_disabled_btn_{uuid.uuid4()}", disabled=True, help="No chat history to download yet.")


    st.markdown("---")

    # Display chat messages from session state
    for message in st.session_state.messages:
        with st.chat_message(message["role"]): # Streamlit automatically handles bubble styling based on role
            st.write(message["content"])

    # Chat input with unique key
    chat_input_key = f"chat_input_{st.session_state.widget_keys['chat_input']}"
    if prompt := st.chat_input("Ask me anything about NCC...", key=chat_input_key):
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
                # Get response from the Gemini model
                response = get_ncc_response(model, model_error, prompt)

                # Show error if model is not responding or returns error
                if not response or response.startswith("Error"):
                    st.error(f"Assistant error: {response}")
                elif "Please wait" in response and "seconds" in response:
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
                    append_message("assistant", response)

        # Rerun to update chat display
        st.rerun()

    # Display cooldown timer if active (can be placed near the input field)
    if st.session_state.cooldown_active and st.session_state.cooldown_time_remaining > 0:
        st.info(f"Please wait {st.session_state.cooldown_time_remaining} seconds before sending another message.")
        # You could also disable the input here, but Streamlit's chat_input doesn't directly support `disabled`
        # A more advanced approach would be to use a regular text_input and a button, and control their disabled state.

# Only run chat_interface() if this file is executed directly
if __name__ == "__main__":
    chat_interface()
