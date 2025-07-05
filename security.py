"""
Security and input validation module for NCC ABYAS
Provides comprehensive input sanitization, validation, and rate limiting
"""
import re
import time
import hashlib
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
import streamlit as st
from functools import wraps
import html

class SecurityValidator:
    """Comprehensive security validation and sanitization"""
    
    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        r'<script.*?>.*?</script>',  # Script tags
        r'javascript:',              # JavaScript URLs
        r'vbscript:',               # VBScript URLs
        r'onload\s*=',              # Event handlers
        r'onerror\s*=',
        r'onclick\s*=',
        r'onmouseover\s*=',
        r'<iframe.*?>',             # Iframes
        r'<object.*?>',             # Objects
        r'<embed.*?>',              # Embeds
        r'<link.*?>',               # Links (potential CSS injection)
        r'<meta.*?>',               # Meta tags
        r'eval\s*\(',               # eval() calls
        r'setTimeout\s*\(',         # setTimeout calls
        r'setInterval\s*\(',        # setInterval calls
    ]
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r'union\s+select',
        r'drop\s+table',
        r'delete\s+from',
        r'insert\s+into',
        r'update\s+set',
        r'exec\s*\(',
        r'sp_\w+',
        r'xp_\w+',
        r';\s*--',
        r'\/\*.*?\*\/',
    ]
    
    @classmethod
    def sanitize_input(cls, input_value: Any, max_length: int = 1000) -> str:
        """
        Sanitize user input to prevent XSS and injection attacks
        
        Args:
            input_value: Input to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
        """
        if input_value is None:
            return ""
        
        # Convert to string and limit length
        text = str(input_value)[:max_length]
        
        # HTML escape to prevent XSS
        text = html.escape(text, quote=True)
        
        # Remove dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Check for SQL injection attempts
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                raise ValueError("Potentially malicious input detected")
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Validate email format"""
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email)) and len(email) <= 254
    
    @classmethod
    def validate_password(cls, password: str) -> Dict[str, Any]:
        """
        Validate password strength
        
        Returns:
            Dict with validation results
        """
        if not password:
            return {"valid": False, "message": "Password is required"}
        
        issues = []
        
        if len(password) < 8:
            issues.append("Password must be at least 8 characters")
        
        if len(password) > 128:
            issues.append("Password too long (max 128 characters)")
        
        if not re.search(r'[A-Z]', password):
            issues.append("Password must contain uppercase letter")
        
        if not re.search(r'[a-z]', password):
            issues.append("Password must contain lowercase letter")
        
        if not re.search(r'\d', password):
            issues.append("Password must contain number")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            issues.append("Password must contain special character")
        
        return {
            "valid": len(issues) == 0,
            "message": "; ".join(issues) if issues else "Password is strong",
            "issues": issues
        }
    
    @classmethod
    def validate_ncc_reg_no(cls, reg_no: str) -> bool:
        """Validate NCC registration number format"""
        if not reg_no:
            return False
        
        # Common NCC reg number patterns (adjust as needed)
        patterns = [
            r'^\d{2}[A-Z]{2}\d{8}$',  # 2 digits + 2 letters + 8 digits
            r'^[A-Z]{2}\d{10}$',      # 2 letters + 10 digits
            r'^\d{12}$',              # 12 digits
        ]
        
        reg_no = reg_no.upper().strip()
        return any(re.match(pattern, reg_no) for pattern in patterns)
    
    @classmethod
    def validate_mobile(cls, mobile: str) -> bool:
        """Validate Indian mobile number"""
        if not mobile:
            return False
        
        # Remove spaces, dashes, and parentheses
        mobile = re.sub(r'[\s\-\(\)]', '', mobile)
        
        # Remove country code if present
        if mobile.startswith('+91'):
            mobile = mobile[3:]
        elif mobile.startswith('91') and len(mobile) == 12:
            mobile = mobile[2:]
        
        # Check if it's a valid 10-digit Indian mobile number
        return bool(re.match(r'^[6-9]\d{9}$', mobile))
    
    @classmethod
    def validate_input(cls, input_value: str, input_type: str = "text", max_length: int = 1000) -> Dict[str, Any]:
        """
        Comprehensive input validation and sanitization
        
        Args:
            input_value: Input to validate
            input_type: Type of input (text, email, password, name, mobile)
            max_length: Maximum allowed length
            
        Returns:
            Dict with validation results
        """
        try:
            if input_value is None:
                return {
                    'valid': False,
                    'error': 'Input cannot be empty',
                    'sanitized': ''
                }
            
            # Convert to string
            text = str(input_value)
            
            # Basic length check
            if len(text) > max_length:
                return {
                    'valid': False,
                    'error': f'Input too long (max {max_length} characters)',
                    'sanitized': text[:max_length]
                }
            
            # Type-specific validation
            if input_type == "email":
                if not cls.validate_email(text):
                    return {
                        'valid': False,
                        'error': 'Invalid email format',
                        'sanitized': cls.sanitize_input(text, max_length)
                    }
            
            elif input_type == "password":
                password_check = cls.validate_password(text)
                if not password_check['valid']:
                    return {
                        'valid': False,
                        'error': password_check['message'],
                        'sanitized': text  # Don't sanitize passwords
                    }
                # For passwords, return as-is (don't sanitize)
                return {
                    'valid': True,
                    'error': None,
                    'sanitized': text
                }
            
            elif input_type == "mobile":
                if not cls.validate_mobile(text):
                    return {
                        'valid': False,
                        'error': 'Invalid mobile number format',
                        'sanitized': cls.sanitize_input(text, max_length)
                    }
            
            elif input_type == "name":
                if len(text.strip()) < 2:
                    return {
                        'valid': False,
                        'error': 'Name must be at least 2 characters',
                        'sanitized': cls.sanitize_input(text, max_length)
                    }
            
            # Sanitize the input
            sanitized = cls.sanitize_input(text, max_length)
            
            return {
                'valid': True,
                'error': None,
                'sanitized': sanitized
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Validation error: {str(e)}',
                'sanitized': cls.sanitize_input(str(input_value), max_length) if input_value else ''
            }


class RateLimiter:
    """Rate limiting implementation"""
    
    def __init__(self):
        if 'rate_limit_data' not in st.session_state:
            st.session_state.rate_limit_data = {}
    
    def check_rate_limit(self, key: str, max_requests: int = 10, window_minutes: int = 5) -> bool:
        """
        Check if a key is rate limited (alias for is_rate_limited for backward compatibility)
        
        Args:
            key: Unique identifier for rate limiting
            max_requests: Maximum requests allowed
            window_minutes: Time window in minutes
            
        Returns:
            True if rate limited, False otherwise
        """
        return self.is_rate_limited(key, max_requests, window_minutes)
    
    def is_rate_limited(self, key: str, max_requests: int = 10, window_minutes: int = 5) -> bool:
        """
        Check if a key is rate limited
        
        Args:
            key: Unique identifier for rate limiting
            max_requests: Maximum requests allowed
            window_minutes: Time window in minutes
            
        Returns:
            True if rate limited, False otherwise
        """
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)
        
        # Clean old entries
        if key in st.session_state.rate_limit_data:
            st.session_state.rate_limit_data[key] = [
                timestamp for timestamp in st.session_state.rate_limit_data[key]
                if timestamp > window_start
            ]
        else:
            st.session_state.rate_limit_data[key] = []
        
        # Check if rate limited
        if len(st.session_state.rate_limit_data[key]) >= max_requests:
            return True
        
        # Record this request
        st.session_state.rate_limit_data[key].append(now)
        return False
    
    def get_reset_time(self, key: str, window_minutes: int = 5) -> Optional[datetime]:
        """Get when the rate limit resets for a key"""
        if key not in st.session_state.rate_limit_data:
            return None
        
        timestamps = st.session_state.rate_limit_data[key]
        if not timestamps:
            return None
        
        oldest_timestamp = min(timestamps)
        return oldest_timestamp + timedelta(minutes=window_minutes)

def rate_limit(max_requests: int = 10, window_minutes: int = 5, key_func=None):
    """
    Decorator for rate limiting functions
    
    Args:
        max_requests: Maximum requests allowed
        window_minutes: Time window in minutes
        key_func: Function to generate rate limit key
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate rate limit key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                user_id = st.session_state.get('user_id', 'anonymous')
                key = f"{func.__name__}_{user_id}"
            
            # Check rate limit
            limiter = RateLimiter()
            if limiter.is_rate_limited(key, max_requests, window_minutes):
                reset_time = limiter.get_reset_time(key, window_minutes)
                reset_str = reset_time.strftime("%H:%M:%S") if reset_time else "soon"
                
                st.error(f"⚠️ Rate limit exceeded. Please try again after {reset_str}")
                return None
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def validate_chat_input(message: str) -> str:
    """Validate and sanitize chat input"""
    if not message or not message.strip():
        raise ValueError("Message cannot be empty")
    
    # Sanitize the input
    sanitized = SecurityValidator.sanitize_input(message, max_length=2000)
    
    if len(sanitized.strip()) < 3:
        raise ValueError("Message too short (minimum 3 characters)")
    
    return sanitized

