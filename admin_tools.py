"""
Admin dashboard and user management for NCC Cadet Platform.
"""
import streamlit as st
from auth_manager import get_user_profile, set_user_role
from firebase_admin import auth as admin_auth
import firebase_admin
from firebase_admin import firestore
import io
import csv
import os
import re
import glob

firestore_db = firestore.client()

def show_admin_dashboard():
    st.title("Admin Dashboard")
    st.markdown("---")
    if st.session_state.get("role") != "admin":
        st.stop()

    tabs = st.tabs(["User Management", "Overall Progress", "Feedback & Error Reports", "Activity Log"])

    # --- User Management Tab ---
    with tabs[0]:
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
        else:
            search_query = st.text_input("Search users (name, email, reg no, role):", "")
            filter_role = st.selectbox("Filter by role:", ["All", "cadet", "instructor", "admin"], index=0)
            filtered_users = [u for u in user_list if (
                (search_query.lower() in u.get('name','').lower() or
                 search_query.lower() in u.get('email','').lower() or
                 search_query.lower() in u.get('reg_no','').lower() or
                 search_query.lower() in u.get('role','').lower()) and
                (filter_role == "All" or u.get('role') == filter_role)
            )]
            # Export Users
            import io, csv
            csv_buffer = io.StringIO()
            csv_writer = csv.writer(csv_buffer)
            csv_writer.writerow(["Name", "Reg No", "Email", "Mobile", "Role", "Created At", "Last Login", "UID"])
            for u in filtered_users:
                csv_writer.writerow([
                    u.get('name',''), u.get('reg_no',''), u.get('email',''), u.get('mobile',''),
                    u.get('role',''), u.get('created_at',''), u.get('last_login',''), u.get('uid','')
                ])
            st.download_button("⬇️ Download User List (CSV)", csv_buffer.getvalue(), "user_list.csv")
            # User Table & Actions
            st.subheader("User List")
            for user in filtered_users:
                with st.expander(f"{user.get('name')} ({user.get('email')}) [{user.get('role','cadet')}]", expanded=False):
                    st.write(f"**Reg No:** {user.get('reg_no')}")
                    st.write(f"**Mobile:** {user.get('mobile')}")
                    st.write(f"**Created At:** {user.get('created_at')}")
                    st.write(f"**Last Login:** {user.get('last_login')}")
                    st.write(f"**UID:** {user.get('uid')}")
                    # Detailed progress
                    progress_ref = firestore_db.collection("users").document(user['uid']).collection("progress").document("summary")
                    progress_doc = progress_ref.get()
                    progress = progress_doc.to_dict() if progress_doc.exists else {}
                    st.write(f"**Progress:** {progress if progress else 'No data'}")
                    # Role update
                    new_role = st.selectbox(f"Set Role for {user.get('name')}", ["cadet", "instructor", "admin"], index=["cadet", "instructor", "admin"].index(user.get('role', 'cadet')), key=f"role_{user['uid']}")
                    if st.button(f"Update Role for {user.get('name')}", key=f"update_{user['uid']}"):
                        set_user_role(user['uid'], new_role)
                        st.rerun()
                    # Delete user
                    def delete_user_and_data(user_uid):
                        try:
                            admin_auth.delete_user(user_uid)
                        except Exception as e:
                            return False, f"Failed to delete user from Auth: {e}"
                        try:
                            user_doc_ref = firestore_db.collection("users").document(user_uid)
                            for subcol in user_doc_ref.collections():
                                for doc in subcol.stream():
                                    doc.reference.delete()
                            user_doc_ref.delete()
                        except Exception as e:
                            return False, f"Failed to delete user data from Firestore: {e}"
                        return True, None
                    confirm_key = f"confirm_delete_{user['uid']}"
                    if st.session_state.get(confirm_key):
                        st.warning(f"Are you sure you want to delete {user.get('name')}? This cannot be undone.")
                        col_yes, col_no = st.columns(2)
                        with col_yes:
                            if st.button(f"Yes, Delete {user.get('name')}", key=f"yes_delete_{user['uid']}"):
                                success, err = delete_user_and_data(user['uid'])
                                if success:
                                    st.success(f"User {user.get('name')} deleted successfully.")
                                    st.session_state.pop(confirm_key)
                                    st.rerun()
                                else:
                                    st.error(err)
                                    st.session_state.pop(confirm_key)
                        with col_no:
                            if st.button("Cancel", key=f"cancel_delete_{user['uid']}"):
                                st.session_state.pop(confirm_key)
                                st.info("Delete cancelled.")
                    else:
                        if st.button(f"Delete {user.get('name')}", key=f"delete_{user['uid']}"):
                            st.session_state[confirm_key] = True

    # --- Overall Progress Tab ---
    with tabs[1]:
        st.header("Overall Users Progress")
        all_progress = []
        for user in user_list:
            progress_ref = firestore_db.collection("users").document(user['uid']).collection("progress").document("summary")
            progress_doc = progress_ref.get()
            progress = progress_doc.to_dict() if progress_doc.exists else {}
            progress['name'] = user.get('name','')
            progress['email'] = user.get('email','')
            progress['role'] = user.get('role','')
            all_progress.append(progress)
        import pandas as pd
        df = pd.DataFrame(all_progress)
        if not df.empty:
            st.dataframe(df.fillna("-"))
            # --- Enhanced Visuals and Insights ---
            st.subheader("Key Metrics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Users", len(df))
            with col2:
                st.metric("Total Quizzes", int(df['total_quizzes'].sum()) if 'total_quizzes' in df else 0)
            with col3:
                st.metric("Avg. Score", f"{df['average_score'].mean():.2f}%" if 'average_score' in df else "-")
            with col4:
                st.metric("Top Performer", df.loc[df['average_score'].idxmax()]['name'] if 'average_score' in df and not df['average_score'].isnull().all() else "-")
            st.markdown("---")
            if 'average_score' in df:
                st.subheader("Score Distribution")
                st.bar_chart(df['average_score'])
            if 'total_quizzes' in df:
                st.subheader("Quiz Participation")
                st.bar_chart(df['total_quizzes'])
            # Top 5 performers
            if 'average_score' in df:
                st.subheader("Top 5 Performers")
                st.table(df.sort_values('average_score', ascending=False)[['name','email','average_score']].head(5))
            # Most active users
            if 'total_quizzes' in df:
                st.subheader("Most Active Users (by Quizzes)")
                st.table(df.sort_values('total_quizzes', ascending=False)[['name','email','total_quizzes']].head(5))
            st.download_button("⬇️ Download All Progress (CSV)", df.to_csv(index=False), "all_users_progress.csv")
        else:
            st.info("No progress data available.")

    # --- Feedback & Error Reports Tab ---
    with tabs[2]:
        st.header("Feedback & Error Reports")
        feedback_file = os.path.join("data", "user_feedback.txt")
        import re
        if os.path.exists(feedback_file):
            with open(feedback_file, "r") as f:
                feedback_entries = f.read().split("---\n")
            for entry in reversed(feedback_entries):
                if entry.strip():
                    st.markdown("---")
                    st.markdown(f"<div style='font-size:1.1em;'><b>Feedback Entry:</b></div>", unsafe_allow_html=True)
                    st.markdown(f"<pre style='white-space:pre-wrap;background:#f3f4f6;border-radius:8px;padding:0.7em 1em;color:#222;border:1.5px solid #6366F1'>{entry.strip()}</pre>", unsafe_allow_html=True)
                    img_names = re.findall(r"Attachments: \[(.*?)\]", entry)
                    if img_names:
                        for img_list in img_names:
                            for img in eval(img_list):
                                img_path = os.path.join("data", img)
                                if os.path.exists(img_path):
                                    st.image(img_path, caption=img, use_column_width=True)
        else:
            st.info("No feedback has been submitted yet.")

    # --- Activity Log Tab ---
    with tabs[3]:
        st.header("Recent Admin Actions (This Session)")
        if 'admin_actions' not in st.session_state:
            st.session_state['admin_actions'] = []
        for action in st.session_state['admin_actions'][-10:][::-1]:
            st.write(action)
