from typing import Dict, Any, List
from app.agents.investigators.merchant.config import MerchantAgentConfig

class MerchantHistoryAnalyzer:
    """Audits merchant historic fraud metrics, chargeback ratios, and dispute frequencies."""

    def __init__(self, config: MerchantAgentConfig) -> None:
        self.config = config

    def analyze(self, tx_data: Dict[str, Any], history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        evidence = []
        merchant_id = tx_data.get("merchant_id") or tx_data.get("merchant")
        
        if not merchant_id:
            return evidence

        fraud_rate = float(tx_data.get("merchant_fraud_rate") or 0.0)
        chargeback_rate = float(tx_data.get("merchant_chargeback_rate") or 0.0)

        # High fraud rate trigger
        if fraud_rate > self.config.high_fraud_rate_threshold:
            evidence.append({
                "type": "HighMerchantFraudRate",
                "severity": "HIGH",
                "confidence": 0.95,
                "description": f"Merchant '{merchant_id}' has a high historical fraud rate of {fraud_rate:.2%} (threshold: {self.config.high_fraud_rate_threshold:.2%}).",
                "source": "MerchantHistoryAnalyzer"
            })

        # High chargeback rate trigger
        if chargeback_rate > self.config.high_chargeback_rate_threshold:
            evidence.append({
                "type": "HighMerchantChargebackRate",
                "severity": "HIGH",
                "confidence": 0.92,
                "description": f"Merchant '{merchant_id}' chargeback rate of {chargeback_rate:.2%} exceeds system threshold of {self.config.high_chargeback_rate_threshold:.2%}.",
                "source": "MerchantHistoryAnalyzer"
            })

        return evidence
