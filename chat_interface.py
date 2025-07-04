import streamlit as st
from datetime import datetime, timedelta
import os
import json
import uuid
from itertools import groupby # Import groupby
# Import from utils
from ncc_utils import (
    setup_gemini,
    get_ncc_response,
    API_CALL_COOLDOWN_MINUTES,
    clear_history,
    read_history,
    save_chat_to_file,
    Config
)
from security import SecurityValidator, RateLimiter, secure_chat_input
from mobile_ui import show_loading_state, create_card
from error_handling import ErrorHandler, handle_api_error, with_error_boundary
# Import chat enhancements
from chat_enhancements import (
    ChatEnhancements, 
    show_chat_search_interface, 
    show_conversation_export_interface, 
    add_chat_enhancements_css
)
# Import gamification
from gamification import award_xp, show_xp_notification

# Initialize Gemini model
model, model_error = setup_gemini()

class ChatConfig:
    """Configuration for chat functionality"""
    TEMP_CHAT = 0.3
    MAX_TOKENS_CHAT = 1000
    HISTORY_FILE = os.path.join(Config.DATA_DIR, "chat_history.json")
    TRANSCRIPT_FILE = os.path.join(Config.DATA_DIR, "chat_transcript.txt")

API_COOLDOWN_SECONDS = 10
CHAT_COOLDOWN_SECONDS = 30

def _check_and_reset_cooldown(cooldown_key, cooldown_seconds):
    if st.session_state.get(f"{cooldown_key}_active", False):
        current_time = datetime.now()
        last_time = st.session_state.get(f"{cooldown_key}_last_time")
        if last_time:
            time_diff = (current_time - last_time).total_seconds()
            time_remaining = max(0, cooldown_seconds - time_diff)
            st.session_state[f"{cooldown_key}_time_remaining"] = int(time_remaining)
            if time_remaining <= 0:
                st.session_state[f"{cooldown_key}_active"] = False
                st.session_state[f"{cooldown_key}_time_remaining"] = 0


@with_error_boundary
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
    
    if "last_interaction_time" not in st.session_state:
        st.session_state.last_interaction_time = None

    # Reset cooldown if enough time has passed
    _check_and_reset_cooldown("chat", CHAT_COOLDOWN_SECONDS)

    # Add styles and enhanced CSS
    add_chat_enhancements_css()
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
        st.title("NCC AI Chat Assistant")
        
        # Display app info
        st.markdown("""
            Ask me questions about NCC (National Cadet Corps) policies, procedures, and guidelines.
            I can provide information about training, protocols, and other aspects of NCC operations.
        """)
        
        # Display cooldown message if active
        if st.session_state.cooldown_active:
            remaining = st.session_state.cooldown_time_remaining
            st.warning(f"⏳ API Cooldown active: {remaining} seconds remaining before you can send another message.")
        if st.session_state.get("chat_active", False):
            remaining = st.session_state.get("chat_time_remaining", 0)
            st.warning(f"⏳ Chat Cooldown active: {remaining} seconds remaining before you can send another message.")
        
        # Controls area
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            with st.expander("📝 Sample Questions", expanded=False):
                st.markdown("""
                    ### Try asking:
                """)
                
                # Quick question buttons
                sample_questions = [
                    "What are the NCC core values?",
                    "How can I become an NCC cadet?",
                    "What are the ranks in NCC?",
                    "What is the NCC motto?"
                ]
                
                # Use columns for better layout of sample question buttons
                scols = st.columns(2)
                for i, question in enumerate(sample_questions):
                    with scols[i % 2]:
                        if st.button(question, key=f"ask_{question}_{i}"):
                            # Submit the question to be processed
                            submit_prompt(question)

        with col2:
            # Clear chat button
            if st.button("🗑️ Clear Chat", key=f"clear_chat_{st.session_state.widget_keys['clear_chat']}"):
                st.session_state.confirm_clear = True
                
        with col3:
            # Search button
            if st.button("🔍 Search", key="show_search"):
                st.session_state.show_search_interface = not st.session_state.get('show_search_interface', False)
                
        with col4:
            # Export button
            if st.button("📤 Export", key="show_export"):
                st.session_state.show_export_interface = not st.session_state.get('show_export_interface', False)
        
        # Show search interface if toggled
        if st.session_state.get('show_search_interface', False):
            with st.expander("🔍 Search Conversations", expanded=True):
                show_chat_search_interface()
        
        # Show export interface if toggled
        if st.session_state.get('show_export_interface', False):
            with st.expander("📤 Export Conversation", expanded=True):
                show_conversation_export_interface()

        # Chat input area (new version)
        chat_input_value = st.chat_input("Ask me about NCC...", key="chat_input")
        if chat_input_value is not None:
            if st.session_state.get("chat_active", False):
                st.warning(f"⏳ Please wait {st.session_state['chat_time_remaining']} seconds before sending another chat message.")
            else:
                submit_prompt(chat_input_value)
                st.session_state["chat_active"] = True
                st.session_state["chat_last_time"] = datetime.now()

        # Display messages in reverse order (newest first for better UX)
        display_chat_messages()
        
