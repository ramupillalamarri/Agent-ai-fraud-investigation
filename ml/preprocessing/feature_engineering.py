"""Feature engineering module for calculating retail fraud-specific signals."""

import pandas as pd
import numpy as np
from typing import Optional, Dict
from ml.config import PreprocessingConfig
from ml.utils.logger import get_ml_logger

logger = get_ml_logger(__name__)

class FeatureEngineer:
    """Calculates behavioral, time-based, and aggregational indicators for fraud detection."""

    def __init__(self, config: Optional[PreprocessingConfig] = None) -> None:
        """Initializes the feature engineer.
        
        Args:
            config: Preprocessing configurations containing target columns.
        """
        self.config = config or PreprocessingConfig()
        self.user_historical_avg_amount: Dict[str, float] = {}
        logger.info("Initialized FeatureEngineer")

    def fit(self, df: pd.DataFrame) -> "FeatureEngineer":
        """Computes statistical baselines (e.g., historical user spend averages) from training data.
        
        Args:
            df: Input training DataFrame (already cleaned).
            
        Returns:
            FeatureEngineer: Fitted instance.
        """
        logger.info("Fitting FeatureEngineer on DataFrame of shape %s", df.shape)
        
        try:
            # Calculate historical spend baseline per user
            if "user_id" in df.columns and "amount" in df.columns:
                user_averages = df.groupby("user_id")["amount"].mean()
                self.user_historical_avg_amount = user_averages.to_dict()
                logger.info("Calculated historical baseline averages for %d users", len(self.user_historical_avg_amount))
            else:
                logger.warning("user_id or amount columns missing. Cannot calculate historical averages.")
                
            return self
        except Exception as e:
            logger.error("Error during FeatureEngineer fit: %s", str(e))
            raise

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applies feature calculations such as transaction frequency, hour of day, and deviation from mean.
        
        Args:
            df: Input cleaned DataFrame to engineer features for.
            
        Returns:
            pd.DataFrame: DataFrame with engineered features appended.
        """
        logger.info("Transforming DataFrame of shape %s with FeatureEngineer", df.shape)
        
        try:
            engineered_df = df.copy()
            
            # 1. Temporal Features (Hour of day, day of week)
            # Find the datetime column
            for datetime_col in self.config.datetime_columns:
                if datetime_col in engineered_df.columns:
                    # Check if conversion is needed or already performed
                    dt_series = pd.to_datetime(engineered_df[datetime_col])
                    engineered_df[f"{datetime_col}_hour"] = dt_series.dt.hour
                    engineered_df[f"{datetime_col}_dayofweek"] = dt_series.dt.dayofweek
                    engineered_df[f"{datetime_col}_is_weekend"] = dt_series.dt.dayofweek.isin([5, 6]).astype(int)
                    logger.debug("Extracted temporal features from %s", datetime_col)
                    
            # 2. Amount Deviation Feature
            # Calculates how much the current amount deviates from the user's historical baseline
            if "user_id" in engineered_df.columns and "amount" in engineered_df.columns:
                # Map baseline averages, default to global median if user not found in training baselines
                global_median = engineered_df["amount"].median()
                user_base = engineered_df["user_id"].map(self.user_historical_avg_amount).fillna(global_median)
                
                # Prevent division by zero
                user_base = user_base.replace(0, 1.0)
                engineered_df["amount_to_historical_avg_ratio"] = engineered_df["amount"] / user_base
                logger.debug("Calculated amount_to_historical_avg_ratio feature")
                
            # 3. Transaction Velocity Mock Feature (placeholder logic layout)
            # TODO: Implement transaction velocity (e.g. transactions in the last 10 minutes)
            # requiring sorting and rolling windows when building live feature stores.
            
            logger.info("Completed feature engineering. Output shape: %s", engineered_df.shape)
            return engineered_df
        except Exception as e:
            logger.error("Error during FeatureEngineer transformation: %s", str(e))
            raise

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Helper to fit and transform in a single call.
        
        Args:
            df: Input DataFrame.
            
        Returns:
            pd.DataFrame: Transformed DataFrame.
        """
        return self.fit(df).transform(df)
