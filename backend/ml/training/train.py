"""Model training orchestration module for the fraud detection model."""

import os
import pandas as pd
from typing import Tuple, Optional, Dict, Any
# pyrefly: ignore [missing-import]
from xgboost import XGBClassifier   
from sklearn.model_selection import train_test_split
from ml.config import MLProjectConfig
from ml.preprocessing.pipeline import PreprocessingPipeline
from ml.utils.logger import get_ml_logger
from ml.utils.helpers import save_serialized_artifact, save_json_metadata, ensure_directory_exists

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
        
        # Configure file logging handler for training logs
        log_file = os.path.join(self.config.paths.logs_dir, "training.log")
        ensure_directory_exists(self.config.paths.logs_dir)
        import logging
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s:%(filename)s:%(lineno)d]: %(message)s"))
        logger.addHandler(file_handler)
        
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
            if X_val is not None and y_val is not None:
                self.model.fit(
                    X_train, y_train,
                    eval_set=[(X_val, y_val)],
                    verbose=False
                )
            else:
                self.model.fit(
                    X_train, y_train,
                    verbose=False
                )
            
            logger.info("Completed model training execution")
            return self.model
        except Exception as e:
            logger.error("Error encountered during training: %s", str(e))
            raise

    def save_model_artifacts(
        self, 
        model_file_name: str = "fraud_model.joblib", 
        pipeline_file_name: str = "pipeline.joblib", 
        metadata_file_name: str = "model_metadata.json",
        metrics_summary: Optional[dict] = None,
        dataset_name: str = "transactions.csv",
        dataset_size: int = 0,
        training_samples: int = 0,
        testing_samples: int = 0
    ) -> None:
        """Saves the trained model, preprocessing pipeline, and detailed metadata to the versioned registry.
        
        Args:
            model_file_name: Filename for model binary.
            pipeline_file_name: Filename for pipeline object.
            metadata_file_name: Filename for the registry metadata file.
            metrics_summary: Optional dictionary containing evaluation metric values.
            dataset_name: Name of the raw dataset used.
            dataset_size: Count of rows in the dataset.
            training_samples: Count of training samples.
            testing_samples: Count of testing samples.
        """
        logger.info("Saving trained model artifacts to registry...")
        
        if self.model is None or self.preprocessing_pipeline is None:
            raise ValueError("Cannot save artifacts; model or preprocessing pipeline has not been trained/fitted.")
            
        import datetime
        timestamp_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # Save to both 'latest/' and version-specific registry paths (e.g. 'v1/')
        registry_paths = [self.config.paths.model_save_dir, self.config.paths.model_v1_dir]
        
        try:
            for target_dir in registry_paths:
                ensure_directory_exists(target_dir)
                
                model_path = os.path.join(target_dir, model_file_name)
                pipeline_path = os.path.join(target_dir, pipeline_file_name)
                metadata_path = os.path.join(target_dir, metadata_file_name)
                
                # Save serialization binaries
                save_serialized_artifact(self.model, model_path)
                self.preprocessing_pipeline.save(pipeline_path)
                
                # Assemble detailed model metadata as requested
                feature_names = self.preprocessing_pipeline.final_feature_columns
                metadata = {
                    "model_version": self.config.model.model_version,
                    "preprocessing_version": self.config.model.preprocessing_version,
                    "training_date": timestamp_str.split("T")[0],
                    "training_timestamp": timestamp_str,
                    "dataset_name": dataset_name,
                    "dataset_size": dataset_size,
                    "training_samples": training_samples,
                    "testing_samples": testing_samples,
                    "feature_count": len(feature_names),
                    "feature_names": feature_names,
                    "algorithm": self.config.model.algorithm,
                    "hyperparameters": {
                        "n_estimators": self.config.training.n_estimators,
                        "max_depth": self.config.training.max_depth,
                        "learning_rate": self.config.training.learning_rate,
                        "subsample": self.config.training.subsample,
                        "colsample_bytree": self.config.training.colsample_bytree,
                        "scale_pos_weight": self.config.training.scale_pos_weight
                    },
                    "metrics": metrics_summary or {"aucpr": 0.0, "roc_auc": 0.0},
                    "evaluation_metrics": metrics_summary or {"aucpr": 0.0, "roc_auc": 0.0}
                }
                save_json_metadata(metadata, metadata_path)
                
            logger.info("Successfully serialized and saved all model registry artifacts.")
        except Exception as e:
            logger.error("Error saving model training registry artifacts: %s", str(e))
            raise

