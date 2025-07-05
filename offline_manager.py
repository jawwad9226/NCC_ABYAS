"""
Offline Functionality Manager for NCC ABYAS
Handles offline data storage, queue management, and sync functionality
"""
import streamlit as st
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

class OfflineManager:
    """Manages offline functionality and data synchronization"""
    
    @staticmethod
    def init_offline_storage():
        """Initialize offline storage in session state"""
        if "offline_queue" not in st.session_state:
            st.session_state.offline_queue = []
        
        if "offline_mode" not in st.session_state:
            st.session_state.offline_mode = False
        
        if "last_sync_time" not in st.session_state:
            st.session_state.last_sync_time = None
    
    @staticmethod
    def check_connectivity() -> bool:
        """Check if the app is online or offline"""
        # In a real implementation, this would check actual connectivity
        # For now, we'll simulate based on session state
        return not st.session_state.get("offline_mode", False)
    
    @staticmethod
    def queue_for_offline_sync(data: Dict[str, Any], data_type: str):
        """Queue data for synchronization when back online"""
        OfflineManager.init_offline_storage()
        
        offline_item = {
            "id": len(st.session_state.offline_queue) + 1,
            "type": data_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "synced": False
        }
        
        st.session_state.offline_queue.append(offline_item)
        
        # Also save to file for persistence
        OfflineManager.save_offline_queue_to_file()
    
    @staticmethod
    def save_offline_queue_to_file():
        """Save offline queue to file for persistence"""
        try:
            queue_file = os.path.join("data", "offline_queue.json")
            with open(queue_file, 'w') as f:
                json.dump(st.session_state.offline_queue, f, indent=2)
        except Exception as e:
            st.error(f"Failed to save offline queue: {e}")
    
    @staticmethod
    def load_offline_queue_from_file():
        """Load offline queue from file"""
        try:
            queue_file = os.path.join("data", "offline_queue.json")
            if os.path.exists(queue_file):
                with open(queue_file, 'r') as f:
                    st.session_state.offline_queue = json.load(f)
        except Exception as e:
            st.warning(f"Could not load offline queue: {e}")
            st.session_state.offline_queue = []
    
    @staticmethod
    def sync_offline_data():
        """Sync queued offline data when back online"""
        if not OfflineManager.check_connectivity():
            return False, "Still offline"
        
        OfflineManager.init_offline_storage()
        
        synced_count = 0
        failed_items = []
        
        for item in st.session_state.offline_queue:
            if item.get("synced"):
                continue
            
            try:
                success = OfflineManager._sync_individual_item(item)
                if success:
                    item["synced"] = True
                    item["sync_time"] = datetime.now().isoformat()
                    synced_count += 1
                else:
                    failed_items.append(item)
            except Exception as e:
                st.error(f"Failed to sync item {item['id']}: {e}")
                failed_items.append(item)
        
        # Update sync time
        st.session_state.last_sync_time = datetime.now().isoformat()
        
        # Save updated queue
        OfflineManager.save_offline_queue_to_file()
        
        return synced_count, failed_items
    
    @staticmethod
    def _sync_individual_item(item: Dict[str, Any]) -> bool:
        """Sync an individual offline item"""
        item_type = item.get("type")
        data = item.get("data", {})
        
        try:
            if item_type == "chat_message":
                # Handle offline chat messages
                return OfflineManager._sync_chat_message(data)
            elif item_type == "quiz_result":
                # Handle offline quiz results
                return OfflineManager._sync_quiz_result(data)
            elif item_type == "feedback":
                # Handle offline feedback
                return OfflineManager._sync_feedback(data)
            else:
                st.warning(f"Unknown offline item type: {item_type}")
                return False
        except Exception as e:
            st.error(f"Error syncing {item_type}: {e}")
            return False
    
    @staticmethod
    def _sync_chat_message(data: Dict[str, Any]) -> bool:
        """Sync offline chat message"""
        try:
            # Add to chat history
            if "messages" not in st.session_state:
                st.session_state.messages = []
            
            # Check if message already exists (avoid duplicates)
            message_exists = any(
                msg.get("content") == data.get("content") and
                msg.get("timestamp") == data.get("timestamp")
                for msg in st.session_state.messages
            )
            
            if not message_exists:
                st.session_state.messages.append(data)
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def _sync_quiz_result(data: Dict[str, Any]) -> bool:
        """Sync offline quiz result"""
        try:
            from ncc_utils import append_quiz_score_entry
            append_quiz_score_entry(data)
            return True
        except Exception:
            return False
    
    @staticmethod
    def _sync_feedback(data: Dict[str, Any]) -> bool:
        """Sync offline feedback"""
        try:
            # Save feedback to file or send to server
            feedback_file = os.path.join("data", "feedback_offline.json")
            
            feedback_list = []
            if os.path.exists(feedback_file):
                with open(feedback_file, 'r') as f:
                    feedback_list = json.load(f)
            
            feedback_list.append(data)
            
            with open(feedback_file, 'w') as f:
                json.dump(feedback_list, f, indent=2)
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_offline_quiz_questions() -> List[Dict[str, Any]]:
        """Get offline quiz questions when no internet"""
        return [
            {
                "question": "What does NCC stand for?",
                "options": [
                    "National Cadet Corps",
                    "National Civil Corps",
                    "Naval Cadet Corps",
                    "National Community Corps"
                ],
                "correct_answer": "National Cadet Corps",
                "explanation": "NCC stands for National Cadet Corps, established in 1948."
            },
            {
                "question": "What is the NCC motto?",
                "options": [
                    "Unity and Discipline",
                    "Service and Sacrifice",
                    "Discipline and Unity",
                    "Honor and Duty"
                ],
                "correct_answer": "Unity and Discipline",
                "explanation": "The NCC motto is 'Unity and Discipline'."
            },
            {
                "question": "NCC was established in which year?",
                "options": [
                    "1947",
                    "1948",
                    "1949",
                    "1950"
                ],
                "correct_answer": "1948",
                "explanation": "NCC was established on 15 July 1948."
            },
            {
                "question": "What are the three wings of NCC?",
                "options": [
                    "Army, Navy, Air Force",
                    "Junior, Senior, Special",
                    "Basic, Advanced, Expert",
                    "Training, Service, Combat"
                ],
                "correct_answer": "Army, Navy, Air Force",
                "explanation": "NCC has three wings: Army, Navy, and Air Force."
            },
            {
                "question": "What is the aim of NCC?",
                "options": [
                    "Military training only",
                    "Character building and nation building",
                    "Physical fitness only",
                    "Academic excellence"
                ],
                "correct_answer": "Character building and nation building",
                "explanation": "The aim of NCC is to develop character, comradeship, discipline, and spirit of adventure among youth."
            }
        ]
    
    @staticmethod
    def show_offline_status():
        """Display offline status and sync information"""
        OfflineManager.init_offline_storage()
        
        is_online = OfflineManager.check_connectivity()
        
        # Status indicator
        if is_online:
            st.success("🟢 **Online** - All features available")
        else:
            st.warning("🔴 **Offline Mode** - Limited functionality available")
        
        # Offline queue status
        queue_size = len([item for item in st.session_state.offline_queue if not item.get("synced")])
        
        if queue_size > 0:
            st.info(f"📦 {queue_size} items queued for sync")
            
            if is_online:
                if st.button("🔄 Sync Now"):
                    with st.spinner("Syncing offline data..."):
                        synced_count, failed_items = OfflineManager.sync_offline_data()
                    
                    if synced_count > 0:
                        st.success(f"✅ Synced {synced_count} items successfully!")
                    
                    if failed_items:
                        st.error(f"❌ Failed to sync {len(failed_items)} items")
        
        # Last sync info
        last_sync = st.session_state.get("last_sync_time")
        if last_sync:
            try:
                sync_time = datetime.fromisoformat(last_sync)
                st.caption(f"Last sync: {sync_time.strftime('%Y-%m-%d %H:%M:%S')}")
            except:
                st.caption("Last sync: Unknown")

