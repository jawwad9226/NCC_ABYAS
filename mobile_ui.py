"""
Mobile-First CSS Framework for NCC ABYAS
Provides responsive design utilities and mobile optimizations
"""
import streamlit as st

def inject_mobile_css():
    """Inject comprehensive mobile-first CSS styling"""
    st.markdown("""
    <style>
    /* ===== MOBILE-FIRST BASE STYLES ===== */
    
    /* Reset and base styles */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }
    
    /* Mobile navigation bar styling */
    .mobile-nav-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 8px 0;
        z-index: 1000;
        box-shadow: 0 -2px 20px rgba(0,0,0,0.15);
        border-top: 1px solid rgba(255,255,255,0.1);
    }
    
    .mobile-nav-button {
        background: transparent !important;
        border: none !important;
        color: white !important;
        font-size: 0.8rem !important;
        padding: 8px 4px !important;
        min-height: 48px !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
        text-align: center !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    .mobile-nav-button:hover {
        background: rgba(255,255,255,0.1) !important;
        transform: translateY(-2px) !important;
    }
    
    .mobile-nav-button.active {
        background: rgba(255,255,255,0.2) !important;
        color: #fff !important;
    }
    
    /* Content area with bottom navigation spacing */
    .main-content {
        padding-bottom: 80px;
    }
    
    /* ===== TOUCH-FRIENDLY ELEMENTS ===== */
    
    /* Minimum 48px touch targets */
    .stButton > button {
        min-height: 48px !important;
        padding: 12px 24px !important;
        font-size: 16px !important;
        border-radius: 12px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    
    /* Enhanced form inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        min-height: 48px !important;
        font-size: 16px !important;
        padding: 12px 16px !important;
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Chat input styling */
    .stChatInput > div {
        border-radius: 25px !important;
        border: 2px solid #e2e8f0 !important;
        background: white !important;
    }
    
    .stChatInput input {
        min-height: 48px !important;
        font-size: 16px !important;
        padding: 12px 20px !important;
    }
    
    /* ===== LOADING STATES ===== */
    
    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        text-align: center;
    }
    
    .loading-spinner {
        width: 40px;
        height: 40px;
        border: 4px solid #f3f4f6;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 1rem;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .loading-text {
        color: #6b7280;
        font-size: 14px;
        font-weight: 500;
    }
    
    /* ===== CARD COMPONENTS ===== */
    
    .card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e7eb;
    }
    
    .card-header {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .card-content {
        color: #4b5563;
        line-height: 1.6;
    }
    
    /* ===== QUIZ STYLING ===== */
    
    .quiz-question {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    .quiz-options .stRadio > div {
        gap: 1rem !important;
    }
    
    .quiz-options .stRadio > div > label {
        background: white !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        border: 2px solid #e2e8f0 !important;
        margin: 0.5rem 0 !important;
        min-height: 48px !important;
        display: flex !important;
        align-items: center !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }
    
    .quiz-options .stRadio > div > label:hover {
        border-color: #667eea !important;
        background: #f8fafc !important;
    }
    
    /* ===== RESPONSIVE BREAKPOINTS ===== */
    
    /* Small mobile (320px and up) */
    @media (min-width: 320px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
    
    /* Large mobile (480px and up) */
    @media (min-width: 480px) {
        .main .block-container {
            padding-left: 1.5rem;
            padding-right: 1.5rem;
        }
        
        .mobile-nav-button {
            font-size: 0.9rem !important;
        }
    }
    
    /* Tablet (768px and up) */
    @media (min-width: 768px) {
        .main .block-container {
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 768px;
            margin: 0 auto;
        }
        
        .mobile-nav-container {
            display: none;
        }
        
        .main-content {
            padding-bottom: 2rem;
        }
    }
    
    /* Desktop (1024px and up) */
    @media (min-width: 1024px) {
        .main .block-container {
            max-width: 1024px;
            padding-left: 3rem;
            padding-right: 3rem;
        }
    }
    
    /* ===== ACCESSIBILITY IMPROVEMENTS ===== */
    
    /* Focus indicators */
    .stButton > button:focus,
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        outline: 2px solid #667eea !important;
        outline-offset: 2px !important;
    }
    
    /* High contrast mode support */
    @media (prefers-contrast: high) {
        .card {
            border: 2px solid #000 !important;
        }
        
        .mobile-nav-button {
            border: 1px solid rgba(255,255,255,0.5) !important;
        }
    }
    
    /* Reduced motion support */
    @media (prefers-reduced-motion: reduce) {
        * {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
    
    /* ===== DARK MODE SUPPORT ===== */
    
    @media (prefers-color-scheme: dark) {
        .card {
            background: #1f2937 !important;
            border-color: #374151 !important;
            color: #f9fafb !important;
        }
        
        .card-header {
            color: #f9fafb !important;
        }
        
        .card-content {
            color: #d1d5db !important;
        }
        
        .quiz-question {
            background: linear-gradient(135deg, #374151 0%, #4b5563 100%) !important;
            color: #f9fafb !important;
        }
    }
    
    /* ===== PERFORMANCE OPTIMIZATIONS ===== */
    
    /* Hardware acceleration for animations */
    .mobile-nav-button,
    .stButton > button,
    .loading-spinner {
        transform: translateZ(0);
        will-change: transform;
    }
    
    /* Optimize image rendering */
    img {
        image-rendering: -webkit-optimize-contrast;
        image-rendering: optimize-contrast;
    }
    </style>
    """, unsafe_allow_html=True)

def show_loading_state(message="Loading..."):
    """Show a mobile-friendly loading state"""
    st.markdown(f"""
    <div class="loading-container">
        <div class="loading-spinner"></div>
        <div class="loading-text">{message}</div>
    </div>
    """, unsafe_allow_html=True)

def create_card(title, content, icon="📋"):
    """Create a mobile-friendly card component"""
    st.markdown(f"""
    <div class="card">
        <div class="card-header">
            <span>{icon}</span>
            <span>{title}</span>
        </div>
        <div class="card-content">
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_quiz_question_card(question, question_number):
    """Create a styled quiz question card"""
    st.markdown(f"""
    <div class="quiz-question">
        <h4>Question {question_number}</h4>
        <p>{question}</p>
    </div>
    """, unsafe_allow_html=True)
