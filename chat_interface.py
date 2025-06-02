import streamlit as st
from typing import Callable, Any
from utils import read_history, clear_history
import logging
from datetime import datetime

# ... (setup logger if not already at module level) ...

def _welcome_message() -> str:
    return "Hello! 👋 I'm your **NCC AI Assistant**. Ask me about anything related to **training**, **camps**, **certificates**, or **NCC rules**!"

def display_chat_interface(
    get_response_func: Callable[[str], str],
    st_session_state: Any
):
    # Initialize chat history if not exists
    if "messages" not in st_session_state:
        st_session_state.messages = [{"role": "assistant", "content": _welcome_message()}]
    
    # Initialize sample question flag if not exists
    if "sample_question_to_process" not in st_session_state:
        st_session_state.sample_question_to_process = None

    # Process sample question if one was selected
    if st_session_state.sample_question_to_process:
        question_content = st_session_state.sample_question_to_process
        st_session_state.sample_question_to_process = None  # Clear the flag first
        
        # Add user message with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st_session_state.messages.append({
            "role": "user", 
            "content": f"{question_content}  *({timestamp})*"
        })
        
        # Generate response
        with st.spinner("🤖 Generating response..."):
            try:
                response = get_response_func(question_content)
                formatted_response = response.strip() + f"\n\n🕒 *Answered at {datetime.now().strftime('%H:%M:%S')}*"
                st_session_state.messages.append({
                    "role": "assistant",
                    "content": formatted_response
                })
            except Exception as e:
                error_msg = "❌ AI failed to respond. Check your API key or connection."
                logging.error(f"Error processing sample question: {e}")
                st_session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
        st.rerun()

    st.header("💬 Chat with NCC Assistant")
    
    # Chat controls
    col1, col2, col3 = st.columns([0.2, 0.4, 0.4])
    
    # Clear chat button with confirmation
    with col1:
        if st.button("🧹 Clear Chat", key="clear_chat_button", 
                    help="Clear the current chat session"):
            st.session_state.confirm_clear = True

        if st.session_state.get("confirm_clear"):
            st.warning("Are you sure? This will clear all chat history.")
            if st.button("Yes, clear all"):
                st_session_state.messages = [{"role": "assistant", "content": _welcome_message()}]
                clear_history("chat")
                st.session_state.confirm_clear = False
                st.rerun()
            if st.button("No, keep chat"):
                st.session_state.confirm_clear = False
                st.rerun()

    # View history button
    with col2:
        if st.button("📜 View Chat History", 
                    key="view_history_btn",
                    help="Show recent chat history"):
            with st.expander("🔎 Recent Chat History", expanded=True):
                history = read_history("chat")
                if history:
                    history_lines = history.splitlines()
                    for line in history_lines[-50:]:  # Show last 50 lines
                        st.write(line)
                    if len(history_lines) > 50:
                        st.info(f"...and {len(history_lines)-50} more lines in the full history.")
                else:
                    st.info("No chat history available.")

    # Download history button
    with col3:
        history_content = read_history("chat")
        st.download_button(
            "⬇️ Download History",
            history_content if history_content else "No history available.",
            "chat_history.txt",
            mime="text/plain",
            help="Download complete chat history as a text file"
        )

    # Sample Questions
    with st.expander("💡 Sample Questions (click to ask)"):
        questions = [
            "What is the NCC motto?",
            "Explain the importance of 'Drill' in NCC.",
            "What are the types of NCC camps?",
            "How does NCC assist in disaster relief?",
            "What is the structure of NCC in India?"
        ]
        cols = st.columns(2)
        for i, q_text in enumerate(questions):
            with cols[i % 2]:
                if st.button(q_text, key=f"sample_{i}"):
                    st_session_state.sample_question_to_process = q_text
                    st.rerun()

    # Display chat history using Streamlit's native chat message styling
    for msg in st_session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"], unsafe_allow_html=True)

    # Chat input with validation
    if prompt := st.chat_input("Type your NCC question here..."):
        # Validate input
        if not prompt.strip():
            st.warning("Please enter a valid question.")
            st.stop()
            
        # Add timestamp to user message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_message = f"{prompt}  *({timestamp})*"
        
        # Add user message to chat history
        st_session_state.messages.append({"role": "user", "content": user_message})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_message, unsafe_allow_html=True)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("🤖 Generating response..."):
                try:
                    response = get_response_func(prompt)
                    formatted_response = response.strip() + f"\n\n🕒 *Answered at {datetime.now().strftime('%H:%M:%S')}*"
                    st.markdown(formatted_response, unsafe_allow_html=True)
                    st_session_state.messages.append({
                        "role": "assistant",
                        "content": formatted_response
                    })
                except Exception as e:
                    error_msg = "❌ AI failed to respond. Check your API key or connection."
                    logging.error(f"Chat error: {e}")
                    st.warning(error_msg)
                    st_session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })

    # Handle follow-up responses to user messages (including sample questions)
    elif st_session_state.messages and st_session_state.messages[-1]["role"] == "user":
        if len(st_session_state.messages) < 2 or st_session_state.messages[-2]["role"] != "assistant" or \
           st_session_state.messages[-2].get("related_to_user_prompt") != st_session_state.messages[-1]["content"]:

            last_user_prompt = st_session_state.messages[-1]["content"]
            with st.chat_message("assistant"):
                with st.spinner("🤖 Thinking about that..."):
                    try:
                        response = get_response_func(last_user_prompt)
                        formatted_response = response.strip() + f"\n\n🕒 *Answered at {datetime.now().strftime('%H:%M:%S')}*"
                        st.markdown(formatted_response, unsafe_allow_html=True)
                        st_session_state.messages.append({
                            "role": "assistant",
                            "content": formatted_response,
                            "related_to_user_prompt": last_user_prompt
                        })
                        st.rerun()
                    except Exception as e:
                        error_msg = "❌ AI failed to respond. Check your API key or connection."
                        logging.error(f"Chat error on follow-up: {e}")
                        st.warning(error_msg)
                        st_session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg
                        })