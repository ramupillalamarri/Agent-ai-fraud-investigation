from dataclasses import dataclass, field
from typing import Set, Dict

@dataclass
class MerchantAgentConfig:
    """Configurable thresholds and reference lists for merchant risk analysis."""
    
    # Merchant Profile & Reputation
    blacklisted_merchants: Set[str] = field(default_factory=lambda: {"MERCH_FRAUD_99", "MERCH_SCAM_01", "MERCH_BLOCKED_05"})
    whitelisted_merchants: Set[str] = field(default_factory=lambda: {"MERCH_SAFE_01", "MERCH_TRUSTED_02"})
    
    # Risk score & fraud rate thresholds
    high_risk_merchant_threshold: float = 0.75  # Scale 0 to 1
    high_fraud_rate_threshold: float = 0.05      # 5% of historic txns
    high_chargeback_rate_threshold: float = 0.02 # 2% chargeback rate
    
    # Category Risk mapping (high-risk merchant categories)
    high_risk_categories: Set[str] = field(default_factory=lambda: {
        "electronics", "jewelry", "crypto_exchange", "gift_cards", "gaming", "luxury_goods"
    })
    category_weights: Dict[str, float] = field(default_factory=lambda: {
        "electronics": 0.80,
        "jewelry": 0.85,
        "crypto_exchange": 0.95,
        "gift_cards": 0.90,
        "gaming": 0.65,
        "luxury_goods": 0.75
    })
    
    # Velocity parameters
    max_transaction_count_per_hour: int = 100
    max_amount_per_transaction: float = 10000.0

    # Merchant Profile Analyzer thresholds
    recently_registered_days: int = 30
    required_profile_fields: Set[str] = field(default_factory=lambda: {"merchant_id", "merchant_name", "merchant_country"})
    important_profile_fields: Set[str] = field(default_factory=lambda: {"merchant_registration_date", "merchant_category", "merchant_verified", "merchant_status"})
    active_merchant_statuses: Set[str] = field(default_factory=lambda: {"ACTIVE", "VERIFIED"})
    invalid_merchant_categories: Set[str] = field(default_factory=lambda: {"unknown", "n/a", "none"})

    # Merchant History Analyzer thresholds
    high_refund_rate_threshold: float = 0.15
    high_dispute_rate_threshold: float = 0.05
    inactivity_days_threshold: int = 180
    min_established_transactions: int = 100
