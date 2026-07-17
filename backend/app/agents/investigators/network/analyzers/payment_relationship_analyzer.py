from typing import Dict, Any, List
from app.agents.investigators.network.config import NetworkAgentConfig

class PaymentRelationshipAnalyzer:
    """Detects payment cards and banking instruments shared across multiple customer profiles."""

    def __init__(self, config: NetworkAgentConfig) -> None:
        self.config = config

    def analyze(self, tx_data: Dict[str, Any], network_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scans payment instruments against associated profile nodes.
        
        Args:
            tx_data: Current transaction properties.
            network_data: Graph/relational entity lists.
            
        Returns:
            List[Dict[str, Any]]: Structured payment link evidence.
        """
        evidence = []
        payment_instrument = tx_data.get("payment_instrument") or tx_data.get("card_id")
        
        if not payment_instrument:
            return evidence

        payment_accounts = network_data.get("payment_accounts", {})
        linked_accounts = payment_accounts.get(payment_instrument, [])

        current_acc = tx_data.get("customer_id") or tx_data.get("user_id")
        other_accounts = [acc for acc in linked_accounts if acc != current_acc]

        total_accounts = len(linked_accounts)
        if total_accounts > self.config.max_unique_accounts_per_payment_instrument:
            evidence.append({
                "type": "SharedPaymentInstrument",
                "severity": "HIGH" if total_accounts >= 3 else "MEDIUM",
                "confidence": 0.95,
                "description": f"Payment instrument '{payment_instrument}' is shared across {total_accounts} customer accounts, indicating potential card sharing.",
                "related_entities": other_accounts,
                "source": "PaymentRelationshipAnalyzer"
            })
            
        return evidence
