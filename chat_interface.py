import streamlit as st
from datetime import datetime, timedelta
import os
import json
import uuid
import logging
from itertools import groupby # Import groupby
# Import from utils
from utils import (
    read_history,
    clear_history,  # Assuming you are calling this with clear_history("chat")
    save_chat_to_file, # Import save_chat_to_file
    setup_gemini,
    get_ncc_response,
    Config,
    API_CALL_COOLDOWN_MINUTES,
)

# Initialize Gemini model
model, model_error = setup_gemini()

class ChatConfig:
    """Configuration for chat functionality"""
    TEMP_CHAT = 0.3
    MAX_TOKENS_CHAT = 1000
    HISTORY_FILE = os.path.join(Config.DATA_DIR, "chat_history.json")
    TRANSCRIPT_FILE = os.path.join(Config.DATA_DIR, "chat_transcript.txt")

def _check_and_reset_cooldown():
    """Check and reset cooldown if enough time has passed."""
    if st.session_state.get("cooldown_active", False):
        current_time = datetime.now()
        last_time = st.session_state.get("last_interaction_time")
        if last_time:
            time_diff = (current_time - last_time).total_seconds()
            cooldown_seconds = 60 * API_CALL_COOLDOWN_MINUTES
            time_remaining = max(0, cooldown_seconds - time_diff)
            st.session_state.cooldown_time_remaining = int(time_remaining)
            if time_remaining <= 0:
                st.session_state.cooldown_active = False
                st.session_state.cooldown_time_remaining = 0


def chat_interface():
    """Main chat interface function with proper widget key management"""
    
    # Initialize all required session states
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "cooldown_active" not in st.session_state:
        st.session_state.cooldown_active = False
    if "cooldown_time_remaining" not in st.session_state:
        st.session_state.cooldown_time_remaining = 0
    if "widget_keys" not in st.session_state:
        st.session_state.widget_keys = {
            "clear_chat": str(uuid.uuid4()),
            "confirm_yes": str(uuid.uuid4()),
            "confirm_no": str(uuid.uuid4()),
            "sample_questions": str(uuid.uuid4())
        }
    # Removed history/clear state management as it's handled in main.py History Viewer
    
    if "last_interaction_time" not in st.session_state:
        st.session_state.last_interaction_time = None

    # Reset cooldown if enough time has passed
    _check_and_reset_cooldown()

    # Add styles
    st.markdown("""
        <style>
        /* Chat container styles */
        .main .block-container {
            padding-bottom: 2rem !important;
        }
        
        /* Chat input container styling */
        .stChatInputContainer {
            position: sticky !important;
            top: 0;
            background: linear-gradient(to bottom, var(--background-color) 50%, transparent) !important;
            padding: 1rem 0 !important;
            z-index: 99;
            margin: 0 -1rem;
        }

        /* Chat input styling */
        .stChatInputContainer textarea {
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(99, 102, 241, 0.2) !important;
            border-radius: 0.8rem !important;
            padding: 0.75rem 1rem !important;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
            transition: all 0.2s ease !important;
        }

        .stChatInputContainer textarea:focus {
            border-color: rgba(99, 102, 241, 0.5) !important;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
            background: rgba(255, 255, 255, 0.1) !important;
        }

        /* Message styling */
        [data-testid="stChatMessage"] {
            background: var(--chat-message-background) !important;
            border: 1px solid var(--chat-message-border) !important;
            padding: 1rem !important;
            border-radius: 0.8rem !important;
            margin: 0.5rem 0 !important;
            line-height: 1.5 !important;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
        }

        [data-testid="stChatMessage"][data-testid="user-message"] {
            background: rgba(99, 102, 241, 0.1) !important;
            border-color: rgba(99, 102, 241, 0.2) !important;
            margin-left: 2rem !important;
        }

        [data-testid="stChatMessage"][data-testid="assistant-message"] {
            background: rgba(99, 102, 241, 0.05) !important;
            border-color: rgba(99, 102, 241, 0.1) !important;
            margin-right: 2rem !important;
        }

        /* Sample questions styling */
        .sample-questions {
            margin: 1rem 0;
            padding: 1rem;
            border-radius: 0.8rem;
            background: rgba(99, 102, 241, 0.05);
            border: 1px solid rgba(99, 102, 241, 0.1);
        }

        /* Timestamp styling */
        .message-timestamp {
            font-size: 0.75rem;
            color: rgba(107, 114, 128, 0.8);
            text-align: right;
            margin-top: 0.25rem;
            font-style: italic;
        }
        </style>
    """, unsafe_allow_html=True)

    # Main chat container
    main_container = st.container()
    
    # Chat input and sample questions are now the primary content here
    with main_container:
        # Clear Chat button (kept here for clearing *current* session, but main history clear is in History Viewer)
        # Consider if this button should clear session state or file history. Let's keep it for session state.
        if st.button(
                "🧹 Clear Chat",
                key=f"clear_chat_btn_{st.session_state.widget_keys['clear_chat']}",
                help="Clear all chat messages",
                use_container_width=True
            ):
                st.session_state.confirm_clear = True

        # Confirmation dialog for clearing current chat session
        if st.session_state.get("confirm_clear", False):
            display_clear_confirmation() # Use the local confirmation function

        # Chat input
        if st.session_state.cooldown_active and st.session_state.cooldown_time_remaining > 0:
            st.info(f"Please wait {st.session_state.cooldown_time_remaining} seconds before sending another message.")
        
        if prompt := st.chat_input(
            "Type your NCC-related question here...",
            disabled=st.session_state.cooldown_active
        ):
            process_chat_input(prompt)

        # Sample Questions
        with st.expander("💡 Sample Questions", expanded=False):
            st.markdown('<div class="sample-questions">', unsafe_allow_html=True)
            st.write("Click a question to try with the assistant:")
            sample_questions = [
                "What is the NCC?",
                "What are the benefits of joining NCC?",
                "Tell me about the NCC syllabus.",
                "What is drill in NCC?",
                "How can I join the NCC?",
                "What is weapon training in NCC?"
            ]
            cols = st.columns(3)
            for i, question in enumerate(sample_questions):
                with cols[i % 3]:
                    if st.button(
                        question,
                        key=f"sample_q_{i}_{st.session_state.widget_keys['sample_questions']}",
                        help="Click to ask this question",
                        use_container_width=True
                    ):
                        process_chat_input(question)
            st.markdown('</div>', unsafe_allow_html=True)


        # Display chat messages
        display_chat_messages()

