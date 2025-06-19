"""
Theme and styling configurations for the NCC ABHYAS application.
Provides functions to get theme configuration and apply theme styles.
"""
from typing import Dict, Any
import streamlit as st

THEME_CONFIG: Dict[str, Dict[str, Any]] = {
    "dark": {
        "background": "#1A1B1E",  # Slightly warmer dark background
        "text": "#E4E5E7",      # Soft white text for better readability
        "body": {
            "background": "#1A1B1E",
            "fontFamily": '"Inter", -apple-system, BlinkMacSystemFont, sans-serif',
            "padding": "0.5rem",
            "margin": "0"
        },
        "base": {
            "backgroundColor": "#1A1B1E",
            "secondaryBackgroundColor": "#2A2B2F",  # Slightly lighter sidebar
            "primaryColor": "#7F3FBF",  # Rich purple
            "textColor": "#E4E5E7"
        },
        "components": {
            "button": {
                "bg": "#7F3FBF",
                "text": "#FFFFFF",
                "border": "#7F3FBF",
                "hover": {
                    "border": "#9B5ACF",
                    "text": "#FFFFFF",
                    "bg": "#9B5ACF"
                }
            },
            "input": {
                "bg": "#2A2B2F",
                "text": "#E4E5E7",
                "border": "#3A3B3F"
            },
            "select": {
                "bg": "#2A2B2F",
                "text": "#E4E5E7",
                "border": "#3A3B3F"
            },
            "expander": {
                "bg": "#2A2B2F",
                "content_bg": "#1A1B1E",
                "border": "#3A3B3F",
                "text": "#E4E5E7"
            },
            "metric": {
                "bg": "#2A2B2F",
                "text": "#E4E5E7",
                "delta_up": "#4CAF50",
                "delta_down": "#F44336"
            },
            "chart": {
                "bg": "#2A2B2F",
                "grid": "#3A3B3F",
                "text": "#E4E5E7",
                "line": "#7F3FBF"
            }
        }
    },
    "light": {
        "background": "#EEF2FF",  # Light indigo background
        "text": "#0F172A",      # Darker Slate-900 for text
        "body": {
            "background": "#EEF2FF",
            "fontFamily": '"Inter", -apple-system, BlinkMacSystemFont, sans-serif',
            "padding": "0.5rem",
            "margin": "0"
        },
        "base": {
            "backgroundColor": "#FFFFFF",  # Pure white for main content
            "secondaryBackgroundColor": "#F1F5F9",  # Slate-50 for sidebar
            "primaryColor": "#6366F1",  # Indigo-500 for primary accents
            "textColor": "#0F172A"  # Darker Slate-900
        },
        "components": {
            "button": {
                "bg": "#6366F1",  # Indigo-500
                "text": "#FFFFFF",
                "border": "#6366F1",
                "hover": {
                    "border": "#4F46E5",  # Indigo-600
                    "text": "#FFFFFF",
                    "bg": "#4F46E5"
                }
            },
            "input": {
                "bg": "#FFFFFF",
                "text": "#1E293B",  # Slate-900
                "border": "#CBD5E1"  # Slate-300
            },
            "select": {
                "bg": "#FFFFFF",
                "text": "#1E293B",
                "border": "#CBD5E1"
            },
            "expander": {
                "bg": "#F8FAFC",  # Slate-50
                "content_bg": "#FFFFFF",
                "border": "#CBD5E1",  # Slate-300
                "text": "#1E293B"
            },
            "metric": {
                "bg": "#FFFFFF",
                "text": "#1E293B",
                "delta_up": "#10B981",  # Emerald-500
                "delta_down": "#EF4444"  # Red-500
            },
            "chart": {
                "bg": "#FFFFFF",
                "grid": "#E2E8F0",  # Slate-200
                "text": "#1E293B",
                "line": "#6366F1"  # Indigo-500
            }
        }
    }
}

def get_theme_config(mode: str) -> Dict[str, Any]:
    """Get the theme configuration for the specified mode."""
    return THEME_CONFIG.get(mode.lower(), THEME_CONFIG["dark"])

