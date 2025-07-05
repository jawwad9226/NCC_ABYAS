# Advanced Chat Interface Improvements

## Current Issues:
- Basic message display without rich formatting
- No message search/filter functionality  
- Limited context awareness
- No conversation export/sharing

## Recommended Enhancements:

### 1. Rich Message Formatting

```python
# Enhanced chat_interface.py additions
import markdown
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

class MessageFormatter:
    @staticmethod
    def format_message(content: str) -> str:
        """Format message with markdown, code highlighting, and NCC-specific formatting"""
        
        # Convert markdown to HTML
        html = markdown.markdown(content, extensions=['codehilite', 'tables', 'fenced_code'])
        
        # Add NCC-specific formatting
        html = MessageFormatter.add_ncc_formatting(html)
        
        return html
    
    @staticmethod
    def add_ncc_formatting(html: str) -> str:
        """Add NCC-specific formatting like rank badges, unit mentions"""
        import re
        
        # Format NCC ranks
        ranks = ['CDT', 'LCDT', 'SGT', 'JUO', 'SUO', 'CSM', 'RSMCSM']
        for rank in ranks:
            pattern = rf'\b{rank}\b'
            replacement = f'<span class="ncc-rank">{rank}</span>'
            html = re.sub(pattern, replacement, html, flags=re.IGNORECASE)
        
        # Format unit references (e.g., 1 DEL BN NCC)
        unit_pattern = r'\b\d+\s+[A-Z]{2,3}\s+BN\s+NCC\b'
        html = re.sub(unit_pattern, r'<span class="ncc-unit">\g<0></span>', html)
        
        return html

### 2. Conversation Management

```python
class ConversationManager:
    def __init__(self):
        self.conversations = {}
    
    def create_conversation(self, title: str = None) -> str:
        """Create a new conversation thread"""
        import uuid
        conv_id = str(uuid.uuid4())
        self.conversations[conv_id] = {
            'id': conv_id,
            'title': title or f"Conversation {len(self.conversations) + 1}",
            'messages': [],
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        return conv_id
    
    def add_message(self, conv_id: str, role: str, content: str):
        """Add message to conversation"""
        if conv_id in self.conversations:
            message = {
                'role': role,
                'content': content,
                'timestamp': datetime.now(),
                'id': str(uuid.uuid4())
            }
            self.conversations[conv_id]['messages'].append(message)
            self.conversations[conv_id]['updated_at'] = datetime.now()
    
    def search_conversations(self, query: str) -> List[Dict]:
        """Search through conversation history"""
        results = []
        for conv in self.conversations.values():
            for msg in conv['messages']:
                if query.lower() in msg['content'].lower():
                    results.append({
                        'conversation_id': conv['id'],
                        'conversation_title': conv['title'],
                        'message': msg,
                        'context': self.get_message_context(conv['id'], msg['id'])
                    })
        return results
    
    def export_conversation(self, conv_id: str, format: str = 'markdown') -> str:
        """Export conversation in various formats"""
        if conv_id not in self.conversations:
            return ""
        
        conv = self.conversations[conv_id]
        
        if format == 'markdown':
            return self.export_as_markdown(conv)
        elif format == 'pdf':
            return self.export_as_pdf(conv)
        elif format == 'txt':
            return self.export_as_text(conv)
    
    def export_as_markdown(self, conv: Dict) -> str:
        """Export conversation as markdown"""
        output = f"# {conv['title']}\n\n"
        output += f"**Created:** {conv['created_at'].strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for msg in conv['messages']:
            role_emoji = "🧑‍🎓" if msg['role'] == 'user' else "🤖"
            timestamp = msg['timestamp'].strftime('%H:%M:%S')
            output += f"## {role_emoji} {msg['role'].title()} ({timestamp})\n\n"
            output += f"{msg['content']}\n\n---\n\n"
        
        return output

### 3. Smart Suggestions

```python
class SmartSuggestions:
    def __init__(self):
        self.ncc_topics = {
            'drill': ['commands', 'formations', 'movements', 'ceremonies'],
            'weapons': ['rifle', 'drill', 'handling', 'safety'],
            'camps': ['annual', 'combined', 'training', 'adventure'],
            'ranks': ['promotion', 'structure', 'badges', 'responsibilities']
        }
    
    def get_suggestions(self, current_input: str, conversation_history: List[Dict]) -> List[str]:
        """Generate smart suggestions based on input and context"""
        suggestions = []
        
        # Context-based suggestions
        if not current_input.strip():
            suggestions.extend(self.get_starter_suggestions())
        else:
            suggestions.extend(self.get_topic_suggestions(current_input))
            suggestions.extend(self.get_context_suggestions(conversation_history))
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def get_starter_suggestions(self) -> List[str]:
        """Get conversation starter suggestions"""
        return [
            "What are the NCC core values?",
            "How do I prepare for annual training camp?",
            "What are the different ranks in NCC?",
            "Tell me about NCC drill commands",
            "What certificates can I earn in NCC?"
        ]
    
    def get_topic_suggestions(self, input_text: str) -> List[str]:
        """Get topic-based suggestions"""
        suggestions = []
        input_lower = input_text.lower()
        
        for topic, keywords in self.ncc_topics.items():
            if any(keyword in input_lower for keyword in keywords):
                suggestions.extend([
                    f"More about {topic} in NCC",
                    f"Common questions about {topic}",
                    f"How to excel in {topic}"
                ])
        
        return suggestions

### 4. Enhanced UI Components

```python
def render_enhanced_chat():
    """Render enhanced chat interface with search, export, and smart features"""
    
    # Chat controls
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        search_query = st.text_input("🔍 Search conversations", key="chat_search")
    
    with col2:
        if st.button("📤 Export", key="export_chat"):
            st.session_state.show_export_dialog = True
    
    with col3:
        if st.button("🗂️ Organize", key="organize_chat"):
            st.session_state.show_organize_dialog = True
    
    with col4:
        if st.button("⚙️ Settings", key="chat_settings"):
            st.session_state.show_chat_settings = True
    
    # Search results
    if search_query:
        display_search_results(search_query)
    
    # Export dialog
    if st.session_state.get('show_export_dialog', False):
        display_export_dialog()
    
    # Smart suggestions
    suggestions = SmartSuggestions().get_suggestions(
        st.session_state.get('current_input', ''),
        st.session_state.get('messages', [])
    )
    
    if suggestions:
        st.markdown("### 💡 Smart Suggestions")
        cols = st.columns(min(len(suggestions), 3))
        for i, suggestion in enumerate(suggestions):
            with cols[i % 3]:
                if st.button(suggestion, key=f"suggestion_{i}"):
                    st.session_state.current_input = suggestion
                    st.rerun()
```
