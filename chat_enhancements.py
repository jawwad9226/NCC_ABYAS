"""
Advanced Chat Interface Features for NCC ABYAS
Provides rich message formatting, conversation management, search, and export functionality
"""
import streamlit as st
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
import markdown
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound

class ChatEnhancements:
    """Enhanced chat functionality with advanced features"""
    
    @staticmethod
    def format_message_content(content: str) -> str:
        """Format message content with markdown and code highlighting"""
        try:
            # Convert markdown to HTML
            html_content = markdown.markdown(
                content,
                extensions=['codehilite', 'fenced_code', 'tables', 'toc']
            )
            
            # Additional formatting for NCC-specific content
            html_content = ChatEnhancements._format_ncc_content(html_content)
            
            return html_content
        except Exception:
            # Fallback to basic formatting
            return content.replace('\n', '<br>')
    
    @staticmethod
    def _format_ncc_content(content: str) -> str:
        """Format NCC-specific content patterns"""
        # Highlight NCC regulations and references
        content = re.sub(
            r'\b(NCC|National Cadet Corps)\b',
            r'<span class="ncc-highlight">\1</span>',
            content
        )
        
        # Format drill commands
        content = re.sub(
            r'\b(Attention|Stand at ease|Quick march|Halt|Left turn|Right turn|About turn)\b',
            r'<strong class="drill-command">\1</strong>',
            content
        )
        
        # Format ranks
        ranks = ['Cadet', 'Lance Corporal', 'Corporal', 'Sergeant', 'Under Officer', 'Warrant Officer']
        for rank in ranks:
            content = re.sub(
                f'\\b{rank}\\b',
                f'<span class="rank-highlight">{rank}</span>',
                content,
                flags=re.IGNORECASE
            )
        
        return content
    
    @staticmethod
    def search_conversations(query: str, messages: List[Dict]) -> List[Dict]:
        """Search through conversation history"""
        if not query.strip():
            return messages
        
        query_lower = query.lower()
        filtered_messages = []
        
        for message in messages:
            content = message.get('content', '').lower()
            if query_lower in content:
                # Highlight search terms
                highlighted_content = re.sub(
                    f'({re.escape(query)})',
                    r'<mark>\1</mark>',
                    message.get('content', ''),
                    flags=re.IGNORECASE
                )
                
                filtered_message = message.copy()
                filtered_message['content'] = highlighted_content
                filtered_messages.append(filtered_message)
        
        return filtered_messages
    
    @staticmethod
    def export_conversation(messages: List[Dict], format_type: str = "markdown") -> str:
        """Export conversation in various formats"""
        if format_type == "markdown":
            return ChatEnhancements._export_as_markdown(messages)
        elif format_type == "html":
            return ChatEnhancements._export_as_html(messages)
        elif format_type == "json":
            return json.dumps(messages, indent=2, ensure_ascii=False)
        elif format_type == "txt":
            return ChatEnhancements._export_as_text(messages)
        else:
            return ChatEnhancements._export_as_markdown(messages)
    
    @staticmethod
    def _export_as_markdown(messages: List[Dict]) -> str:
        """Export conversation as markdown"""
        export_content = f"# NCC Chat Conversation\n\n"
        export_content += f"**Exported on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        export_content += "---\n\n"
        
        for i, message in enumerate(messages, 1):
            role = message.get('role', 'unknown')
            content = message.get('content', '')
            timestamp = message.get('timestamp', '')
            
            if role == 'user':
                export_content += f"## 👤 Question {i}\n"
                export_content += f"**Time:** {timestamp}\n\n"
                export_content += f"{content}\n\n"
            else:
                export_content += f"## 🤖 NCC Assistant Response\n"
                export_content += f"**Time:** {timestamp}\n\n"
                export_content += f"{content}\n\n"
            
            export_content += "---\n\n"
        
        return export_content
    
    @staticmethod
    def _export_as_html(messages: List[Dict]) -> str:
        """Export conversation as HTML"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>NCC Chat Conversation</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; }
                .message { margin: 20px 0; padding: 15px; border-radius: 8px; }
                .user { background: #e3f2fd; border-left: 4px solid #2196f3; }
                .assistant { background: #f3e5f5; border-left: 4px solid #9c27b0; }
                .timestamp { color: #666; font-size: 0.9em; }
                .ncc-highlight { background: #ffeb3b; font-weight: bold; }
                .drill-command { color: #d32f2f; font-weight: bold; }
                .rank-highlight { background: #4caf50; color: white; padding: 2px 4px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>NCC Chat Conversation</h1>
            <p><strong>Exported on:</strong> {}</p>
        """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        for message in messages:
            role = message.get('role', 'unknown')
            content = ChatEnhancements.format_message_content(message.get('content', ''))
            timestamp = message.get('timestamp', '')
            
            role_class = "user" if role == "user" else "assistant"
            role_emoji = "👤" if role == "user" else "🤖"
            
            html_content += f"""
            <div class="message {role_class}">
                <div class="timestamp">{role_emoji} {timestamp}</div>
                <div class="content">{content}</div>
            </div>
            """
        
        html_content += "</body></html>"
        return html_content
    
    @staticmethod
    def _export_as_text(messages: List[Dict]) -> str:
        """Export conversation as plain text"""
        text_content = f"NCC Chat Conversation\n"
        text_content += f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        text_content += "=" * 50 + "\n\n"
        
        for message in messages:
            role = message.get('role', 'unknown')
            content = message.get('content', '')
            timestamp = message.get('timestamp', '')
            
            role_prefix = "YOU" if role == "user" else "NCC ASSISTANT"
            text_content += f"[{timestamp}] {role_prefix}:\n"
            text_content += f"{content}\n\n"
            text_content += "-" * 30 + "\n\n"
        
        return text_content
    
    @staticmethod
    def get_conversation_statistics(messages: List[Dict]) -> Dict[str, Any]:
        """Get conversation statistics"""
        stats = {
            "total_messages": len(messages),
            "user_messages": 0,
            "assistant_messages": 0,
            "total_words": 0,
            "conversation_duration": None,
            "topics_discussed": []
        }
        
        timestamps = []
        all_content = ""
        
        for message in messages:
            role = message.get('role', '')
            content = message.get('content', '')
            timestamp_str = message.get('timestamp', '')
            
            if role == 'user':
                stats["user_messages"] += 1
            elif role == 'assistant':
                stats["assistant_messages"] += 1
            
            stats["total_words"] += len(content.split())
            all_content += " " + content
            
            # Parse timestamp
            try:
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                timestamps.append(timestamp)
            except:
                pass
        
        # Calculate duration
        if len(timestamps) > 1:
            duration = max(timestamps) - min(timestamps)
            stats["conversation_duration"] = str(duration)
        
        # Extract topics (simple keyword extraction)
        ncc_keywords = ['drill', 'parade', 'camp', 'training', 'uniform', 'rank', 'parade', 'ceremony']
        for keyword in ncc_keywords:
            if keyword in all_content.lower():
                stats["topics_discussed"].append(keyword.title())
        
        return stats

