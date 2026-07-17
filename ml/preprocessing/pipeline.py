"""Pipeline orchestrator for cleaning, feature engineering, and encoding steps."""

import pandas as pd
from typing import Optional, Tuple, List
from ml.config import PreprocessingConfig
from ml.preprocessing.cleaner import DataCleaner
from ml.preprocessing.encoder import DataEncoder
from ml.preprocessing.feature_engineering import FeatureEngineer
from ml.utils.logger import get_ml_logger
from ml.utils.helpers import save_serialized_artifact, load_serialized_artifact

logger = get_ml_logger(__name__)

class PreprocessingPipeline:
    """Orchestrates cleaner, feature engineering, and encoding components into a single interface.
    
    This pipeline is designed to be serialized and loaded for training and inference modules.
    """

    def __init__(self, config: Optional[PreprocessingConfig] = None) -> None:
        """Initializes the preprocessing pipeline pipeline stages.
        
        Args:
            config: Preprocessing configurations defining target and features.
        """
        self.config = config or PreprocessingConfig()
        self.cleaner = DataCleaner(self.config)
        self.feature_engineer = FeatureEngineer(self.config)
        self.encoder = DataEncoder(self.config)
        
        # Store final feature names list (excluding label/ids)
        self.feature_columns: List[str] = []
        logger.info("Initialized PreprocessingPipeline")

    def fit(self, df: pd.DataFrame) -> "PreprocessingPipeline":
        """Fits all steps (cleaner, feature engineer, and encoder) on training data.
        
        Args:
            df: Raw input DataFrame for training.
            
        Returns:
            PreprocessingPipeline: Fitted pipeline.
        """
        logger.info("Fitting PreprocessingPipeline on raw dataset of shape %s", df.shape)
        
        try:
            # 1. Clean
            cleaned_df = self.cleaner.fit_transform(df)
            
            # 2. Feature Engineer
            engineered_df = self.feature_engineer.fit_transform(cleaned_df)
            
            # 3. Fit Encoder
            self.encoder.fit(engineered_df)
            
            # 4. Determine final feature columns list
            transformed_df = self.encoder.transform(engineered_df)
            
            # Exclude id columns and target columns from feature list
            cols_to_exclude = set(self.config.id_columns + [self.config.target_column] + self.config.datetime_columns)
            self.feature_columns = [col for col in transformed_df.columns if col not in cols_to_exclude]
            
            logger.info("Successfully fitted preprocessing pipeline. Final features count: %d", len(self.feature_columns))
            return self
        except Exception as e:
            logger.error("Error during pipeline fit: %s", str(e))
            raise

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transforms a raw input DataFrame through the fitted pipeline.
        
        Args:
            df: Raw input DataFrame.
            
        Returns:
            pd.DataFrame: Transformed features DataFrame.
        """
        logger.info("Transforming DataFrame of shape %s through PreprocessingPipeline", df.shape)
        
        try:
            # 1. Clean
            cleaned_df = self.cleaner.transform(df)
            
            # 2. Feature Engineer
            engineered_df = self.feature_engineer.transform(cleaned_df)
            
            # 3. Encode and Scale
            transformed_df = self.encoder.transform(engineered_df)
            
            logger.info("Pipeline transform completed. Final shape: %s", transformed_df.shape)
            return transformed_df
        except Exception as e:
            logger.error("Error during pipeline transformation: %s", str(e))
            raise

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convenience function to fit and transform in one step.
        
        Args:
            df: Raw training DataFrame.
            
        Returns:
            pd.DataFrame: Transformed features.
        """
        return self.fit(df).transform(df)

    def extract_features_and_target(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Optional[pd.Series]]:
        """Processes raw dataset and splits it into X (features) and y (target label).
        
        Args:
            df: Raw input DataFrame.
            
        Returns:
            Tuple[pd.DataFrame, Optional[pd.Series]]: Transformed features (X) and target (y).
        """
        transformed_df = self.transform(df)
        
        X = transformed_df[self.feature_columns]
        
        y = None
        if self.config.target_column in transformed_df.columns:
            y = transformed_df[self.config.target_column]
            
        return X, y

    def save(self, file_path: str) -> None:
        """Saves the fitted pipeline object to disk.
        
        Args:
            file_path: The target filepath to write the pickle.
        """
        logger.info("Saving preprocessing pipeline to %s", file_path)
        save_serialized_artifact(self, file_path)

    @classmethod
    def load(cls, file_path: str) -> "PreprocessingPipeline":
        """Loads a pre-trained pipeline object from disk.
        
        Args:
            file_path: Source filepath of the serialized pipeline.
            
        Returns:
            PreprocessingPipeline: Loaded pipeline instance.
        """
        logger.info("Loading preprocessing pipeline from %s", file_path)
        pipeline = load_serialized_artifact(file_path)
        if not isinstance(pipeline, cls):
            raise TypeError(f"Loaded object is not of type {cls.__name__}")
        return pipeline
