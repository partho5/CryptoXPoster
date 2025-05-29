import json
import os
from typing import List, Dict, Any, Union

from data_manager import logger


def prepend_data(existing_path: str, new_data: List[Dict[str, Any]],
                 resolve_path: bool = True, encoding: str = 'utf-8') -> None:
    """
    Prepend new data to existing JSON data in a file.

    Args:
        existing_path: Path to the JSON file (relative or absolute)
        new_data: List of new data items to prepend
        resolve_path: Whether to resolve path relative to parent directory of script
        encoding: File encoding to use (default: 'utf-8')

    Raises:
        IOError: If file cannot be read or written
        ValueError: If new_data is not a list
    """
    if not isinstance(new_data, list):
        raise ValueError("input data must be a list")

    try:
        # Resolve file path if needed
        if resolve_path:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.abspath(os.path.join(base_dir, os.pardir))
            full_file_path = os.path.join(parent_dir, existing_path)
        else:
            full_file_path = existing_path

        # Load existing data if file exists
        existing_data = []
        if os.path.exists(full_file_path):
            try:
                with open(full_file_path, 'r', encoding=encoding) as f:
                    existing_data = json.load(f)
                    # Ensure it's a list
                    if not isinstance(existing_data, list):
                        logger.warning(f"Existing data in {full_file_path} is not a list. Starting with empty list.")
                        existing_data = []
                logger.info(f"Loaded {len(existing_data)} existing items from {full_file_path}")
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(
                    f"Could not load existing data from {full_file_path}: {str(e)}. Starting with empty list.")
                existing_data = []
        else:
            logger.info(f"File {full_file_path} does not exist. Creating new file.")

        # Prepend new data to existing data (new items first)
        combined_data = new_data + existing_data

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(full_file_path), exist_ok=True)

        # Write combined data back to file
        with open(full_file_path, 'w', encoding=encoding) as f:
            json.dump(combined_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Successfully prepended {len(new_data)} new items to {len(existing_data)} existing items")
        logger.info(f"Total items in file: {len(combined_data)}")

    except IOError as e:
        logger.error(f"Failed to save data to {full_file_path}: {str(e)}")
        raise IOError(f"Failed to save data: {str(e)}") from e


DATA_FILE = os.getenv('DATA_FILE', 'news_data.json')


def get_file_path():
    """Get the consistent file path for the data file."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, DATA_FILE)
