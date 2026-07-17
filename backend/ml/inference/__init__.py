"""Inference package providing loaded predictors and model loading handlers."""

from ml.inference.model_loader import ModelLoader
from ml.inference.predict import FraudPredictor

__all__ = [
    "ModelLoader",
    "FraudPredictor",
]
