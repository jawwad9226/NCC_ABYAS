# Security Improvements for NCC ABYAS

## Current Security Analysis

### Strengths:
- Firebase Auth integration
- Role-based access control
- Environment variable usage for sensitive data
- Backend session verification

### Areas for Improvement:

## 1. Input Validation & Sanitization

```python
# Create: utils/validation.py
import re
from typing import Optional, Dict, Any
import bleach

class InputValidator:
    @staticmethod
    def validate_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_reg_no(reg_no: str) -> bool:
        # NCC registration number format validation
        pattern = r'^[A-Z]{2}\d{2}[A-Z]{2}\d{6}$'
        return bool(re.match(pattern, reg_no))
    
    @staticmethod
    def validate_mobile(mobile: str) -> bool:
        pattern = r'^[6-9]\d{9}$'  # Indian mobile number
        return bool(re.match(pattern, mobile))
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input to prevent XSS"""
        if not text:
            return ""
        # Remove potentially dangerous characters
        sanitized = bleach.clean(text, tags=[], strip=True)
        return sanitized.strip()
    
    @staticmethod
    def validate_chat_input(prompt: str) -> Dict[str, Any]:
        """Validate chat input for safety"""
        if not prompt or len(prompt.strip()) == 0:
            return {"valid": False, "error": "Empty prompt"}
        
        if len(prompt) > 1000:
            return {"valid": False, "error": "Prompt too long"}
        
        # Check for potential injection attempts
        dangerous_patterns = [
            r'<script.*?>',
            r'javascript:',
            r'onload=',
            r'onclick=',
            r'eval\(',
            r'document\.cookie'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                return {"valid": False, "error": "Invalid characters detected"}
        
        return {"valid": True, "sanitized": InputValidator.sanitize_input(prompt)}
```

## 2. Rate Limiting Enhancement

```python
# Create: utils/rate_limiter.py
from datetime import datetime, timedelta
from typing import Dict, Optional
import streamlit as st

class RateLimiter:
    def __init__(self):
        self.limits = {
            'chat': {'requests': 10, 'window': 300},  # 10 requests per 5 minutes
            'quiz': {'requests': 5, 'window': 600},   # 5 requests per 10 minutes
            'login': {'requests': 5, 'window': 900},  # 5 attempts per 15 minutes
            'registration': {'requests': 3, 'window': 3600}  # 3 attempts per hour
        }
    
    def is_rate_limited(self, user_id: str, action: str) -> Dict[str, Any]:
        """Check if user is rate limited for specific action"""
        if action not in self.limits:
            return {"limited": False}
        
        key = f"rate_limit_{action}_{user_id}"
        limit_config = self.limits[action]
        
        now = datetime.now()
        
        if key not in st.session_state:
            st.session_state[key] = []
        
        # Remove old requests outside the window
        window_start = now - timedelta(seconds=limit_config['window'])
        st.session_state[key] = [
            req_time for req_time in st.session_state[key] 
            if req_time > window_start
        ]
        
        # Check if limit exceeded
        if len(st.session_state[key]) >= limit_config['requests']:
            remaining_time = int((st.session_state[key][0] + timedelta(seconds=limit_config['window']) - now).total_seconds())
            return {
                "limited": True, 
                "remaining_time": max(0, remaining_time),
                "message": f"Rate limit exceeded. Try again in {remaining_time} seconds."
            }
        
        # Add current request
        st.session_state[key].append(now)
        return {"limited": False}
```

## 3. Data Encryption

```python
# Create: utils/encryption.py
from cryptography.fernet import Fernet
import os
import base64

class DataEncryption:
    def __init__(self):
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)
    
    def _get_or_create_key(self) -> bytes:
        """Get encryption key from environment or generate new one"""
        key_str = os.environ.get('ENCRYPTION_KEY')
        if key_str:
            return base64.urlsafe_b64decode(key_str.encode())
        else:
            # For development only - in production, use a fixed key
            return Fernet.generate_key()
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data before storage"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data after retrieval"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
```

## 4. Enhanced Logging & Monitoring

```python
# Enhance: utils/logging_utils.py
import logging
from datetime import datetime
import json
from typing import Dict, Any

class SecurityLogger:
    def __init__(self):
        self.security_logger = logging.getLogger('security')
        handler = logging.FileHandler('logs/security.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.security_logger.addHandler(handler)
        self.security_logger.setLevel(logging.INFO)
    
    def log_login_attempt(self, email: str, success: bool, ip: str = None):
        """Log login attempts for security monitoring"""
        self.security_logger.info(json.dumps({
            'event': 'login_attempt',
            'email': email,
            'success': success,
            'ip': ip,
            'timestamp': datetime.now().isoformat()
        }))
    
    def log_suspicious_activity(self, user_id: str, activity: str, details: Dict[str, Any]):
        """Log suspicious activities"""
        self.security_logger.warning(json.dumps({
            'event': 'suspicious_activity',
            'user_id': user_id,
            'activity': activity,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }))
```
