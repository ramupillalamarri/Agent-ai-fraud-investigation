"""Feature engineering module for calculating retail fraud behavior signals."""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
from ml.config import PreprocessingConfig
from ml.utils.logger import get_ml_logger

logger = get_ml_logger(__name__)

# Independent feature engineering functions (not dataset-specific)

def extract_hour(df: pd.DataFrame, datetime_col: str) -> pd.Series:
    """Extracts the hour of day (0-23) from a datetime column.
    
    Args:
        df: Input DataFrame.
        datetime_col: Column name containing datetime values.
        
    Returns:
        pd.Series: Integer hour representations.
    """
    if datetime_col not in df.columns:
        raise KeyError(f"Datetime column '{datetime_col}' not found in DataFrame.")
    return pd.to_datetime(df[datetime_col]).dt.hour

def extract_day_of_week(df: pd.DataFrame, datetime_col: str) -> pd.Series:
    """Extracts the day of the week (0=Monday, 6=Sunday) from a datetime column.
    
    Args:
        df: Input DataFrame.
        datetime_col: Column name containing datetime values.
        
    Returns:
        pd.Series: Integer day representations.
    """
    if datetime_col not in df.columns:
        raise KeyError(f"Datetime column '{datetime_col}' not found in DataFrame.")
    return pd.to_datetime(df[datetime_col]).dt.dayofweek

def extract_weekend_flag(df: pd.DataFrame, datetime_col: str) -> pd.Series:
    """Generates a binary flag indicating if a datetime falls on a weekend.
    
    Args:
        df: Input DataFrame.
        datetime_col: Column name containing datetime values.
        
    Returns:
        pd.Series: Binary flags (1 = Weekend, 0 = Weekday).
    """
    dayofweek = extract_day_of_week(df, datetime_col)
    return dayofweek.isin([5, 6]).astype(int)

def create_amount_buckets(
    df: pd.DataFrame, 
    amount_col: str, 
    bins: Optional[List[float]] = None,
    labels: Optional[List[str]] = None
) -> pd.Series:
    """Bins continuous numerical amount values into discrete range labels.
    
    Args:
        df: Input DataFrame.
        amount_col: Column name containing monetary transaction values.
        bins: List of float values representing boundaries.
        labels: String identifiers for the resulting buckets.
        
    Returns:
        pd.Series: Binned category objects (returned as strings for encoding).
    """
    if amount_col not in df.columns:
        raise KeyError(f"Amount column '{amount_col}' not found in DataFrame.")
        
    # Default bins: low, medium, high, suspicious
    if bins is None:
        bins = [0.0, 50.0, 200.0, 1000.0, np.inf]
    if labels is None:
        labels = ["low", "medium", "high", "critical"]
        
    binned = pd.cut(df[amount_col], bins=bins, labels=labels, right=True)
    return binned.astype(str)

def calculate_frequency_counts(df: pd.DataFrame, entity_col: str) -> Dict[Any, int]:
    """Computes occurrence counts for individual entities inside a reference dataframe.
    
    Args:
        df: Input reference DataFrame.
        entity_col: Identifier column to aggregate (e.g. user_id).
        
    Returns:
        Dict[Any, int]: Map of entity values to their transaction frequency counts.
    """
    if entity_col not in df.columns:
        raise KeyError(f"Entity column '{entity_col}' not found in DataFrame.")
    return df[entity_col].value_counts().to_dict()


