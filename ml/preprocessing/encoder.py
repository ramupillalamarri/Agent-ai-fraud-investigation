"""Categorical encoding and numeric scaling module."""

import pandas as pd
from typing import Optional, Dict
from sklearn.preprocessing import OneHotEncoder, StandardScaler, RobustScaler, MinMaxScaler
from ml.config import PreprocessingConfig
from ml.utils.logger import get_ml_logger

logger = get_ml_logger(__name__)

class DataEncoder:
    """Manages encoding of categorical variables and scaling of numerical features."""

    def __init__(self, config: Optional[PreprocessingConfig] = None) -> None:
        """Initializes the encoder configurations.
        
        Args:
            config: Preprocessing configurations defining columns and methods.
        """
        self.config = config or PreprocessingConfig()
        self.cat_encoder: Optional[OneHotEncoder] = None
        self.num_scaler = None
        self.encoded_feature_names: list[str] = []
        logger.info("Initialized DataEncoder with scaling method: %s", self.config.scaling_method)

    def fit(self, df: pd.DataFrame) -> "DataEncoder":
        """Fits encoders and scalers on the training dataset.
        
        Args:
            df: Input training DataFrame (already cleaned).
            
        Returns:
            DataEncoder: Fitted encoder instance.
        """
        logger.info("Fitting DataEncoder on DataFrame of shape %s", df.shape)
        
        try:
            # 1. Fit Categorical OneHotEncoder
            cat_cols = [c for c in self.config.categorical_columns if c in df.columns]
            if cat_cols:
                # Use sparse_output=False for convenient dataframe manipulation
                self.cat_encoder = OneHotEncoder(
                    handle_unknown="ignore", 
                    sparse_output=False
                )
                self.cat_encoder.fit(df[cat_cols])
                
                # Retrieve generated feature names
                feature_names = self.cat_encoder.get_feature_names_out(cat_cols)
                self.encoded_feature_names = list(feature_names)
                logger.info("Fitted OneHotEncoder for columns: %s. Output features count: %d", cat_cols, len(self.encoded_feature_names))
            else:
                logger.warning("No categorical columns found to fit in the input DataFrame")

            # 2. Fit Numeric Scaler
            num_cols = [c for c in self.config.numerical_columns if c in df.columns]
            if num_cols:
                if self.config.scaling_method == "standard":
                    self.num_scaler = StandardScaler()
                elif self.config.scaling_method == "minmax":
                    self.num_scaler = MinMaxScaler()
                elif self.config.scaling_method == "robust":
                    self.num_scaler = RobustScaler()
                else:
                    logger.warning("Unknown scaling method '%s', defaulting to RobustScaler", self.config.scaling_method)
                    self.num_scaler = RobustScaler()
                
                self.num_scaler.fit(df[num_cols])
                logger.info("Fitted numerical scaler on columns: %s", num_cols)
            else:
                logger.warning("No numerical columns found to fit in the input DataFrame")
                
            return self
        except Exception as e:
            logger.error("Error during DataEncoder fit: %s", str(e))
            raise

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encodes and scales columns of the input DataFrame.
        
        Args:
            df: Cleaned input DataFrame to encode and scale.
            
        Returns:
            pd.DataFrame: DataFrame containing transformed features, keeping ID fields.
        """
        logger.info("Transforming DataFrame of shape %s with DataEncoder", df.shape)
        
        try:
            transformed_df = df.copy()
            
            # 1. Apply Categorical OneHotEncoding
            cat_cols = [c for c in self.config.categorical_columns if c in df.columns]
            if cat_cols and self.cat_encoder is not None:
                encoded_arr = self.cat_encoder.transform(df[cat_cols])
                encoded_df = pd.DataFrame(
                    encoded_arr, 
                    columns=self.encoded_feature_names, 
                    index=df.index
                )
                # Drop original categorical columns and concatenate encoded columns
                transformed_df = transformed_df.drop(columns=cat_cols)
                transformed_df = pd.concat([transformed_df, encoded_df], axis=1)
                logger.debug("Applied categorical encoding.")
                
            # 2. Apply Numerical Scaling
            num_cols = [c for c in self.config.numerical_columns if c in df.columns]
            if num_cols and self.num_scaler is not None:
                scaled_arr = self.num_scaler.transform(df[num_cols])
                scaled_df = pd.DataFrame(
                    scaled_arr, 
                    columns=num_cols, 
                    index=df.index
                )
                # Replace numerical columns with scaled versions
                for col in num_cols:
                    transformed_df[col] = scaled_df[col]
                logger.debug("Applied numerical scaling.")
                
            # TODO: Handle encoding alignment validation for unseen inputs
            
            logger.info("Completed encoding and scaling. Output shape: %s", transformed_df.shape)
            return transformed_df
        except Exception as e:
            logger.error("Error during DataEncoder transform: %s", str(e))
            raise

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fits on training set and transforms in one step.
        
        Args:
            df: Input DataFrame.
            
        Returns:
            pd.DataFrame: Transformed DataFrame.
        """
        return self.fit(df).transform(df)
