import logging
from typing import List, Dict, Any, Optional
from app.agents.base.base_agent import BaseAgent
from app.agents.models.investigation_context import InvestigationContext
from app.agents.models.agent_result import AgentResult

from app.agents.investigators.network.config import NetworkAgentConfig
from app.agents.investigators.network.analyzers.ip_relationship_analyzer import IPRelationshipAnalyzer
from app.agents.investigators.network.analyzers.device_relationship_analyzer import DeviceRelationshipAnalyzer
from app.agents.investigators.network.analyzers.account_link_analyzer import AccountLinkAnalyzer
from app.agents.investigators.network.analyzers.merchant_relationship_analyzer import MerchantRelationshipAnalyzer
from app.agents.investigators.network.analyzers.payment_relationship_analyzer import PaymentRelationshipAnalyzer
from app.agents.investigators.network.analyzers.fraud_cluster_analyzer import FraudClusterAnalyzer

logger = logging.getLogger("app.agents.NetworkRiskAgent")

class NetworkRiskAgent(BaseAgent):
    """Investigation agent that evaluates relational transaction links, shared network nodes, and fraud rings."""

    def __init__(
        self,
        agent_id: str = "network-risk-investigator-01",
        agent_name: str = "NetworkRiskAgent",
        description: str = "Analyzes transaction relationship networks and linked entities.",
        version: str = "1.0.0",
        enabled: bool = True,
        execution_priority: int = 30,
        supported_features: Optional[List[str]] = None,
        config: Optional[NetworkAgentConfig] = None
    ) -> None:
        """Initializes the NetworkRiskAgent and relational sub-analyzers."""
        super().__init__(
            agent_id=agent_id,
            agent_name=agent_name,
            description=description,
            version=version,
            enabled=enabled,
            execution_priority=execution_priority,
            supported_features=supported_features or ["network", "relations"]
        )
        self.config = config or NetworkAgentConfig()
        
        # Instantiate sub-analyzers
        self.ip_analyzer = IPRelationshipAnalyzer(self.config)
        self.device_analyzer = DeviceRelationshipAnalyzer(self.config)
        self.account_analyzer = AccountLinkAnalyzer(self.config)
        self.merchant_analyzer = MerchantRelationshipAnalyzer(self.config)
        self.payment_analyzer = PaymentRelationshipAnalyzer(self.config)
        self.cluster_analyzer = FraudClusterAnalyzer(self.config)

    def validate(self, context: InvestigationContext) -> None:
        """Checks for minimum properties required for network relation validation."""
        tx_data = context.transaction_data or {}
        if "customer_id" not in tx_data and "user_id" not in tx_data:
            raise ValueError("NetworkRiskAgent requires either 'customer_id' or 'user_id' inside transaction_data.")

    def health_check(self) -> bool:
        """Confirms health status."""
        return True

    def _execute(self, context: InvestigationContext) -> AgentResult:
        """Executes the relational auditing sequence across network map entities."""
        tx_data = context.transaction_data
        
        # Retrieve relational network database mapping from memory context
        network_data = context.shared_memory.get("network_data") or context.metadata.get("network_data") or {}
        
        # Map of relational sub-analyzers
        analyzers_map = {
            "IPRelationshipAnalyzer": self.ip_analyzer,
            "DeviceRelationshipAnalyzer": self.device_analyzer,
            "AccountLinkAnalyzer": self.account_analyzer,
            "MerchantRelationshipAnalyzer": self.merchant_analyzer,
            "PaymentRelationshipAnalyzer": self.payment_analyzer,
            "FraudClusterAnalyzer": self.cluster_analyzer
        }
        
        evidence_list: List[Dict[str, Any]] = []
        analyzers_executed: List[str] = []
        triggered_rules: List[str] = []
        
        for name, analyzer in analyzers_map.items():
            try:
                self.log_info("Executing relational sub-module: %s", name)
                res = analyzer.analyze(tx_data, network_data)
                evidence_list.extend(res)
                analyzers_executed.append(name)
                for ev in res:
                    triggered_rules.append(ev["type"])
            except Exception as e:
                self.logger.exception("Error executing relational analyzer %s: %s", name, str(e))
                evidence_list.append({
                    "type": "RelationalAnalyzerError",
                    "severity": "LOW",
                    "confidence": 0.0,
                    "description": f"Internal crash in relational sub-module {name}: {str(e)}",
                    "related_entities": [],
                    "source": name
                })

        # Deduplicate evidence list
        seen_evidence = set()
        unique_evidence = []
        for ev in evidence_list:
            key = (ev["type"], ev["severity"], ev["source"])
            if key not in seen_evidence:
                seen_evidence.add(key)
                unique_evidence.append(ev)

        findings: List[str] = []
        recommendations: List[str] = []

        has_high = any(ev["severity"] == "HIGH" for ev in unique_evidence)
        has_med = any(ev["severity"] == "MEDIUM" for ev in unique_evidence)

        if unique_evidence:
            overall_confidence = sum(ev["confidence"] for ev in unique_evidence) / len(unique_evidence)
        else:
            overall_confidence = 1.0

        if has_high:
            findings.append("Severe network risk relationship links identified.")
            recommendations.append("Escalate investigation")
            recommendations.append("Freeze linked accounts")
            recommendations.append("Review related transactions")
        elif has_med:
            findings.append("Moderate profile relation link matches identified.")
            recommendations.append("Review related transactions")
            recommendations.append("Add entities to watchlist")
        elif unique_evidence:
            findings.append("Minor connection node links flagged.")
            recommendations.append("Review related transactions")
        else:
            findings.append("No suspicious network links or clusters associated with this transaction.")
            recommendations.append("Add entities to watchlist")

        metadata = {
            "analyzers_executed": analyzers_executed,
            "triggered_rules": triggered_rules,
            "analyzed_features": list(tx_data.keys()),
            "confidence_breakdown": {ev["type"]: ev["confidence"] for ev in unique_evidence}
        }

        return AgentResult(
            agent_name=self.agent_name,
            status="SUCCESS",
            confidence_score=overall_confidence,
            findings=findings,
            recommendations=recommendations,
            evidence=unique_evidence,
            execution_time_ms=0,  # calculated automatically by BaseAgent execute
            metadata=metadata
        )
