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
        if token:
            st.session_state["id_token"] = token
    if not st.session_state.get("user_id") and st.session_state.get("id_token"):
        try:
            resp = requests.get(
                "http://localhost:5001/verify_session",
                headers={"Authorization": f"Bearer {st.session_state['id_token']}"},
                timeout=5
            )
            data = resp.json()
            if data.get("success"):
                st.session_state["user_id"] = data.get("uid")
                st.session_state["profile"] = data.get("profile")
                st.session_state["role"] = data.get("profile", {}).get("role", "cadet")
                st.rerun()
            else:
                pass  # Handle session verification failure silently
        except Exception as e:
            pass  # Handle exception silently
