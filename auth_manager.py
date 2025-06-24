"""
Handles Firebase authentication, registration, and role management for NCC Cadet Platform.
"""
import os
import json
import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore, auth as admin_auth
from datetime import datetime
import requests
from streamlit_browser_storage.local_storage import LocalStorage
import streamlit as st
from utils.logging_utils import log_info, log_warning, log_error

# Load Firebase config
with open("firebase_config.json") as f:
    firebase_config = json.load(f)

# Initialize pyrebase (for user auth)
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()  # Not used, but required by pyrebase

# Initialize firebase_admin (for Firestore) with service account config
with open("firebase_config.json") as f:
    firebase_config = json.load(f)
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)
firestore_db = firestore.client()

# --- Registration ---
def register_user(name, reg_no, email, mobile, password):
    """Register a new user with Firebase Auth and store profile in Firestore."""
    try:
        # 1. Create user in Firebase Auth
        user = auth.create_user_with_email_and_password(email, password)
        uid = user['localId']
        # 2. Save user profile in Firestore
        profile = {
            "name": name,
            "reg_no": reg_no,
            "email": email,
            "mobile": mobile,
            "role": "cadet",
            "created_at": datetime.utcnow().isoformat(),
            "last_login": datetime.utcnow().isoformat()
        }
        firestore_db.collection("users").document(uid).set(profile)
        return {"success": True, "uid": uid}
    except Exception as e:
        return {"success": False, "error": str(e)}

# --- Login ---
def login_user(email, password):
    """Authenticate user and fetch profile from Firestore."""
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        uid = user['localId']
        # Fetch user profile
        doc = firestore_db.collection("users").document(uid).get()
        if doc.exists:
            # Update last_login
            firestore_db.collection("users").document(uid).update({"last_login": datetime.utcnow().isoformat()})
            profile = doc.to_dict()
            return {"success": True, "uid": uid, "profile": profile}
        else:
            return {"success": False, "error": "Profile not found."}
    except Exception as e:
        return {"success": False, "error": str(e)}

# --- Get User Profile ---
def get_user_profile(uid):
    doc = firestore_db.collection("users").document(uid).get()
    if doc.exists:
        return doc.to_dict()
    return None

# --- Set User Role ---
def set_user_role(uid, role):
    firestore_db.collection("users").document(uid).update({"role": role})

# --- Send Password Reset ---
def send_password_reset(email):
    try:
        auth.send_password_reset_email(email)
        return True
    except Exception:
        return False

def restore_session():
    """Restore id_token from localStorage and verify session with backend."""
    if "id_token" not in st.session_state:
        storage = LocalStorage(key="id_token")
        token = storage.get("id_token")
        # log_info(f"auth_manager: token from localStorage: {token}")  # REMOVE for security
        if token:
            st.session_state["id_token"] = token
    # log_info(f"auth_manager: id_token in session_state: {st.session_state.get('id_token')}")  # REMOVE for security
    log_info(f"auth_manager: user_id in session_state: {st.session_state.get('user_id')}")
    # Token-based session restore: check /verify_session on app load
    if not st.session_state.get("user_id") and st.session_state.get("id_token"):
        log_info(f"Attempting /verify_session with id_token: (redacted)...")
        try:
            resp = requests.get(
                "http://localhost:5001/verify_session",
                headers={"Authorization": f"Bearer {st.session_state['id_token']}"},
                timeout=5
            )
            data = resp.json()
            log_info(f"/verify_session response: {data}")
            if data.get("success"):
                st.session_state["user_id"] = data.get("uid")
                st.session_state["profile"] = data.get("profile")
                st.session_state["role"] = data.get("profile", {}).get("role", "cadet")
                log_info(f"Login success, rerunning app.")
                st.rerun()
                print("[DEBUG] auth_manager: Called st.rerun() after session restore.")
            else:
                log_warning(f"/verify_session failed: {data}")
        except Exception as e:
            log_error(f"auth_manager: /verify_session error: {e}")
