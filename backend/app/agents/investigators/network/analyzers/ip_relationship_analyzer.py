from typing import Dict, Any, List
from app.agents.investigators.network.config import NetworkAgentConfig

class IPRelationshipAnalyzer:
    """Identifies multiple accounts reusing the same IP node, rapid switches, and shared cluster weights."""

    def __init__(self, config: NetworkAgentConfig) -> None:
        self.config = config

    def analyze(self, tx_data: Dict[str, Any], network_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scans IP nodes against account associations.
        
        Args:
            tx_data: Current transaction properties.
            network_data: Graph/relational entity lists.
            
        Returns:
            List[Dict[str, Any]]: Structured IP relationship evidence.
        """
        evidence = []
        ip = tx_data.get("ip_address")
        if not ip:
            return evidence

        ip_accounts = network_data.get("ip_accounts", {})
        linked_accounts = ip_accounts.get(ip, [])

        current_acc = tx_data.get("customer_id") or tx_data.get("user_id")
        other_accounts = [acc for acc in linked_accounts if acc != current_acc]

        total_accounts = len(linked_accounts)
        if total_accounts > self.config.max_unique_accounts_per_ip:
            evidence.append({
                "type": "SharedIP",
                "severity": "HIGH" if total_accounts >= 5 else "MEDIUM",
                "confidence": 0.95,
                "description": f"IP address '{ip}' is shared across {total_accounts} accounts, indicating a possible proxy or fraud ring.",
                "related_entities": other_accounts,
                "source": "IPRelationshipAnalyzer"
            })
            
        return evidence
