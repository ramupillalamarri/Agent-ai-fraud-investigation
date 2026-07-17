from typing import Dict, Any, List
from app.agents.investigators.network.config import NetworkAgentConfig

class DeviceRelationshipAnalyzer:
    """Analyzes device sharing counts across multiple customer accounts and historical blocks."""

    def __init__(self, config: NetworkAgentConfig) -> None:
        self.config = config

    def analyze(self, tx_data: Dict[str, Any], network_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scans device IDs against associated account records.
        
        Args:
            tx_data: Current transaction properties.
            network_data: Graph/relational entity lists.
            
        Returns:
            List[Dict[str, Any]]: Structured device relationship evidence.
        """
        evidence = []
        device_id = tx_data.get("device_id")
        if not device_id:
            return evidence

        device_accounts = network_data.get("device_accounts", {})
        linked_accounts = device_accounts.get(device_id, [])

        current_acc = tx_data.get("customer_id") or tx_data.get("user_id")
        other_accounts = [acc for acc in linked_accounts if acc != current_acc]

        total_accounts = len(linked_accounts)
        if total_accounts > self.config.max_unique_accounts_per_device:
            evidence.append({
                "type": "SharedDevice",
                "severity": "HIGH" if total_accounts >= 3 else "MEDIUM",
                "confidence": 0.95,
                "description": f"Device ID '{device_id}' is shared across {total_accounts} accounts, indicating a possible device takeover.",
                "related_entities": other_accounts,
                "source": "DeviceRelationshipAnalyzer"
            })
            
        return evidence