def apply_theme(mode: str) -> None:
    """Apply the theme configuration to the Streamlit app."""
    theme_data = get_theme_config(mode)
    base_theme = theme_data["base"]
    components_theme = theme_data["components"]
    
    css = f"""
        <style>
        /* --- Global Styles --- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        .stApp {{
            background-color: {theme_data["background"]};
            color: {theme_data["text"]};
            font-family: {theme_data["body"]["fontFamily"]};
        }}

        /* --- Main Content Area --- */
        .main .block-container {{
            background-color: {base_theme["backgroundColor"]};
            padding: 2rem;
            border-radius: 1rem;
            box-shadow: 0 4px 20px rgba(148, 163, 184, 0.1);  # Soft shadow
            margin: 1rem;
        }}

        /* --- Sidebar with Fresh Color --- */
        [data-testid="stSidebar"] {{
            background-color: {base_theme["secondaryBackgroundColor"]};
            border-right: 1px solid {components_theme["input"]["border"]};
            padding: 2rem 1rem;
            box-shadow: 2px 0 10px rgba(148, 163, 184, 0.05);
        }}

        /* --- Navigation Elements --- */
        [data-testid="stSidebar"] {{
            color: {theme_data["text"]};  /* Use theme's text color */
        }}

        [data-testid="stSidebar"] [role="radiogroup"] {{
            background: {base_theme["backgroundColor"]};
            padding: 1rem;
            border-radius: 0.8rem;
            box-shadow: 0 2px 8px rgba(148, 163, 184, 0.05);
            color: {theme_data["text"]};  /* Use theme's text color */
        }}

        [data-testid="stSidebar"] [role="radio"] {{
            margin: 0.3rem 0;
            padding: 0.8rem;
            border-radius: 0.5rem;
            transition: all 0.2s ease;
            color: {theme_data["text"]};  /* Use theme's text color */
            font-weight: 500;
        }}

        /* Ensure all text elements in sidebar match theme */
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] h4,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] div {{
            color: {theme_data["text"]};  /* Use theme's text color */
        }}

        /* Make info messages in sidebar match theme */
        [data-testid="stSidebar"] [data-testid="stAlert"] {{
            color: {theme_data["text"]};
        }}

        /* --- Cards and Content Containers --- */
        div[data-testid="stExpander"] {{
            background: {components_theme["expander"]["bg"]};
            border: 1px solid {components_theme["expander"]["border"]};
            border-radius: 0.8rem;
            overflow: hidden;
            margin: 1rem 0;
            box-shadow: 0 2px 12px rgba(148, 163, 184, 0.05);
        }}

        /* --- Input Fields --- */
        .stTextInput input, .stTextArea textarea {{
            background-color: {components_theme["input"]["bg"]};
            border: 1px solid {components_theme["input"]["border"]};
            border-radius: 0.5rem;
            padding: 0.75rem;
            box-shadow: 0 2px 4px rgba(148, 163, 184, 0.05);
            transition: all 0.2s ease;
        }}

        .stTextInput input:focus, .stTextArea textarea:focus {{
            border-color: {base_theme["primaryColor"]};
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        }}

        /* --- Buttons with Fresh Style --- */
        .stButton button {{
            background-color: {components_theme["button"]["bg"]};
            color: {components_theme["button"]["text"]};
            border: none;
            padding: 0.6rem 1.2rem;
            border-radius: 0.5rem;
            font-weight: 500;
            box-shadow: 0 2px 4px rgba(99, 102, 241, 0.15);
            transition: all 0.2s ease;
        }}

        .stButton button:hover {{
            background-color: {components_theme["button"]["hover"]["bg"]};
            box-shadow: 0 4px 8px rgba(99, 102, 241, 0.2);
            transform: translateY(-1px);
        }}

        /* --- Metrics and Stats --- */
        [data-testid="stMetricValue"] {{
            background-color: {components_theme["metric"]["bg"]};
            padding: 1.5rem;
            border-radius: 0.8rem;
            border: 1px solid {components_theme["input"]["border"]};
            box-shadow: 0 2px 12px rgba(148, 163, 184, 0.05);
        }}

        /* --- Headers --- */
        h1, h2, h3, h4, h5, h6 {{
            color: {theme_data["text"]};
            font-weight: 600;
            letter-spacing: -0.02em;
            margin-bottom: 1rem;
        }}

        /* --- Streamlit Default Header Integration --- */
        header [data-testid="stToolbar"] {{
            z-index: 1000;
        }}

        /* Custom header container to align with Streamlit's header */
        .stApp > header + div [data-testid="stHeader"] {{
            background-color: transparent !important;
            gap: 0;
            padding-left: 1rem;
            margin-top: -1rem;
            height: 50px;
            position: fixed;
            top: 3.5rem;  /* Position below Streamlit's header */
            left: 0;
            right: 0;
            z-index: 100;
            backdrop-filter: blur(8px);
        }}

        /* App title in header */
        [data-testid="stHeader"] h1 {{
            font-size: 1.25rem !important;
            margin: 0 !important;
            padding: 0 !important;
            line-height: 1.5 !important;
            color: {theme_data["text"]} !important;
        }}

        /* Theme toggle button in header */
        [data-testid="stHeader"] [data-testid="baseButton-secondary"] {{
            position: absolute !important;
            right: 1rem !important;
            top: 50% !important;
            transform: translateY(-50%) !important;
            margin: 0 !important;
            padding: 0.35rem !important;
            height: 32px !important;
            width: 32px !important;
        }}

        /* Adjust main content padding */
        .main .block-container {{
            padding-top: 5rem !important;  /* Add space for our header */
        }}

        /* Make sidebar start below headers */
        [data-testid="stSidebar"] {{
            padding-top: 0 !important;
            margin-top: 5rem !important;
        }}

        /* Style sidebar content */
        [data-testid="stSidebar"] .block-container {{
            padding-top: 1rem !important;
        }}

        /* Ensure text color matches theme */
        [data-testid="stSidebar"] {{
            color: {theme_data["text"]} !important;
        }}

        /* Style navigation menu */
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:first-child {{
            padding: 1rem;
            border-bottom: 1px solid {components_theme["input"]["border"]};
            margin-bottom: 1rem;
        }}

        /* Make header text visible */
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {{
            color: {theme_data["text"]} !important;
        }}

        /* --- Tabs with Fresh Style --- */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 1rem;
            border-bottom: 2px solid {components_theme["input"]["border"]};
            padding: 0 1rem;
            background: {base_theme["backgroundColor"]};
        }}

        .stTabs [data-baseweb="tab"] {{
            padding: 0.75rem 1rem;
            font-weight: 500;
            color: {theme_data["text"]};
            opacity: 0.7;
            border-radius: 0.5rem 0.5rem 0 0;
            transition: all 0.2s ease;
        }}

        .stTabs [data-baseweb="tab"][aria-selected="true"] {{
            background: {components_theme["button"]["bg"]};
            color: white;
            opacity: 1;
            box-shadow: 0 2px 4px rgba(99, 102, 241, 0.15);
        }}

        /* --- Links --- */
        a {{
            color: {base_theme["primaryColor"]};
            text-decoration: none;
            transition: color 0.2s ease;
        }}

        a:hover {{
            color: {components_theme["button"]["hover"]["bg"]};
        }}
        </style>
    """
    st.markdown(css, unsafe_allow_html=True)