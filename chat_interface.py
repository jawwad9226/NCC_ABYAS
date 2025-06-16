import streamlit as st
from datetime import datetime
from itertools import groupby
import time  # For simulating cooldown display
import os
import json
from pathlib import Path
import uuid

# Import from utils
from utils import (
    read_history,
    clear_history,
    setup_gemini,
    get_ncc_response,
    Config,
    _load_json_file  # Import the helper function
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
                    st.session_state.messages.append({"role": "user", "content": q, "timestamp": timestamp})
                    # Saving to file is handled by get_ncc_response -> _save_chat_to_file
                    st.rerun()

    # Initialize chat history tab state if not exists
    if "show_history" not in st.session_state:
        st.session_state.show_history = False
    if "selected_conversation" not in st.session_state:
        st.session_state.selected_conversation = None
    
    # Top bar with actions
    col_actions1, col_actions2, col_spacer = st.columns([1, 1, 2])
    
    with col_actions1:
        if st.button("🕒 View History", key="view_history_btn", use_container_width=True):
            st.session_state.show_history = not st.session_state.show_history
    
    with col_actions2:
        clear_chat_key = f"clear_chat_btn_{st.session_state.widget_keys['clear_chat']}"
        if st.button("🧹", key=clear_chat_key, help="Clear Chat"):
            st.session_state.confirm_clear = True

    # History view or confirmation dialog
    if st.session_state.show_history:
        with st.container():
            st.markdown("### 📜 Chat History")
            # Load and parse chat history from JSON
            history = _load_json_file(Config.LOG_PATHS['chat']['history'], [])
            
            if history:
                # Sort history by timestamp
                history.sort(key=lambda x: x.get('timestamp', ''))
                
                # Group by date
                from itertools import groupby  # This import is fine here as it's just for groupby functionality
                for date, items in groupby(history, key=lambda x: x.get('timestamp', '')[:10]):
                    items = list(items)  # Convert iterator to list
                    with st.expander(f"📅 {date}", expanded=True):
                        for item in items:
                            # Create a clickable conversation preview
                            prompt = item.get('prompt', '')
                            timestamp = item.get('timestamp', '').split('T')[1][:8]  # Extract time HH:MM:SS
                            preview = f"🕒 {timestamp} - {prompt[:50]}..."
                            
                            if st.button(preview, key=f"conv_{item.get('timestamp', '')}"):
                                st.session_state.selected_conversation = item
                                st.rerun()
                
                # Show full conversation if one is selected
                if st.session_state.selected_conversation:
                    st.markdown("### Selected Conversation")
                    with st.chat_message("user"):
                        st.write(st.session_state.selected_conversation['prompt'])
                    with st.chat_message("assistant"):
                        st.write(st.session_state.selected_conversation['response'])
                
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.download_button(
                        "⬇️ Download History",
                        data=json.dumps(history, indent=2),
                        file_name="chat_history.json",
                        mime="application/json",
                        key="download_history"
                    )
            else:
                st.info("No chat history available yet.")

    elif st.session_state.confirm_clear:
        st.warning("Are you sure you want to clear the chat history?")
        col_yes, col_no = st.columns(2)
        with col_yes:
            if st.button("Yes", key=f"confirm_yes_{st.session_state.widget_keys['confirm_yes']}"):
                st.session_state.messages = []
                clear_history("chat")
                st.session_state.confirm_clear = False
                st.session_state.show_history = False
                st.success("Chat history cleared!")
                st.rerun()
        with col_no:
            if st.button("No", key=f"confirm_no_{st.session_state.widget_keys['confirm_no']}"):
                st.session_state.confirm_clear = False
                st.info("Operation cancelled.")
                st.rerun()


    st.markdown("---")

    # Display chat messages from session state
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(f"{message['content']} *(at {message.get('timestamp', '')})*")

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
        st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": timestamp})

        # Display user message immediately
        with st.chat_message("user"):
            st.write(f"{prompt} *(at {timestamp})*")

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
                    # The user message was already added, let it stay. The AI response is the cooldown message.
                    st.session_state.messages.append({"role": "assistant", "content": response, "timestamp": datetime.now().strftime('%H:%M:%S')})
                else:
                    st.session_state.cooldown_active = False
                    st.session_state.cooldown_time_remaining = 0
                    assistant_timestamp = datetime.now().strftime('%H:%M:%S')
                    st.write(f"{response} *(at {assistant_timestamp})*")
                    st.session_state.messages.append({"role": "assistant", "content": response, "timestamp": assistant_timestamp})

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