def create_offline_chat_response(user_input: str) -> str:
    """Create an offline response for chat when no internet"""
    responses = {
        "ncc": "NCC (National Cadet Corps) is a voluntary organization which recruits cadets from high schools, colleges and universities. I'm currently offline, but here's what I can tell you: NCC was established in 1948 with the motto 'Unity and Discipline'.",
        "drill": "Drill in NCC involves precise, coordinated movements and commands. Basic drill commands include Attention, Stand at Ease, Quick March, Halt, Left Turn, Right Turn, and About Turn. I'm offline, so I can't provide detailed responses right now.",
        "rank": "NCC has various ranks including Cadet, Lance Corporal, Corporal, Sergeant, Under Officer, and Warrant Officer. I'm currently offline - please connect to internet for detailed information.",
        "training": "NCC training includes drill, weapon training, map reading, field craft, leadership, and social service. I'm offline right now, so I can only provide basic information.",
        "default": "I'm currently offline and have limited information available. Please connect to the internet for comprehensive responses about NCC topics."
    }
    
    user_input_lower = user_input.lower()
    
    for keyword, response in responses.items():
        if keyword in user_input_lower:
            return response
    
    return responses["default"]

def show_offline_quiz():
    """Show offline quiz interface"""
    st.markdown("### 🎯 Offline Quiz Mode")
    st.info("📡 You're currently offline. Taking a quiz with cached questions.")
    
    # Initialize offline quiz state
    if "offline_quiz_active" not in st.session_state:
        st.session_state.offline_quiz_active = False
        st.session_state.offline_quiz_questions = []
        st.session_state.offline_quiz_answers = []
        st.session_state.offline_current_question = 0
    
    if not st.session_state.offline_quiz_active:
        st.markdown("#### Start Offline Quiz")
        
        if st.button("🚀 Start Quiz (5 Questions)"):
            st.session_state.offline_quiz_active = True
            st.session_state.offline_quiz_questions = OfflineManager.get_offline_quiz_questions()
            st.session_state.offline_quiz_answers = []
            st.session_state.offline_current_question = 0
            st.rerun()
    
    else:
        # Show current question
        questions = st.session_state.offline_quiz_questions
        current_q = st.session_state.offline_current_question
        
        if current_q < len(questions):
            question = questions[current_q]
            
            st.markdown(f"#### Question {current_q + 1} of {len(questions)}")
            st.markdown(f"**{question['question']}**")
            
            # Show options
            selected_option = st.radio(
                "Choose your answer:",
                question["options"],
                key=f"offline_q_{current_q}"
            )
            
            col1, col2 = st.columns(2)
            with col2:
                if st.button("Next Question ➡️"):
                    # Save answer
                    st.session_state.offline_quiz_answers.append({
                        "question": question["question"],
                        "selected": selected_option,
                        "correct": question["correct_answer"],
                        "is_correct": selected_option == question["correct_answer"]
                    })
                    
                    st.session_state.offline_current_question += 1
                    st.rerun()
        
        else:
            # Show results
            st.markdown("### 🎉 Quiz Completed!")
            
            answers = st.session_state.offline_quiz_answers
            correct_count = sum(1 for ans in answers if ans["is_correct"])
            total_questions = len(answers)
            score_percentage = (correct_count / total_questions) * 100
            
            st.metric("Your Score", f"{correct_count}/{total_questions} ({score_percentage:.1f}%)")
            
            # Queue result for sync
            quiz_result = {
                "timestamp": datetime.now().isoformat(),
                "score": score_percentage,
                "total_questions": total_questions,
                "correct_answers": correct_count,
                "difficulty": "offline",
                "topic": "offline_mode",
                "offline": True
            }
            
            OfflineManager.queue_for_offline_sync(quiz_result, "quiz_result")
            
            st.success("📦 Quiz result saved for sync when online!")
            
            # Reset quiz
            if st.button("🔄 Take Another Quiz"):
                st.session_state.offline_quiz_active = False
                st.rerun()

def show_offline_chat():
    """Show offline chat interface"""
    st.markdown("### 💬 Offline Chat Mode")
    st.info("📡 You're currently offline. I can provide basic information from cached data.")
    
    # Initialize offline chat
    if "offline_messages" not in st.session_state:
        st.session_state.offline_messages = []
    
    # Display offline messages
    for message in st.session_state.offline_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if user_input := st.chat_input("Ask about NCC basics..."):
        # Add user message
        user_message = {
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        }
        st.session_state.offline_messages.append(user_message)
        
        # Generate offline response
        response = create_offline_chat_response(user_input)
        assistant_message = {
            "role": "assistant", 
            "content": response,
            "timestamp": datetime.now().isoformat(),
            "offline": True
        }
        st.session_state.offline_messages.append(assistant_message)
        
        # Queue for sync
        OfflineManager.queue_for_offline_sync(user_message, "chat_message")
        
        st.rerun()
