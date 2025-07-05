"""
Accessibility improvements for NCC ABYAS
Provides ARIA labels, keyboard navigation, screen reader support, and compliance features
"""
import streamlit as st

def inject_accessibility_css():
    """Inject accessibility-focused CSS improvements"""
    st.markdown("""
    <style>
    /* ===== ACCESSIBILITY ENHANCEMENTS ===== */
    
    /* Focus indicators for keyboard navigation */
    .stButton > button:focus,
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus,
    .stRadio > div > label:focus {
        outline: 3px solid #667eea !important;
        outline-offset: 2px !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* High contrast mode improvements */
    @media (prefers-contrast: high) {
        .stButton > button {
            border: 2px solid currentColor !important;
            background: ButtonFace !important;
            color: ButtonText !important;
        }
        
        .card {
            border: 2px solid CanvasText !important;
            background: Canvas !important;
            color: CanvasText !important;
        }
        
        .mobile-nav-button {
            border: 2px solid currentColor !important;
        }
    }
    
    /* Reduced motion preferences */
    @media (prefers-reduced-motion: reduce) {
        *,
        *::before,
        *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
            scroll-behavior: auto !important;
        }
        
        .loading-spinner {
            animation: none !important;
        }
    }
    
    /* Screen reader only content */
    .sr-only {
        position: absolute !important;
        width: 1px !important;
        height: 1px !important;
        padding: 0 !important;
        margin: -1px !important;
        overflow: hidden !important;
        clip: rect(0, 0, 0, 0) !important;
        white-space: nowrap !important;
        border: 0 !important;
    }
    
    /* Skip links for keyboard navigation */
    .skip-link {
        position: absolute;
        top: -40px;
        left: 6px;
        background: #667eea;
        color: white;
        padding: 8px;
        text-decoration: none;
        border-radius: 4px;
        z-index: 1000;
    }
    
    .skip-link:focus {
        top: 6px;
    }
    
    /* Improved form labels */
    .stTextInput > label,
    .stTextArea > label,
    .stSelectbox > label {
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
        color: #374151 !important;
    }
    
    /* ARIA live regions */
    .status-message {
        position: absolute;
        left: -10000px;
        width: 1px;
        height: 1px;
        overflow: hidden;
    }
    
    /* Color contrast improvements */
    .quiz-question {
        border-left-color: #2563eb !important; /* Better contrast blue */
    }
    
    .mobile-nav-button.active {
        background: rgba(37, 99, 235, 0.8) !important; /* Better contrast */
    }
    
    /* Text size and spacing for readability */
    body, .main {
        line-height: 1.6 !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        line-height: 1.3 !important;
        margin-bottom: 0.8rem !important;
    }
    
    p, li {
        margin-bottom: 0.6rem !important;
    }
    
    /* Touch target improvements for mobile accessibility */
    .stButton > button,
    .mobile-nav-button {
        min-width: 44px !important;
        min-height: 44px !important;
    }
    
    /* Error message accessibility */
    .stAlert[data-baseweb="notification"] {
        border-left: 4px solid currentColor !important;
        padding-left: 1rem !important;
    }
    
    /* Loading state accessibility */
    .loading-container[aria-live="polite"] {
        /* Ensure loading states are announced */
    }
    </style>
    """, unsafe_allow_html=True)

def add_skip_navigation():
    """Add skip navigation links for keyboard users"""
    st.markdown("""
    <a href="#main-content" class="skip-link">Skip to main content</a>
    <div id="main-content" tabindex="-1"></div>
    """, unsafe_allow_html=True)

def add_aria_live_region():
    """Add ARIA live region for dynamic content announcements"""
    st.markdown("""
    <div aria-live="polite" aria-atomic="false" class="status-message" id="status-messages"></div>
    <div aria-live="assertive" aria-atomic="true" class="status-message" id="error-messages"></div>
    """, unsafe_allow_html=True)

def announce_to_screen_reader(message: str, priority: str = "polite"):
    """Announce message to screen readers"""
    region_id = "status-messages" if priority == "polite" else "error-messages"
    st.markdown(f"""
    <script>
    document.getElementById('{region_id}').textContent = '{message}';
    setTimeout(() => {{
        document.getElementById('{region_id}').textContent = '';
    }}, 1000);
    </script>
    """, unsafe_allow_html=True)

def create_accessible_button(label: str, onclick_action: str = None, icon: str = None, 
                           description: str = None, key: str = None):
    """Create an accessible button with proper ARIA attributes"""
    aria_label = f"{icon} {label}" if icon else label
    aria_describedby = f"desc-{key}" if description and key else ""
    
    button_html = f"""
    <button 
        role="button"
        aria-label="{aria_label}"
        {f'aria-describedby="{aria_describedby}"' if aria_describedby else ''}
        class="accessible-button"
        style="
            min-height: 44px;
            min-width: 44px;
            padding: 12px 16px;
            border: 2px solid #667eea;
            background: #667eea;
            color: white;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
        "
        onmouseover="this.style.background='#5a67d8'"
        onmouseout="this.style.background='#667eea'"
        onfocus="this.style.boxShadow='0 0 0 3px rgba(102, 126, 234, 0.3)'"
        onblur="this.style.boxShadow='none'"
        {f'onclick="{onclick_action}"' if onclick_action else ''}
    >
        {f'<span aria-hidden="true">{icon}</span>' if icon else ''} {label}
    </button>
    """
    
    if description and key:
        button_html += f'<div id="desc-{key}" class="sr-only">{description}</div>'
    
    return button_html

