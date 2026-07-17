from dataclasses import dataclass, field
from typing import Set, List

@dataclass
class NetworkAgentConfig:
    """Configurable thresholds for entity relationship and graph link analysis."""
    
    # IP relationship thresholds
    max_unique_accounts_per_ip: int = 3
    
    # Device relationship thresholds
    max_unique_accounts_per_device: int = 2
    
    # Account link thresholds
    shared_attribute_alert_threshold: int = 1
    
    # Merchant reputation settings
    high_risk_merchant_categories: List[str] = field(default_factory=lambda: ["gaming", "crypto", "giftcards", "prepaid"])
    flagged_merchants: Set[str] = field(default_factory=lambda: {"MERCH_FRAUD_88", "MERCH_BLOCKED_12", "MERCH_HIGH_RISK_01"})
    
    # Payment link thresholds
    max_unique_accounts_per_payment_instrument: int = 2
    
    # Fraud cluster threshold
    cluster_connection_count_limit: int = 3
