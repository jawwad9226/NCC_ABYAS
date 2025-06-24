# 🎖️ NCC AI Assistant

An intelligent AI-powered assistant designed for NCC (National Cadet Corps) cadets to enhance learning, exam preparation, and digital engagement.

## ✨ Features

- **👤 Profile Page:** Modern profile view with personal info, history, and progress dashboard tabs.
- **💬 Chat Assistant:** Interactive Q&A about NCC topics, real-time responses, and chat history.
- **🎯 Knowledge Quiz:** AI-generated quizzes, topic-based, with progress tracking and history.
- **📚 Syllabus Viewer:** Browse syllabus, search topics, and view the official NCC handbook PDF.
- **🎥 Video Guides:** Curated video library with categories, search, and playback.
- **📁 History Viewer:** Review chat and quiz history, clear/download logs.
- **📊 Progress Dashboard:** Visualize quiz performance, trends, and topic strengths.
- **🛡️ Admin Dashboard:** Manage users, roles, and view global stats (admin only).
- **Firebase Integration:** Secure login, registration, role management, and cloud data sync.
- **Modern UI/UX:** Floating chat button, sidebar profile, theme toggle, and accessibility.

## 🗂️ Directory Map

```text
├── main.py                  # App entry, navigation, and routing
├── config.py                # Centralized config (paths, constants)
├── profile_interface.py     # Profile page UI and logic
├── sidebar.py               # Sidebar profile header and navigation
├── chat_interface.py        # Chat assistant UI and logic
├── quiz_interface.py        # Quiz UI, logic, and state
├── syllabus_interface.py    # Syllabus and PDF viewer UI
├── video_guides_interface.py# Video guides UI
├── history_viewer.py        # Full history viewer UI
├── progress_dashboard.py    # Progress dashboard UI and analytics
├── admin_tools.py           # Admin dashboard and user management
├── auth_manager.py          # Firebase authentication logic
├── login_interface.py       # Login, registration, and password reset UI
├── syllabus_manager.py      # Syllabus data loading and search
├── utils.py                 # Shared utility functions
├── src/utils/               # Theming, error handling, preferences, UI components
├── data/                    # Static assets, SVGs, PDFs, and local data
│   ├── logo.svg, profile-icon.svg, chat-icon.svg
│   ├── Ncc-CadetHandbook.pdf
│   ├── syllabus.json, videos.json, ...
├── logs/                    # Application logs
├── requirements.txt         # Python dependencies
├── README.md                # Project documentation
```

## 🚀 Setup & Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/jawwad9226/ncc_ai_assistant.git
   cd ncc_ai_assistant
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Firebase:**

   - Add your Firebase credentials to `firebase_config.json`.
   - Ensure Firestore and Authentication are enabled in your Firebase project.

4. **Run the application:**

   ```bash
   streamlit run main.py
   ```

## 📋 Requirements

- Python 3.8+
- Streamlit
- Firebase Admin SDK, Pyrebase4
- Pandas, NumPy, PyPDF2, etc. (see requirements.txt)

## 🛡️ Security & Privacy

- User authentication and data are managed securely via Firebase.
- No plain-text passwords or sensitive info stored in code.

## 🤝 Contributing

Contributions are welcome! Please submit a Pull Request or open an Issue.

## 📄 License

MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- National Cadet Corps (NCC)
- Google AI & Firebase
- The open-source community

## ⚠️ Limitations & Known Issues

- Persistent login is limited: If you clear your browser storage or use incognito mode, you may need to log in again.
- Session may expire if the app reloads or updates.
- If you encounter login issues, try refreshing the page or logging in again.
- For best experience, use a modern browser and avoid private/incognito mode.
- We are actively working to improve reliability and user experience. Your feedback is welcome!

## 🛠️ Monitoring & Logging

- All critical user actions and errors are logged to `logs/app.log`.
- Log rotation is enabled to prevent logs from growing indefinitely (see `utils/logging_utils.py`).
- For production, consider using external log monitoring (e.g., Loggly, Papertrail, or cloud provider logging).

## 🔗 Help & Support

- For help, use the in-app feedback form or contact your NCC unit/support email.
- If you have trouble logging in or registering, use the 'Forgot Password?' link or contact support.
