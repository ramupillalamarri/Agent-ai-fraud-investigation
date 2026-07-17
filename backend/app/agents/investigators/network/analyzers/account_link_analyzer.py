from typing import Dict, Any, List
from app.agents.investigators.network.config import NetworkAgentConfig

class AccountLinkAnalyzer:
    """Analyzes shared attributes (phone, email, physical address) linking customer identities."""

    def __init__(self, config: NetworkAgentConfig) -> None:
        self.config = config

    def analyze(self, tx_data: Dict[str, Any], network_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scans attributes to identify linked customer account profiles.
        
        Args:
            tx_data: Current transaction properties.
            network_data: Graph/relational entity lists.
            
        Returns:
            List[Dict[str, Any]]: Structured identity connection evidence.
        """
        evidence = []
        shared_attributes = network_data.get("shared_attributes", {})
        current_acc = tx_data.get("customer_id") or tx_data.get("user_id")

        if not current_acc:
            return evidence

        linked_accounts = set()
        matched_attributes = []

        for attr, accounts in shared_attributes.items():
            if current_acc in accounts:
                other_accounts = [acc for acc in accounts if acc != current_acc]
                if other_accounts:
                    linked_accounts.update(other_accounts)
                    matched_attributes.append(attr)

        if linked_accounts:
            evidence.append({
                "type": "LinkedAccounts",
                "severity": "HIGH" if len(linked_accounts) >= 3 else "MEDIUM",
                "confidence": 0.90,
                "description": f"Account links detected with {len(linked_accounts)} other profiles sharing attributes: {', '.join(matched_attributes)}.",
                "related_entities": list(linked_accounts),
                "source": "AccountLinkAnalyzer"
            })
            
        return evidence
