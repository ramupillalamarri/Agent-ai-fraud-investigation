"""Path configurations for directories and artifacts."""

import os
from dataclasses import dataclass, field

@dataclass(frozen=True)
class PathConfig:
    """Paths mapping datasets, model registry versions, serialized preprocessors, and artifacts."""
    base_dir: str = field(default_factory=lambda: os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Datasets
    raw_data_dir: str = field(default_factory=lambda: os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datasets", "raw"
    ))
    processed_data_dir: str = field(default_factory=lambda: os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datasets", "processed"
    ))
    feature_store_dir: str = field(default_factory=lambda: os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datasets", "feature_store"
    ))
    
    # Model Registry
    model_registry_dir: str = field(default_factory=lambda: os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "saved_models"
    ))
    model_save_dir: str = field(default_factory=lambda: os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "saved_models", "latest"
    ))
    model_v1_dir: str = field(default_factory=lambda: os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "saved_models", "v1"
    ))
    
    # Preprocessors
    preprocessor_save_dir: str = field(default_factory=lambda: os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "preprocessors"
    ))
    
    # Artifacts
    artifacts_dir: str = field(default_factory=lambda: os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "artifacts"
    ))
    reports_dir: str = field(default_factory=lambda: os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "artifacts", "reports"
    ))
    metrics_dir: str = field(default_factory=lambda: os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "artifacts", "metrics"
    ))
    logs_dir: str = field(default_factory=lambda: os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "artifacts", "logs"
    ))
