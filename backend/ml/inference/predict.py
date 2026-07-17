"""Real-time transaction prediction engine."""

import os
import json
import datetime
import logging
import pandas as pd
from typing import Dict, Any, List, Union, Optional
from ml.config import MLProjectConfig
from ml.inference.model_loader import ModelLoader
from ml.utils.logger import get_ml_logger
from ml.utils.helpers import ensure_directory_exists

logger = get_ml_logger(__name__)

class PredictionEngine:
    """Production prediction engine executing automated validation, preprocessing, and inference."""

    def __init__(self, config: Optional[MLProjectConfig] = None) -> None:
        """Initializes the prediction engine.
        
        Args:
            config: Consolidated ML project configuration.
        """
        self.config = config or MLProjectConfig()
        
        # Configure file logging handler for prediction logs
        log_file = os.path.join(self.config.paths.logs_dir, "prediction.log")
        ensure_directory_exists(self.config.paths.logs_dir)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"))
        logger.addHandler(file_handler)
        
        # Retrieve components from ModelLoader singleton
        self.loader = ModelLoader.get_loader(self.config)
        self.model = self.loader.load_model()
        self.pipeline = self.loader.load_preprocessing_pipeline()
        self.model_version = self.config.model.model_version
        logger.info("Initialized PredictionEngine using model version %s", self.model_version)

    def validate_input(self, data: pd.DataFrame) -> None:
        """Validates that input data columns align with the baseline expectations.
        
        Args:
            data: DataFrame containing input transaction rows.
        """
        expected_cols = (
            self.config.preprocessing.numerical_columns +
            self.config.preprocessing.categorical_columns +
            self.config.preprocessing.datetime_columns +
            self.config.preprocessing.id_columns
        )
        # Exclude amount_bucket since it is an engineered categorical
        expected_cols = [col for col in expected_cols if col not in ["amount_bucket"]]
        
        missing_cols = [col for col in expected_cols if col not in data.columns]
        if missing_cols:
            raise ValueError(f"Input validation failed. Missing expected columns: {missing_cols}")

    def predict(self, transactions: Union[Dict[str, Any], List[Dict[str, Any]], pd.DataFrame]) -> List[Dict[str, Any]]:
        """Executes automated preprocessing and predicts fraud for transaction inputs.
        
        Args:
            transactions: Input transaction(s) as a dict, list of dicts, or pandas DataFrame.
            
        Returns:
            List[Dict[str, Any]]: List of structured JSON prediction responses.
        """
        # Convert inputs to DataFrame
        if isinstance(transactions, dict):
            df = pd.DataFrame([transactions])
        elif isinstance(transactions, list):
            df = pd.DataFrame(transactions)
        elif isinstance(transactions, pd.DataFrame):
            df = transactions.copy()
        else:
            raise TypeError("Input transactions must be a dictionary, list of dictionaries, or pandas DataFrame.")
            
        if df.empty:
            return []

        try:
            # 1. Validate Input Schema
            self.validate_input(df)
            
            # 2. Run Preprocessing
            X, _ = self.pipeline.extract_features_and_target(df)
            
            # Align features with training feature order
            X = X[self.pipeline.final_feature_columns]
            
            # 3. Generate Predictions
            proba_arr = self.model.predict_proba(X)[:, 1]
            pred_arr = self.model.predict(X)
            
            results = []
            timestamp_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
            
            # Preserve transaction ID metadata
            tx_col = "transaction_id"
            tx_ids = df[tx_col].tolist() if tx_col in df.columns else [f"TX_IDX_{i}" for i in range(len(df))]
            
            for idx, (prob, pred) in enumerate(zip(proba_arr, pred_arr)):
                # Calculate risk score (0-100) and confidence score
                risk_score = int(prob * 100)
                confidence = float(prob * 100) if pred == 1 else float((1 - prob) * 100)
                
                # Configurable risk score warning limit (e.g. risk score >= 80)
                requires_investigation = risk_score >= 80
                
                # Determine investigation priority
                priority = "LOW"
                if risk_score >= 85:
                    priority = "HIGH"
                elif risk_score >= 50:
                    priority = "MEDIUM"
                    
                # Collect initial evidence for the downstream agent
                initial_evidence = []
                row_raw = df.iloc[idx].to_dict()
                
                # Cast Timestamps to ISO strings in the serialized raw dict
                for k, v in row_raw.items():
                    if isinstance(v, (pd.Timestamp, datetime.date, datetime.datetime)):
                        row_raw[k] = v.isoformat()
                
                if requires_investigation:
                    initial_evidence.append(f"Model classified transaction as high fraud risk with probability {prob:.4f}.")
                if row_raw.get("amount", 0) > 1000.00:
                    initial_evidence.append(f"Transaction amount (${row_raw.get('amount')}) exceeds high-value threshold.")
                if row_raw.get("user_age", 0) < 18:
                    initial_evidence.append(f"Cardholder is under-age ({row_raw.get('user_age')} years old).")
                if row_raw.get("account_balance", 0) < 50.00:
                    initial_evidence.append(f"Cardholder has depleted account balance (${row_raw.get('account_balance')}).")
                
                res = {
                    "transaction": row_raw,
                    "prediction": {
                        "fraud_probability": round(float(prob), 4),
                        "risk_score": risk_score,
                        "prediction": "Fraud" if pred == 1 else "Legitimate",
                        "confidence": round(confidence, 2),
                        "prediction_timestamp": timestamp_str
                    },
                    "model_metadata": {
                        "model_version": self.model_version
                    },
                    "investigation_context": {
                        "requires_investigation": bool(requires_investigation),
                        "priority": priority,
                        "initial_evidence": initial_evidence
                    }
                }
                
                # Log predictions to prediction.log
                logger.info(
                    "Prediction Context logged: TX_ID=%s, RiskScore=%d, Prediction=%s, Priority=%s, InvRequired=%s",
                    tx_ids[idx], res["prediction"]["risk_score"], res["prediction"]["prediction"],
                    res["investigation_context"]["priority"], res["investigation_context"]["requires_investigation"]
                )
                results.append(res)
                
            return results
        except Exception as e:
            logger.error("Error during prediction calculation: %s", str(e))
            raise

