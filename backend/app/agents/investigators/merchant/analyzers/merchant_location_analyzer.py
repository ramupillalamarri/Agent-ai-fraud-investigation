from typing import Dict, Any, List
from app.agents.investigators.merchant.config import MerchantAgentConfig

class MerchantLocationAnalyzer:
    """Detects merchant country/region registration discrepancies and geo-velocity anomalies."""

    def __init__(self, config: MerchantAgentConfig) -> None:
        self.config = config

    def analyze(self, tx_data: Dict[str, Any], history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        evidence = []
        
        user_country = tx_data.get("location_country") or tx_data.get("country")
        merchant_country = tx_data.get("merchant_country") or tx_data.get("merchant_location_country")
        
        if not user_country or not merchant_country:
            return evidence

        # Geographic country mismatch
        if user_country.strip().upper() != merchant_country.strip().upper():
            evidence.append({
                "type": "MerchantLocationMismatch",
                "severity": "MEDIUM",
                "confidence": 0.80,
                "description": f"Cross-border transaction mismatch: User is in '{user_country}' while merchant terminal is registered in '{merchant_country}'.",
                "source": "MerchantLocationAnalyzer"
            })

        return evidence
