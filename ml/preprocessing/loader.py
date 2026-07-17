"""Data loading and schema validation module for raw transaction records."""

import os
import pandas as pd
from typing import Optional, List, Dict, Any
from ml.config import PathConfig, PreprocessingConfig
from ml.utils.logger import get_ml_logger

logger = get_ml_logger(__name__)

class DataLoader:
    """Handles raw CSV/Parquet data loading, existence checking, target verification, and schema validation."""

    def __init__(
        self, 
        path_config: Optional[PathConfig] = None,
        preprocessing_config: Optional[PreprocessingConfig] = None
    ) -> None:
        """Initializes the loader with configurations.
        
        Args:
            path_config: Optional path configurations.
            preprocessing_config: Optional preprocessing parameters (for target column and schema checks).
        """
        self.path_config = path_config or PathConfig()
        self.preprocessing_config = preprocessing_config or PreprocessingConfig()
        logger.info("Initialized DataLoader")

    def validate_file_existence(self, file_path: str) -> None:
        """Verifies that the target file exists on disk.
        
        Args:
            file_path: Absolute or relative path to the file.
            
        Raises:
            FileNotFoundError: If the file does not exist.
        """
        if not os.path.exists(file_path):
            error_msg = f"Data file not found at path: {file_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        logger.debug("File existence verified: %s", file_path)

    def validate_target_column(self, df: pd.DataFrame, target_column: str) -> None:
        """Ensures the dataset contains the required classification target label column.
        
        Args:
            df: Loaded Pandas DataFrame.
            target_column: The expected target label column name.
            
        Raises:
            ValueError: If the target column is missing.
        """
        if target_column not in df.columns:
            error_msg = f"Target column '{target_column}' is missing from the dataset."
            logger.error(error_msg)
            raise ValueError(error_msg)
        logger.debug("Target column presence verified: %s", target_column)

    def validate_schema(self, df: pd.DataFrame, expected_columns: List[str]) -> None:
        """Checks that all essential columns defined in the schema are present in the dataset.
        
        Args:
            df: Loaded Pandas DataFrame.
            expected_columns: List of columns required by the pipeline.
            
        Raises:
            ValueError: If any expected columns are missing.
        """
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            error_msg = f"Schema validation failed. Missing required columns: {missing_columns}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        logger.debug("Schema column presence validation succeeded.")

    def load_csv(self, file_path: str) -> pd.DataFrame:
        """Loads a raw CSV dataset and runs schema and target validations.
        
        Args:
            file_path: The exact path to the CSV file.
            
        Returns:
            pd.DataFrame: Loaded and validated DataFrame.
        """
        self.validate_file_existence(file_path)
        
        logger.info("Loading dataset from %s", file_path)
        try:
            df = pd.read_csv(file_path)
            logger.info("Successfully loaded CSV dataset with shape %s", df.shape)
            
            # Run schema validations
            target_col = self.preprocessing_config.target_column
            self.validate_target_column(df, target_col)
            
            # Assemble expected columns list from config
            expected_cols = (
                self.preprocessing_config.numerical_columns +
                self.preprocessing_config.categorical_columns +
                self.preprocessing_config.datetime_columns +
                self.preprocessing_config.id_columns
            )
            
            # Exclude engineered columns that are created dynamically by feature engineering
            expected_cols = [col for col in expected_cols if col not in ["amount_bucket"]]
            
            # Filter expected columns to exclude target (which is checked separately)
            self.validate_schema(df, expected_cols)
            
            return df
        except Exception as e:
            logger.error("Failed to load or validate dataset: %s", str(e))
            raise

    def load_raw_dataset(self, filename: str) -> pd.DataFrame:
        """Loader proxy method pointing to raw_data_dir for backward compatibility.
        
        Args:
            filename: Name of the raw data file.
            
        Returns:
            pd.DataFrame: Loaded and validated DataFrame.
        """
        file_path = os.path.join(self.path_config.raw_data_dir, filename)
        return self.load_csv(file_path)
