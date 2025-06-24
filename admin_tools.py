"""
Admin dashboard and user management for NCC Cadet Platform.
"""
import streamlit as st
from auth_manager import get_user_profile, set_user_role
import firebase_admin
from firebase_admin import firestore

firestore_db = firestore.client()

def show_admin_dashboard():
    st.title("Admin Dashboard")
    st.markdown("---")
    # Only allow admin access
    if st.session_state.get("role") != "admin":
        st.warning("Unauthorized: Admins only.")
        st.stop()

    st.header("User Management")
    users_ref = firestore_db.collection("users")
    users = users_ref.stream()
    user_list = []
    for user in users:
        data = user.to_dict()
        data['uid'] = user.id
        user_list.append(data)
    if not user_list:
        st.info("No users found.")
        return
    st.write(f"**Total Users:** {len(user_list)}")
    st.markdown("---")
    # Show overall stats
    all_progress = []
    for user in user_list:
        # Try to get progress summary for each user
        progress_ref = firestore_db.collection("users").document(user['uid']).collection("progress").document("summary")
        progress_doc = progress_ref.get()
        progress = progress_doc.to_dict() if progress_doc.exists else {}
        all_progress.append(progress)
        st.write(f"**Name:** {user.get('name')} | **Reg No:** {user.get('reg_no')} | **Email:** {user.get('email')} | **Role:** {user.get('role', 'cadet')}")
        st.write(f"Progress: {progress if progress else 'No data'}")
        if user.get('role') != 'admin':
            new_role = st.selectbox(f"Set Role for {user.get('name')}", ["cadet", "instructor", "admin"], index=["cadet", "instructor", "admin"].index(user.get('role', 'cadet')), key=f"role_{user['uid']}")
            if st.button(f"Update Role for {user.get('name')}", key=f"update_{user['uid']}"):
                set_user_role(user['uid'], new_role)
                st.success(f"Role updated for {user.get('name')} to {new_role}")
                st.rerun()
        st.markdown("---")
    # Aggregate stats (example: total quizzes, avg score)
    total_quizzes = sum(p.get('total_quizzes', 0) for p in all_progress if p)
    avg_score = (sum(p.get('average_score', 0) for p in all_progress if p) / len([p for p in all_progress if p])) if any(all_progress) else 0
    st.header("Overall App Stats")
    st.write(f"Total Quizzes Taken: {total_quizzes}")
    st.write(f"Average Score: {avg_score:.2f}%")
