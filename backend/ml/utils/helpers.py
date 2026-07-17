"""General helper utilities for data, model IO, and validation operations."""

import os
import json
import joblib
from typing import Any, Dict
from ml.utils.logger import get_ml_logger

logger = get_ml_logger(__name__)

def ensure_directory_exists(directory_path: str) -> None:
    """Ensures that a directory exists, creating parent directories if necessary.
    
    Args:
        directory_path: Path to the target directory.
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)
        logger.info("Created directory: %s", directory_path)

def save_serialized_artifact(artifact: Any, file_path: str) -> None:
    """Saves a Python object to disk using Joblib serialization.
    
    Args:
        artifact: The object to serialize (e.g. model, encoder).
        file_path: The target file path to write to.
    """
    try:
        ensure_directory_exists(os.path.dirname(file_path))
        joblib.dump(artifact, file_path)
        logger.info("Successfully saved serialized artifact to %s", file_path)
    except Exception as e:
        logger.error("Failed to save serialized artifact to %s: %s", file_path, str(e))
        raise

def load_serialized_artifact(file_path: str) -> Any:
    """Loads a serialized Python object from disk using Joblib.
    
    Args:
        file_path: The source file path.
        
    Returns:
        Any: The deserialized Python object.
    """
    if not os.path.exists(file_path):
        error_msg = f"Artifact file does not exist at {file_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
        
    try:
        artifact = joblib.load(file_path)
        logger.info("Successfully loaded serialized artifact from %s", file_path)
        return artifact
    except Exception as e:
        logger.error("Failed to load serialized artifact from %s: %s", file_path, str(e))
        raise

def save_json_metadata(metadata: Dict[str, Any], file_path: str) -> None:
    """Saves a dictionary as a JSON file.
    
    Args:
        metadata: Dictionary containing metadata.
        file_path: Target path to write JSON file.
    """
    try:
        ensure_directory_exists(os.path.dirname(file_path))
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)
        logger.info("Successfully saved JSON metadata to %s", file_path)
    except Exception as e:
        logger.error("Failed to save JSON metadata to %s: %s", file_path, str(e))
        raise

def load_json_metadata(file_path: str) -> Dict[str, Any]:
    """Loads JSON metadata from disk.
    
    Args:
        file_path: The JSON source file path.
        
    Returns:
        Dict[str, Any]: Parsed JSON data.
    """
    if not os.path.exists(file_path):
        error_msg = f"JSON file does not exist at {file_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        logger.info("Successfully loaded JSON metadata from %s", file_path)
        return metadata
    except Exception as e:
        logger.error("Failed to load JSON metadata from %s: %s", file_path, str(e))
        raise
