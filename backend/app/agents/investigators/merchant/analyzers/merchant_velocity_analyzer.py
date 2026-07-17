from typing import Dict, Any, List
from app.agents.investigators.merchant.config import MerchantAgentConfig

class MerchantVelocityAnalyzer:
    """Monitors transaction frequencies, velocities, and sudden amount spikes for a merchant."""

    def __init__(self, config: MerchantAgentConfig) -> None:
        self.config = config

    def analyze(self, tx_data: Dict[str, Any], history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        evidence = []
        merchant_id = tx_data.get("merchant_id") or tx_data.get("merchant")
        amount = float(tx_data.get("amount") or 0.0)
        
        if not merchant_id:
            return evidence

        # Sudden high transaction amount check
        if amount > self.config.max_amount_per_transaction:
            evidence.append({
                "type": "ExcessiveMerchantAmount",
                "severity": "HIGH",
                "confidence": 0.88,
                "description": f"Transaction amount (${amount:,.2f}) exceeds merchant velocity cap (${self.config.max_amount_per_transaction:,.2f}).",
                "source": "MerchantVelocityAnalyzer"
            })

        # Count consecutive transactions at this merchant in history
        merchant_txns = [h for h in history if (h.get("merchant") == merchant_id or h.get("merchant_id") == merchant_id)]
        if len(merchant_txns) >= 5:
            evidence.append({
                "type": "MerchantVelocitySpike",
                "severity": "MEDIUM",
                "confidence": 0.75,
                "description": f"Customer has established high velocity ({len(merchant_txns)} consecutive transactions) at merchant '{merchant_id}' in recent history.",
                "source": "MerchantVelocityAnalyzer"
            })

        return evidence
