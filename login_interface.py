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

    if st.button("Login", key="login_btn"):
        if not email or not password:
            st.warning("Please enter both email and password. If you forgot your password, click 'Forgot Password?' below.")
            log_warning("Login attempt with missing email or password.")
        else:
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                id_token = user['idToken']
                resp = requests.post(
                    "http://localhost:5001/login",
                    json={"idToken": id_token, "email": email, "password": password},
                    timeout=10
                )
                data = resp.json()
                if data.get("success"):
                    st.session_state["user_id"] = user.get("localId")
                    st.session_state["profile"] = data["profile"]
                    st.session_state["role"] = data["profile"].get("role", "cadet")
                    st.session_state["id_token"] = id_token
                    st.session_state["just_logged_in"] = True  # Set flag for JS save
                    st.success("Login successful!")
                    log_info(f"Login successful for user: {email}")
                    st.rerun()
                else:
                    st.error(f"Login failed: {data.get('error')}\nIf you need help, contact support or click 'Forgot Password?'.")
                    log_warning(f"Login failed for user: {email}, error: {data.get('error')}")
            except Exception as e:
                st.error(f"Login error: {e}\nIf you need help, contact support or click 'Forgot Password?'.")
                log_error(f"Login error for user: {email}, error: {e}")

    if st.button("Register as Cadet"):
        st.session_state["show_register"] = True
        st.info("If you have trouble registering, please contact your NCC unit or email support.")

    # JS event handler for the hyperlink
    st.markdown("""
    <script>
    window.addEventListener('streamlit_select_forgot', function() {
        window.parent.postMessage({isStreamlitMessage: true, type: 'streamlit:setComponentValue', key: 'show_forgot', value: true}, '*');
    });
    </script>
    """, unsafe_allow_html=True)
    if st.session_state.get("show_forgot"):
        st.session_state["show_forgot"] = False
        st.session_state["show_forgot"] = True
        st.rerun()

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
    if st.button("Register", key="register_btn"):
        # Validation
        if not all([name, reg_no, email, mobile, password, confirm]):
            st.warning("Please fill all fields.")
            log_warning("Registration attempt with missing fields.")
        elif password != confirm:
            st.warning("Passwords do not match.")
            log_warning("Registration attempt with password mismatch.")
        elif not re.match(r"^[A-Za-z0-9]+$", reg_no):
            st.warning("Regimental number must be alphanumeric.")
            log_warning("Registration attempt with invalid regimental number.")
        elif not re.match(r"^[6-9]\d{9}$", mobile):
            st.warning("Enter a valid 10-digit Indian mobile number.")
            log_warning("Registration attempt with invalid mobile number.")
        else:
            try:
                user = auth.create_user_with_email_and_password(email, password)
                uid = user['localId']
                profile = {
                    "name": name,
                    "reg_no": reg_no,
                    "email": email,
                    "mobile": mobile,
                    "role": "cadet"
                }
                db.child("users").child(uid).set(profile)
                st.success("Registration successful! Please log in.")
                st.session_state["show_register"] = False
                log_info(f"Registration successful for user: {email}")
            except Exception as e:
                st.error(f"Registration failed: {e}")
                log_error(f"Registration failed for user: {email}, error: {e}")
    if st.button("Back to Login"):
        st.session_state["show_register"] = False

def show_forgot_password():
    ensure_pyrebase_initialized()
    auth = st.session_state['pyrebase_auth']
    st.title("Forgot Password")
    email = st.text_input("Registered Email", key="forgot_email")
    if st.button("Send Password Reset Email"):
        if not email:
            st.warning("Please enter your registered email.")
            log_warning("Password reset attempt with missing email.")
            pass
        else:
            try:
                auth.send_password_reset_email(email)
                st.success("Password reset email sent. Check your inbox.")
                log_info(f"Password reset email sent for: {email}")
            except Exception as e:
                st.error("Failed to send password reset email. Check your email address.")
                log_error(f"Password reset failed for: {email}, error: {e}")
    if st.button("Back to Login", key="forgot_back"):
        st.session_state["show_forgot"] = False

def logout():
    """Logs out the user by clearing session state and localStorage, then reruns the app."""
    log_info(f"User {st.session_state.get('user_id', 'unknown')} logging out.")
    print("[DEBUG] logout: Clearing session state and localStorage.")
    # Clear Streamlit session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    print("[DEBUG] login_interface.py: Session state cleared by logout().")
    # Clear localStorage id_token
    storage = LocalStorage(key="id_token")
    storage.remove("id_token")
    st.write("")  # Force Streamlit to render the component
    st.session_state["wait_for_logout"] = True
    st.rerun()

def login_interface():
    ensure_pyrebase_initialized()

    # Only set id_token in localStorage after login, do not read from it here
    if st.session_state.get("just_logged_in") and st.session_state.get("id_token"):
        print(f"[DEBUG] login_interface: Setting id_token in localStorage: {st.session_state['id_token'][:10]}...")
        storage = LocalStorage(key="id_token")
        result = storage.set("id_token", st.session_state["id_token"])
        st.write("")  # Force Streamlit to render the component
        del st.session_state["just_logged_in"]
        st.session_state["wait_for_storage"] = True
        print("[DEBUG] login_interface: Waiting for localStorage to persist token.")
        return  # Let Streamlit rerun naturally

    if st.session_state.get("wait_for_storage"):
        print("[DEBUG] login_interface: wait_for_storage detected, clearing and rerunning.")
        del st.session_state["wait_for_storage"]
        st.rerun()
        return

    if st.session_state.get("wait_for_logout"):
        print("[DEBUG] login_interface: wait_for_logout detected, rerunning to show login.")
        del st.session_state["wait_for_logout"]
        st.rerun()
        return

    if st.session_state.get("user_id"):
        print(f"[DEBUG] login_interface: user_id present, login complete.")
        st.success(f"Logged in as {st.session_state['profile'].get('name', 'Cadet')}")
        if st.button("Logout", key="logout_btn"):
            logout()
        return
    if st.session_state.get("show_register"):
        show_registration()
        return
    if st.session_state.get("show_forgot"):
        show_forgot_password()
        return
    print(f"[DEBUG] login_interface: Showing login. user_id: {st.session_state.get('user_id')}, id_token: {st.session_state.get('id_token')}")
    show_login()
    show_limitations_note()  # Show limitations/info at the very end

def show_limitations_note():
    """Display a visible limitations/info note for users about session persistence and login."""
    st.info("""
    **Limitations & Important Notes:**
    - Persistent login is limited: If you clear your browser storage or use incognito mode, you may need to log in again.
    - Session may expire if the app reloads or updates.
    - If you encounter login issues, try refreshing the page or logging in again.
    - For best experience, use a modern browser and avoid private/incognito mode.
    - We are actively working to improve reliability and user experience. Your feedback is welcome!
    """)
