from typing import Dict, Any, List
from app.agents.investigators.network.config import NetworkAgentConfig

class MerchantRelationshipAnalyzer:
    """Evaluates merchant chargeback reputations, risk categories, and direct fraud logs."""

    def __init__(self, config: NetworkAgentConfig) -> None:
        self.config = config

    def analyze(self, tx_data: Dict[str, Any], network_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scans merchant identifiers against reputational risk flags.
        
        Args:
            tx_data: Current transaction properties.
            network_data: Graph/relational entity lists.
            
        Returns:
            List[Dict[str, Any]]: Structured merchant relationship evidence.
        """
        evidence = []
        merchant_id = tx_data.get("merchant_id")
        if not merchant_id:
            return evidence

        flagged_merchants = network_data.get("flagged_merchants", [])

        # Check local config lists or dynamic relational graph flagged merchants list
        is_flagged = merchant_id in self.config.flagged_merchants or merchant_id in flagged_merchants

        if is_flagged:
            evidence.append({
                "type": "LinkedMerchantFraud",
                "severity": "HIGH",
                "confidence": 0.95,
                "description": f"Target merchant '{merchant_id}' is flagged on active fraud watchlists.",
                "related_entities": [merchant_id],
                "source": "MerchantRelationshipAnalyzer"
            })
            
        return evidence
