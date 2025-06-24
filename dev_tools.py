"""
Development tools for debugging and monitoring the NCC AI Assistant
"""
import os
import sys
import platform
import psutil
import streamlit as st
from datetime import datetime, timedelta
import json
from typing import Dict, Any, List
from pathlib import Path
import numpy as np
import pandas as pd

class DevTools:
    def __init__(self):
        # Initialize performance history if not exists
        if "performance_history" not in st.session_state:
            st.session_state.performance_history = []
        
    def update_performance_history(self):
        """Update performance history with current metrics"""
        current_time = datetime.now()
        metrics = {
            'timestamp': current_time,
            'memory_usage': psutil.Process().memory_info().rss / 1024 / 1024,  # MB
            'cpu_usage': psutil.cpu_percent(),
            'disk_usage': psutil.disk_usage('/').percent
        }
        
        # Keep only last hour of data
        one_hour_ago = current_time - timedelta(hours=1)
        st.session_state.performance_history = [
            m for m in st.session_state.performance_history 
            if m['timestamp'] > one_hour_ago
        ]
        st.session_state.performance_history.append(metrics)

    def plot_performance_history(self):
        """Plot performance metrics over time"""
        if not st.session_state.performance_history:
            return
            
        # Convert to DataFrame for easier plotting
        df = pd.DataFrame(st.session_state.performance_history)
        df.set_index('timestamp', inplace=True)
        
        # Create three separate line charts
        st.line_chart(df['memory_usage'], use_container_width=True)
        st.caption("Memory Usage (MB) over time")
        
        st.line_chart(df['cpu_usage'], use_container_width=True)
        st.caption("CPU Usage (%) over time")
        
        st.line_chart(df['disk_usage'], use_container_width=True)
        st.caption("Disk Usage (%) over time")

    def get_system_info(self) -> Dict[str, str]:
        """Get system information"""
        return {
            "OS": platform.system(),
            "Python Version": sys.version.split()[0],
            "Streamlit Version": st.__version__,
            "Memory Usage": f"{psutil.Process().memory_info().rss / 1024 / 1024:.2f} MB",
            "CPU Usage": f"{psutil.cpu_percent()}%",
            "Timestamp": datetime.now().isoformat()
        }

    def display_session_state(self):
        """Display current session state in a organized way"""
        if not st.session_state:
            return
            
        # Group session state items by category
        categories = {
            "PDF Viewer": {},
            "Quiz": {},
            "Chat": {},
            "Theme": {},
            "Other": {}
        }
        
        for key, value in st.session_state.items():
            if key.startswith('pdf_'):
                categories["PDF Viewer"][key] = value
            elif key.startswith('quiz_'):
                categories["Quiz"][key] = value
            elif key.startswith('chat_'):
                categories["Chat"][key] = value
            elif key.startswith('theme_'):
                categories["Theme"][key] = value
            else:
                categories["Other"][key] = value

        # Create tabs for each category
        category_tabs = st.tabs([f"📁 {category}" for category in categories.keys()])
        
        # Display each category in its own tab
        for tab, (category, items) in zip(category_tabs, categories.items()):
            with tab:
                if items:
                    st.json(self._clean_for_json(items))
                else:
                    st.info(f"No {category} variables in session state")

    def _clean_for_json(self, obj: Any) -> Any:
        """Clean objects for JSON serialization"""
        if isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        elif isinstance(obj, (list, tuple)):
            return [self._clean_for_json(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: self._clean_for_json(value) for key, value in obj.items()}
        else:
            return str(obj)

    def show_performance_metrics(self):
        """Display performance metrics"""
        # Update performance history
        self.update_performance_history()
        
        # Current metrics
        metrics_col1, metrics_col2 = st.columns(2)
        with metrics_col1:
            st.metric(
                "Memory Usage (MB)", 
                f"{psutil.Process().memory_info().rss / 1024 / 1024:.1f}"
            )
            st.metric(
                "Disk Usage (%)", 
                f"{psutil.disk_usage('/').percent:.1f}"
            )
        with metrics_col2:
            st.metric(
                "CPU Usage (%)", 
                f"{psutil.cpu_percent()}"
            )
            st.metric(
                "Python Threads", 
                len(psutil.Process().threads())
            )
            
        # Performance history graphs
        st.subheader("Performance History")
        self.plot_performance_history()

def dev_tools():
    """Main function to display dev tools in a new tab"""
    dev = DevTools()
    
    st.set_page_config(
        page_title="NCC AI Assistant - Dev Tools",
        page_icon="🛠️",
        layout="wide"
    )
    
    st.title("🛠️ Developer Tools")
    
    # Main tabs
    tool_tabs = st.tabs([
        "📊 Performance",
        "💾 Session State",
        "🖥️ System Info",
        "📝 Logs"
    ])
    
    # Performance Tab
    with tool_tabs[0]:
        dev.show_performance_metrics()
        
    # Session State Tab
    with tool_tabs[1]:
        dev.display_session_state()
        
    # System Info Tab
    with tool_tabs[2]:
        st.json(dev.get_system_info())
        
    # Logs Tab
    with tool_tabs[3]:
        log_file = Path("logs/app.log")
        if log_file.exists():
            with log_file.open() as f:
                logs = f.read()
            st.text_area("Application Logs", logs, height=400)
            if st.button("🧹 Clear Logs", key="clear_logs_button", help="Delete all application logs and refresh view"):
                log_file.write_text("")
                st.success("Logs cleared!")
                st.rerun()
        else:
            st.warning("No log file found")
