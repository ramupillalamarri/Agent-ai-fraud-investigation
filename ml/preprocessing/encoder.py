"""Categorical feature encoding module supporting OneHot, Ordinal, and Label encoders."""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Union, Any
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, LabelEncoder
from ml.config import PreprocessingConfig
from ml.utils.logger import get_ml_logger

logger = get_ml_logger(__name__)

class DataEncoder:
    """Manages auto-detection and encoding of categorical fields and target labels.
    
    Stores fitted scikit-learn encoders internally to support repeatable transformations 
    during real-time prediction and model inference.
    """

    def __init__(
        self, 
        config: Optional[PreprocessingConfig] = None,
        encoding_strategy: str = "onehot"  # options: "onehot", "ordinal"
    ) -> None:
        """Initializes the encoder configurations.
        
        Args:
            config: Preprocessing configurations containing predefined columns.
            encoding_strategy: Choice of categorical encoding ("onehot" or "ordinal").
        """
        self.config = config or PreprocessingConfig()
        self.encoding_strategy = encoding_strategy.lower()
        
        # Encoders stored for inference serialization
        self.one_hot_encoder: Optional[OneHotEncoder] = None
        self.ordinal_encoder: Optional[OrdinalEncoder] = None
        self.label_encoders: Dict[str, LabelEncoder] = {}
        
        self.categorical_cols: List[str] = []
        self.one_hot_feature_names: List[str] = []
        
        logger.info("Initialized DataEncoder with encoding strategy: %s", self.encoding_strategy)

    def detect_categorical_columns(self, df: pd.DataFrame) -> List[str]:
        """Automatically identifies categorical columns based on dtype or config.
        
        Args:
            df: Input DataFrame.
            
        Returns:
            List[str]: Names of categorical columns.
        """
        # Combine config columns with actual dataframe columns of object/category dtypes
        config_cats = set(self.config.categorical_columns)
        detected_cats = set(df.select_dtypes(include=["object", "category", "bool"]).columns)
        
        # Exclude ID or Datetime columns from encoding
        exclusions = set(self.config.id_columns + self.config.datetime_columns + [self.config.target_column])
        
        final_cats = list((config_cats | detected_cats) - exclusions)
        # Filter to make sure they exist in the input dataframe
        final_cats = [col for col in final_cats if col in df.columns]
        
        logger.info("Auto-detected %d categorical columns for encoding: %s", len(final_cats), final_cats)
        return final_cats

    def fit(self, df: pd.DataFrame, target_col: Optional[str] = None) -> "DataEncoder":
        """Identifies columns and fits selected encoding strategies.
        
        Args:
            df: Input training DataFrame.
            target_col: Optional name of the label column to fit a LabelEncoder on.
            
        Returns:
            DataEncoder: Fitted encoder instance.
        """
        logger.info("Fitting DataEncoder...")
        try:
            # 1. Detect columns
            self.categorical_cols = self.detect_categorical_columns(df)
            
            # 2. Fit Feature Encoders
            if self.categorical_cols:
                if self.encoding_strategy == "onehot":
                    self.one_hot_encoder = OneHotEncoder(
                        handle_unknown="ignore", 
                        sparse_output=False,
                        dtype=np.float32
                    )
                    self.one_hot_encoder.fit(df[self.categorical_cols])
                    # Store generated columns names
                    names = self.one_hot_encoder.get_feature_names_out(self.categorical_cols)
                    self.one_hot_feature_names = list(names)
                    logger.info("Fitted OneHotEncoder on %s columns", len(self.categorical_cols))
                    
                elif self.encoding_strategy == "ordinal":
                    self.ordinal_encoder = OrdinalEncoder(
                        handle_unknown="use_encoded_value", 
                        unknown_value=-1,
                        dtype=np.float32
                    )
                    self.ordinal_encoder.fit(df[self.categorical_cols])
                    logger.info("Fitted OrdinalEncoder on %s columns", len(self.categorical_cols))
                    
            # 3. Fit Target LabelEncoder if target is passed and categorical
            actual_target = target_col or self.config.target_column
            if actual_target in df.columns:
                target_series = df[actual_target]
                # Only LabelEncode if target is not numeric
                if target_series.dtype == "object" or target_series.dtype == "category":
                    logger.info("Fitting LabelEncoder on target: %s", actual_target)
                    l_enc = LabelEncoder()
                    l_enc.fit(target_series)
                    self.label_encoders[actual_target] = l_enc
                    
            return self
        except Exception as e:
            logger.error("Failed to fit DataEncoder: %s", str(e))
            raise

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applies fitted encoding strategies on the input DataFrame.
        
        Args:
            df: Input DataFrame.
            
        Returns:
            pd.DataFrame: Transformed DataFrame.
        """
        logger.info("Encoding categorical columns...")
        try:
            encoded_df = df.copy()
            
            if not self.categorical_cols:
                logger.info("No categorical columns to encode.")
                return encoded_df
                
            # 1. Apply Categorical Encoding
            if self.encoding_strategy == "onehot" and self.one_hot_encoder is not None:
                encoded_arr = self.one_hot_encoder.transform(df[self.categorical_cols])
                one_hot_df = pd.DataFrame(
                    encoded_arr, 
                    columns=self.one_hot_feature_names, 
                    index=df.index
                )
                # Drop original categorical columns and append one-hot columns
                encoded_df = encoded_df.drop(columns=self.categorical_cols)
                encoded_df = pd.concat([encoded_df, one_hot_df], axis=1)
                
            elif self.encoding_strategy == "ordinal" and self.ordinal_encoder is not None:
                encoded_arr = self.ordinal_encoder.transform(df[self.categorical_cols])
                encoded_df[self.categorical_cols] = encoded_arr
                
            # 2. Apply Label Encoding for target if needed
            for col, l_enc in self.label_encoders.items():
                if col in encoded_df.columns:
                    logger.debug("Applying LabelEncoder on column: %s", col)
                    encoded_df[col] = l_enc.transform(encoded_df[col].astype(str))
                    
            logger.debug("Encoding complete. Categorical columns encoded.")
            return encoded_df
        except Exception as e:
            logger.error("Failed to apply encoding transformations: %s", str(e))
            raise

    def fit_transform(self, df: pd.DataFrame, target_col: Optional[str] = None) -> pd.DataFrame:
        """Fits on training set and encodes in one step.
        
        Args:
            df: Input DataFrame.
            target_col: Target column name.
            
        Returns:
            pd.DataFrame: Encoded DataFrame.
        """
        return self.fit(df, target_col).transform(df)
        
    def encode_column_labels(self, labels: pd.Series, col_name: str) -> pd.Series:
        """Utility method to fit or transform target columns dynamically.
        
        Args:
            labels: Input Series.
            col_name: Column identifier to cache.
            
        Returns:
            pd.Series: Encoded labels.
        """
        if col_name not in self.label_encoders:
            logger.info("Initializing new LabelEncoder for column '%s'", col_name)
            self.label_encoders[col_name] = LabelEncoder()
            return pd.Series(self.label_encoders[col_name].fit_transform(labels.astype(str)), index=labels.index)
        
        return pd.Series(self.label_encoders[col_name].transform(labels.astype(str)), index=labels.index)

    def decode_column_labels(self, encoded_labels: Union[pd.Series, np.ndarray], col_name: str) -> np.ndarray:
        """Utility method to decode encoded numerical values back to strings.
        
        Args:
            encoded_labels: Encoded category values.
            col_name: Column identifier containing the cached encoder.
            
        Returns:
            np.ndarray: Decoded category labels.
        """
        if col_name not in self.label_encoders:
            error_msg = f"No fitted LabelEncoder found for column '{col_name}'"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        return self.label_encoders[col_name].inverse_transform(encoded_labels)
