import streamlit as st

def apply_modern_theme():
    """Apply a modern, clean theme to the Streamlit app."""
    
    # Modern styling
    st.markdown("""
        <style>
        /* Modern Button Styling */
        .stButton button {
            border-radius: 8px;
            transition: all 0.3s ease;
            border: none !important;
            background-color: #2e2e2e;
        }
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        /* Chat Message Styling */
        .message {
            padding: 1rem;
            border-radius: 12px;
            margin: 0.5rem 0;
            max-width: 85%;
        }
        .user-message {
            background: #e9ecef;
            margin-left: auto;
        }
        .assistant-message {
            background: #007bff;
            color: white;
            margin-right: auto;
        }
        
        /* Clean Headers */
        h1, h2, h3 {
            font-weight: 600 !important;
            letter-spacing: -0.5px;
        }
        
        /* Modern Card-like Containers */
        div[data-testid="stExpander"] {
            background: #ffffff;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            margin: 0.5rem 0;
            border: none !important;
        }
        
        /* Hover Effects for Interactive Elements */
        button, [role="button"] {
            transition: all 0.2s ease !important;
        }
        button:hover, [role="button"]:hover {
            filter: brightness(1.1);
        }
        
        /* Tooltips */
        [data-tooltip]:before {
            content: attr(data-tooltip);
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            padding: 4px 8px;
            background: #333;
            color: white;
            border-radius: 4px;
            font-size: 12px;
            white-space: nowrap;
            opacity: 0;
            visibility: hidden;
            transition: all 0.2s ease;
        }
        [data-tooltip]:hover:before {
            opacity: 1;
            visibility: visible;
        }
        
        /* Streamlit Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #f8f9fa;
            border-right: 1px solid #eaecef;
        }
        section[data-testid="stSidebar"] > div {
            padding: 1rem;
        }
        
        /* PDF Controls */
        .pdf-controls {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px;
            background: #f8f9fa;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        .pdf-controls button {
            padding: 4px 8px;
            border: none;
            background: transparent;
            cursor: pointer;
        }
        .pdf-controls button:hover {
            background: #e9ecef;
        }
        
        /* Modern Toggle Switch */
        .toggle-switch {
            position: relative;
            display: inline-block;
            width: 60px;
            height: 34px;
        }
        .toggle-switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }
        .toggle-slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: .4s;
            border-radius: 34px;
        }
        .toggle-slider:before {
            position: absolute;
            content: "";
            height: 26px;
            width: 26px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }
        input:checked + .toggle-slider {
            background-color: #2196F3;
        }
        input:checked + .toggle-slider:before {
            transform: translateX(26px);
        }
        </style>
    """, unsafe_allow_html=True)

def apply_icon_tooltips():
    """Apply modern tooltips to icon-only buttons."""
    st.markdown("""
        <script>
        // Add tooltips to icon-only buttons
        document.querySelectorAll('button').forEach(button => {
            if (button.innerText.length === 2) {  // Emoji + space
                const tooltip = button.getAttribute('title');
                if (tooltip) {
                    button.setAttribute('data-tooltip', tooltip);
                    button.removeAttribute('title');
                }
            }
        });
        </script>
    """, unsafe_allow_html=True)

def apply_compact_layout():
    """Apply a more compact layout with reduced spacing."""
    st.markdown("""
        <style>
        /* Reduce Sidebar Spacing */
        section[data-testid="stSidebar"] {
            padding-top: 1rem !important;
        }
        section[data-testid="stSidebar"] > div {
            padding-top: 1rem !important;
        }
        section[data-testid="stSidebar"] .block-container {
            padding-top: 1rem !important;
        }
        
        /* More Compact Headers */
        .main .block-container {
            padding-top: 2rem !important;
            padding-bottom: 1rem !important;
        }
        
        h1 {
            margin-top: 0 !important;
            padding-top: 1rem !important;
            font-size: 1.8rem !important;
        }
        
        h2 {
            font-size: 1.4rem !important;
            margin-top: 1rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        h3 {
            font-size: 1.2rem !important;
            margin-top: 0.8rem !important;
            margin-bottom: 0.3rem !important;
        }
        
        /* Compact Widgets */
        .stButton button {
            padding: 0.3rem 1rem !important;
            font-size: 0.9rem !important;
        }
        
        .stTextInput input {
            padding: 0.3rem 0.5rem !important;
            font-size: 0.9rem !important;
        }
        
        /* Reduce Card Padding */
        div[data-testid="stExpander"] {
            padding: 0.5rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Compact Lists */
        ul, ol {
            margin: 0 0 0.5rem 0 !important;
            padding-left: 1.2rem !important;
        }
        
        li {
            margin-bottom: 0.2rem !important;
        }
        
        /* Reduce Space Between Elements */
        .element-container {
            margin-bottom: 0.5rem !important;
        }
        
        /* Compact Metrics */
        [data-testid="stMetricValue"] {
            font-size: 1.2rem !important;
        }
        
        /* Reduce Space in Chat Messages */
        .stChatMessage {
            padding: 0.5rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Compact Forms */
        .stForm {
            padding: 0.5rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Remove Extra Margins from Text */
        p {
            margin-bottom: 0.5rem !important;
        }
        
        /* Compact Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding-top: 0.3rem !important;
            padding-bottom: 0.3rem !important;
        }
        
        /* Compact Selectbox */
        [data-baseweb="select"] {
            min-height: 35px !important;
        }
        </style>
    """, unsafe_allow_html=True)
