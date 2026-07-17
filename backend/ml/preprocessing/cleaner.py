"""Data cleaning and type alignment component for the preprocessing pipeline."""

import pandas as pd
from typing import Optional, Dict
from ml.config import PreprocessingConfig
from ml.utils.logger import get_ml_logger

logger = get_ml_logger(__name__)

class DataCleaner:
    """Handles missing values, duplicate entries, and incorrect column data types."""

    def __init__(self, config: Optional[PreprocessingConfig] = None) -> None:
        """Initializes the cleaner with the preprocessing config.
        
        Args:
            config: Preprocessing configurations defining missing value strategies.
        """
        self.config = config or PreprocessingConfig()
        self.impute_values: Dict[str, any] = {}
        logger.info("Initialized DataCleaner")

    def fit(self, df: pd.DataFrame) -> "DataCleaner":
        """Calculates values to impute for missing columns based on target strategies.
        
        Args:
            df: Training DataFrame to analyze.
            
        Returns:
            DataCleaner: Fitted cleaner instance.
        """
        logger.info("Fitting DataCleaner on DataFrame of shape %s", df.shape)
        
        try:
            for col, strategy in self.config.missing_value_strategies.items():
                if col not in df.columns:
                    logger.warning("Column '%s' specified in strategy is missing from input", col)
                    continue
                
                # Compute strategy value
                if strategy == "median":
                    self.impute_values[col] = df[col].median()
                elif strategy == "mean":
                    self.impute_values[col] = df[col].mean()
                elif strategy == "mode":
                    self.impute_values[col] = df[col].mode()[0] if not df[col].mode().empty else 0
                elif strategy == "constant":
                    # Assume "unknown" for objects, 0 for numeric
                    self.impute_values[col] = "unknown" if df[col].dtype == "object" else 0
                else:
                    logger.warning("Unknown missing value strategy: %s. Defaulting to mode.", strategy)
                    self.impute_values[col] = df[col].mode()[0] if not df[col].mode().empty else 0
            
            logger.info("Fitted imputation values: %s", self.impute_values)
            return self
        except Exception as e:
            logger.error("Error during DataCleaner fit: %s", str(e))
            raise

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applies missing value imputation, type casting, and deduplication.
        
        Args:
            df: Input DataFrame to clean.
            
        Returns:
            pd.DataFrame: Cleaned DataFrame.
        """
        logger.info("Transforming DataFrame of shape %s with DataCleaner", df.shape)
        
        try:
            cleaned_df = df.copy()
            
            # 1. Drop duplicate rows
            cleaned_df = cleaned_df.drop_duplicates()
            
            # 2. Impute missing values calculated during fit
            for col, val in self.impute_values.items():
                if col in cleaned_df.columns:
                    cleaned_df[col] = cleaned_df[col].fillna(val)
                    
            # TODO: Add dynamic check for other columns with nulls not explicitly configured in config
            
            # 3. Handle datetime conversions
            for col in self.config.datetime_columns:
                if col in cleaned_df.columns:
                    cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors="coerce")
                    
            # 4. Cast categorical columns to string/category types
            for col in self.config.categorical_columns:
                if col in cleaned_df.columns:
                    cleaned_df[col] = cleaned_df[col].astype(str)
                    
            # 5. Cast numeric columns
            for col in self.config.numerical_columns:
                if col in cleaned_df.columns:
                    cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors="coerce")
                    
            logger.info("Completed cleaning. Output shape: %s", cleaned_df.shape)
            return cleaned_df
        except Exception as e:
            logger.error("Error during DataCleaner transformation: %s", str(e))
            raise

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convenience method to fit and transform in one step.
        
        Args:
            df: Input DataFrame to fit and transform.
            
        Returns:
            pd.DataFrame: Cleaned DataFrame.
        """
        return self.fit(df).transform(df)
