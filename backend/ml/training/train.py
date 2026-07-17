"""Model training orchestration module for the fraud detection model."""

import os
import pandas as pd
from typing import Tuple, Optional
# pyrefly: ignore [missing-import]
from xgboost import XGBClassifier   
from sklearn.model_selection import train_test_split
from ml.config import MLProjectConfig
from ml.preprocessing.pipeline import PreprocessingPipeline
from ml.utils.logger import get_ml_logger
from ml.utils.helpers import save_serialized_artifact, save_json_metadata

logger = get_ml_logger(__name__)

class ModelTrainer:
    """Manages data splitting, algorithm configuration, training execution, and serialization."""

    def __init__(
        self, 
        config: Optional[MLProjectConfig] = None,
        preprocessing_pipeline: Optional[PreprocessingPipeline] = None
    ) -> None:
        """Initializes the trainer with configuration parameters.
        
        Args:
            config: ML configuration class containing training and path parameters.
            preprocessing_pipeline: Optional fitted or raw PreprocessingPipeline instance.
        """
        self.config = config or MLProjectConfig()
        self.model: Optional[XGBClassifier] = None
        self.preprocessing_pipeline = preprocessing_pipeline
        logger.info("Initialized ModelTrainer")

    def split_data(self, X: pd.DataFrame, y: pd.Series) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Splits features and targets into training and validation sets.
        
        Args:
            X: Input features DataFrame.
            y: Target label Series.
            
        Returns:
            Tuple: X_train, X_val, y_train, y_val.
        """
        logger.info("Splitting dataset into train and validation sets (test_size=%s)", self.config.training.test_size)
        
        try:
            X_train, X_val, y_train, y_val = train_test_split(
                X, y,
                test_size=self.config.training.test_size,
                random_state=self.config.training.random_state,
                stratify=y  # Maintain class ratio for fraud imbalance
            )
            logger.info("Train shape: %s, Val shape: %s", X_train.shape, X_val.shape)
            return X_train, X_val, y_train, y_val
        except Exception as e:
            logger.error("Error during train-test split: %s", str(e))
            raise

    def initialize_estimator(self) -> XGBClassifier:
        """Initializes an XGBoost Classifier with settings defined in the configuration.
        
        Returns:
            XGBClassifier: An un-fitted XGBoost model instance.
        """
        logger.info("Initializing XGBClassifier with training config hyper-parameters")
        
        try:
            estimator = XGBClassifier(
                n_estimators=self.config.training.n_estimators,
                max_depth=self.config.training.max_depth,
                learning_rate=self.config.training.learning_rate,
                subsample=self.config.training.subsample,
                colsample_bytree=self.config.training.colsample_bytree,
                scale_pos_weight=self.config.training.scale_pos_weight,
                random_state=self.config.training.random_state,
                eval_metric=self.config.training.eval_metric,
                early_stopping_rounds=self.config.training.early_stopping_rounds
            )
            return estimator
        except Exception as e:
            logger.error("Failed to initialize estimator: %s", str(e))
            raise

    def train(
        self, 
        X_train: pd.DataFrame, 
        y_train: pd.Series, 
        X_val: Optional[pd.DataFrame] = None, 
        y_val: Optional[pd.Series] = None
    ) -> XGBClassifier:
        """Executes model fitting with early stopping on the validation set.
        
        Args:
            X_train: Training features.
            y_train: Training target labels.
            X_val: Optional validation features.
            y_val: Optional validation target labels.
            
        Returns:
            XGBClassifier: The fitted model instance.
        """
        logger.info("Starting model training...")
        self.model = self.initialize_estimator()
        
        try:
            # TODO: Implement the actual xgboost fit logic here when real data is integrated.
            # self.model.fit(
            #     X_train, y_train,
            #     eval_set=[(X_val, y_val)],
            #     verbose=False
            # )
            
            logger.info("Completed model training placeholder execution")
            return self.model
        except Exception as e:
            logger.error("Error encountered during training: %s", str(e))
            raise

    def save_model_artifacts(self, model_file_name: str, pipeline_file_name: str, metadata_file_name: str) -> None:
        """Saves the trained model, preprocessing pipeline, and model metadata to disk.
        
        Args:
            model_file_name: Target filename for the model (e.g. 'model.joblib').
            pipeline_file_name: Target filename for the preprocessing pipeline.
            metadata_file_name: Target filename for metadata JSON.
        """
        logger.info("Saving trained model artifacts...")
        
        if self.model is None or self.preprocessing_pipeline is None:
            raise ValueError("Cannot save artifacts; model or preprocessing pipeline has not been trained/fitted.")
            
        model_path = os.path.join(self.config.paths.model_save_dir, model_file_name)
        pipeline_path = os.path.join(self.config.paths.model_save_dir, pipeline_file_name)
        metadata_path = os.path.join(self.config.paths.model_save_dir, metadata_file_name)
        
        try:
            # Save estimators
            save_serialized_artifact(self.model, model_path)
            self.preprocessing_pipeline.save(pipeline_path)
            
            # Save metadata summary
            metadata = {
                "model_name": self.config.model.model_name,
                "model_version": self.config.model.model_version,
                "features_used": self.preprocessing_pipeline.feature_columns,
                "hyperparameters": {
                    "n_estimators": self.config.training.n_estimators,
                    "max_depth": self.config.training.max_depth,
                    "learning_rate": self.config.training.learning_rate,
                }
            }
            save_json_metadata(metadata, metadata_path)
            logger.info("Successfully serialized and saved all model training artifacts.")
        except Exception as e:
            logger.error("Error saving model training artifacts: %s", str(e))
            raise

if __name__ == "__main__":
    # Test initialization
    trainer = ModelTrainer()

