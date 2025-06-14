"""
Development tools for debugging and monitoring the NCC AI Assistant
"""
import os
import sys
import platform
import psutil
import streamlit as st
from datetime import datetime
import json
from typing import Dict, Any
import logging
from pathlib import Path

class DevTools:
    def __init__(self):
        self.setup_logging()
        
    @staticmethod
    def setup_logging():
        """Configure logging for the application"""
        log_file = Path("logs/app.log")
        log_file.parent.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(log_file)
            ]
        )

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
            st.info("Session state is empty")
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
        metrics_col1, metrics_col2 = st.columns(2)
        
        with metrics_col1:
            st.metric(
                "Memory Usage (MB)", 
                f"{psutil.Process().memory_info().rss / 1024 / 1024:.1f}"
            )
            
        with metrics_col2:
            st.metric(
                "CPU Usage (%)", 
                f"{psutil.cpu_percent()}"
            )

    def show_logs(self, num_lines: int = 50):
        """Display application logs"""
        try:
            log_file = Path("logs/app.log")
            if log_file.exists():
                with log_file.open('r') as f:
                    logs = f.readlines()[-num_lines:]
                    
                log_level_filter = st.multiselect(
                    "Filter by log level",
                    ["INFO", "WARNING", "ERROR", "DEBUG"],
                    default=["ERROR", "WARNING"]
                )
                
                filtered_logs = [
                    log for log in logs 
                    if any(level in log for level in log_level_filter)
                ]
                
                if filtered_logs:
                    st.code("".join(filtered_logs), language="text")
                else:
                    st.info(f"No logs found matching the selected levels: {', '.join(log_level_filter)}")
            else:
                st.info("No logs found")
        except Exception as e:
            st.error(f"Error reading logs: {str(e)}")

    def display_dev_tools(self):
        """Main method to display all development tools"""
        st.sidebar.markdown("---")
        show_tools = st.sidebar.checkbox("🛠️ Developer Tools", value=False)
        
        if show_tools:
            # Create a new tab for dev tools
            if 'active_tab' not in st.session_state:
                st.session_state.active_tab = 'System'
                
            # Create dev tools container
            st.markdown("## 🛠️ Developer Tools")
                # Create tabs for different tool categories
            system_tab, state_tab, perf_tab, logs_tab, controls_tab = st.tabs([
                "🖥️ System",
                "💾 State",
                "📊 Performance",
                "📝 Logs",
                "⚙️ Controls"
            ])
            
            # System Information Tab
            with system_tab:
                st.markdown("### System Information")
                sys_info = self.get_system_info()
                
                # Display system info in a more organized way
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("OS", sys_info["OS"])
                    st.metric("Python Version", sys_info["Python Version"])
                    st.metric("Streamlit Version", sys_info["Streamlit Version"])
                with col2:
                    st.metric("Memory Usage", sys_info["Memory Usage"])
                    st.metric("CPU Usage", sys_info["CPU Usage"])
                    st.metric("Last Updated", datetime.now().strftime("%H:%M:%S"))
                    
                if st.button("🔄 Refresh System Info", key="refresh_sys"):
                    st.rerun()
            
            # Session State Tab
            with state_tab:
                st.markdown("### Session State Explorer")
                self.display_session_state()
                if st.button("🔄 Refresh State", key="refresh_state"):
                    st.rerun()
            
            # Performance Tab
            with perf_tab:
                st.markdown("### Performance Metrics")
                    
                # Add auto-refresh option
                auto_refresh = st.checkbox("🔄 Auto-refresh (5s)", value=False)
                if auto_refresh:
                    st.empty()
                    st.rerun()
                
                # Show metrics in columns
                metric_cols = st.columns(2)
                with metric_cols[0]:
                    self.show_performance_metrics()
                with metric_cols[1]:
                    st.markdown("#### Resource Usage History")
                    # Add placeholder for future graph implementation
                    st.info("Performance history graph coming soon!")
                
            # Logs Tab
            with logs_tab:
                st.markdown("### Application Logs")
                
                # Add log controls
                col1, col2 = st.columns([2, 1])
                with col1:
                    log_levels = st.multiselect(
                        "Log Levels",
                        ["DEBUG", "INFO", "WARNING", "ERROR"],
                        default=["ERROR", "WARNING"]
                    )
                with col2:
                    num_lines = st.number_input(
                        "Lines to show",
                        min_value=10,
                        max_value=200,
                        value=50,
                        step=10
                    )
                    
                self.show_logs(num_lines)
                
                # Add log controls
                if st.button("🔄 Refresh Logs", key="refresh_logs"):
                    st.rerun()
                
                if st.button("📝 Clear Logs"):
                    try:
                        open("logs/app.log", "w").close()
                        st.success("Logs cleared successfully!")
                    except Exception as e:
                        st.error(f"Error clearing logs: {e}")
            
            # Controls Tab
            with controls_tab:
                st.markdown("### Developer Controls")
                    
                # Organize controls in columns
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Session Management")
                    if st.button("🧹 Clear Session State", use_container_width=True):
                        for key in list(st.session_state.keys()):
                            del st.session_state[key]
                        st.success("Session state cleared!")
                        st.rerun()
                    
                    if st.button("🔄 Force Reload App", use_container_width=True):
                        st.rerun()
                
                with col2:
                    st.markdown("#### Testing & Debug")
                    if st.button("🧪 Run Tests", use_container_width=True):
                        st.info("Test functionality coming soon!")
                    
                    if st.button("📊 Generate Debug Report", use_container_width=True):
                        st.info("Debug report generation coming soon!")
                
                # Add experimental features section
                st.markdown("#### ⚡ Experimental Features")
                exp_features = st.multiselect(
                    "Enable experimental features",
                    ["Performance Monitoring", "Auto Log Rotation", "State Time Travel"],
                    help="Warning: These features are experimental and may not work as expected."
                )
