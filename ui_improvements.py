# Mobile-First CSS Framework for Streamlit
# Add to main.py at the top after imports

MOBILE_CSS_FRAMEWORK = """
<style>
/* Mobile-first responsive framework */
:root {
  --primary-color: #6366F1;
  --primary-light: #A5B4FC;
  --primary-dark: #4338CA;
  --success-color: #10B981;
  --warning-color: #F59E0B;
  --error-color: #EF4444;
  --text-primary: #1F2937;
  --text-secondary: #6B7280;
  --bg-primary: #FFFFFF;
  --bg-secondary: #F9FAFB;
  --border-color: #E5E7EB;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --radius-sm: 0.375rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
}

/* Mobile-optimized touch targets */
@media (max-width: 768px) {
  .stButton > button {
    min-height: 48px !important;
    font-size: 16px !important;
    padding: 12px 16px !important;
    border-radius: var(--radius-md) !important;
    transition: all 0.2s ease !important;
  }
  
  .stSelectbox > div > div {
    min-height: 48px !important;
  }
  
  .stTextInput > div > div > input {
    font-size: 16px !important; /* Prevents zoom on iOS */
    min-height: 48px !important;
    padding: 12px !important;
  }
  
  .stTextArea textarea {
    font-size: 16px !important;
    min-height: 120px !important;
    padding: 12px !important;
  }
}

/* Enhanced chat interface */
.chat-container {
  max-height: calc(100vh - 200px);
  overflow-y: auto;
  padding: var(--spacing-md);
  scroll-behavior: smooth;
}

.chat-message {
  margin: var(--spacing-sm) 0;
  padding: var(--spacing-md);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.chat-message.user {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
  color: white;
  margin-left: 20%;
}

.chat-message.assistant {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  margin-right: 20%;
}

/* Improved loading states */
.loading-spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid rgba(var(--primary-color), 0.3);
  border-radius: 50%;
  border-top-color: var(--primary-color);
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Enhanced form styling */
.form-container {
  background: var(--bg-primary);
  padding: var(--spacing-xl);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  margin: var(--spacing-lg) 0;
}

/* Accessibility improvements */
.focus-visible {
  outline: 2px solid var(--primary-color) !important;
  outline-offset: 2px !important;
}

/* Dark mode support (future) */
@media (prefers-color-scheme: dark) {
  :root {
    --text-primary: #F9FAFB;
    --text-secondary: #D1D5DB;
    --bg-primary: #1F2937;
    --bg-secondary: #374151;
    --border-color: #4B5563;
  }
}
</style>
"""

st.markdown(MOBILE_CSS_FRAMEWORK, unsafe_allow_html=True)