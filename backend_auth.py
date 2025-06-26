from flask import Flask, request, jsonify
from auth_manager import login_user, get_user_profile
from firebase_admin import auth as admin_auth
from utils.logging_utils import log_info, log_warning, log_error
from ncc_utils import read_history
import os

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    result = login_user(email, password)
    debug_info = {}
    if result['success']:
        id_token = data.get('idToken')
        try:
            decoded_token = admin_auth.verify_id_token(id_token)
            uid = decoded_token.get('uid')
        except Exception as e:
            log_warning(f"Invalid ID token for {email}: {str(e)}")
            return jsonify({'success': False, 'error': 'Invalid ID token'}), 401
        # Hybrid storage debug: check where data exists
        chat_local = read_history("chat")
        quiz_local = read_history("quiz")
        quiz_score_local = read_history("quiz_score")
        debug_info['chat_local_count'] = len(chat_local) if isinstance(chat_local, list) else 0
        debug_info['quiz_local_count'] = len(quiz_local) if isinstance(quiz_local, list) else 0
        debug_info['quiz_score_local'] = bool(quiz_score_local)
        # Try to fetch cloud data (Firestore)
        try:
            from firebase_admin import firestore
            firestore_db = firestore.client()
            chat_cloud = firestore_db.collection("users").document(uid).collection("chat_history").stream()
            quiz_cloud = firestore_db.collection("users").document(uid).collection("quiz_history").stream()
            quiz_score_cloud = firestore_db.collection("users").document(uid).collection("progress").document("summary").get()
            debug_info['chat_cloud_count'] = len([doc for doc in chat_cloud])
            debug_info['quiz_cloud_count'] = len([doc for doc in quiz_cloud])
            debug_info['quiz_score_cloud'] = quiz_score_cloud.exists
        except Exception as e:
            debug_info['cloud_error'] = str(e)
        log_info(f"User {email} logged in successfully. Hybrid debug: {debug_info}")
        return jsonify({'success': True, 'profile': result['profile'], 'idToken': id_token, 'hybrid_debug': debug_info})
    else:
        log_warning(f"Failed login attempt for {email}: {result['error']}")
        return jsonify({'success': False, 'error': result['error']}), 401

# Token-based session verification endpoint
@app.route('/verify_session', methods=['GET'])
def verify_session():
    auth_header = request.headers.get('Authorization', None)
    if not auth_header or not auth_header.startswith('Bearer '):
        log_warning("Missing or invalid Authorization header in /verify_session")
        return jsonify({'success': False, 'error': 'Missing or invalid Authorization header'}), 401
    id_token = auth_header.split(' ')[1]
    debug_info = {}
    try:
        decoded_token = admin_auth.verify_id_token(id_token)
        uid = decoded_token.get('uid')
        profile = get_user_profile(uid)
        # Hybrid storage debug: check where data exists
        chat_local = read_history("chat")
        quiz_local = read_history("quiz")
        quiz_score_local = read_history("quiz_score")
        debug_info['chat_local_count'] = len(chat_local) if isinstance(chat_local, list) else 0
        debug_info['quiz_local_count'] = len(quiz_local) if isinstance(quiz_local, list) else 0
        debug_info['quiz_score_local'] = bool(quiz_score_local)
        try:
            from firebase_admin import firestore
            firestore_db = firestore.client()
            chat_cloud = firestore_db.collection("users").document(uid).collection("chat_history").stream()
            quiz_cloud = firestore_db.collection("users").document(uid).collection("quiz_history").stream()
            quiz_score_cloud = firestore_db.collection("users").document(uid).collection("progress").document("summary").get()
            debug_info['chat_cloud_count'] = len([doc for doc in chat_cloud])
            debug_info['quiz_cloud_count'] = len([doc for doc in quiz_cloud])
            debug_info['quiz_score_cloud'] = quiz_score_cloud.exists
        except Exception as e:
            debug_info['cloud_error'] = str(e)
        log_info(f"Session verified for user: {uid}. Hybrid debug: {debug_info}")
        return jsonify({'success': True, 'profile': profile, 'uid': uid, 'hybrid_debug': debug_info})
    except Exception as e:
        log_warning(f"Token verification failed: {str(e)}")
        return jsonify({'success': False, 'error': 'Invalid or expired token'}), 401

@app.route('/register_profile', methods=['POST'])
def register_profile():
    data = request.json
    uid = data.get('uid')
    name = data.get('name')
    reg_no = data.get('reg_no')
    email = data.get('email')
    mobile = data.get('mobile')
    if not all([uid, name, reg_no, email, mobile]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    try:
        from datetime import datetime
        from firebase_admin import firestore
        firestore_db = firestore.client()
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
        return jsonify({'success': True})
    except Exception as e:
        log_error(f"Failed to create Firestore profile for {email}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    import os
    import sys
    port = int(os.environ.get("PORT", 5001))
    if not os.environ.get('WERKZEUG_RUN_MAIN'):
        print("\033[93m[WARNING] You are running the backend without HTTPS. For production, use a WSGI server (gunicorn/uwsgi) behind HTTPS.\033[0m", file=sys.stderr)
    app.run(host='0.0.0.0', port=port, debug=False)
