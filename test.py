import pyrebase

firebaseConfig = {
    # your Firebase config here
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
user = auth.sign_in_with_email_and_password("jams9226@gmail.com", "SJAM9226")
id_token = user['idToken']