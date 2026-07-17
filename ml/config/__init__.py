"""Unified configuration package exporting configurations for paths, processing, and training."""

from dataclasses import dataclass, field
from ml.config.paths import PathConfig
from ml.config.settings import PreprocessingConfig, TrainingConfig, ModelConfig

@dataclass(frozen=True)
class MLProjectConfig:
    """Unified configuration class uniting configurations across subsystems."""
    paths: PathConfig = field(default_factory=PathConfig)
    preprocessing: PreprocessingConfig = field(default_factory=PreprocessingConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    model: ModelConfig = field(default_factory=ModelConfig)

    @classmethod
    def load_from_env(cls) -> "MLProjectConfig":
        """Loads configuration overrides if any are provided in environmental values."""
        # Config placeholder
        return cls()

__all__ = [
    "PathConfig",
    "PreprocessingConfig",
    "TrainingConfig",
    "ModelConfig",
    "MLProjectConfig",
]