# Alias for backward compatibility
FraudPredictor = PredictionEngine

if __name__ == "__main__":
    print("Loading latest model...")
    print("Loading preprocessing artifacts...")
    engine = PredictionEngine()
    
    # Single Transaction Example
    single_tx = {
        "transaction_id": "TX9999",
        "user_id": "USR001",
        "merchant_id": "MERCH001",
        "device_id": "DEV001",
        "ip_address": "192.168.1.100",
        "amount": 450.00,
        "user_age": 35,
        "account_balance": 1500.00,
        "merchant_category": "retail",
        "payment_method": "credit",
        "device_type": "mobile",
        "location_country": "US",
        "transaction_timestamp": "2026-07-17T12:00:00"
    }
    
    print("Running preprocessing...")
    print("Generating prediction...")
    print("Calculating risk score...")
    single_res = engine.predict(single_tx)
    print("\n[Single Prediction Response Example]")
    print(json.dumps(single_res[0], indent=4))
    
    # Batch Transaction Example
    batch_tx = [
        single_tx,
        {
            "transaction_id": "TX8888",
            "user_id": "USR002",
            "merchant_id": "MERCH002",
            "device_id": "DEV002",
            "ip_address": "192.168.1.101",
            "amount": 25.00,
            "user_age": 22,
            "account_balance": 120.00,
            "merchant_category": "electronics",
            "payment_method": "debit",
            "device_type": "desktop",
            "location_country": "CA",
            "transaction_timestamp": "2026-07-17T13:00:00"
        }
    ]
    batch_res = engine.predict(batch_tx)
    print("\n[Batch Predictions Response Example]")
    print(json.dumps(batch_res, indent=4))
    
    # Invalid Input Example
    print("\n[Testing Invalid Input Handling]")
    invalid_tx = {
        "transaction_id": "TX7777",
        "user_id": "USR003"
    }
    try:
        engine.predict(invalid_tx)
    except Exception as e:
        print(f"Captured expected invalid input exception: {e}")
        
    print("Prediction completed successfully.")
