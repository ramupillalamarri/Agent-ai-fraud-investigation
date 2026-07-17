"""System-wide constant declarations and schema configuration definitions."""

from typing import List, Dict

# Dataset Column Definitions
TARGET_COLUMN: str = "is_fraud"

ID_COLUMNS: List[str] = [
    "transaction_id",
    "user_id",
    "merchant_id",
    "device_id",
    "ip_address"
]

DATETIME_COLUMNS: List[str] = [
    "transaction_timestamp"
]

CATEGORICAL_COLUMNS: List[str] = [
    "merchant_category",
    "payment_method",
    "device_type",
    "location_country",
    "amount_bucket"
]

NUMERICAL_COLUMNS: List[str] = [
    "amount",
    "user_age",
    "account_balance"
]

# Imputation Strategies
DEFAULT_MISSING_VALUE_STRATEGIES: Dict[str, str] = {
    "amount": "median",
    "account_balance": "median",
    "user_age": "mean",
    "device_type": "constant",
    "location_country": "constant",
    "payment_method": "constant"
}

# Feature Engineering Settings
DEFAULT_AMOUNT_BINS: List[float] = [0.0, 50.0, 200.0, 1000.0, float("inf")]
DEFAULT_AMOUNT_LABELS: List[str] = ["low", "medium", "high", "critical"]

# Validation Thresholds
ALERT_PROBABILITY_THRESHOLD: float = 0.85
WARNING_PROBABILITY_THRESHOLD: float = 0.50
MIN_TRANSACTION_AMOUNT: float = 0.01
MAX_TRANSACTION_AMOUNT: float = 1000000.00
MIN_CUSTOMER_AGE: int = 12
MAX_CUSTOMER_AGE: int = 110