class FeatureEngineer:
    """Orchestrates independent feature engineering functions based on config columns.
    
    Stores fitted behavioral frequencies from the training data for repeatable mappings 
    during real-time prediction.
    """

    def __init__(self, config: Optional[PreprocessingConfig] = None) -> None:
        """Initializes the feature engineer.
        
        Args:
            config: Preprocessing configurations containing metadata.
        """
        self.config = config or PreprocessingConfig()
        
        # Baselines stored during fit for prediction routing lookup
        self.user_frequency_baselines: Dict[Any, int] = {}
        self.merchant_frequency_baselines: Dict[Any, int] = {}
        self.device_frequency_baselines: Dict[Any, int] = {}
        
        logger.info("Initialized FeatureEngineer")

    def fit(self, df: pd.DataFrame) -> "FeatureEngineer":
        """Calculates frequency baselines from training data to avoid test set leakage.
        
        Args:
            df: Cleaned input training DataFrame.
            
        Returns:
            FeatureEngineer: Fitted instance.
        """
        logger.info("Fitting FeatureEngineer...")
        
        try:
            # 1. Fit User Frequency Baselines
            if "user_id" in df.columns:
                self.user_frequency_baselines = calculate_frequency_counts(df, "user_id")
                
            # 2. Fit Merchant Frequency Baselines
            if "merchant_id" in df.columns:
                self.merchant_frequency_baselines = calculate_frequency_counts(df, "merchant_id")
                
            # 3. Fit Device Frequency Baselines
            if "device_id" in df.columns:
                self.device_frequency_baselines = calculate_frequency_counts(df, "device_id")
                
            logger.info(
                "Fitted frequency baselines. Users: %d, Merchants: %d, Devices: %d",
                len(self.user_frequency_baselines),
                len(self.merchant_frequency_baselines),
                len(self.device_frequency_baselines)
            )
            return self
        except Exception as e:
            logger.error("Failed to fit FeatureEngineer: %s", str(e))
            raise

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Invokes the individual engineering methods to generate behavioral and statistical features.
        
        Args:
            df: Cleaned input DataFrame.
            
        Returns:
            pd.DataFrame: DataFrame containing newly engineered columns.
        """
        logger.info("Creating engineered features...")
        try:
            feat_df = df.copy()
            
            # 1. Apply Temporal Features
            for dt_col in self.config.datetime_columns:
                if dt_col in feat_df.columns:
                    feat_df[f"{dt_col}_hour"] = extract_hour(feat_df, dt_col)
                    feat_df[f"{dt_col}_dayofweek"] = extract_day_of_week(feat_df, dt_col)
                    feat_df[f"{dt_col}_is_weekend"] = extract_weekend_flag(feat_df, dt_col)
                    logger.debug("Applied temporal features for %s", dt_col)
                    
            # 2. Apply Amount Bucketing Features
            # Amount column should exist
            if "amount" in feat_df.columns:
                feat_df["amount_bucket"] = create_amount_buckets(feat_df, "amount")
                # Add amount_bucket to categorical list dynamically so encoder captures it
                if "amount_bucket" not in self.config.categorical_columns:
                    self.config.categorical_columns.append("amount_bucket")
                logger.debug("Applied transaction amount buckets.")
                
            # 3. Apply Behavioral Frequency Mapping (using fitted frequencies, default to 1 for unseen values)
            if "user_id" in feat_df.columns:
                feat_df["user_transaction_frequency"] = feat_df["user_id"].map(self.user_frequency_baselines).fillna(1).astype(int)
            else:
                logger.warning("user_id column missing. User transaction frequency set to default (1).")
                feat_df["user_transaction_frequency"] = 1
                
            if "merchant_id" in feat_df.columns:
                feat_df["merchant_transaction_frequency"] = feat_df["merchant_id"].map(self.merchant_frequency_baselines).fillna(1).astype(int)
            else:
                logger.warning("merchant_id column missing. Merchant transaction frequency set to default (1).")
                feat_df["merchant_transaction_frequency"] = 1
                
            if "device_id" in feat_df.columns:
                feat_df["device_transaction_frequency"] = feat_df["device_id"].map(self.device_frequency_baselines).fillna(1).astype(int)
            else:
                # Add default fallback
                feat_df["device_transaction_frequency"] = 1
                
            logger.info("Feature engineering complete. Output shape: %s", feat_df.shape)
            return feat_df
        except Exception as e:
            logger.error("Failed to run feature engineering transform: %s", str(e))
            raise

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fits baseline parameters and applies engineering operations.
        
        Args:
            df: Input DataFrame.
            
        Returns:
            pd.DataFrame: Transformed DataFrame.
        """
        return self.fit(df).transform(df)
