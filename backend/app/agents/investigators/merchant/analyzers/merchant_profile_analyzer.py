from typing import Dict, Any, List
from app.agents.investigators.merchant.config import MerchantAgentConfig

class MerchantProfileAnalyzer:
    """Evaluates merchant profile registration, verification status, and profile metrics."""

    def __init__(self, config: MerchantAgentConfig) -> None:
        self.config = config

    def analyze(self, tx_data: Dict[str, Any], history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        evidence = []
        merchant_id = tx_data.get("merchant_id") or tx_data.get("merchant")
        
        if not merchant_id:
            return evidence

        # Evaluation of registration tenure (new vs established)
        is_new_merchant = tx_data.get("merchant_is_new", False)
        merchant_age_days = tx_data.get("merchant_age_days")
        
        if is_new_merchant or (merchant_age_days is not None and merchant_age_days < 30):
            evidence.append({
                "type": "NewMerchantProfile",
                "severity": "MEDIUM",
                "confidence": 0.85,
                "description": f"Merchant '{merchant_id}' is a newly registered terminal (registered less than 30 days ago).",
                "source": "MerchantProfileAnalyzer"
            })

        # Verification status validation
        is_verified = tx_data.get("merchant_is_verified", True)
        if not is_verified:
            evidence.append({
                "type": "UnverifiedMerchantProfile",
                "severity": "HIGH",
                "confidence": 0.90,
                "description": f"Merchant '{merchant_id}' profile is unverified or lacks valid business registry credentials.",
                "source": "MerchantProfileAnalyzer"
            })

        return evidence
