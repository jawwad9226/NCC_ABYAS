"""
Global error handling and user feedback system for NCC ABYAS
Provides consistent error handling, user-friendly error messages, and feedback mechanisms
"""
import streamlit as st
import traceback
from typing import Optional, Callable, Any
from datetime import datetime
import logging
from utils.logging_utils import log_error, log_warning, log_info

class ErrorHandler:
    """Centralized error handling for the application"""
    
    @staticmethod
    def show_error(message: str, details: Optional[str] = None, show_contact: bool = True):
        """Show a user-friendly error message"""
        st.error(f"⚠️ {message}")
        
        if details:
            with st.expander("Technical Details", expanded=False):
                st.code(details, language='text')
        
        if show_contact:
            st.info("💡 If this problem persists, please report it using the feedback section.")
    
    @staticmethod
    def show_warning(message: str, icon: str = "⚠️"):
        """Show a warning message"""
        st.warning(f"{icon} {message}")
    
    @staticmethod
    def show_success(message: str, icon: str = "✅"):
        """Show a success message"""
        st.success(f"{icon} {message}")
    
    @staticmethod
    def show_info(message: str, icon: str = "ℹ️"):
        """Show an info message"""
        st.info(f"{icon} {message}")

def safe_execute(func: Callable, *args, error_message: str = "An error occurred", **kwargs) -> Any:
    """
    Safely execute a function with error handling
    Args:
        func: Function to execute
        error_message: User-friendly error message
        *args, **kwargs: Arguments to pass to the function
    Returns:
        Function result or None if error occurred
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        log_error(f"Error in {func.__name__}: {str(e)}")
        ErrorHandler.show_error(
            error_message,
            details=str(e)
        )
        return None

def handle_api_error(error: Exception, operation: str = "API call") -> str:
    """
    Handle API-specific errors with appropriate user messages
    Args:
        error: The exception that occurred
        operation: Description of the operation that failed
    Returns:
        User-friendly error message
    """
    error_str = str(error).lower()
    
    if "quota" in error_str or "429" in error_str:
        message = "⏳ API quota exceeded. Please try again in a few minutes."
        ErrorHandler.show_warning(message)
        return message
    elif "network" in error_str or "connection" in error_str:
        message = "🌐 Network connection issue. Please check your internet and try again."
        ErrorHandler.show_warning(message)
        return message
    elif "timeout" in error_str:
        message = "⏱️ Request timed out. Please try again."
        ErrorHandler.show_warning(message)
        return message
    elif "permission" in error_str or "unauthorized" in error_str:
        message = "🔒 Authentication error. Please log in again."
        ErrorHandler.show_error(message)
        return message
    else:
        message = f"❌ {operation} failed. Please try again."
        ErrorHandler.show_error(message, details=str(error))
        return message

def handle_validation_error(error: Exception, field_name: str = "input") -> str:
    """
    Handle validation errors with specific field guidance
    Args:
        error: The validation exception
        field_name: Name of the field that failed validation
    Returns:
        User-friendly error message
    """
    message = f"📝 Invalid {field_name}: {str(error)}"
    ErrorHandler.show_warning(message, icon="📝")
    return message

class UserFeedback:
    """Enhanced user feedback system"""
    
    @staticmethod
    def show_loading(message: str = "Loading..."):
        """Show loading feedback"""
        return st.spinner(message)
    
    @staticmethod
    def show_progress(message: str, progress: float):
        """Show progress feedback"""
        progress_bar = st.progress(progress)
        st.text(message)
        return progress_bar
    
    @staticmethod
    def show_toast(message: str, icon: str = "ℹ️"):
        """Show toast notification"""
        st.toast(f"{icon} {message}")
    
    @staticmethod
    def show_balloons():
        """Show celebration effect"""
        st.balloons()
    
    @staticmethod
    def confirm_action(message: str, key: str) -> bool:
        """Show confirmation dialog"""
        if f"confirm_{key}" not in st.session_state:
            st.session_state[f"confirm_{key}"] = False
        
        if not st.session_state[f"confirm_{key}"]:
            st.warning(f"⚠️ {message}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Confirm", key=f"confirm_yes_{key}"):
                    st.session_state[f"confirm_{key}"] = True
                    st.rerun()
            with col2:
                if st.button("❌ Cancel", key=f"confirm_no_{key}"):
                    return False
            return False
        else:
            # Reset confirmation state
            st.session_state[f"confirm_{key}"] = False
            return True

def with_error_boundary(func):
    """
    Decorator to wrap functions with error boundary
    Usage:
        @with_error_boundary
        def my_function():
            # Function code here
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log_error(f"Error in {func.__name__}: {str(e)}")
            ErrorHandler.show_error(
                f"An error occurred in {func.__name__.replace('_', ' ').title()}",
                details=str(e)
            )
            return None
    return wrapper

def setup_global_error_handler():
    """Setup global exception handler for Streamlit"""
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        log_error(f"Uncaught exception: {error_msg}")
        
        # Don't show technical details to users in production
        ErrorHandler.show_error(
            "An unexpected error occurred. Please refresh the page and try again.",
            show_contact=True
        )
    
    import sys
    sys.excepthook = handle_exception

# Enhanced form validation
class FormValidator:
    """Enhanced form validation with better error messages"""
    
    @staticmethod
    def validate_required_fields(fields: dict) -> list:
        """
        Validate required fields
        Args:
            fields: Dictionary of field_name: value pairs
        Returns:
            List of error messages
        """
        errors = []
        for field_name, value in fields.items():
            if not value or (isinstance(value, str) and not value.strip()):
                errors.append(f"📝 {field_name.replace('_', ' ').title()} is required")
        return errors
    
    @staticmethod
    def validate_email(email: str) -> Optional[str]:
        """Validate email format"""
        import re
        if not email:
            return "Email is required"
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return "Please enter a valid email address"
        return None
    
    @staticmethod
    def validate_password(password: str) -> Optional[str]:
        """Validate password strength"""
        if not password:
            return "Password is required"
        if len(password) < 6:
            return "Password must be at least 6 characters long"
        return None
    
    @staticmethod
    def validate_mobile(mobile: str) -> Optional[str]:
        """Validate mobile number"""
        import re
        if not mobile:
            return "Mobile number is required"
        if not re.match(r'^[6-9]\d{9}$', mobile):
            return "Please enter a valid 10-digit mobile number starting with 6-9"
        return None

# Initialize error handling
setup_global_error_handler()
