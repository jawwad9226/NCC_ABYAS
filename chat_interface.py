import streamlit as st
from typing import Callable, Any
from utils import read_history, clear_history # Ensure clear_history is used or remove if not
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
        
        # Add user message
        st_session_state.messages.append({"role": "user", "content": question_content})
        
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
    
    # Clear chat button
    col1, col2, col3 = st.columns([0.2, 0.4, 0.4])
    with col1:
        if st.button("🧹 Clear Chat", key="clear_chat_button"):
            st_session_state.messages = [{"role": "assistant", "content": _welcome_message()}]
            clear_history("chat")
            st.rerun()

    with col2:
        if st.button("📜 View Chat History", key="view_history_btn"):
            with st.expander("🔎 Past Chat History (.txt)", expanded=True):
                history = read_history("chat")
                st.text(history if history else "No chat history available.")

    with col3:
        history_content = read_history("chat")
        st.download_button(
            "⬇️ Download History", 
            history_content if history_content else "No history available.", 
            "chat_history.txt", 
            mime="text/plain"
        )

    # Sample Questions
    with st.expander("💡 Sample Questions"):
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

    # Display chat history
    for msg in st_session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Type your NCC question here..."):
        # Add user message to chat history
        st_session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("🤖 Generating response..."):
                try:
                    response = get_response_func(prompt)
                    formatted_response = response.strip() + f"\n\n🕒 *Answered at {datetime.now().strftime('%H:%M:%S')}*"
                    st.markdown(formatted_response)
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

    # Add logic here if assistant should respond to the latest user message (including sample questions)
    # This is a common pattern:
    elif st_session_state.messages and st_session_state.messages[-1]["role"] == "user":
        # Check if the last user message already has a follow-up assistant message
        # This check avoids re-responding if an assistant message already exists for the last user message
        if len(st_session_state.messages) < 2 or st_session_state.messages[-2]["role"] != "assistant" or \
           st_session_state.messages[-2].get("related_to_user_prompt") != st_session_state.messages[-1]["content"]:

            last_user_prompt = st_session_state.messages[-1]["content"]
            with st.chat_message("assistant"): # This will appear below the last user message
                with st.spinner("🤖 Thinking about that sample question..."):
                    try:
                        response = get_response_func(last_user_prompt)
                        formatted_response = response.strip() + f"\n\n🕒 *Answered at {datetime.now().strftime('%H:%M:%S')}*"
                        st.markdown(formatted_response)
                        st_session_state.messages.append({
                            "role": "assistant",
                            "content": formatted_response,
                            # Add a way to link this response to the specific user prompt if needed for more robust state
                            "related_to_user_prompt": last_user_prompt
                        })
                        st.rerun() # Rerun to display the new assistant message immediately
                    except Exception as e:
                        error_msg = "❌ AI failed to respond to the sample question. Check API key or connection."
                        logging.error(f"Chat error on sample question: {e}")
                        st.warning(error_msg)
                        st_session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg
                        })
                        # st.rerun() # Optional: rerun even on error to show the error message