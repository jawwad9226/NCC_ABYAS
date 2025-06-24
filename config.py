import os

# Base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Firebase config
FIREBASE_CONFIG_PATH = os.path.join(BASE_DIR, "firebase_config.json")

# PDF and static assets
NCC_HANDBOOK_PDF = os.path.join(BASE_DIR, "Ncc-CadetHandbook.pdf")
PROFILE_ICON = os.path.join(DATA_DIR, "profile-icon.svg")
LOGO_SVG = os.path.join(DATA_DIR, "logo.svg")
CHAT_ICON = os.path.join(DATA_DIR, "chat-icon.svg")

# Other constants
APP_TITLE = "NCC ABYAS"

# Add more as needed
