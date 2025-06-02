"""
NCC Syllabus Module
Handles syllabus data and provides utilities for topic management and search.
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple, TypedDict
from dataclasses import dataclass
import json
from pathlib import Path


class DifficultyLevel(Enum):
    """Difficulty levels for NCC syllabus"""
    JD_JW = "JD/JW"  # Junior Division/Junior Wing
    SD_SW = "SD/SW"  # Senior Division/Senior Wing
    BOTH = "BOTH"    # Common to both levels


class Wing(Enum):
    """NCC Wings"""
    COMMON = "COMMON"
    ARMY = "ARMY"
    NAVY = "NAVY"
    AIR_FORCE = "AIR_FORCE"


@dataclass
class Topic:
    """Represents a topic in the NCC syllabus"""
    id: str
    title: str
    content: str
    difficulty: List[DifficultyLevel]
    wing: Wing
    chapter_id: str
    section_id: str
    learning_objectives: List[str] = None
    keywords: List[str] = None


class SyllabusManager:
    """Manages the NCC syllabus data and provides search capabilities"""
    
    def __init__(self, data_file: str = "data/syllabus.json"):
        self.data_file = Path(data_file)
        self.chapters: Dict[str, Dict] = {}
        self.topics: Dict[str, Topic] = {}
        self._load_data()
    
    def _load_data(self) -> None:
        """Load syllabus data from JSON file"""
        try:
            if not self.data_file.exists():
                # Initialize with empty data if file doesn't exist
                self._initialize_sample_data()
                return
                
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._process_data(data)
                
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid syllabus data: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to load syllabus: {e}")
    
    def _process_data(self, data: dict) -> None:
        """Process the loaded syllabus data"""
        for chapter_id, chapter_data in data.items():
            self.chapters[chapter_id] = {
                'title': chapter_data.get('title', ''),
                'wing': Wing(chapter_data.get('wing', 'COMMON')),
                'sections': {}
            }
            
            for section_id, section_data in chapter_data.get('sections', {}).items():
                self.chapters[chapter_id]['sections'][section_id] = {
                    'title': section_data.get('title', ''),
                    'difficulty': [DifficultyLevel(d) for d in section_data.get('difficulty', [])]
                }
                
                # Process topics
                for i, topic_title in enumerate(section_data.get('topics', [])):
                    topic_id = f"{chapter_id}_{section_id}_T{i}"
                    self.topics[topic_id] = Topic(
                        id=topic_id,
                        title=topic_title,
                        content=section_data.get('content', ''),
                        difficulty=[DifficultyLevel(d) for d in section_data.get('difficulty', [])],
                        wing=Wing(chapter_data.get('wing', 'COMMON')),
                        chapter_id=chapter_id,
                        section_id=section_id,
                        learning_objectives=section_data.get('learning_objectives', []),
                        keywords=section_data.get('keywords', [])
                    )
    
    def _initialize_sample_data(self) -> None:
        """Initialize with sample data if no data file exists"""
        sample_data = {
            "CHAPTER-I": {
                "title": "NCC",
                "wing": "COMMON",
                "sections": {
                    "SECTION-1": {
                        "title": "General",
                        "difficulty": ["JD/JW", "SD/SW"],
                        "topics": [
                            "History and formation of NCC",
                            "Aims and objectives of NCC",
                            "NCC motto and pledge",
                            "Organization structure"
                        ],
                        "learning_objectives": [
                            "Understanding NCC's role in nation building",
                            "Knowledge of NCC history and evolution",
                            "Comprehension of NCC values and principles"
                        ],
                        "keywords": ["history", "organization", "structure"]
                    }
                }
            }
        }
        self._process_data(sample_data)
    
    def get_chapters(self, wing: Wing = None) -> List[Dict]:
        """Get all chapters, optionally filtered by wing"""
        return [
            {'id': cid, 'title': data['title']}
            for cid, data in self.chapters.items()
            if wing is None or data['wing'] == wing
        ]
    
    def get_sections(self, chapter_id: str, difficulty: DifficultyLevel = None) -> List[Dict]:
        """Get all sections for a chapter, optionally filtered by difficulty"""
        if chapter_id not in self.chapters:
            return []
            
        sections = []
        for sid, sdata in self.chapters[chapter_id]['sections'].items():
            if difficulty is None or difficulty in sdata['difficulty']:
                sections.append({
                    'id': sid,
                    'title': sdata['title'],
                    'difficulty': sdata['difficulty']
                })
        return sections
    
    def get_topics(self, chapter_id: str = None, section_id: str = None, 
                  difficulty: DifficultyLevel = None) -> List[Topic]:
        """Get topics with optional filters"""
        filtered = []
        for topic in self.topics.values():
            if chapter_id and topic.chapter_id != chapter_id:
                continue
            if section_id and topic.section_id != section_id:
                continue
            if difficulty and difficulty not in topic.difficulty:
                continue
            filtered.append(topic)
        return filtered
    
    def search_topics(self, query: str, difficulty: DifficultyLevel = None) -> List[Topic]:
        """Search topics by keyword in title or content"""
        query = query.lower()
        results = []
        for topic in self.topics.values():
            if difficulty and difficulty not in topic.difficulty:
                continue
                
            if (query in topic.title.lower() or 
                query in topic.content.lower() or
                any(query in kw.lower() for kw in topic.keywords)):
                results.append(topic)
        return results
    
    def get_learning_objectives(self, topic_id: str) -> List[str]:
        """Get learning objectives for a topic"""
        topic = self.topics.get(topic_id)
        return topic.learning_objectives if topic else []
    
    def get_topic_context(self, topic_id: str) -> Dict:
        """Get complete context for a topic including chapter and section info"""
        topic = self.topics.get(topic_id)
        if not topic:
            return None
            
        return {
            'topic': {
                'id': topic.id,
                'title': topic.title,
                'content': topic.content,
                'learning_objectives': topic.learning_objectives,
                'keywords': topic.keywords
            },
            'section': self.chapters[topic.chapter_id]['sections'][topic.section_id],
            'chapter': {
                'id': topic.chapter_id,
                'title': self.chapters[topic.chapter_id]['title']
            }
        }


# Global instance
syllabus_manager = SyllabusManager()

# Example usage:
if __name__ == "__main__":
    # Get all chapters
    chapters = syllabus_manager.get_chapters()
    print("Chapters:", [c['title'] for c in chapters])
    
    # Get sections for a chapter
    if chapters:
        chapter_id = chapters[0]['id']
        sections = syllabus_manager.get_sections(chapter_id)
        print(f"\nSections in {chapters[0]['title']}:", 
              [s['title'] for s in sections])
    
    # Search topics
    results = syllabus_manager.search_topics("history")
    print("\nSearch results for 'history':")
    for topic in results:
        print(f"- {topic.title}")
    
    # Get topic context
    if results:
        context = syllabus_manager.get_topic_context(results[0].id)
        print("\nTopic context:", context['topic']['title'])
