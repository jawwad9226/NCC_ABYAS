"""
Streamlit UI for login, registration, and forgot password for NCC Cadet Platform.
"""
import streamlit as st
import pyrebase
import json
import requests
import re
import time
from streamlit_browser_storage.local_storage import LocalStorage
from feedback_interface import show_feedback_section
from utils.logging_utils import log_info, log_warning, log_error
from security import SecurityValidator, RateLimiter, secure_chat_input, secure_login_input
from error_handling import ErrorHandler, handle_api_error, FormValidator

def ensure_pyrebase_initialized():
    if 'pyrebase_auth' not in st.session_state:
        with open("firebase_web_config.json") as f:
            pyrebase_config = json.load(f)
        firebase = pyrebase.initialize_app(pyrebase_config)
        st.session_state['pyrebase_auth'] = firebase.auth()
        st.session_state['pyrebase_db'] = firebase.database()

def show_login():
    ensure_pyrebase_initialized()
    auth = st.session_state['pyrebase_auth']
    st.title("NCC Cadet Login")
    email = st.text_input("Email", key="login_email")
    col1, col2 = st.columns([3,1])
    with col1:
        password = st.text_input("Password", type="password", key="login_password")
    with col2:
        st.markdown('<div style="height:2.2em"></div>', unsafe_allow_html=True)
        st.markdown('<a href="#" style="color:#6366F1;float:right;font-size:0.95em;" onclick="window.dispatchEvent(new CustomEvent(\'streamlit_select_forgot\'))">Forgot Password?</a>', unsafe_allow_html=True)
    remember_me = st.checkbox("Remember me", value=True, help="Keep me logged in on this device")

    login_error = st.session_state.pop("login_error", None)
    login_success = st.session_state.pop("login_success", None)
    if login_error:
        st.error(login_error)
    if login_success:
        st.success(login_success)

    if st.button("Login", key="login_btn"):
        if not email or not password:
            st.session_state["login_error"] = "Please enter both email and password."
            st.rerun()
        else:
            # Security validation
            validation_result = secure_login_input(email, password)
            if not validation_result['valid']:
                ErrorHandler.show_warning(f"Login validation failed: {validation_result['error']}")
                log_warning(f"Login validation failed for {email}: {validation_result['error']}")
                st.rerun()
                return
            
            # Use sanitized inputs
            clean_email = validation_result['email']
            clean_password = validation_result['password']
            
            try:
                user = auth.sign_in_with_email_and_password(clean_email, clean_password)
                id_token = user['idToken']
                resp = requests.post(
                    "https://nccabyas.up.railway.app/login",
                    json={"idToken": id_token, "email": clean_email, "password": clean_password},
                    timeout=10
                )
                data = resp.json()
                if data.get("success"):
                    st.session_state["user_id"] = user.get("localId")
                    st.session_state["profile"] = data["profile"]
                    st.session_state["role"] = data["profile"].get("role", "cadet")
                    st.session_state["id_token"] = id_token
                    st.session_state["just_logged_in"] = True
                    st.session_state["login_success"] = "Login successful!"
                    log_info(f"Login successful for user: {clean_email}")
                    st.rerun()
                else:
                    st.session_state["login_error"] = f"Login failed: {data.get('error', 'Unknown error')}"
                    log_warning(f"Login failed for user: {clean_email}, error: {data.get('error')}")
                    st.rerun()
            except Exception as e:
                st.session_state["login_error"] = f"Login error: {e}"
                log_error(f"Login error for user: {clean_email}, error: {e}")
                st.rerun()

    if st.button("Register as Cadet"):
        st.session_state["auth_page"] = "register"
        st.rerun()

    # JS event handler for the hyperlink
    st.markdown("""
    <script>
    window.addEventListener('streamlit_select_forgot', function() {
        window.parent.postMessage({isStreamlitMessage: true, type: 'streamlit:setComponentValue', key: 'show_forgot', value: true}, '*');
    });
    </script>
    """, unsafe_allow_html=True)
    if st.session_state.get("show_forgot"):
        st.session_state["auth_page"] = "forgot"
        st.rerun()

    # --- App Warnings & Limitations ---
    st.markdown("""
    <div style='margin-top:2em; padding:1.2em; border-radius:10px; background:linear-gradient(90deg,#fffbe6 70%,#fef3c7 100%); border:2px solid #f59e42; box-shadow:0 2px 8px #f59e4222;'>
        <b style='color:#b45309;font-size:1.1em;'>⚠️ App Limitations & Warnings:</b><br>
        <ul style='margin-bottom:0; color:#92400e; font-size:1.05em; line-height:1.6;'>
            <li><b>Chat and Quiz History</b> is stored only on your device for privacy and storage efficiency. If you clear your browser storage or switch devices, your detailed chat and quiz history will be lost.</li>
            <li><b>Only your profile, progress, and summary data</b> are stored in the cloud for cross-device access.</li>
            <li>If you reload, logout, or use a different browser/device, your local history will not be available unless you export/import it.</li>
            <li>For best results, regularly export your history if you want to keep a backup.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def show_registration():
    ensure_pyrebase_initialized()
    auth = st.session_state['pyrebase_auth']
    db = st.session_state['pyrebase_db']
    st.title("NCC Cadet Registration")
    name = st.text_input("Full Name", key="reg_name")
    reg_no = st.text_input("NCC Regimental Number", key="reg_regno")
    email = st.text_input("Email", key="reg_email")
    mobile = st.text_input("Mobile Number", key="reg_mobile")
    password = st.text_input("Password", type="password", key="reg_password")
    confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")

    reg_error = st.session_state.pop("reg_error", None)
    reg_success = st.session_state.pop("reg_success", None)
    if reg_error:
        st.error(reg_error)
    if reg_success:
        st.success(reg_success)

    if st.button("Register", key="register_btn"):
        # Security validation first
        from security import secure_registration_input
        validation_result = secure_registration_input(name, email, mobile, reg_no, password)
        
        if not validation_result['valid']:
            st.session_state["reg_error"] = validation_result['error']
            st.rerun()
            return
        
        # Use sanitized inputs
        clean_name = validation_result['name']
        clean_email = validation_result['email'] 
        clean_mobile = validation_result['mobile']
        clean_reg_no = validation_result['reg_no']
        clean_password = validation_result['password']
        
        # Additional validation
        if password != confirm:
            st.session_state["reg_error"] = "Passwords do not match."
            st.rerun()
            return
            
        # Check for unique reg_no and mobile
        existing_users = db.child("users").get().val() or {}
        reg_no_exists = any(u.get("reg_no", "").upper() == clean_reg_no.upper() for u in existing_users.values())
        mobile_exists = any(u.get("mobile", "") == clean_mobile for u in existing_users.values())
        
        if reg_no_exists:
            st.session_state["reg_error"] = "This regimental number is already registered."
            st.rerun()
        elif mobile_exists:
            st.session_state["reg_error"] = "This mobile number is already registered."
            st.rerun()
        else:
            try:
                user = auth.create_user_with_email_and_password(clean_email, clean_password)
                uid = user['localId']
                profile = {
                    "name": clean_name,
                    "reg_no": clean_reg_no.upper(),
                    "email": clean_email,
                    "mobile": clean_mobile,
                    "role": "cadet"
                }
                db.child("users").child(uid).set(profile)
                # --- Create Firestore profile via backend ---
                resp = requests.post(
                    "https://nccabyas.up.railway.app/register_profile",
                    json={
                        "uid": uid,
                        "name": clean_name,
                        "reg_no": clean_reg_no.upper(),
                        "email": clean_email,
                        "mobile": clean_mobile
                    },
                    timeout=10
                )
                data = resp.json()
                if data.get("success"):
                    # --- Automatic login after successful registration ---
                    try:
                        user = auth.sign_in_with_email_and_password(clean_email, clean_password)
                        id_token = user['idToken']
                        login_resp = requests.post(
                            "https://nccabyas.up.railway.app/login",
                            json={"idToken": id_token, "email": clean_email, "password": clean_password},
                            timeout=10
                        )
                        login_data = login_resp.json()
                        if login_data.get("success"):
                            st.session_state["user_id"] = user.get("localId")
                            st.session_state["profile"] = login_data["profile"]
                            st.session_state["role"] = login_data["profile"].get("role", "cadet")
                            st.session_state["id_token"] = id_token
                            st.session_state["login_success"] = "Registration and login successful!"
                            log_info(f"Auto-login after registration for user: {email}")
                            st.rerun()
                        else:
                            st.session_state["reg_success"] = "Registration successful! Please login. (Auto-login failed)"
                            log_warning(f"Auto-login failed after registration for user: {email}, error: {login_data.get('error')}")
                    except Exception as e:
                        st.session_state["reg_success"] = "Registration successful! Please login. (Auto-login error)"
                        log_error(f"Auto-login error after registration for user: {email}, error: {e}")
                else:
                    st.session_state["reg_error"] = f"Registration failed (profile): {data.get('error', 'Unknown error')}"
                    log_error(f"Registration failed for user: {email}, error: {data.get('error')}")
                st.rerun()
            except Exception as e:
                # Handle Firebase Auth errors with user-friendly messages
                error_msg = str(e)
                if 'EMAIL_EXISTS' in error_msg or 'email address is already in use' in error_msg:
                    st.session_state["reg_error"] = "This email is already registered. Please use a different email or login."
                elif 'WEAK_PASSWORD' in error_msg or 'Password should be at least' in error_msg:
                    st.session_state["reg_error"] = "Password is too weak. Please use a stronger password."
                elif 'INVALID_EMAIL' in error_msg or 'email address is badly formatted' in error_msg:
                    st.session_state["reg_error"] = "Invalid email address format."
                else:
                    st.session_state["reg_error"] = f"Registration failed: {e}"
                log_error(f"Registration failed for user: {email}, error: {e}")
                st.rerun()
    if st.button("Back to Login"):
        st.session_state["auth_page"] = "login"
        st.rerun()

def show_forgot_password():
    ensure_pyrebase_initialized()
    auth = st.session_state['pyrebase_auth']
    st.title("Forgot Password")
    email = st.text_input("Registered Email", key="forgot_email")
    forgot_error = st.session_state.pop("forgot_error", None)
    forgot_success = st.session_state.pop("forgot_success", None)
    if forgot_error:
        st.error(forgot_error)
    if forgot_success:
        st.success(forgot_success)
    if st.button("Send Password Reset Email"):
        if not email:
            st.session_state["forgot_error"] = "Please enter your registered email."
            st.rerun()
        else:
            try:
                auth.send_password_reset_email(email)
                st.session_state["forgot_success"] = "Password reset email sent!"
                log_info(f"Password reset email sent for: {email}")
                st.rerun()
            except Exception as e:
                st.session_state["forgot_error"] = f"Password reset failed: {e}"
                log_error(f"Password reset failed for: {email}, error: {e}")
                st.rerun()
    if st.button("Back to Login", key="forgot_back"):
        st.session_state["auth_page"] = "login"
        st.rerun()

def logout():
    """Logs out the user by clearing session state and localStorage, then reruns the app."""
    log_info(f"User {st.session_state.get('user_id', 'unknown')} logging out.")
    # Clear Streamlit session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    # Clear localStorage id_token
    storage = LocalStorage(key="id_token")
    storage.remove("id_token")
    st.session_state["wait_for_logout"] = True
    st.rerun()

def login_interface():
    ensure_pyrebase_initialized()

    # Navigation state: 'login', 'register', 'forgot'
    if "auth_page" not in st.session_state:
        st.session_state["auth_page"] = "login"

    if st.session_state["auth_page"] == "login":
        show_login()
    elif st.session_state["auth_page"] == "register":
        show_registration()
    elif st.session_state["auth_page"] == "forgot":
        show_forgot_password()
