# Performance Optimization Recommendations

## 1. Streamlit Caching Improvements

### Current Issues:
- Limited use of st.cache_resource and st.cache_data
- Repeated API calls without proper caching
- Heavy computations not cached

### Recommended Solutions:

```python
# Enhanced caching strategy
import streamlit as st
from functools import lru_cache
import hashlib

@st.cache_resource
def get_gemini_model():
    """Cache the Gemini model instance"""
    return setup_gemini()

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cached_response(prompt_hash: str, prompt: str):
    """Cache API responses to avoid repeated calls"""
    model, _ = get_gemini_model()
    return get_ncc_response(model, None, prompt)

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_syllabus_data():
    """Cache syllabus data"""
    return read_json_file(Config.SYLLABUS_PATH)

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def get_user_progress(user_id: str):
    """Cache user progress data"""
    return firestore_db.collection("users").document(user_id).get()

# Implement prompt hashing for cache keys
def hash_prompt(prompt: str) -> str:
    return hashlib.md5(prompt.encode()).hexdigest()
```

## 2. Database Query Optimization

```python
# Implement pagination for large datasets
def get_paginated_users(page_size=20, last_doc=None):
    query = firestore_db.collection("users").limit(page_size)
    if last_doc:
        query = query.start_after(last_doc)
    return query.stream()

# Batch operations for better performance
def batch_update_users(updates: List[Dict]):
    batch = firestore_db.batch()
    for update in updates:
        doc_ref = firestore_db.collection("users").document(update['uid'])
        batch.update(doc_ref, update['data'])
    batch.commit()
```

## 3. Asset Optimization

```python
# Implement image optimization
from PIL import Image
import io

@st.cache_data
def optimize_image(image_path: str, max_size=(800, 600)) -> str:
    """Optimize images for web display"""
    with Image.open(image_path) as img:
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format='WEBP', quality=85)
        return base64.b64encode(buffer.getvalue()).decode()
```

## 4. Session State Optimization

```python
# Implement session state cleanup
def cleanup_session_state():
    """Remove unnecessary session state variables"""
    keys_to_remove = [k for k in st.session_state.keys() 
                     if k.startswith('temp_') and 
                     k not in st.session_state.get('active_keys', [])]
    for key in keys_to_remove:
        del st.session_state[key]

# Call cleanup on app start
if 'app_initialized' not in st.session_state:
    cleanup_session_state()
    st.session_state.app_initialized = True
```
