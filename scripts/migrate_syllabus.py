import json
import os
import logging
import jsonschema # Make sure to install: pip install pip install jsonschema
import argparse # For command-line arguments

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define paths using os.path.join for robustness
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Directory of this script
PROJECT_ROOT = os.path.join(BASE_DIR, os.pardir, os.pardir) # Go up two levels to reach project root

# Default file paths - these can now be overridden by CLI arguments
DEFAULT_INPUT_TEXT_FILE = os.path.join(PROJECT_ROOT, "ncc syllabus.txt")
DEFAULT_OUTPUT_JSON_FILE = os.path.join(PROJECT_ROOT, "data", "syllabus.json")
SCHEMA_FILE = os.path.join(PROJECT_ROOT, "data", "syllabus_schema.json")

def _load_json_schema(schema_path):
    """Loads a JSON schema from a given path."""
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        logging.info(f"Successfully loaded JSON schema from '{schema_path}'.")
        return schema
    except FileNotFoundError:
        logging.error(f"Schema file not found: {schema_path}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON schema from {schema_path}: {e}")
        return None

def parse_txt_syllabus(input_filepath, interactive=False):
    """
    Parses a plain text syllabus file into a structured dictionary.
    Assumes chapter titles are typically uppercase and may start with 'CHAPTER'.
    Subsequent lines are treated as sections until a new chapter is found.

    Args:
        input_filepath (str): Path to the input text file.
        interactive (bool): If True, prompts the user on parsing errors.

    Returns:
        dict: The parsed syllabus data, or None if an unrecoverable error occurs.
    """
    syllabus = {"chapters": []}
    current_chapter = None
    logging.info(f"Starting to parse text file: {input_filepath}")

    try:
        with open(input_filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                stripped_line = line.strip()
                if not stripped_line:
                    continue # Skip empty lines

                # Heuristic to detect a new chapter/main section
                # Adjust this logic if your text file has a different chapter pattern
                is_chapter_heading = stripped_line.isupper() and (
                    stripped_line.startswith("CHAPTER") or
                    stripped_line.startswith("SECTION") or
                    stripped_line.startswith("PART") or
                    len(stripped_line.split()) <= 5 # Heuristic: short, all-caps lines
                )

                if is_chapter_heading:
                    if current_chapter:
                        syllabus["chapters"].append(current_chapter)
                        logging.debug(f"Added chapter: {current_chapter['title']}")
                    current_chapter = {"title": stripped_line, "sections": []}
                    logging.info(f"Detected new chapter/main section at line {line_num}: '{stripped_line}'")
                elif current_chapter:
                    # Treat other non-empty lines as sections of the current chapter
                    current_chapter["sections"].append({"name": stripped_line})
                    logging.debug(f"Added section to '{current_chapter['title']}': '{stripped_line}'")
                else:
                    # Lines before the first detected chapter/main section
                    logging.info(f"Skipping leading line {line_num} (before first chapter): '{stripped_line}'")
                    if interactive:
                        choice = input(f"Warning: Line {line_num} '{stripped_line}' appears before first chapter. Skip? (y/n/exit): ").lower()
                        if choice == 'exit':
                            logging.error("User chose to exit parsing.")
                            return None
                        elif choice == 'n':
                            logging.warning("User chose not to skip. This line will be ignored for now.")
                    pass

        if current_chapter: # Add the last chapter
            syllabus["chapters"].append(current_chapter)
            logging.debug(f"Added final chapter: {current_chapter['title']}")

        logging.info("Finished parsing text file.")
        return syllabus

    except FileNotFoundError:
        logging.error(f"Input text file not found: {input_filepath}")
        return None
    except Exception as e:
        logging.error(f"Error parsing text file {input_filepath}: {e}")
        if interactive:
            choice = input(f"An error occurred during parsing: {e}. Continue anyway? (y/n): ").lower()
            if choice == 'n':
                logging.error("User chose to abort parsing due to error.")
                return None
        return None # Return None if parsing failed and not continuing

def migrate_syllabus_data(input_filepath, output_filepath, schema_filepath, input_type='txt', interactive=False):
    """
    Migrates syllabus data from a source (e.g., text file) to a JSON file.
    Includes JSON schema validation.
    """
    logging.info(f"Starting syllabus migration process (Input type: {input_type}).")
    logging.info(f"Source: '{input_filepath}' -> Destination: '{output_filepath}'")

    syllabus_data = None
    if input_type == 'txt':
        syllabus_data = parse_txt_syllabus(input_filepath, interactive)
        if syllabus_data is None:
            logging.error("Failed to parse syllabus from text file. Migration aborted.")
            return False
    # elif input_type == 'csv':
    #     logging.warning("CSV parsing not yet implemented.")
    #     # Add logic here to parse CSV if needed
    #     # syllabus_data = parse_csv_syllabus(input_filepath)
    #     return False
    else:
        logging.error(f"Unsupported input type: {input_type}. Migration aborted.")
        return False

    # --- Logging parsed counts ---
    num_chapters = len(syllabus_data.get("chapters", []))
    num_sections = sum(len(c.get("sections", [])) for c in syllabus_data.get("chapters", []))
    logging.info(f"Parsed {num_chapters} chapters with {num_sections} sections total.")

    # --- JSON Schema Validation ---
    schema = _load_json_schema(schema_filepath)
    if schema:
        try:
            logging.info(f"Validating generated syllabus data against schema: {schema_filepath}")
            jsonschema.validate(instance=syllabus_data, schema=schema)
            logging.info("Syllabus data successfully validated against schema.")
        except jsonschema.exceptions.ValidationError as e:
            logging.error(f"Syllabus data failed schema validation: {e.message} at {e.path}")
            logging.error("Migration aborted due to schema validation error.")
            return False
        except Exception as e:
            logging.error(f"An unexpected error occurred during schema validation: {e}")
            return False
    else:
        logging.warning("Skipping JSON schema validation as schema could not be loaded.")

    # --- Write to JSON File ---
    try:
        os.makedirs(os.path.dirname(output_filepath), exist_ok=True) # Ensure data directory exists
        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(syllabus_data, f, indent=4, ensure_ascii=False)
        logging.info(f"Successfully migrated data to '{output_filepath}'.")
        return True
    except IOError as e:
        logging.error(f"Error writing output JSON file {output_filepath}: {e}")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred during JSON writing: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate NCC syllabus data from text to JSON.")
    parser.add_argument(
        "--src",
        default=DEFAULT_INPUT_TEXT_FILE,
        help=f"Path to source syllabus text file (default: {DEFAULT_INPUT_TEXT_FILE})"
    )
    parser.add_argument(
        "--dest",
        default=DEFAULT_OUTPUT_JSON_FILE,
        help=f"Path to output JSON file (default: {DEFAULT_OUTPUT_JSON_FILE})"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Enable interactive mode for parsing errors."
    )
    args = parser.parse_args()

    logging.info("Script started: migrate_syllabus.py")
    if migrate_syllabus_data(
        input_filepath=args.src,
        output_filepath=args.dest,
        schema_filepath=SCHEMA_FILE,
        input_type='txt',
        interactive=args.interactive
    ):
        logging.info("Syllabus migration completed successfully.")
    else:
        logging.error("Syllabus migration failed.")
    logging.info("Script finished: migrate_syllabus.py")