def show_chat_search_interface():
    """Show chat search interface"""
    st.markdown("### 🔍 Search Conversations")
    
    search_query = st.text_input(
        "Search your chat history",
        placeholder="Enter keywords to search...",
        key="chat_search_query"
    )
    
    if search_query:
        messages = st.session_state.get('messages', [])
        filtered_messages = ChatEnhancements.search_conversations(search_query, messages)
        
        if filtered_messages:
            st.success(f"Found {len(filtered_messages)} messages containing '{search_query}'")
            
            for i, message in enumerate(filtered_messages):
                role = message.get('role', '')
                content = message.get('content', '')
                timestamp = message.get('timestamp', '')
                
                with st.expander(f"{'👤 You' if role == 'user' else '🤖 Assistant'} - {timestamp}"):
                    st.markdown(content, unsafe_allow_html=True)
        else:
            st.info("No messages found matching your search.")

def show_conversation_export_interface():
    """Show conversation export interface"""
    st.markdown("### 📤 Export Conversation")
    
    messages = st.session_state.get('messages', [])
    
    if not messages:
        st.info("No conversation to export yet. Start chatting to build your conversation history!")
        return
    
    # Show conversation statistics
    stats = ChatEnhancements.get_conversation_statistics(messages)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Messages", stats["total_messages"])
    with col2:
        st.metric("Your Questions", stats["user_messages"])
    with col3:
        st.metric("AI Responses", stats["assistant_messages"])
    
    st.metric("Total Words", stats["total_words"])
    
    if stats["topics_discussed"]:
        st.write("**Topics Discussed:**", ", ".join(stats["topics_discussed"]))
    
    # Export options
    st.markdown("#### Choose Export Format:")
    
    export_format = st.selectbox(
        "Select format",
        ["markdown", "html", "json", "txt"],
        format_func=lambda x: {
            "markdown": "📝 Markdown (.md)",
            "html": "🌐 HTML (.html)",
            "json": "📊 JSON (.json)",
            "txt": "📄 Plain Text (.txt)"
        }[x]
    )
    
    if st.button("📥 Generate Export", key="export_conversation"):
        export_content = ChatEnhancements.export_conversation(messages, export_format)
        
        # Create download button
        file_extension = export_format if export_format != "txt" else "txt"
        filename = f"ncc_chat_conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_extension}"
        
        st.download_button(
            label=f"💾 Download {export_format.upper()} file",
            data=export_content,
            file_name=filename,
            mime=f"text/{export_format}" if export_format != "json" else "application/json"
        )
        
        # Preview
        with st.expander("📋 Preview Export Content"):
            if export_format == "html":
                st.components.v1.html(export_content, height=400, scrolling=True)
            else:
                st.code(export_content[:1000] + "..." if len(export_content) > 1000 else export_content)

def add_chat_enhancements_css():
    """Add CSS for chat enhancements"""
    st.markdown("""
    <style>
    .ncc-highlight {
        background: linear-gradient(135deg, #ffeb3b 0%, #ffc107 100%);
        font-weight: bold;
        padding: 2px 4px;
        border-radius: 3px;
    }
    
    .drill-command {
        color: #d32f2f;
        font-weight: bold;
        text-transform: uppercase;
    }
    
    .rank-highlight {
        background: linear-gradient(135deg, #4caf50 0%, #2e7d32 100%);
        color: white;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: 500;
    }
    
    .chat-search-result {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
    }
    
    .conversation-stats {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
    
    mark {
        background: #ffeb3b;
        padding: 1px 2px;
        border-radius: 2px;
    }
    </style>
    """, unsafe_allow_html=True)