def validate_quiz_answer(answer: str) -> str:
    """Validate and sanitize quiz answer"""
    if not answer:
        raise ValueError("Answer cannot be empty")
    
    # Sanitize the input
    sanitized = SecurityValidator.sanitize_input(answer, max_length=500)
    
    return sanitized

def validate_user_registration(name: str, email: str, mobile: str, reg_no: str, password: str) -> Dict[str, Any]:
    """
    Comprehensive user registration validation
    
    Returns:
        Dict with validation results
    """
    errors = []
    
    # Validate name
    if not name or len(name.strip()) < 2:
        errors.append("Name must be at least 2 characters")
    elif len(name) > 100:
        errors.append("Name too long (max 100 characters)")
    
    # Validate email
    if not SecurityValidator.validate_email(email):
        errors.append("Invalid email format")
    
    # Validate mobile
    if not SecurityValidator.validate_mobile(mobile):
        errors.append("Invalid mobile number (use Indian format)")
    
    # Validate registration number
    if not SecurityValidator.validate_ncc_reg_no(reg_no):
        errors.append("Invalid NCC registration number format")
    
    # Validate password
    password_check = SecurityValidator.validate_password(password)
    if not password_check["valid"]:
        errors.append(password_check["message"])
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "sanitized_data": {
            "name": SecurityValidator.sanitize_input(name, 100),
            "email": email.lower().strip(),
            "mobile": re.sub(r'[\s\-\(\)]', '', mobile),
            "reg_no": SecurityValidator.sanitize_input(reg_no, 20),
        }
    }

