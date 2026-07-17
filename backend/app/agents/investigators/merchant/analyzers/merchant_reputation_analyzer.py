from typing import Dict, Any, List
from app.agents.investigators.merchant.config import MerchantAgentConfig

class MerchantReputationAnalyzer:
    """Verifies merchant status against reputation blacklists, whitelists, and compliance databases."""

    def __init__(self, config: MerchantAgentConfig) -> None:
        self.config = config

    def analyze(self, tx_data: Dict[str, Any], history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        evidence = []
        merchant_id = tx_data.get("merchant_id") or tx_data.get("merchant")
        merchant_risk = float(tx_data.get("merchant_risk_score") or tx_data.get("merchant_risk") or 0.0)
        
        if not merchant_id:
            return evidence

        # Blacklist check
        if merchant_id in self.config.blacklisted_merchants:
            evidence.append({
                "type": "BlacklistedMerchant",
                "severity": "CRITICAL",
                "confidence": 0.99,
                "description": f"Merchant ID '{merchant_id}' is present on the system blacklist for historical compliance/fraud violations.",
                "source": "MerchantReputationAnalyzer"
            })

        # Whitelist exemption check
        if merchant_id in self.config.whitelisted_merchants:
            evidence.append({
                "type": "WhitelistedMerchantExemption",
                "severity": "LOW",
                "confidence": 0.95,
                "description": f"Merchant ID '{merchant_id}' matches a trusted whitelist profile, lowering overall risk classification.",
                "source": "MerchantReputationAnalyzer"
            })

        # General risk index check
        if merchant_risk > self.config.high_risk_merchant_threshold:
            evidence.append({
                "type": "CompromisedMerchantReputation",
                "severity": "HIGH",
                "confidence": 0.90,
                "description": f"Merchant risk reputation score ({merchant_risk:.2f}) exceeds system safety threshold ({self.config.high_risk_merchant_threshold:.2f}).",
                "source": "MerchantReputationAnalyzer"
            })

        return evidence
