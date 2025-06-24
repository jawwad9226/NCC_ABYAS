"""
Admin dashboard and user management for NCC Cadet Platform.
"""
import streamlit as st
from auth_manager import get_user_profile, set_user_role
import firebase_admin
from firebase_admin import firestore
import io
import csv

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

    # --- Search & Filter ---
    search_query = st.text_input("Search users (name, email, reg no, role):", "")
    filter_role = st.selectbox("Filter by role:", ["All", "cadet", "instructor", "admin"], index=0)
    filtered_users = [u for u in user_list if (
        (search_query.lower() in u.get('name','').lower() or
         search_query.lower() in u.get('email','').lower() or
         search_query.lower() in u.get('reg_no','').lower() or
         search_query.lower() in u.get('role','').lower()) and
        (filter_role == "All" or u.get('role') == filter_role)
    )]
    st.write(f"**Total Users:** {len(filtered_users)}")
    st.markdown("---")

    # --- Bulk Role Update ---
    st.subheader("Bulk Role Update")
    selected_uids = st.multiselect(
        "Select users to update role:",
        options=[u['uid'] for u in filtered_users],
        format_func=lambda uid: next((u['name']+f" ({u['email']})" for u in filtered_users if u['uid']==uid), uid)
    )
    new_bulk_role = st.selectbox("Set selected users' role to:", ["cadet", "instructor", "admin"])
    if st.button("Update Role for Selected Users"):
        for uid in selected_uids:
            set_user_role(uid, new_bulk_role)
        st.success(f"Updated role for {len(selected_uids)} users to {new_bulk_role}.")
        st.rerun()

    # --- Export Users ---
    csv_buffer = io.StringIO()
    csv_writer = csv.writer(csv_buffer)
    csv_writer.writerow(["Name", "Reg No", "Email", "Mobile", "Role", "Created At", "Last Login", "UID"])
    for u in filtered_users:
        csv_writer.writerow([
            u.get('name',''), u.get('reg_no',''), u.get('email',''), u.get('mobile',''),
            u.get('role',''), u.get('created_at',''), u.get('last_login',''), u.get('uid','')
        ])
    st.download_button("⬇️ Download User List (CSV)", csv_buffer.getvalue(), "user_list.csv")

    # --- User Table & Actions ---
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
                st.success(f"Role updated for {user.get('name')} to {new_role}")
                st.rerun()
            # Delete user
            if st.button(f"Delete {user.get('name')}", key=f"delete_{user['uid']}"):
                if st.confirm(f"Are you sure you want to delete {user.get('name')}? This cannot be undone."):
                    firestore_db.collection("users").document(user['uid']).delete()
                    st.success(f"Deleted user {user.get('name')}")
                    st.rerun()

    # --- Activity Log (simple) ---
    st.subheader("Recent Admin Actions (This Session)")
    if 'admin_actions' not in st.session_state:
        st.session_state['admin_actions'] = []
    for action in st.session_state['admin_actions'][-10:][::-1]:
        st.write(action)

    # --- Overall Stats ---
    all_progress = []
    for user in user_list:
        progress_ref = firestore_db.collection("users").document(user['uid']).collection("progress").document("summary")
        progress_doc = progress_ref.get()
        progress = progress_doc.to_dict() if progress_doc.exists else {}
        all_progress.append(progress)
    total_quizzes = sum(p.get('total_quizzes', 0) for p in all_progress if p)
    avg_score = (sum(p.get('average_score', 0) for p in all_progress if p) / len([p for p in all_progress if p])) if any(all_progress) else 0
    st.header("Overall App Stats")
    st.write(f"Total Quizzes Taken: {total_quizzes}")
    st.write(f"Average Score: {avg_score:.2f}%")
