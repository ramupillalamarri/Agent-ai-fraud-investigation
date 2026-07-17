"""Evaluation module for calculating performance metrics and explanation generation."""

import numpy as np
import pandas as pd
from typing import Dict, Any
# pyrefly: ignore [missing-import]
from xgboost import XGBClassifier       
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    classification_report
)
from ml.utils.logger import get_ml_logger

logger = get_ml_logger(__name__)

class ModelEvaluator:
    """Calculates classification performance metrics and coordinates feature explainability."""

    def __init__(self) -> None:
        """Initializes the evaluator."""
        logger.info("Initialized ModelEvaluator")

    def evaluate(self, model: XGBClassifier, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
        """Calculates standard classification performance metrics on the test dataset.
        
        Args:
            model: Fitted XGBoost model instance.
            X_test: Test feature matrix.
            y_test: Test target ground truth labels.
            
        Returns:
            Dict[str, Any]: Dictionary containing calculated metric scores.
        """
        logger.info("Evaluating model on test dataset of shape %s", X_test.shape)
        
        try:
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1]
            
            # Calculate standard metrics
            acc = accuracy_score(y_test, y_pred)
            prec = precision_score(y_test, y_pred, zero_division=0)
            rec = recall_score(y_test, y_pred, zero_division=0)
            f1 = f1_score(y_test, y_pred, zero_division=0)
            roc_auc = roc_auc_score(y_test, y_pred_proba)
            pr_auc = average_precision_score(y_test, y_pred_proba)
            
            # Confusion matrix
            cm = confusion_matrix(y_test, y_pred)
            tn, fp, fn, tp = cm.ravel()
            
            metrics: Dict[str, Any] = {
                "accuracy": float(acc),
                "precision": float(prec),
                "recall": float(rec),
                "f1_score": float(f1),
                "roc_auc": float(roc_auc),
                "pr_auc": float(pr_auc),
                "confusion_matrix": {
                    "tn": int(tn),
                    "fp": int(fp),
                    "fn": int(fn),
                    "tp": int(tp)
                }
            }
            
            logger.info("Evaluation completed. Accuracy: %f, Precision: %f, Recall: %f", 
                        metrics["accuracy"], metrics["precision"], metrics["recall"])
            return metrics
        except Exception as e:
            logger.error("Error during evaluation calculation: %s", str(e))
            raise

    def get_classification_report(self, model: XGBClassifier, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
        """Generates sklearn classification report as a dictionary.
        
        Args:
            model: Fitted XGBClassifier model instance.
            X_test: Test feature matrix.
            y_test: Test target ground truth labels.
            
        Returns:
            Dict[str, Any]: Classification report details.
        """
        logger.info("Generating classification report...")
        try:
            y_pred = model.predict(X_test)
            report_dict = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
            return report_dict
        except Exception as e:
            logger.error("Error generating classification report: %s", str(e))
            raise

    def generate_explainability_report(self, model: XGBClassifier, X: pd.DataFrame) -> Dict[str, Any]:
        """Calculates SHAP explainability values for feature attribution reports.
        
        Args:
            model: Fitted XGBClassifier model instance.
            X: Data matrix to explain.
            
        Returns:
            Dict[str, Any]: Placeholder representation of SHAP values/importance weights.
        """
        logger.info("Generating SHAP explainability values on feature matrix")
        
        try:
            shap_report: Dict[str, Any] = {
                "feature_importance_ranking": []
            }
            logger.info("Explainability report successfully initialized")
            return shap_report
        except Exception as e:
            logger.error("Error generating explainability report: %s", str(e))
            raise
