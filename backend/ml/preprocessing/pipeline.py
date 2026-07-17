"""Unified preprocessing pipeline orchestrator matching SOLID and DRY design patterns."""

import os
import joblib
import pandas as pd
from typing import Optional, Tuple
from sklearn.model_selection import train_test_split
from ml.config import MLProjectConfig
from ml.preprocessing.loader import DataLoader
from ml.preprocessing.cleaner import DataCleaner
from ml.preprocessing.encoder import DataEncoder
from ml.preprocessing.feature_engineering import FeatureEngineer
from ml.utils.logger import get_ml_logger
from ml.utils.helpers import ensure_directory_exists

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
        
        # Store fitted feature list
        self.final_feature_columns = []
        logger.info("Initialized FraudPreprocessingPipeline")

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
        
        # 2. Clean Data
        logger.info("Cleaning dataset...")
        cleaned_df = self.cleaner.fit_transform(raw_df)
        
        # 3. Feature Engineering
        logger.info("Creating engineered features...")
        engineered_df = self.feature_engineer.fit_transform(cleaned_df)
        
        # 4. Encode Features
        logger.info("Encoding categorical columns...")
        encoded_df = self.encoder.fit_transform(engineered_df)
        
        # 5. Extract Feature Matrix (X) and Target Label (y)
        # Exclude IDs, Datetime fields, and the target label from training features
        target_col = self.config.preprocessing.target_column
        exclusions = set(
            self.config.preprocessing.id_columns + 
            self.config.preprocessing.datetime_columns + 
            [target_col]
        )
        self.final_feature_columns = [col for col in encoded_df.columns if col not in exclusions]
        
        X = encoded_df[self.final_feature_columns]
        y = encoded_df[target_col]
        
        # 6. Split train/test data
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

# Alias for backward compatibility
PreprocessingPipeline = FraudPreprocessingPipeline

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
        
        logger.info("Completed successfully.")
    except Exception as exc:
        logger.error("Pipeline run failed: %s", str(exc))
        sys.exit(1)