if __name__ == "__main__":
    import sys
    import json
    
    print("Loading configuration...")
    config = MLProjectConfig()
    
    raw_dir = config.paths.raw_data_dir
    train_raw_path = os.path.join(raw_dir, "fraudTrain.csv")
    test_raw_path = os.path.join(raw_dir, "fraudTest.csv")
    
    # Instantiate preprocessing pipeline orchestrator
    from ml.preprocessing.pipeline import FraudPreprocessingPipeline
    pipeline_obj = FraudPreprocessingPipeline(config)
    
    # 1. Check if Kaggle datasets are present
    if os.path.exists(train_raw_path) and os.path.exists(test_raw_path):
        logger.info("Kaggle Fraud Detection dataset detected. Proceeding with Kaggle training pipeline...")
        
        print("Loading processed dataset...")
        logger.info("Loading raw training dataset: %s", train_raw_path)
        train_raw = pipeline_obj.loader.load_raw_dataset("fraudTrain.csv")
        
        logger.info("Fitting preprocessing pipeline on training dataset...")
        pipeline_obj.fit(train_raw)
        
        logger.info("Extracting features on training dataset...")
        X_train, y_train = pipeline_obj.extract_features_and_target(train_raw)
        
        # Save fitted preprocessors
        pipeline_obj.save_preprocessors()
        
        logger.info("Loading raw testing dataset: %s", test_raw_path)
        test_raw = pipeline_obj.loader.load_raw_dataset("fraudTest.csv")
        
        logger.info("Extracting features from testing dataset using fitted pipeline...")
        X_test, y_test = pipeline_obj.extract_features_and_target(test_raw)
        
        # Save processed splits to processed datasets directory
        pipeline_obj.save_processed_splits(X_train, X_test, y_train, y_test)
        
        # Save training features to feature store
        logger.info("Saving transformed training features to feature store...")
        train_transformed = pipeline_obj.transform(train_raw)
        pipeline_obj.save_to_feature_store(train_transformed, "train_features.csv")
        
        dataset_name = "fraudTrain.csv / fraudTest.csv"
        dataset_size = len(train_raw) + len(test_raw)
        training_samples = len(X_train)
        testing_samples = len(X_test)
    else:
        # Fallback to standard transactions.csv flow for backward compatibility
        print("Loading processed dataset...")
        processed_dir = config.paths.processed_data_dir
        X_train_path = os.path.join(processed_dir, "X_train.csv")
        X_test_path = os.path.join(processed_dir, "X_test.csv")
        y_train_path = os.path.join(processed_dir, "y_train.csv")
        y_test_path = os.path.join(processed_dir, "y_test.csv")
        
        if not (os.path.exists(X_train_path) and os.path.exists(X_test_path)):
            X_train, X_test, y_train, y_test = pipeline_obj.run("transactions.csv")
            pipeline_obj.save_processed_splits(X_train, X_test, y_train, y_test)
            pipeline_obj.save_preprocessors()
        else:
            X_train = pd.read_csv(X_train_path)
            X_test = pd.read_csv(X_test_path)
            y_train = pd.read_csv(y_train_path).squeeze("columns")
            y_test = pd.read_csv(y_test_path).squeeze("columns")
            
        pipeline_obj_path = os.path.join(config.paths.preprocessor_save_dir, "pipeline.joblib")
        if os.path.exists(pipeline_obj_path):
            pipeline_obj = FraudPreprocessingPipeline.load(pipeline_obj_path)
        else:
            pipeline_obj.final_feature_columns = list(X_train.columns)
            
        dataset_name = "transactions.csv"
        dataset_size = len(X_train) + len(X_test)
        training_samples = len(X_train)
        testing_samples = len(X_test)
        
    trainer = ModelTrainer(config=config, preprocessing_pipeline=pipeline_obj)
    
    print("Training XGBoost model...")
    X_train_split, X_val_split, y_train_split, y_val_split = trainer.split_data(X_train, y_train)
    trainer.train(X_train_split, y_train_split, X_val_split, y_val_split)
    
    print("Evaluating model...")
    from ml.training.evaluate import ModelEvaluator
    evaluator = ModelEvaluator()
    metrics_summary = evaluator.evaluate(trainer.model, X_test, y_test)
    class_report = evaluator.get_classification_report(trainer.model, X_test, y_test)
    
    print("Saving trained model...")
    print("Saving metadata...")
    trainer.save_model_artifacts(
        metrics_summary=metrics_summary,
        dataset_name=dataset_name,
        dataset_size=int(dataset_size),
        training_samples=int(training_samples),
        testing_samples=int(testing_samples)
    )
    
    print("Saving reports...")
    ensure_directory_exists(config.paths.reports_dir)
    ensure_directory_exists(config.paths.metrics_dir)
    save_json_metadata(metrics_summary, os.path.join(config.paths.metrics_dir, "metrics.json"))
    save_json_metadata(class_report, os.path.join(config.paths.reports_dir, "classification_report.json"))
    
    feature_names = list(X_train.columns)
    feature_list_path = os.path.join(config.paths.reports_dir, "feature_list.json")
    with open(feature_list_path, "w") as f:
        json.dump(feature_names, f, indent=4)
        
    # Real-time Inference Validation Check
    print("Inference validation...")
    logger.info("Executing post-training inference validation check...")
    from ml.inference.predict import PredictionEngine
    
    # Reload model from disk to verify singleton load & inference contracts
    engine = PredictionEngine(config)
    
    # Grab sample rows from raw test data
    if os.path.exists(test_raw_path):
        sample_df = pd.read_csv(test_raw_path).head(5)
    else:
        sample_df = pd.read_csv(os.path.join(raw_dir, "transactions.csv")).head(5)
        
    sample_records = sample_df.to_dict(orient="records")
    validation_preds = engine.predict(sample_records)
    
    logger.info("Inference verification completed successfully. Outputs schema validated.")
    print("Training completed successfully.")
