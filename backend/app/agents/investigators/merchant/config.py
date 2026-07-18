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

    # Merchant Category Analyzer configuration
    medium_risk_categories: Set[str] = field(default_factory=lambda: {
        "electronics", "jewelry", "luxury_goods", "travel", "marketplace", "digital_services"
    })
    restricted_categories: Set[str] = field(default_factory=lambda: {
        "restricted_gambling", "restricted_weapons"
    })
    category_amount_norms: Dict[str, float] = field(default_factory=lambda: {
        "grocery": 250.0,
        "apparel": 500.0,
        "electronics": 2000.0,
        "jewelry": 5000.0,
        "luxury_goods": 5000.0,
        "crypto_exchange": 1000.0,
        "gift_cards": 500.0,
        "gaming": 100.0,
        "marketplace": 1500.0,
        "travel": 3000.0,
        "money_transfer": 1000.0
    })
    cross_border_high_risk_categories: Set[str] = field(default_factory=lambda: {
        "crypto_exchange", "gift_cards", "money_transfer", "jewelry"
    })

    # Merchant Location Analyzer configuration
    sanctioned_countries: Set[str] = field(default_factory=lambda: {"KP", "IR", "SY", "CU"})
    watchlist_countries: Set[str] = field(default_factory=lambda: {"RU", "BY", "SD", "YE"})
    restricted_regions: Set[str] = field(default_factory=lambda: {"high_risk_zone_01", "unverified_region"})
    location_risk_weights: Dict[str, float] = field(default_factory=lambda: {
        "sanctioned": 0.99,
        "watchlist": 0.75,
        "restricted": 0.80,
        "cross_border_mismatch": 0.60
    })

    # Merchant Velocity Analyzer configuration
    velocity_burst_multiplier: float = 5.0
    amount_deviation_multiplier: float = 3.0
    max_failed_tx_rate: float = 0.20
    max_refunds_last_day: int = 10
    max_chargebacks_last_week: int = 5
    new_customer_ratio_threshold: float = 0.80
    growth_rate_multiplier: float = 4.0
    high_freq_low_value_count: int = 20
    high_freq_low_value_threshold: float = 10.0

    # Merchant Reputation Analyzer configuration
    watchlist_merchants: Set[str] = field(default_factory=lambda: {"MERCH_WATCH_01", "MERCH_SUSPICIOUS_99"})
    min_allowed_trust_score: float = 0.60
    max_allowed_risk_score: float = 0.40
    max_dispute_score: float = 0.25

    # Analyzer activation toggles
    enable_profile: bool = True
    enable_history: bool = True
    enable_category: bool = True
    enable_location: bool = True
    enable_velocity: bool = True
    enable_reputation: bool = True
