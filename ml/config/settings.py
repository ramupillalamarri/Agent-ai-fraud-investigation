"""Configuration classes for preprocessing, model metadata, and training hyperparameters."""

from dataclasses import dataclass, field
from typing import Dict, Any, List
from ml.config import constants

@dataclass(frozen=True)
class PreprocessingConfig:
    """Settings for data cleaning, categorical encoding, and feature engineering."""
    target_column: str = constants.TARGET_COLUMN
    id_columns: List[str] = field(default_factory=lambda: list(constants.ID_COLUMNS))
    categorical_columns: List[str] = field(default_factory=lambda: list(constants.CATEGORICAL_COLUMNS))
    numerical_columns: List[str] = field(default_factory=lambda: list(constants.NUMERICAL_COLUMNS))
    datetime_columns: List[str] = field(default_factory=lambda: list(constants.DATETIME_COLUMNS))
    missing_value_strategies: Dict[str, str] = field(
        default_factory=lambda: dict(constants.DEFAULT_MISSING_VALUE_STRATEGIES)
    )
    scaling_method: str = "robust"  # options: standard, minmax, robust
    amount_bins: List[float] = field(default_factory=lambda: list(constants.DEFAULT_AMOUNT_BINS))
    amount_labels: List[str] = field(default_factory=lambda: list(constants.DEFAULT_AMOUNT_LABELS))

@dataclass(frozen=True)
class TrainingConfig:
    """Settings for model split validation and estimator fitting."""
    random_state: int = 42
    test_size: float = 0.2
    val_size: float = 0.1
    
    # XGBoost Parameters
    n_estimators: int = 500
    max_depth: int = 6
    learning_rate: float = 0.05
    subsample: float = 0.8
    colsample_bytree: float = 0.8
    scale_pos_weight: float = 1.0
    early_stopping_rounds: int = 50
    eval_metric: str = "aucpr"

@dataclass(frozen=True)
class ModelConfig:
    """Metadata configurations describing the trained models."""
    model_name: str = "retail_fraud_xgboost"
    model_version: str = "1.0.0"
    algorithm: str = "XGBClassifier"
    preprocessing_version: str = "1.0.0"
