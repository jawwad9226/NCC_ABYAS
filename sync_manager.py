import os
import json
import logging
from typing import Dict, Any, List
from pathlib import Path
import streamlit as st

SYNC_QUEUE_FILE = os.path.join("data", "offline_queue.json")

# --- Utility: Read/Write Offline Queue ---
def load_offline_queue() -> List[Dict[str, Any]]:
    if os.path.exists(SYNC_QUEUE_FILE):
        with open(SYNC_QUEUE_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return []
    return []

def save_offline_queue(queue: List[Dict[str, Any]]):
    with open(SYNC_QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f)

# --- Add to Queue ---
def queue_for_sync(data: Dict[str, Any], data_type: str):
    queue = load_offline_queue()
    queue.append({"type": data_type, "data": data})
    save_offline_queue(queue)

# --- Sync to Firestore ---
def sync_to_cloud():
    from firebase_admin import firestore
    firestore_db = firestore.client()
    user_id = st.session_state.get("user_id")
    if not user_id:
        return 0
    queue = load_offline_queue()
    synced = 0
    new_queue = []
    for item in queue:
        # Skip and remove empty data items
        if not item.get("data"):
            continue
        try:
            if item["type"] == "quiz_metadata":
                firestore_db.collection("users").document(user_id).collection("quiz_metadata").add(item["data"])
                synced += 1
            elif item["type"] == "progress_summary":
                firestore_db.collection("users").document(user_id).collection("progress").document("summary").set(item["data"], merge=True)
                synced += 1
            elif item["type"] == "bookmark":
                firestore_db.collection("users").document(user_id).collection("bookmarks").add(item["data"])
                synced += 1
            else:
                new_queue.append(item)  # Unknown type, keep in queue
        except Exception as e:
            logging.warning(f"Sync failed for {item['type']}: {e}")
            new_queue.append(item)
    save_offline_queue(new_queue)
    return synced

# --- UI Sync Status ---
def show_sync_status():
    queue = load_offline_queue()
    if not queue:
        st.success("✅ All data synced to cloud.")
    else:
        st.warning(f"⚠️ {len(queue)} items pending sync (offline or error). Will sync when online.")