def secure_chat_request(message: str):
    """Legacy function - use secure_chat_input instead"""
    return secure_chat_input(message)

def secure_login_attempt(email: str, password: str):
    """Legacy function - use secure_login_input instead"""
    return secure_login_input(email, password)

def secure_login_input(email: str, password: str) -> Dict[str, Any]:
    """Secure and validate login input"""
    try:
        validator = SecurityValidator()
        
        # Validate email
        email_result = validator.validate_input(email, input_type="email")
        if not email_result['valid']:
            return {
                'valid': False,
                'error': email_result['error'],
                'email': email,
                'password': ''
            }
        
        # Validate password (basic validation, not as strict as registration)
        if not password or len(password) < 6:
            return {
                'valid': False,
                'error': 'Password must be at least 6 characters',
                'email': email_result['sanitized'],
                'password': ''
            }
        
        return {
            'valid': True,
            'error': None,
            'email': email_result['sanitized'],
            'password': password  # Don't sanitize password for login
        }
        
    except Exception as e:
        return {
            'valid': False,
            'error': f"Login validation error: {str(e)}",
            'email': email,
            'password': ''
        }

def secure_registration_input(name: str, email: str, mobile: str, reg_no: str, password: str) -> Dict[str, Any]:
    """Secure and validate registration input"""
    try:
        validator = SecurityValidator()
        
        # Validate all inputs
        name_result = validator.validate_input(name, input_type="name")
        email_result = validator.validate_input(email, input_type="email")
        mobile_result = validator.validate_input(mobile, input_type="mobile")
        reg_no_result = validator.validate_input(reg_no, input_type="text")
        password_result = validator.validate_input(password, input_type="password")
        
        # Collect all errors
        errors = []
        if not name_result['valid']:
            errors.append(name_result['error'])
        if not email_result['valid']:
            errors.append(email_result['error'])
        if not mobile_result['valid']:
            errors.append(mobile_result['error'])
        if not reg_no_result['valid']:
            errors.append(reg_no_result['error'])
        if not password_result['valid']:
            errors.append(password_result['error'])
        
        if errors:
            return {
                'valid': False,
                'error': '; '.join(errors),
                'data': {}
            }
        
        return {
            'valid': True,
            'error': None,
            'data': {
                'name': name_result['sanitized'],
                'email': email_result['sanitized'],
                'mobile': mobile_result['sanitized'],
                'reg_no': reg_no_result['sanitized'],
                'password': password  # Don't sanitize password, just validate
            }
        }
        
    except Exception as e:
        return {
            'valid': False,
            'error': f"Validation error: {str(e)}",
            'data': {}
        }

def secure_quiz_input(quiz_input: str) -> Dict[str, Any]:
    """Secure and validate quiz input"""
    try:
        validator = SecurityValidator()
        
        # Validate quiz input (questions, answers, etc.)
        result = validator.validate_input(quiz_input, input_type="text")
        
        if not result['valid']:
            return {
                'valid': False,
                'error': result['error'],
                'input': quiz_input
            }
        
        return {
            'valid': True,
            'error': None,
            'input': result['sanitized']
        }
        
    except Exception as e:
        return {
            'valid': False,
            'error': f"Quiz input validation error: {str(e)}",
            'input': quiz_input
        }

def get_client_id() -> str:
    """Get a client identifier for rate limiting"""
    # In Streamlit, we can use session state
    if 'client_id' not in st.session_state:
        import uuid
        st.session_state.client_id = str(uuid.uuid4())
    return st.session_state.client_id

def secure_chat_input(message: str) -> Dict[str, Any]:
    """Secure and validate chat input"""
    try:
        validator = SecurityValidator()
        
        # Validate chat message
        result = validator.validate_input(message, input_type="text")
        
        if not result['valid']:
            return {
                'valid': False,
                'error': result['error'],
                'message': message
            }
        
        # Additional chat-specific validation
        if len(result['sanitized'].strip()) < 3:
            return {
                'valid': False,
                'error': 'Message too short (minimum 3 characters)',
                'message': message
            }
        
        if len(result['sanitized']) > 2000:
            return {
                'valid': False,
                'error': 'Message too long (maximum 2000 characters)',
                'message': message
            }
        
        return {
            'valid': True,
            'error': None,
            'message': result['sanitized']
        }
        
    except Exception as e:
        return {
            'valid': False,
            'error': f"Chat input validation error: {str(e)}",
            'message': message
        }

