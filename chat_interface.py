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
    API_CALL_COOLDOWN_MINUTES,
    _load_json_file  # Import the helper function
)

# Initialize Gemini model
model, model_error = setup_gemini()

class ChatConfig:
    """Configuration for chat functionality"""
    TEMP_CHAT = 0.3
    MAX_TOKENS_CHAT = 1000
    HISTORY_FILE = os.path.join(Config.DATA_DIR, "chat_history.json")
    TRANSCRIPT_FILE = os.path.join(Config.DATA_DIR, "chat_transcript.txt")

def save_chat_to_file(user_prompt: str, assistant_response: str) -> None:
    """Save chat interaction to history file and transcript."""
    try:
        # Save to JSON history
        chat_entry = {
            "timestamp": datetime.now().isoformat(),
            "prompt": user_prompt,
            "response": assistant_response
        }
        
        try:
            with open(ChatConfig.HISTORY_FILE, 'r') as f:
                history = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            history = []
            
        history.append(chat_entry)
        with open(ChatConfig.HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
            
        # Save to transcript
        with open(ChatConfig.TRANSCRIPT_FILE, 'a') as f:
            f.write(f"\nUser ({chat_entry['timestamp']}):\n{user_prompt}\n")
            f.write(f"\nAssistant:\n{assistant_response}\n")
            f.write("\n" + "-"*80 + "\n")
            
    except Exception as e:
        st.error(f"Failed to save chat: {str(e)}")
        
def clear_chat_history() -> bool:
    """Clear chat history files."""
    try:
        # Clear JSON history
        with open(ChatConfig.HISTORY_FILE, 'w') as f:
            json.dump([], f)
        
        # Clear transcript
        with open(ChatConfig.TRANSCRIPT_FILE, 'w') as f:
            f.write("")
            
        return True
    except Exception as e:
        st.error(f"Failed to clear chat history: {str(e)}")
        return False
        
def read_chat_history() -> str:
    """Read chat history from file."""
    try:
        with open(ChatConfig.HISTORY_FILE, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return ""
    except Exception as e:
        st.error(f"Failed to read chat history: {str(e)}")
        return ""

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
            "chat_input": str(uuid.uuid4()),
            "sample_questions": str(uuid.uuid4())
        }
    if "show_history" not in st.session_state:
        st.session_state.show_history = False
    if "selected_conversation" not in st.session_state:
        st.session_state.selected_conversation = None
    if "confirm_clear" not in st.session_state:
        st.session_state.confirm_clear = False
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
    with main_container:
        # Top actions bar
        col_actions1, col_actions2, col_spacer = st.columns([1, 1, 2])
        
        with col_actions1:
            if st.button(
                "🕒 View History",
                key=f"view_history_btn_{st.session_state.widget_keys['clear_chat']}",
                help="Show or hide your chat history",
                use_container_width=True
            ):
                st.session_state.show_history = not st.session_state.show_history
        
        with col_actions2:
            if st.button(
                "🧹 Clear Chat",
                key=f"clear_chat_btn_{st.session_state.widget_keys['clear_chat']}",
                help="Clear all chat messages",
                use_container_width=True
            ):
                st.session_state.confirm_clear = True

        # Chat input
        if st.session_state.cooldown_active and st.session_state.cooldown_time_remaining > 0:
            st.info(f"Please wait {st.session_state.cooldown_time_remaining} seconds before sending another message.")
        
        if prompt := st.chat_input(
            "Type your NCC-related question here...",
            key=f"chat_input_{st.session_state.widget_keys['chat_input']}",
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

        # History view or confirmation dialog
        if st.session_state.show_history:
            display_chat_history()
        elif st.session_state.confirm_clear:
            display_clear_confirmation()

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
                st.session_state.messages.append(assistant_message)
                save_chat_to_file(prompt, response)
    
    st.rerun()

def display_chat_history():
    """Display the chat history view."""
    st.markdown("### 📜 Chat History")
    history = read_chat_history()
    if history:
        try:
            history_data = json.loads(history)
            history_data.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            for date, items in groupby(history_data, key=lambda x: x.get('timestamp', '')[:10]):
                items = list(items)
                with st.expander(f"📅 {date}", expanded=True):
                    for item in items:
                        prompt = item.get('prompt', '')
                        timestamp = item.get('timestamp', '').split('T')[1][:8]
                        preview = f"🕒 {timestamp} - {prompt[:50]}..."
                        
                        if st.button(
                            preview,
                            key=f"conv_{item.get('timestamp', '')}_{st.session_state.widget_keys['chat_input']}"
                        ):
                            st.session_state.selected_conversation = item
                            st.rerun()
            
            if st.session_state.selected_conversation:
                st.markdown("### Selected Conversation")
                with st.chat_message("user"):
                    st.write(st.session_state.selected_conversation['prompt'])
                with st.chat_message("assistant"):
                    st.write(st.session_state.selected_conversation['response'])
            
            st.download_button(
                "⬇️ Download History",
                data=json.dumps(history_data, indent=2),
                file_name="chat_history.json",
                mime="application/json",
                key=f"download_history_{st.session_state.widget_keys['chat_input']}"
            )
        except json.JSONDecodeError:
            st.error("Failed to parse chat history.")
    else:
        st.info("No chat history available yet.")

def display_clear_confirmation():
    """Display the clear history confirmation dialog."""
    st.warning("Are you sure you want to clear the chat history?")
    col_yes, col_no = st.columns(2)
    with col_yes:
        if st.button("Yes", key=f"confirm_yes_{st.session_state.widget_keys['confirm_yes']}"):
            st.session_state.messages = []
            clear_chat_history()
            st.session_state.confirm_clear = False
            st.session_state.show_history = False
            st.success("Chat history cleared!")
            st.rerun()
    with col_no:
        if st.button("No", key=f"confirm_no_{st.session_state.widget_keys['confirm_no']}"):
            st.session_state.confirm_clear = False
            st.info("Operation cancelled.")
            st.rerun()

def display_chat_messages():
    """Display the chat messages."""
    for message in reversed(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.write(message['content'])
            timestamp = message.get('timestamp', '')
            if timestamp:
                st.markdown(f'<div class="message-timestamp">{timestamp}</div>', unsafe_allow_html=True)
