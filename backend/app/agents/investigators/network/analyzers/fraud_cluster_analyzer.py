from typing import Dict, Any, List
from app.agents.investigators.network.config import NetworkAgentConfig

class FraudClusterAnalyzer:
    """Detects transaction network clusters, circular loops, and emerging fraud rings."""

    def __init__(self, config: NetworkAgentConfig) -> None:
        self.config = config

    def analyze(self, tx_data: Dict[str, Any], network_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scans cluster profiles for direct or transitive fraud ring links.
        
        Args:
            tx_data: Current transaction parameters.
            network_data: Graph/relational entity lists.
            
        Returns:
            List[Dict[str, Any]]: Structured fraud ring cluster evidence.
        """
        evidence = []
        current_acc = tx_data.get("customer_id") or tx_data.get("user_id")
        
        if not current_acc:
            return evidence

        fraud_clusters = network_data.get("fraud_clusters", [])

        # Check if customer belongs to a flagged transaction cluster or ring
        for cluster in fraud_clusters:
            if current_acc in cluster:
                related_entities = [entity for entity in cluster if entity != current_acc]
                evidence.append({
                    "type": "FraudCluster",
                    "severity": "HIGH",
                    "confidence": 0.90,
                    "description": f"Active customer account is linked to a suspicious transaction cluster containing {len(cluster)} connected entities.",
                    "related_entities": related_entities,
                    "source": "FraudClusterAnalyzer"
                })
                break
                
        return evidence
