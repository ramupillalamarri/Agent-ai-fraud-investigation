"""Data cleaning, missing value imputation, type casting, and validation module."""

import pandas as pd
from typing import Optional, Dict, Any
from ml.config import PreprocessingConfig
from ml.utils.logger import get_ml_logger

logger = get_ml_logger(__name__)

class DataCleaner:
    """Handles missing values, duplicate removal, invalid value filtering, and type parsing."""

    def __init__(self, config: Optional[PreprocessingConfig] = None) -> None:
        """Initializes the cleaner with configurations.
        
        Args:
            config: Preprocessing configurations containing missing value strategies.
        """
        self.config = config or PreprocessingConfig()
        self.impute_values: Dict[str, Any] = {}
        logger.info("Initialized DataCleaner")

    def fit(self, df: pd.DataFrame) -> "DataCleaner":
        """Calculates default imputation values for columns from the training set.
        
        Args:
            df: Training DataFrame.
            
        Returns:
            DataCleaner: Fitted instance.
        """
        logger.info("Fitting DataCleaner on dataset of shape %s", df.shape)
        
        try:
            for col, strategy in self.config.missing_value_strategies.items():
                if col not in df.columns:
                    logger.warning("Configured column '%s' for missing values is not in the data", col)
                    continue
                
                # Compute statistical defaults
                if strategy == "median":
                    self.impute_values[col] = df[col].median()
                elif strategy == "mean":
                    self.impute_values[col] = df[col].mean()
                elif strategy == "mode":
                    self.impute_values[col] = df[col].mode()[0] if not df[col].mode().empty else 0
                elif strategy == "constant":
                    # Fill categorical with 'unknown', numeric with 0
                    self.impute_values[col] = "unknown" if df[col].dtype == "object" else 0
                else:
                    logger.warning("Unrecognized imputation strategy '%s' for '%s'. Defaulting to mode.", strategy, col)
                    self.impute_values[col] = df[col].mode()[0] if not df[col].mode().empty else 0
            
            logger.info("Imputation baselines computed: %s", self.impute_values)
            return self
        except Exception as e:
            logger.error("Error fitting DataCleaner: %s", str(e))
            raise

    def parse_datetimes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Robustly parses datetime columns to datetime formats.
        
        Args:
            df: Input DataFrame.
            
        Returns:
            pd.DataFrame: DataFrame with parsed datetimes.
        """
        cleaned_df = df.copy()
        for col in self.config.datetime_columns:
            if col in cleaned_df.columns:
                logger.debug("Parsing datetime column: %s", col)
                cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors="coerce")
                
                # Validation check: count unparseable dates
                nat_count = cleaned_df[col].isna().sum()
                if nat_count > 0:
                    logger.warning("Found %d invalid/unparseable timestamps in '%s'", nat_count, col)
        return cleaned_df

    def detect_and_filter_invalid_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Identifies and filters out logically invalid entries (e.g. amount <= 0, age < 0).
        
        Args:
            df: Input DataFrame.
            
        Returns:
            pd.DataFrame: Cleaned DataFrame with invalid values resolved or dropped.
        """
        cleaned_df = df.copy()
        initial_len = len(cleaned_df)
        
        # 1. Validate Transaction Amounts: must be positive
        if "amount" in cleaned_df.columns:
            invalid_amt_mask = cleaned_df["amount"] <= 0
            invalid_amt_count = invalid_amt_mask.sum()
            if invalid_amt_count > 0:
                logger.warning("Detected %d transactions with negative/zero amount. Filtering them out.", invalid_amt_count)
                cleaned_df = cleaned_df[~invalid_amt_mask]
                
        # 2. Validate Customer Age: must be non-negative
        if "user_age" in cleaned_df.columns:
            invalid_age_mask = cleaned_df["user_age"] < 0
            invalid_age_count = invalid_age_mask.sum()
            if invalid_age_count > 0:
                logger.warning("Detected %d profiles with negative age. Filtering them out.", invalid_age_count)
                cleaned_df = cleaned_df[~invalid_age_mask]
                
        # TODO: Add dynamic validation rules for customer credit scores or balance limits if available
        
        filtered_count = initial_len - len(cleaned_df)
        if filtered_count > 0:
            logger.info("Filtered %d rows due to invalid data values.", filtered_count)
            
        return cleaned_df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applies missing value imputation, parsing, invalid value filtering, and deduplication.
        
        Args:
            df: Raw DataFrame.
            
        Returns:
            pd.DataFrame: Cleaned DataFrame.
        """
        logger.info("Cleaning dataset of shape %s...", df.shape)
        try:
            # 1. Remove duplicate records
            cleaned_df = df.drop_duplicates()
            dup_diff = len(df) - len(cleaned_df)
            if dup_diff > 0:
                logger.info("Dropped %d duplicate rows.", dup_diff)
                
            # 2. Parse datetimes
            cleaned_df = self.parse_datetimes(cleaned_df)
            
            # 3. Filter invalid records
            cleaned_df = self.detect_and_filter_invalid_values(cleaned_df)
            
            # 4. Impute missing values
            for col, val in self.impute_values.items():
                if col in cleaned_df.columns:
                    null_count = cleaned_df[col].isna().sum()
                    if null_count > 0:
                        logger.debug("Imputing %d missing values in '%s' with %s", null_count, col, val)
                        cleaned_df[col] = cleaned_df[col].fillna(val)
                        
            # 5. Type casting verification (aligning schema fields)
            for col in self.config.categorical_columns:
                if col in cleaned_df.columns:
                    cleaned_df[col] = cleaned_df[col].astype(str)
                    
            for col in self.config.numerical_columns:
                if col in cleaned_df.columns:
                    cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors="coerce")
                    
            logger.info("Cleaning dataset complete. Cleaned shape: %s", cleaned_df.shape)
            return cleaned_df
        except Exception as e:
            logger.error("Error during data cleaning execution: %s", str(e))
            raise

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fits on training set and cleans in one step.
        
        Args:
            df: Input DataFrame.
            
        Returns:
            pd.DataFrame: Cleaned DataFrame.
        """
        return self.fit(df).transform(df)
