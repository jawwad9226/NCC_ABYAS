"""
JSON schema validation for data files
"""
import json
from typing import Dict, Any, Optional
from pathlib import Path
import jsonschema

# Schema definitions
SYLLABUS_SCHEMA = {
    "type": "object",
    "properties": {
        "chapters": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "sections": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "content": {"type": "string"},
                                "page_number": {"type": "integer"}
                            },
                            "required": ["name", "content"]
                        }
                    }
                },
                "required": ["title", "sections"]
            }
        }
    },
    "required": ["chapters"]
}

VIDEOS_SCHEMA = {
    "type": "object",
    "properties": {
        "version": {"type": "string"}
    },
    "patternProperties": {
        # This pattern matches any property key that is NOT "version"
        # These keys are expected to be category names.
        "^(?!version$).*$": { 
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"}, # Can be YouTube ID or manual
                    "title": {"type": "string"},
                    "url": {"type": "string", "format": "uri-reference"},
                    "description": {"type": "string"},
                    "duration": {"type": "string"}, # Format like "HH:MM:SS" or "MM:SS"
                    "thumbnail": {"type": "string", "format": "uri-reference"}, # URL or local path placeholder
                    "tags": {"type": "array", "items": {"type": "string"}},
                    # Optional fields for overriding API-fetched data
                    "title_override": {"type": "string"},
                    "description_override": {"type": "string"}
                },
                "required": ["title", "url"] # Core requirements for a video entry
            }
        }
    },
    "additionalProperties": False # No other top-level keys unless defined (like 'version' or category names)
}

def validate_json_file(file_path: str, schema: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validates a JSON file against a schema
    Returns (is_valid, error_message)
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        jsonschema.validate(instance=data, schema=schema)
        return True, None
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON format: {str(e)}"
    except jsonschema.exceptions.ValidationError as e:
        return False, f"Schema validation error: {str(e)}"
    except Exception as e:
        return False, f"Error validating {file_path}: {str(e)}"

def validate_all_json_files() -> Dict[str, tuple[bool, Optional[str]]]:
    """
    Validates all JSON data files in the project
    Returns a dictionary of results
    """
    base_dir = Path(__file__).parent
    data_dir = base_dir / "data"
    
    results = {}
    
    # Validate syllabus.json
    syllabus_path = data_dir / "syllabus.json"
    if syllabus_path.exists():
        results["syllabus.json"] = validate_json_file(str(syllabus_path), SYLLABUS_SCHEMA)
    
    # Validate videos.json
    videos_path = data_dir / "videos.json"
    if videos_path.exists():
        results["videos.json"] = validate_json_file(str(videos_path), VIDEOS_SCHEMA)
    
    return results

if __name__ == "__main__":
    # When run directly, validate all files and print results
    results = validate_all_json_files()
