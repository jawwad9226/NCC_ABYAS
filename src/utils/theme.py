"""
Theme and styling configurations for the NCC AI Assistant.
Provides functions to get theme configuration and apply theme styles.
"""
from typing import Dict, Any
import streamlit as st

THEME_CONFIG: Dict[str, Dict[str, Any]] = {
    "dark": {
        "background": "#1e1e1e",  # Overall app background
        "text": "#ffffff",        # Default text color
        "body": { # This section might be for more specific body styling if needed
            "background": "#121212", # More specific body background if different from app
            "fontFamily": "sans-serif",
            "padding": "0.5rem",
            "margin": "0"
        },
        "base": { # Corresponds to st.set_option values
            "backgroundColor": "#1e1e1e",
            "secondaryBackgroundColor": "#2c2c2c", # Sidebar, expander header backgrounds
            "primaryColor": "#bb86fc", # Accent color for widgets
            "textColor": "#ffffff"
        },
        "components": {
            "button": {
                "bg": "#bb86fc",
                "text": "#000000", # Text on purple button
                "border": "#bb86fc",
                "hover": {
                    "border": "#3700b3", # Darker purple on hover
                    "text": "#ffffff",
                    "bg": "#3700b3" # Optional: hover background
                }
            },
            "input": {
                "bg": "#2c2c2c",
                "text": "#ffffff",
                "border": "#3c3c3c"
            },
            "select": {
                "bg": "#2c2c2c",
                "text": "#ffffff",
                "border": "#3c3c3c"
            },
            "expander": { # For the expander content area and header
                "bg": "#2c2c2c", # Header background
                "content_bg": "#1e1e1e", # Content area background
                "border": "#3c3c3c",
                "text": "#ffffff" # Header text color
            },
            "metric": {
                "bg": "#2c2c2c",
                "text": "#ffffff",
                "delta_up": "#03dac6", # Teal for positive delta
                "delta_down": "#cf6679" # Pink/Red for negative delta
            },
            "chart": {
                "bg": "#1e1e1e",
                "grid": "#3c3c3c",
                "text": "#ffffff",
                "line": "#bb86fc"
            }
        }
    },
    "light": {
        "background": "#ffffff",
        "text": "#000000",
        "body": {
            "background": "#f0f2f6", # Light grey body background
            "fontFamily": "sans-serif",
            "padding": "0.5rem",
            "margin": "0"
        },
        "base": {
            "backgroundColor": "#ffffff",
            "secondaryBackgroundColor": "#f0f2f6",
            "primaryColor": "#007bff", # Standard blue
            "textColor": "#212529" # Dark grey text
        },
        "components": {
            "button": {
                "bg": "#007bff",
                "text": "#ffffff",
                "border": "#007bff",
                "hover": {
                    "border": "#0056b3",
                    "text": "#ffffff",
                    "bg": "#0056b3"
                }
            },
            "input": {
                "bg": "#ffffff",
                "text": "#495057",
                "border": "#ced4da"
            },
            "select": {
                "bg": "#ffffff",
                "text": "#495057",
                "border": "#ced4da"
            },
            "expander": {
                "bg": "#f0f2f6", # Header background
                "content_bg": "#ffffff", # Content area background
                "border": "#dee2e6",
                "text": "#212529"
            },
            "metric": {
                "bg": "#ffffff",
                "text": "#212529",
                "delta_up": "#28a745", # Green for positive
                "delta_down": "#dc3545"  # Red for negative
            },
            "chart": {
                "bg": "#ffffff",
                "grid": "#e9ecef",
                "text": "#212529",
                "line": "#007bff"
            }
        }
    }
}

def get_theme_config(mode: str) -> Dict[str, Any]:
    """
    Get the theme configuration dictionary for the specified mode.
    Converts mode to lowercase and defaults to "light" if the mode is not found.
    """
    return THEME_CONFIG.get(mode.lower(), THEME_CONFIG["light"])

