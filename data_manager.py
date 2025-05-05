"""
Module for managing news data storage and processing.
"""
import json
import logging
import os
from typing import Dict, Any, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataManagerError(Exception):
    """Base exception for data manager errors"""
    pass


class FileOperationError(DataManagerError):
    """Exception raised for file operation errors"""
    pass


class EmptyDataError(DataManagerError):
    """Exception raised when data file is empty"""
    pass


def read_json_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Read data from a JSON file

    Args:
        file_path: Path to the JSON file

    Returns:
        List of data items from the JSON file

    Raises:
        FileOperationError: If file cannot be read or parsed
    """
    try:
        if not os.path.exists(file_path):
            logger.warning(f"File {file_path} does not exist. Returning empty list.")
            return []

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            logger.warning(f"Expected list in {file_path}, but got {type(data)}. Converting to list.")
            data = [data]

        return data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from {file_path}: {str(e)}")
        raise FileOperationError(f"Failed to parse JSON: {str(e)}") from e
    except IOError as e:
        logger.error(f"Failed to read file {file_path}: {str(e)}")
        raise FileOperationError(f"Failed to read file: {str(e)}") from e


def write_json_file(file_path: str, data: List[Dict[str, Any]]) -> None:
    """
    Write data to a JSON file

    Args:
        file_path: Path to the JSON file
        data: List of data items to write

    Raises:
        FileOperationError: If file cannot be written
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Successfully wrote {len(data)} items to {file_path}")
    except IOError as e:
        logger.error(f"Failed to write to file {file_path}: {str(e)}")
        raise FileOperationError(f"Failed to write to file: {str(e)}") from e


def get_and_remove_first_item(file_path: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Get the first item from a JSON file and remove it from the list

    Args:
        file_path: Path to the JSON file

    Returns:
        Tuple containing the first item and the remaining items

    Raises:
        EmptyDataError: If the file is empty or contains an empty list
        FileOperationError: If file operations fail
    """
    try:
        data = read_json_file(file_path)

        if not data:
            logger.error(f"No data found in {file_path}")
            raise EmptyDataError(f"No data found in {file_path}")

        first_item = data.pop(0)
        logger.info(f"Retrieved first item from {file_path}")

        return first_item, data
    except FileOperationError:
        # Re-raise if it's already a FileOperationError
        raise
    except Exception as e:
        logger.error(f"Failed to get and remove first item: {str(e)}")
        raise DataManagerError(f"Failed to get and remove first item: {str(e)}") from e


def process_next_item(file_path: str, processor_func) -> Optional[Dict[str, Any]]:
    """
    Process the next item in the data file

    Args:
        file_path: Path to the JSON file
        processor_func: Function to process the item

    Returns:
        The processed item or None if processing failed
    """
    try:
        item, remaining_data = get_and_remove_first_item(file_path)

        # Process the item
        result = processor_func(item)

        # Update the file with the remaining data
        write_json_file(file_path, remaining_data)

        logger.info("Successfully processed an item and updated the data file")
        return item
    except EmptyDataError as e:
        logger.warning(str(e))
        return None
    except DataManagerError as e:
        logger.error(f"Data manager error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error processing item: {str(e)}")
        return None