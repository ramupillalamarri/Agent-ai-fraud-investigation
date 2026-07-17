"""Unified preprocessing pipeline orchestrator matching SOLID and DRY design patterns."""

import os
import joblib
import pandas as pd
from typing import Optional, Tuple, List
from sklearn.model_selection import train_test_split
from ml.config import MLProjectConfig
from ml.preprocessing.loader import DataLoader
from ml.preprocessing.cleaner import DataCleaner
from ml.preprocessing.encoder import DataEncoder
from ml.preprocessing.feature_engineering import FeatureEngineer
from ml.utils.logger import get_ml_logger
from ml.utils.helpers import ensure_directory_exists, save_serialized_artifact, load_serialized_artifact

logger = get_ml_logger(__name__)

class FraudPreprocessingPipeline:
    """Manages raw transaction data loading, cleaning, encoding, feature engineering, and splitting.
    
    Acts as a single orchestrator that coordinates individual components, exporting 
    final features and saving serialized configurations for live prediction routing.
    """

    def __init__(self, config: Optional[MLProjectConfig] = None) -> None:
        """Initializes the preprocessing pipeline components.
        
        Args:
            config: Consolidated ML project configuration.
        """
        self.config = config or MLProjectConfig()
        
        # Instantiate subcomponents (Single Responsibility Principle)
        self.loader = DataLoader(self.config.paths, self.config.preprocessing)
        self.cleaner = DataCleaner(self.config.preprocessing)
        self.encoder = DataEncoder(self.config.preprocessing)
        self.feature_engineer = FeatureEngineer(self.config.preprocessing)
        
        # Store final feature names list (excluding label/ids)
        self.final_feature_columns: List[str] = []
        logger.info("Initialized FraudPreprocessingPipeline")

    def fit(self, df: pd.DataFrame) -> "FraudPreprocessingPipeline":
        """Fits all preprocessing estimators (cleaner, feature engineer, encoder) on raw data.
        
        Args:
            df: Raw input DataFrame.
            
        Returns:
            FraudPreprocessingPipeline: Fitted instance.
        """
        logger.info("Fitting Preprocessing Pipeline stages...")
        try:
            # 1. Fit cleaner
            cleaned_df = self.cleaner.fit_transform(df)
            
            # 2. Fit feature engineer
            engineered_df = self.feature_engineer.fit_transform(cleaned_df)
            
            # 3. Fit encoder
            self.encoder.fit(engineered_df)
            
            # 4. Generate a trial transform to list final output features (excluding IDs, dates, target)
            transformed_df = self.encoder.transform(engineered_df)
            
            target_col = self.config.preprocessing.target_column
            exclusions = set(
                self.config.preprocessing.id_columns + 
                self.config.preprocessing.datetime_columns + 
                [target_col]
            )
            self.final_feature_columns = [col for col in transformed_df.columns if col not in exclusions]
            
            logger.info("Successfully fitted preprocessing pipeline. Final features count: %d", len(self.final_feature_columns))
            return self
        except Exception as e:
            logger.error("Failed to fit Preprocessing Pipeline: %s", str(e))
            raise

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transforms raw input data through the fitted pipeline stages, preserving identifiers.
        
        Args:
            df: Raw input DataFrame.
            
        Returns:
            pd.DataFrame: Fully processed DataFrame containing both features and identifiers.
        """
        logger.info("Transforming dataset...")
        try:
            cleaned_df = self.cleaner.transform(df)
            engineered_df = self.feature_engineer.transform(cleaned_df)
            encoded_df = self.encoder.transform(engineered_df)
            return encoded_df
        except Exception as e:
            logger.error("Failed to transform dataset: %s", str(e))
            raise

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fits baseline parameters and applies engineering operations.
        
        Args:
            df: Input DataFrame.
            
        Returns:
            pd.DataFrame: Transformed DataFrame.
        """
        return self.fit(df).transform(df)

    def extract_features_and_target(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Optional[pd.Series]]:
        """Processes raw dataset and extracts clean features (X) and target label (y).
        
        This handles excluding identification fields from the model input matrix X.
        
        Args:
            df: Raw input DataFrame.
            
        Returns:
            Tuple[pd.DataFrame, Optional[pd.Series]]: Clean features (X) and target (y).
        """
        transformed_df = self.transform(df)
        
        X = transformed_df[self.final_feature_columns]
        
        y = None
        target_col = self.config.preprocessing.target_column
        if target_col in transformed_df.columns:
            y = transformed_df[target_col]
            
        return X, y

    def run(self, filename: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Runs the complete preprocessing workflow: load, clean, engineer, encode, split.
        
        Args:
            filename: Target file name inside raw datasets directory.
            
        Returns:
            Tuple containing train/test features and target splits:
            X_train, X_test, y_train, y_test.
        """
        # 1. Load Data
        logger.info("Loading dataset...")
        raw_df = self.loader.load_raw_dataset(filename)
        
        # 2. Fit and Transform
        transformed_df = self.fit_transform(raw_df)
        
        # 3. Extract split targets
        X = transformed_df[self.final_feature_columns]
        target_col = self.config.preprocessing.target_column
        y = transformed_df[target_col]
        
        # 4. Split train/test data
        logger.info("Splitting train/test...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=self.config.training.test_size,
            random_state=self.config.training.random_state,
            stratify=y  # Maintain class ratio
        )
        
        return X_train, X_test, y_train, y_test

    def save_processed_splits(
        self, 
        X_train: pd.DataFrame, 
        X_test: pd.DataFrame, 
        y_train: pd.Series, 
        y_test: pd.Series
    ) -> None:
        """Saves final split data matrices to the processed datasets directory.
        
        Args:
            X_train: Training features.
            X_test: Test features.
            y_train: Training labels.
            y_test: Test labels.
        """
        logger.info("Saving processed datasets...")
        processed_dir = self.config.paths.processed_data_dir
        ensure_directory_exists(processed_dir)
        
        try:
            X_train.to_csv(os.path.join(processed_dir, "X_train.csv"), index=False)
            X_test.to_csv(os.path.join(processed_dir, "X_test.csv"), index=False)
            y_train.to_csv(os.path.join(processed_dir, "y_train.csv"), index=False)
            y_test.to_csv(os.path.join(processed_dir, "y_test.csv"), index=False)
            logger.debug("Successfully saved processed train and test splits.")
        except Exception as e:
            logger.error("Failed to save processed dataset splits: %s", str(e))
            raise

    def save_preprocessors(self) -> None:
        """Saves fitted cleaner, encoder, and feature engineering states to disk."""
        logger.info("Saving preprocessing objects...")
        save_dir = self.config.paths.preprocessor_save_dir
        ensure_directory_exists(save_dir)
        
        try:
            # Save individual preprocessor modules
            joblib.dump(self.cleaner, os.path.join(save_dir, "cleaner.joblib"))
            joblib.dump(self.encoder, os.path.join(save_dir, "encoder.joblib"))
            joblib.dump(self.feature_engineer, os.path.join(save_dir, "feature_engineer.joblib"))
            # Save unified pipeline
            joblib.dump(self, os.path.join(save_dir, "pipeline.joblib"))
            logger.debug("Successfully serialized and saved all preprocessing objects.")
        except Exception as e:
            logger.error("Failed to serialize preprocessing objects: %s", str(e))
            raise

    def save_to_feature_store(self, df: pd.DataFrame, filename: str) -> None:
        """Saves fully transformed features (retaining identifiers) to the feature store directory.
        
        Args:
            df: Fully transformed features DataFrame.
            filename: Target file name (e.g. 'features.csv').
        """
        logger.info("Saving engineered features to feature store...")
        fs_dir = self.config.paths.feature_store_dir
        ensure_directory_exists(fs_dir)
        try:
            df.to_csv(os.path.join(fs_dir, filename), index=False)
            logger.debug("Successfully saved features to feature store: %s", filename)
        except Exception as e:
            logger.error("Failed to save to feature store: %s", str(e))
            raise

    def save(self, file_path: str) -> None:
        """Saves the pipeline instance to disk."""
        logger.info("Saving preprocessing pipeline to %s", file_path)
        save_serialized_artifact(self, file_path)

    @classmethod
    def load(cls, file_path: str) -> "FraudPreprocessingPipeline":
        """Loads a pre-trained pipeline object from disk."""
        logger.info("Loading preprocessing pipeline from %s", file_path)
        pipeline = load_serialized_artifact(file_path)
        if not isinstance(pipeline, cls):
            raise TypeError(f"Loaded object is not of type {cls.__name__}")
        return pipeline

# Alias for backward compatibility
PreprocessingPipeline = FraudPreprocessingPipeline
# Alias for feature columns attribute mapping compatibility
FraudPreprocessingPipeline.feature_columns = property(lambda self: self.final_feature_columns)

if __name__ == "__main__":
    import logging
    import sys
    
    # Configure root logger with raw format so verification prints exactly the target phrases
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
    
    # Define paths
    project_config = MLProjectConfig()
    raw_dir = project_config.paths.raw_data_dir
    ensure_directory_exists(raw_dir)
    
    raw_filepath = os.path.join(raw_dir, "transactions.csv")
    
    # Generate dummy transaction dataset for validation if not present
    if not os.path.exists(raw_filepath):
        logger.info("Generating mock raw transaction dataset for pipeline validation...")
        dummy_data = pd.DataFrame({
            "transaction_id": [f"TX{i:04d}" for i in range(100)],
            "user_id": [f"USR{i%10:03d}" for i in range(100)],
            "merchant_id": [f"MERCH{i%5:03d}" for i in range(100)],
            "device_id": [f"DEV{i%8:03d}" for i in range(100)],
            "ip_address": [f"192.168.1.{10+i%50}" for i in range(100)],
            "amount": [float(10.0 + (i * 2.5)) for i in range(100)],
            "user_age": [20 + (i % 45) for i in range(100)],
            "account_balance": [500.0 + (i * 15.0) for i in range(100)],
            "merchant_category": ["retail" if i%2==0 else "electronics" for i in range(100)],
            "payment_method": ["credit" if i%3==0 else "debit" for i in range(100)],
            "device_type": ["mobile" if i%2==0 else "desktop" for i in range(100)],
            "location_country": ["US" if i%4==0 else "CA" for i in range(100)],
            "transaction_timestamp": [pd.Timestamp("2026-07-17") + pd.Timedelta(hours=i) for i in range(100)],
            "is_fraud": [1 if i%20==0 else 0 for i in range(100)]
        })
        dummy_data.to_csv(raw_filepath, index=False)
        logger.info("Mock dataset generated successfully.")

    try:
        # Instantiate and run pipeline
        pipeline = FraudPreprocessingPipeline(project_config)
        X_train, X_test, y_train, y_test = pipeline.run("transactions.csv")
        
        # Save processed splits and preprocessor objects
        pipeline.save_processed_splits(X_train, X_test, y_train, y_test)
        pipeline.save_preprocessors()
        
        # Save complete transformed dataset containing identifiers to the feature store
        raw_df = pipeline.loader.load_raw_dataset("transactions.csv")
        transformed_df = pipeline.transform(raw_df)
        pipeline.save_to_feature_store(transformed_df, "transactions_features.csv")
        
        logger.info("Completed successfully.")
    except Exception as exc:
        logger.error("Pipeline run failed: %s", str(exc))
        sys.exit(1)
