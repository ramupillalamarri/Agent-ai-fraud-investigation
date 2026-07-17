import logging
from typing import List, Dict, Any, Optional
from app.agents.base.base_agent import BaseAgent
from app.agents.models.investigation_context import InvestigationContext
from app.agents.models.agent_result import AgentResult

from app.agents.investigators.merchant.config import MerchantAgentConfig
from app.agents.investigators.merchant.analyzers.merchant_profile_analyzer import MerchantProfileAnalyzer
from app.agents.investigators.merchant.analyzers.merchant_history_analyzer import MerchantHistoryAnalyzer
from app.agents.investigators.merchant.analyzers.merchant_category_analyzer import MerchantCategoryAnalyzer
from app.agents.investigators.merchant.analyzers.merchant_location_analyzer import MerchantLocationAnalyzer
from app.agents.investigators.merchant.analyzers.merchant_velocity_analyzer import MerchantVelocityAnalyzer
from app.agents.investigators.merchant.analyzers.merchant_reputation_analyzer import MerchantReputationAnalyzer

logger = logging.getLogger("app.agents.MerchantInvestigationAgent")

class MerchantInvestigationAgent(BaseAgent):
    """Coordinates independent analyzers to audit merchant profiles, history, categories, locations, reputation, and velocity."""

    def __init__(
        self,
        agent_id: str = "merchant-investigator-01",
        agent_name: str = "MerchantInvestigationAgent",
        description: str = "Analyzes transaction context merchant reputation, fraud history, and categorization risks.",
        version: str = "1.0.0",
        enabled: bool = True,
        execution_priority: int = 40,
        supported_features: Optional[List[str]] = None,
        config: Optional[MerchantAgentConfig] = None
    ) -> None:
        """Initializes the MerchantInvestigationAgent and child analyzers."""
        super().__init__(
            agent_id=agent_id,
            agent_name=agent_name,
            description=description,
            version=version,
            enabled=enabled,
            execution_priority=execution_priority,
            supported_features=supported_features or ["merchant", "velocity", "reputation"]
        )
        self.config = config or MerchantAgentConfig()
        
        # Initialize child independent analyzers
        self.profile_analyzer = MerchantProfileAnalyzer(self.config)
        self.history_analyzer = MerchantHistoryAnalyzer(self.config)
        self.category_analyzer = MerchantCategoryAnalyzer(self.config)
        self.location_analyzer = MerchantLocationAnalyzer(self.config)
        self.velocity_analyzer = MerchantVelocityAnalyzer(self.config)
        self.reputation_analyzer = MerchantReputationAnalyzer(self.config)

    def validate(self, context: InvestigationContext) -> None:
        """Checks for minimum properties required for merchant context validation."""
        tx_data = context.transaction_data or {}
        if "merchant_id" not in tx_data and "merchant" not in tx_data:
            raise ValueError("MerchantInvestigationAgent requires either 'merchant_id' or 'merchant' inside transaction_data.")

    def health_check(self) -> bool:
        """Confirms health status."""
        return True

    def _execute(self, context: InvestigationContext) -> AgentResult:
        """Executes the analysis sequence by routing payloads to child analyzers."""
        tx_data = context.transaction_data
        
        # Load transaction history if present
        history: List[Dict[str, Any]] = context.shared_memory.get("customer_history") or context.metadata.get("customer_history") or []
        
        # List of analyzers
        analyzers_map = {
            "MerchantProfileAnalyzer": self.profile_analyzer,
            "MerchantHistoryAnalyzer": self.history_analyzer,
            "MerchantCategoryAnalyzer": self.category_analyzer,
            "MerchantLocationAnalyzer": self.location_analyzer,
            "MerchantVelocityAnalyzer": self.velocity_analyzer,
            "MerchantReputationAnalyzer": self.reputation_analyzer
        }
        
        evidence_list: List[Dict[str, Any]] = []
        analyzers_executed: List[str] = []
        triggered_rules: List[str] = []
        
        for name, analyzer in analyzers_map.items():
            try:
                self.log_info("Executing analyzer sub-module: %s", name)
                res = analyzer.analyze(tx_data, history)
                evidence_list.extend(res)
                analyzers_executed.append(name)
                for ev in res:
                    triggered_rules.append(ev["type"])
            except Exception as e:
                self.logger.exception("Error executing analyzer %s: %s", name, str(e))
                evidence_list.append({
                    "type": "AnalyzerError",
                    "severity": "LOW",
                    "confidence": 0.0,
                    "description": f"Internal crash during sub-module execution in {name}: {str(e)}",
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

        # Risk severity triggers
        has_crit = any(ev["severity"] == "CRITICAL" for ev in unique_evidence)
        has_high = any(ev["severity"] == "HIGH" for ev in unique_evidence)
        has_med = any(ev["severity"] == "MEDIUM" for ev in unique_evidence)

        if unique_evidence:
            overall_confidence = sum(ev["confidence"] for ev in unique_evidence) / len(unique_evidence)
        else:
            overall_confidence = 1.0  # safe certitude

        if has_crit or has_high:
            findings.append("Critical risk factors flagged on merchant registration/history.")
            recommendations.append("Block transaction")
            recommendations.append("Flag merchant for manual compliance review")
        elif has_med:
            findings.append("Moderate risk merchant categorization or velocity spike flagged.")
            recommendations.append("Flag transaction for manual review")
            recommendations.append("Limit maximum transaction amount on card")
        elif unique_evidence:
            findings.append("Minor merchant profile updates detected.")
            recommendations.append("Manual review")
        else:
            findings.append("Merchant status, history, and category risk parameters are optimal.")
            recommendations.append("No actions required")

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
