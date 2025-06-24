import os
import json
from datetime import datetime

# Path to the chat history file (update if needed)
HISTORY_PATH = os.path.join(os.path.dirname(__file__), "data", "chat_history.json")

# Load old history
with open(HISTORY_PATH, 'r', encoding='utf-8') as f:
    old_history = json.load(f)

# Convert old format (role/content pairs) to new format (prompt/response pairs)
new_history = []
user_msg = None
for entry in old_history:
    if entry.get("role") == "user":
        user_msg = entry.get("content", "")
        timestamp = entry.get("timestamp", datetime.now().isoformat())
    elif entry.get("role") == "assistant" and user_msg is not None:
        assistant_msg = entry.get("content", "")
        new_history.append({
            "timestamp": timestamp,
            "prompt": user_msg,
            "response": assistant_msg
        })
        user_msg = None

# Save new history
with open(HISTORY_PATH, 'w', encoding='utf-8') as f:
    json.dump(new_history, f, ensure_ascii=False, indent=4)

print(f"Migrated {len(new_history)} chat entries to new format.")