def submit_prompt(prompt):
    """Handle a submitted prompt."""
    if not prompt or not prompt.strip() or st.session_state.cooldown_active:
        return
    
    # Security validation
    validation_result = secure_chat_input(prompt)
    if not validation_result['valid']:
        ErrorHandler.show_warning(f"Message validation failed: {validation_result['error']}")
        return
    
    # Use sanitized input
    clean_prompt = validation_result['message']
    
    # Record timestamp for the user message
    user_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create user message object
    user_message = {
        "role": "user",
        "content": clean_prompt,
        "timestamp": user_timestamp
    }
    st.session_state.messages.append(user_message) # Add to current session messages
    
    # Award XP for asking a question
    award_xp("chat_message", {"message_length": len(clean_prompt)})
    
    # Send the request to API
    with st.chat_message("assistant"):
        # Enhanced loading state with mobile-friendly spinner
        placeholder = st.empty()
        with placeholder.container():
            show_loading_state("AI is thinking about your question...")
        
        try:
            # Get response from Gemini
            response = get_ncc_response(model, model_error, clean_prompt)
            
            # Clear loading state
            placeholder.empty()
            
            # Update state
            st.session_state.last_interaction_time = datetime.now()
            
            # Rate limit handling
            if "429" in str(response) or "Error: Quota exceeded" in str(response) or "Please wait" in str(response):
                st.session_state.cooldown_active = True
                # Try to extract remaining time from error
                try:
                    parts = str(response).split("seconds")
                    time_index = 0
                    if len(parts) > 1:
                        time_index = -2 # Index right before "seconds"
                    st.session_state.cooldown_time_remaining = int(parts[time_index])
                except (ValueError, IndexError):
                    st.session_state.cooldown_time_remaining = 0
            else:
                # Successful response
                st.session_state.cooldown_active = False
                st.session_state.cooldown_time_remaining = 0
                assistant_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Display response
                if response and response.strip():
                    st.markdown(f'<div class="message-timestamp">{assistant_timestamp}</div>', unsafe_allow_html=True)
                    # Save to session and history
                    assistant_message = {
                        "role": "assistant",
                        "content": response,
                        "timestamp": assistant_timestamp
                    }
                    st.session_state.messages.append(assistant_message) # Add to current session messages
                    save_chat_to_file(clean_prompt, response)
                    
                    # Award XP for valid interactions
                    award_xp(10) # Award 10 XP for each valid interaction
                    show_xp_notification() # Show XP notification
        except Exception as e:
            placeholder.empty()
            handle_api_error(e, "Chat response generation")
            return
    
    st.rerun()

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
            st.rerun()
    with col_no:
        if st.button("No", key=f"confirm_no_{st.session_state.widget_keys['confirm_no']}"):
            st.session_state.confirm_clear = False
            st.info("Operation cancelled.")
            st.rerun()

# Moved save_chat_to_file and clear_chat_history to utils.py
# to centralize file operations.
# The local clear_chat_history function above is only for the confirmation dialog
# within the chat tab itself, clearing the *current* session and files.
# The main History Viewer tab in main.py will use the utils.clear_history function.

def display_chat_messages():
    """Display the chat messages with enhanced formatting."""
    for message in reversed(st.session_state.messages):
        with st.chat_message(message["role"]):
            content = message.get('content', '')
            
            # Apply rich formatting for assistant messages
            if message["role"] == "assistant":
                formatted_content = ChatEnhancements.format_message_content(content)
                st.markdown(formatted_content, unsafe_allow_html=True)
            else:
                st.write(content)
            
            timestamp = message.get('timestamp', '')
            if timestamp:
                st.markdown(f'<div class="message-timestamp">{timestamp}</div>', unsafe_allow_html=True)
