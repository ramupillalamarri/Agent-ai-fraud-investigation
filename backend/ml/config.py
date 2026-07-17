"""Configuration management for the ML module of the Retail Fraud Investigation framework.

This module defines configuration schemas using Python dataclasses to manage paths,
preprocessing settings, training hyperparameters, and inference parameters.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass(frozen=True)
class PathConfig:
    """Configuration for dataset and model paths."""
    base_dir: str = field(default_factory=lambda: os.path.dirname(os.path.abspath(__file__)))
    raw_data_dir: str = field(default_factory=lambda: os.path.join(os.path.dirname(os.path.abspath(__file__)), "datasets", "raw"))
    processed_data_dir: str = field(default_factory=lambda: os.path.join(os.path.dirname(os.path.abspath(__file__)), "datasets", "processed"))
    model_save_dir: str = field(default_factory=lambda: os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_models"))
    preprocessor_save_dir: str = field(default_factory=lambda: os.path.join(os.path.dirname(os.path.abspath(__file__)), "preprocessors"))

@dataclass(frozen=True)
class PreprocessingConfig:
    """Configuration for data cleaning, feature engineering, and encoding."""
    target_column: str = "is_fraud"
    id_columns: List[str] = field(default_factory=lambda: ["transaction_id", "user_id", "merchant_id"])
    categorical_columns: List[str] = field(default_factory=lambda: ["merchant_category", "payment_method", "device_type", "location_country"])
    numerical_columns: List[str] = field(default_factory=lambda: ["amount", "user_age", "account_balance"])
    datetime_columns: List[str] = field(default_factory=lambda: ["transaction_timestamp"])
    missing_value_strategies: Dict[str, str] = field(default_factory=lambda: {
        "amount": "median",
        "account_balance": "median",
        "device_type": "constant"
    })
    scaling_method: str = "robust"  # standard, minmax, robust

@dataclass(frozen=True)
class TrainingConfig:
    """Configuration for model training hyperparameters (XGBoost)."""
    random_state: int = 42
    test_size: float = 0.2
    val_size: float = 0.1  # For early stopping
    
    # XGBoost Hyperparameters
    n_estimators: int = 500
    max_depth: int = 6
    learning_rate: float = 0.05
    subsample: float = 0.8
    colsample_bytree: float = 0.8
    scale_pos_weight: float = 1.0  # Should be updated dynamically depending on class imbalance
    early_stopping_rounds: int = 50
    eval_metric: str = "aucpr"

@dataclass(frozen=True)
class ModelConfig:
    """Configuration for model metadata."""
    model_name: str = "retail_fraud_xgboost"
    model_version: str = "1.0.0"

@dataclass(frozen=True)
class MLProjectConfig:
    """Top-level unified ML project configuration."""
    paths: PathConfig = field(default_factory=PathConfig)
    preprocessing: PreprocessingConfig = field(default_factory=PreprocessingConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    model: ModelConfig = field(default_factory=ModelConfig)

    @classmethod
    def load_from_env(cls) -> "MLProjectConfig":
        """Loads configuration overrides from environment variables if present.
        
        TODO: Implement configuration override parsing from environment variables or a YAML file.
        """
        # Exposing standard configuration loading pattern
        return cls()