def apply_theme(mode: str) -> None:
    """Apply the current theme configuration to the Streamlit app."""
    theme_data = get_theme_config(mode)
    
    # Extract parts of the theme for easier access
    base_theme = theme_data["base"]
    components_theme = theme_data["components"]
    
    # Apply custom CSS
    # Note: Selectors might need adjustment based on Streamlit's evolving HTML structure.
    # Using data-testid attributes is generally more robust.
    css = f"""
        <style>
        /* --- Global & App Background --- */
        .stApp {{
            background-color: {theme_data["background"]};
            color: {theme_data["text"]};
        }}
        /* Fallback for body if .stApp doesn't cover everything, or for general page style */
        body {{
            font-family: {theme_data["body"]["fontFamily"]};
        }}

        /* --- Sidebar --- */
        [data-testid="stSidebar"] {{
            background-color: {base_theme["secondaryBackgroundColor"]};
        }}
        [data-testid="stSidebar"] .stButton button {{
            background-color: {components_theme["button"]["bg"]};
            color: {components_theme["button"]["text"]};
            border: 1px solid {components_theme["button"]["border"]};
        }}
        [data-testid="stSidebar"] .stButton button:hover {{
            background-color: {components_theme["button"]["hover"].get("bg", components_theme["button"]["bg"])};
            color: {components_theme["button"]["hover"]["text"]};
            border-color: {components_theme["button"]["hover"]["border"]};
        }}

        /* --- Main Content Buttons --- */
        .stButton button {{
            background-color: {components_theme["button"]["bg"]};
            color: {components_theme["button"]["text"]};
            border: 1px solid {components_theme["button"]["border"]};
            padding: 0.5rem 1rem;
            border-radius: 0.3rem;
        }}
        .stButton button:hover {{
            background-color: {components_theme["button"]["hover"].get("bg", components_theme["button"]["bg"])};
            color: {components_theme["button"]["hover"]["text"]};
            border-color: {components_theme["button"]["hover"]["border"]};
        }}

        /* --- Input Elements --- */
        .stTextInput input, .stTextArea textarea {{
            background-color: {components_theme["input"]["bg"]};
            color: {components_theme["input"]["text"]};
            border: 1px solid {components_theme["input"]["border"]};
        }}
        .stSelectbox div[data-baseweb="select"] > div {{ /* Targets the visible part of the selectbox */
            background-color: {components_theme["select"]["bg"]};
            color: {components_theme["select"]["text"]};
            border: 1px solid {components_theme["select"]["border"]};
        }}
        /* For dropdown list items of selectbox */
        div[data-baseweb="popover"] ul[role="listbox"] li {{
            background-color: {components_theme["select"]["bg"]};
            color: {components_theme["select"]["text"]};
        }}
        div[data-baseweb="popover"] ul[role="listbox"] li:hover {{
            background-color: {base_theme["primaryColor"]}; /* Or a specific hover color */
            color: {components_theme["button"]["text"]}; /* Text color on hover */
        }}


        /* --- Expander --- */
        .streamlit-expanderHeader {{
            background-color: {components_theme["expander"]["bg"]};
            color: {components_theme["expander"]["text"]};
            border: 1px solid {components_theme["expander"]["border"]};
            border-radius: 0.25rem; /* For the header itself */
        }}
        .streamlit-expander {{ /* Targets the whole expander container for border */
            border-radius: 0.25rem;
            background-color: {components_theme["expander"].get("content_bg", theme_data["background"])}; /* Background for content area */
        }}
        .streamlit-expander p, .streamlit-expander div {{ /* Text inside expander body */
            color: {theme_data["text"]} !important; 
        }}

        /* --- Metric --- */
        .stMetric {{
            background-color: {components_theme["metric"]["bg"]};
            color: {components_theme["metric"]["text"]};
            padding: 1rem;
            border-radius: 0.3rem;
        }}
        .stMetric [data-testid="stMetricDelta"].positive {{ /* Streamlit uses 'positive' class for up */
            color: {components_theme["metric"]["delta_up"]};
        }}
        .stMetric [data-testid="stMetricDelta"].negative {{
            color: {components_theme["metric"]["delta_down"]};
        }}

        /* --- Chart Styles (General) --- */
        .stPlotlyChart, .stVegaLiteChart, .stAltairChart {{ /* Common chart containers */
            background-color: {components_theme["chart"]["bg"]};
            padding: 0.5rem;
            border-radius: 0.3rem;
        }}
        /* More specific styling if needed, e.g., for ECharts if you use it directly */
        .stChart .echarts-for-react {{
            background: {components_theme["chart"]["bg"]};
            color: {components_theme["chart"]["text"]};
        }}
        .stChart .echarts-for-react line {{ /* Grid lines */
            stroke: {components_theme["chart"]["grid"]};
        }}
        .stChart .echarts-for-react path {{ /* Data lines */
            stroke: {components_theme["chart"]["line"]};
        }}
        </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    
    # Set Streamlit's global theme options using the 'base' config
    # Ensure mode is 'dark' or 'light' as strings for theme.base
    # st.set_option('theme.base', mode.lower()) # This line causes the error and should be removed or commented.
                                             # theme.base must be set in config.toml or via command line.
    # st.set_option('theme.primaryColor', base_theme["primaryColor"]) # Cannot be set on the fly
    # st.set_option('theme.backgroundColor', base_theme["backgroundColor"]) # Cannot be set on the fly
    # st.set_option('theme.secondaryBackgroundColor', base_theme["secondaryBackgroundColor"]) # Cannot be set on the fly
    # st.set_option('theme.textColor', base_theme["textColor"]) # Cannot be set on the fly
    # st.set_option('theme.font', 'sans serif') # Example: "sans serif", "serif", or "monospace"
