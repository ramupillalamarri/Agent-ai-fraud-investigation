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

    def _map_kaggle_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Translates Kaggle fraud detection columns to the schema expected by the pipeline."""
        df = df.copy()
        
        # Check if Kaggle columns are present
        kaggle_cols = ["trans_num", "cc_num", "merchant", "category", "amt", "trans_date_trans_time", "dob"]
        if all(col in df.columns for col in kaggle_cols):
            logger.info("Auto-detecting Kaggle Fraud Detection dataset format. Mapping columns...")
            
            # Map existing columns
            df["transaction_id"] = df["trans_num"].astype(str)
            df["user_id"] = "USR_" + df["cc_num"].astype(str).str[-4:]
            df["merchant_id"] = df["merchant"].astype(str)
            df["merchant_category"] = df["category"].astype(str)
            df["amount"] = df["amt"].astype(float)
            
            # Timestamp coercion
            df["transaction_timestamp"] = pd.to_datetime(df["trans_date_trans_time"])
            
            # Calculate user age from dob and transaction timestamp
            dob_dt = pd.to_datetime(df["dob"])
            df["user_age"] = (df["transaction_timestamp"] - dob_dt).dt.days // 365
            
            # Map/generate missing columns expected by pipeline
            # Generate deterministic IP address using zip code if present, otherwise default
            if "zip" in df.columns:
                df["ip_address"] = "192.168.1." + (df["zip"] % 250).astype(str)
            else:
                df["ip_address"] = "192.168.1.1"
                
            df["device_id"] = "DEV_" + df["cc_num"].astype(str).str[-4:]
            
            # Mock account balance using city_pop if present, else default
            if "city_pop" in df.columns:
                df["account_balance"] = df["city_pop"].astype(float) * 2.5
            else:
                df["account_balance"] = 1000.0
                
            df["payment_method"] = "credit"
            df["device_type"] = "mobile"
            df["location_country"] = "US"
                
            # Retain target column
            if "is_fraud" in df.columns:
                df["is_fraud"] = df["is_fraud"].astype(int)
                
            # Keep only the expected columns
            expected_cols = [
                "transaction_id", "user_id", "merchant_id", "device_id", "ip_address",
                "amount", "user_age", "account_balance", "merchant_category", "payment_method",
                "device_type", "location_country", "transaction_timestamp"
            ]
            if "is_fraud" in df.columns:
                expected_cols.append("is_fraud")
                
            df = df[expected_cols]
            logger.info("Successfully translated Kaggle columns to standard pipeline schema.")
            
        return df

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
            
            # Map Kaggle schema to standard layout
            df = self._map_kaggle_columns(df)
            
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
