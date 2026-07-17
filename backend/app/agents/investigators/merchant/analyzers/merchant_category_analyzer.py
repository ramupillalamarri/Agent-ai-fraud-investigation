from typing import Dict, Any, List
from app.agents.investigators.merchant.config import MerchantAgentConfig

class MerchantCategoryAnalyzer:
    """Evaluates category classifications to detect high-risk merchant categories."""

    def __init__(self, config: MerchantAgentConfig) -> None:
        self.config = config

    def analyze(self, tx_data: Dict[str, Any], history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        evidence = []
        category = tx_data.get("category") or tx_data.get("merchant_category")
        
        if not category:
            return evidence

        normalized_cat = category.lower().strip()
        
        # High-risk category matching
        if normalized_cat in self.config.high_risk_categories:
            weight = self.config.category_weights.get(normalized_cat, 0.70)
            evidence.append({
                "type": "HighRiskMerchantCategory",
                "severity": "HIGH" if weight >= 0.85 else "MEDIUM",
                "confidence": weight,
                "description": f"Merchant category '{category}' is classified as a high-risk industry (weight: {weight:.2f}).",
                "source": "MerchantCategoryAnalyzer"
            })

        return evidence