def process_chat_input(prompt: str) -> None:
    """Process a chat input and generate a response."""
    if not prompt.strip():
        st.warning("Please enter a valid question.")
        return
        
    # Add user message
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_message = {
        "role": "user",
        "content": prompt,
        "timestamp": timestamp
    }
    st.session_state.messages.append(user_message)
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
        st.markdown(f'<div class="message-timestamp">{timestamp}</div>', unsafe_allow_html=True)
    
    # Get and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_ncc_response(model, model_error, prompt)
            
            if not response:
                st.error("Sorry, I couldn't generate a response. Please try again.")
                return
                
            if response.startswith("Error"):
                st.error(f"Assistant error: {response}")
                return
                
            if "Please wait" in response and "seconds" in response:
                st.session_state.cooldown_active = True
                try:
                    parts = response.split(" ")
                    time_index = parts.index("wait") + 1
                    st.session_state.cooldown_time_remaining = int(parts[time_index])
                except (ValueError, IndexError):
                    st.session_state.cooldown_time_remaining = 0
                st.warning(response)
            else:
                # Successful response
                st.session_state.cooldown_active = False
                st.session_state.cooldown_time_remaining = 0
                assistant_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Display response
                st.write(response)
                st.markdown(f'<div class="message-timestamp">{assistant_timestamp}</div>', unsafe_allow_html=True)
                
                # Save to session and history
                assistant_message = {
                    "role": "assistant",
                    "content": response,
                    "timestamp": assistant_timestamp
                }
                st.session_state.messages.append(assistant_message) # Add to current session messages
                save_chat_to_file(prompt, response)
    
    st.experimental_rerun()

def display_clear_confirmation():
    """Display the clear history confirmation dialog."""
    st.warning("Are you sure you want to clear the chat history?")
    col_yes, col_no = st.columns(2)
    with col_yes:
        if st.button("Yes", key=f"confirm_yes_{st.session_state.widget_keys['confirm_yes']}", on_click=lambda: clear_history("chat")):
            st.session_state.messages = [] # Clear session state messages
            clear_history("chat") # Use utils.clear_history for file operations
            # Note: This clear_chat_history is local to chat_interface.py and clears files.
            st.session_state.confirm_clear = False
            st.session_state.show_history = False
            st.success("Chat history cleared!")
            st.experimental_rerun()
    with col_no:
        if st.button("No", key=f"confirm_no_{st.session_state.widget_keys['confirm_no']}"):
            st.session_state.confirm_clear = False
            st.info("Operation cancelled.")
            st.experimental_rerun()

# Moved save_chat_to_file and clear_chat_history to utils.py
# to centralize file operations.
# The local clear_chat_history function above is only for the confirmation dialog
# within the chat tab itself, clearing the *current* session and files.
# The main History Viewer tab in main.py will use the utils.clear_history function.

def display_chat_messages():
    """Display the chat messages."""
    for message in reversed(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.write(message['content'])
            timestamp = message.get('timestamp', '')
            if timestamp:
                st.markdown(f'<div class="message-timestamp">{timestamp}</div>', unsafe_allow_html=True)
