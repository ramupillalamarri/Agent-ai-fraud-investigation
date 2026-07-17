"""Data loading module for fetching raw records and saving processed features."""

import os
import pandas as pd
from typing import Optional
from ml.config import PathConfig
from ml.utils.logger import get_ml_logger

logger = get_ml_logger(__name__)

class DataLoader:
    """Handles raw data loading and storage of processed intermediate states."""

    def __init__(self, path_config: Optional[PathConfig] = None) -> None:
        """Initializes the loader with specific path parameters.
        
        Args:
            path_config: Optional path configurations. If none, defaults are used.
        """
        self.path_config = path_config or PathConfig()
        logger.info("Initialized DataLoader with base directory: %s", self.path_config.base_dir)

    def load_raw_dataset(self, filename: str) -> pd.DataFrame:
        """Loads a raw dataset file (CSV or Parquet) from the raw datasets folder.
        
        Args:
            filename: Name of the file inside raw_data_dir (e.g. 'transactions.csv').
            
        Returns:
            pd.DataFrame: Loaded dataset.
            
        Raises:
            FileNotFoundError: If the specified file does not exist.
        """
        file_path = os.path.join(self.path_config.raw_data_dir, filename)
        if not os.path.exists(file_path):
            error_msg = f"Raw data file not found at path: {file_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
            
        logger.info("Loading raw dataset from %s", file_path)
        
        try:
            # Check format and load accordingly
            if filename.endswith(".csv"):
                df = pd.read_csv(file_path)
            elif filename.endswith(".parquet") or filename.endswith(".pq"):
                df = pd.read_parquet(file_path)
            else:
                # TODO: Add support for JSON/JSONL format if required by raw logs
                raise ValueError(f"Unsupported file format: {filename}")
                
            logger.info("Successfully loaded dataset with shape %s from %s", df.shape, filename)
            return df
        except Exception as e:
            logger.error("Error loading file %s: %s", filename, str(e))
            raise

    def save_processed_dataset(self, df: pd.DataFrame, filename: str) -> None:
        """Saves a processed Pandas DataFrame to the processed data directory.
        
        Args:
            df: The processed Pandas DataFrame to save.
            filename: The target filename (e.g. 'features.parquet').
        """
        os.makedirs(self.path_config.processed_data_dir, exist_ok=True)
        file_path = os.path.join(self.path_config.processed_data_dir, filename)
        
        logger.info("Saving processed dataset of shape %s to %s", df.shape, file_path)
        
        try:
            if filename.endswith(".csv"):
                df.to_csv(file_path, index=False)
            elif filename.endswith(".parquet") or filename.endswith(".pq"):
                df.to_parquet(file_path, index=False)
            else:
                raise ValueError(f"Unsupported export format: {filename}")
            logger.info("Successfully saved processed dataset.")
        except Exception as e:
            logger.error("Error saving processed dataset: %s", str(e))
            raise
