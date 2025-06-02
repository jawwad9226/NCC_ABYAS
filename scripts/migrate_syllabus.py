#!/usr/bin/env python3
"""
NCC Syllabus Migration Script
Converts the detailed syllabus format to the new structured format.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any

# Define paths
PROJECT_ROOT = Path(__file__).parent.parent
DOWNLOAD_FOLDER = Path.home() / "Downloads"
SOURCE_SYLLABUS = DOWNLOAD_FOLDER / "ncc_syllabus.py"
TARGET_SYLLABUS = PROJECT_ROOT / "ncc_syllabus.py"

def copy_syllabus_file():
    """Copy the syllabus file from Downloads to project directory"""
    if not SOURCE_SYLLABUS.exists():
        raise FileNotFoundError(f"Source syllabus file not found at {SOURCE_SYLLABUS}")
    
    # Create backup if target exists
    if TARGET_SYLLABUS.exists():
        backup = PROJECT_ROOT / "ncc_syllabus.py.bak"
        shutil.copy2(TARGET_SYLLABUS, backup)
        print(f"Created backup at {backup}")
    
    shutil.copy2(SOURCE_SYLLABUS, TARGET_SYLLABUS)
    print(f"Copied syllabus to {TARGET_SYLLABUS}")

def migrate_syllabus() -> Dict[str, Any]:
    """Convert the detailed syllabus to the new format"""
    # Import the syllabus after ensuring it's in the right location
    sys.path.append(str(PROJECT_ROOT))
    from ncc_syllabus import NCC_SYLLABUS, DifficultyLevel, Wing
    
    new_syllabus = {}
    
    for chapter_id, chapter_data in NCC_SYLLABUS.items():
        new_chapter = {
            'title': chapter_data['title'],
            'wing': chapter_data['wing'].value,
            'sections': {}
        }
        
        for section_id, section_data in chapter_data.get('sections', {}).items():
            # Skip sections that don't match the difficulty level
            if 'difficulty_restriction' in chapter_data and section_data.get('difficulty') not in chapter_data['difficulty_restriction']:
                continue
                
            new_section = {
                'title': section_data['title'],
                'difficulty': [d.value for d in section_data.get('difficulty', [])],
                'topics': section_data.get('topics', []),
                'learning_objectives': section_data.get('learning_objectives', []),
                'content': ''  # Will be filled from the detailed content
            }
            
            # Extract keywords from topics and learning objectives
            keywords = set()
            for topic in section_data.get('topics', []):
                keywords.update(word.lower() for word in str(topic).split() if len(word) > 3)
            for obj in section_data.get('learning_objectives', []):
                keywords.update(word.lower() for word in str(obj).split() if len(word) > 3)
                
            new_section['keywords'] = list(keywords)
            new_chapter['sections'][section_id] = new_section
            
        new_syllabus[chapter_id] = new_chapter
    
    return new_syllabus

def save_syllabus(data: Dict[str, Any], output_path: str) -> None:
    """Save the migrated syllabus to a JSON file"""
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Syllabus saved to {output_path}")

def main():
    try:
        # First, ensure we have the latest syllabus file
        copy_syllabus_file()
        
        # Define output path
        output_path = PROJECT_ROOT / 'data' / 'syllabus.json'
        
        # Migrate the syllabus
        print("Migrating NCC syllabus...")
        migrated_data = migrate_syllabus()
        
        # Save to file
        save_syllabus(migrated_data, output_path)
        
        print("Migration completed successfully!")
        print(f"Output file: {output_path.absolute()}")
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    import sys
    main()
