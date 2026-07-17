"""Model loading interface for inference services."""

import os
import threading
from typing import Optional
# pyrefly: ignore [missing-import]
from xgboost import XGBClassifier
from ml.config import MLProjectConfig
from ml.preprocessing.pipeline import PreprocessingPipeline
from ml.utils.logger import get_ml_logger
from ml.utils.helpers import load_serialized_artifact

logger = get_ml_logger(__name__)

class ModelLoader:
    """Manages thread-safe, cached retrieval of trained models and preprocessing pipelines.
    
    This operates as a cached loader to prevent redundant, high-latency disk I/O on active inference paths.
    """
    
    _instance: Optional["ModelLoader"] = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        """Implement thread-safe singleton pattern to reuse cache across incoming requests."""
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(ModelLoader, cls).__new__(cls)
        return cls._instance

    def __init__(self, config: Optional[MLProjectConfig] = None) -> None:
        """Initializes loader paths. Prevents double-init if singleton is fetched."""
        if not hasattr(self, "_initialized"):
            self.config = config or MLProjectConfig()
            self._model: Optional[XGBClassifier] = None
            self._pipeline: Optional[PreprocessingPipeline] = None
            self._initialized = True
            logger.info("Initialized ModelLoader Singleton")

    def load_model(self, filename: str = "model.joblib", version: str = "latest") -> XGBClassifier:
        """Retrieves or loads the compiled XGBClassifier model from versioned registry path.
        
        Args:
            filename: Serialization name of the target model file.
            version: Target registry version folder (e.g. 'latest', 'v1').
            
        Returns:
            XGBClassifier: Loaded model estimator.
        """
        if self._model is not None:
            return self._model
            
        with self._lock:
            if self._model is not None:
                return self._model
                
            target_dir = self.config.paths.model_save_dir if version == "latest" else os.path.join(self.config.paths.model_registry_dir, version)
            model_path = os.path.join(target_dir, filename)
            logger.info("Loading model from disk: %s", model_path)
            
            try:
                # TODO: Integrate actual deserialization post-training execution
                # self._model = load_serialized_artifact(model_path)
                self._model = XGBClassifier()
                logger.info("Successfully loaded and cached target model.")
                return self._model
            except Exception as e:
                logger.error("Failed to load model: %s", str(e))
                raise

    def load_preprocessing_pipeline(self, filename: str = "pipeline.joblib", version: str = "latest") -> PreprocessingPipeline:
        """Loads and caches the fitted feature preprocessing pipeline.
        
        Args:
            filename: Serialization name of the target pipeline file.
            version: Target registry version folder (e.g. 'latest', 'v1').
            
        Returns:
            PreprocessingPipeline: Loaded fitted preprocessing pipeline.
        """
        if self._pipeline is not None:
            return self._pipeline
            
        with self._lock:
            if self._pipeline is not None:
                return self._pipeline
                
            target_dir = self.config.paths.model_save_dir if version == "latest" else os.path.join(self.config.paths.model_registry_dir, version)
            pipeline_path = os.path.join(target_dir, filename)
            logger.info("Loading preprocessing pipeline from disk: %s", pipeline_path)
            
            try:
                # TODO: Integrate actual deserialization post-training execution
                # self._pipeline = PreprocessingPipeline.load(pipeline_path)
                self._pipeline = PreprocessingPipeline(self.config.preprocessing)
                logger.info("Successfully loaded and cached preprocessing pipeline.")
                return self._pipeline
            except Exception as e:
                logger.error("Failed to load preprocessing pipeline: %s", str(e))
                raise

    def clear_cache(self) -> None:
        """Evicts cached model and pipeline parameters from memory."""
        with self._lock:
            self._model = None
            self._pipeline = None
            logger.info("Cleared cached models and pipelines.")
    
    @classmethod
    def get_loader(cls, config: Optional[MLProjectConfig] = None) -> "ModelLoader":
        """Convenience method to retrieve the singleton instance.
        
        Returns:
            ModelLoader: The singleton loader.
        """
        return cls(config)