def create_accessible_form_field(label: str, input_type: str = "text", 
                                required: bool = False, help_text: str = None,
                                error_message: str = None, field_id: str = None):
    """Create an accessible form field with proper labels and ARIA attributes"""
    field_id = field_id or f"field-{label.lower().replace(' ', '-')}"
    help_id = f"help-{field_id}" if help_text else ""
    error_id = f"error-{field_id}" if error_message else ""
    
    describedby_ids = []
    if help_id:
        describedby_ids.append(help_id)
    if error_id:
        describedby_ids.append(error_id)
    
    aria_describedby = ' '.join(describedby_ids) if describedby_ids else ""
    
    form_html = f"""
    <div class="form-field">
        <label for="{field_id}" class="form-label">
            {label}
            {' <span aria-label="required">*</span>' if required else ''}
        </label>
        <input 
            type="{input_type}"
            id="{field_id}"
            name="{field_id}"
            {f'aria-describedby="{aria_describedby}"' if aria_describedby else ''}
            {f'aria-invalid="{bool(error_message)}"' if error_message else ''}
            {'required' if required else ''}
            style="
                width: 100%;
                min-height: 44px;
                padding: 12px 16px;
                border: 2px solid {('#dc2626' if error_message else '#d1d5db')};
                border-radius: 8px;
                font-size: 16px;
                transition: border-color 0.2s ease;
            "
            onfocus="this.style.borderColor='#667eea'; this.style.boxShadow='0 0 0 3px rgba(102, 126, 234, 0.3)'"
            onblur="this.style.boxShadow='none'"
        />
        {f'<div id="{help_id}" class="help-text" style="font-size: 14px; color: #6b7280; margin-top: 4px;">{help_text}</div>' if help_text else ''}
        {f'<div id="{error_id}" class="error-text" style="font-size: 14px; color: #dc2626; margin-top: 4px;" role="alert">{error_message}</div>' if error_message else ''}
    </div>
    """
    
    return form_html

def add_landmark_navigation():
    """Add landmark navigation for screen readers"""
    st.markdown("""
    <nav role="navigation" aria-label="Main navigation">
        <!-- Navigation content will be injected here -->
    </nav>
    <main role="main" aria-label="Main content">
        <!-- Main content starts here -->
    </main>
    """, unsafe_allow_html=True)

def create_accessible_quiz_option(option_text: str, option_key: str, 
                                question_number: int, is_selected: bool = False):
    """Create accessible quiz option with proper ARIA attributes"""
    return f"""
    <label 
        class="quiz-option"
        for="option-{question_number}-{option_key}"
        style="
            display: block;
            padding: 16px;
            margin: 8px 0;
            border: 2px solid {'#667eea' if is_selected else '#d1d5db'};
            border-radius: 12px;
            background: {'#f8fafc' if is_selected else 'white'};
            cursor: pointer;
            transition: all 0.2s ease;
            min-height: 44px;
            display: flex;
            align-items: center;
        "
        onmouseover="this.style.borderColor='#667eea'"
        onmouseout="this.style.borderColor='{'#667eea' if is_selected else '#d1d5db'}'"
    >
        <input 
            type="radio"
            id="option-{question_number}-{option_key}"
            name="question-{question_number}"
            value="{option_key}"
            {'checked' if is_selected else ''}
            style="margin-right: 12px; width: 20px; height: 20px;"
            aria-describedby="question-{question_number}-text"
        />
        <span>{option_text}</span>
    </label>
    """

# Keyboard navigation helpers
def add_keyboard_navigation_script():
    """Add JavaScript for enhanced keyboard navigation"""
    st.markdown("""
    <script>
    // Enhanced keyboard navigation
    document.addEventListener('DOMContentLoaded', function() {
        // Focus management for modal dialogs
        const focusableElements = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
        
        // Trap focus in modal dialogs
        function trapFocus(element) {
            const focusableContent = element.querySelectorAll(focusableElements);
            const firstFocusableElement = focusableContent[0];
            const lastFocusableElement = focusableContent[focusableContent.length - 1];
            
            element.addEventListener('keydown', function(e) {
                if (e.key === 'Tab') {
                    if (e.shiftKey) {
                        if (document.activeElement === firstFocusableElement) {
                            lastFocusableElement.focus();
                            e.preventDefault();
                        }
                    } else {
                        if (document.activeElement === lastFocusableElement) {
                            firstFocusableElement.focus();
                            e.preventDefault();
                        }
                    }
                }
                if (e.key === 'Escape') {
                    // Close modal on Escape key
                    element.style.display = 'none';
                }
            });
        }
        
        // Add keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            // Alt + H for Home
            if (e.altKey && e.key === 'h') {
                const homeButton = document.querySelector('[data-page="home"]');
                if (homeButton) homeButton.click();
            }
            
            // Alt + C for Chat
            if (e.altKey && e.key === 'c') {
                const chatButton = document.querySelector('[data-page="chat"]');
                if (chatButton) chatButton.click();
            }
            
            // Alt + Q for Quiz
            if (e.altKey && e.key === 'q') {
                const quizButton = document.querySelector('[data-page="quiz"]');
                if (quizButton) quizButton.click();
            }
        });
        
        // Announce navigation changes to screen readers
        let currentPage = '';
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    const newPage = document.title;
                    if (newPage !== currentPage) {
                        announcePageChange(newPage);
                        currentPage = newPage;
                    }
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        function announcePageChange(pageName) {
            const announcement = `Navigated to ${pageName}`;
            const statusRegion = document.getElementById('status-messages');
            if (statusRegion) {
                statusRegion.textContent = announcement;
                setTimeout(() => {
                    statusRegion.textContent = '';
                }, 1000);
            }
        }
    });
    </script>
    """, unsafe_allow_html=True)
