import logging
from typing import List, Dict, Any, Optional
from app.agents.base.base_agent import BaseAgent
from app.agents.models.investigation_context import InvestigationContext
from app.agents.models.agent_result import AgentResult

from app.agents.investigators.device.config import DeviceAgentConfig
from app.agents.investigators.device.analyzers.device_recognition_analyzer import DeviceRecognitionAnalyzer
from app.agents.investigators.device.analyzers.device_reputation_analyzer import DeviceReputationAnalyzer
from app.agents.investigators.device.analyzers.browser_analyzer import BrowserAnalyzer
from app.agents.investigators.device.analyzers.ip_address_analyzer import IPAddressAnalyzer
from app.agents.investigators.device.analyzers.vpn_proxy_analyzer import VPNProxyAnalyzer
from app.agents.investigators.device.analyzers.geo_consistency_analyzer import GeoConsistencyAnalyzer
from app.agents.investigators.device.analyzers.session_analyzer import SessionAnalyzer

logger = logging.getLogger("app.agents.DeviceInvestigationAgent")

class DeviceInvestigationAgent(BaseAgent):
    """Coordinates independent device, browser, network, routing, and session analyzers to audit transaction security."""

    def __init__(
        self,
        agent_id: str = "device-investigator-01",
        agent_name: str = "DeviceInvestigationAgent",
        description: str = "Analyzes transaction context device and network security reputation.",
        version: str = "1.0.0",
        enabled: bool = True,
        execution_priority: int = 20,
        supported_features: Optional[List[str]] = None,
        config: Optional[DeviceAgentConfig] = None
    ) -> None:
        """Initializes the DeviceInvestigationAgent and child analyzers."""
        super().__init__(
            agent_id=agent_id,
            agent_name=agent_name,
            description=description,
            version=version,
            enabled=enabled,
            execution_priority=execution_priority,
            supported_features=supported_features or ["device", "network", "location"]
        )
        self.config = config or DeviceAgentConfig()
        
        # Initialize child independent analyzers
        self.recognition_analyzer = DeviceRecognitionAnalyzer(self.config)
        self.reputation_analyzer = DeviceReputationAnalyzer(self.config)
        self.browser_analyzer = BrowserAnalyzer(self.config)
        self.ip_analyzer = IPAddressAnalyzer(self.config)
        self.vpn_analyzer = VPNProxyAnalyzer(self.config)
        self.geo_analyzer = GeoConsistencyAnalyzer(self.config)
        self.session_analyzer = SessionAnalyzer(self.config)

    def validate(self, context: InvestigationContext) -> None:
        """Checks for minimum properties required for device context validation."""
        tx_data = context.transaction_data or {}
        if "device_id" not in tx_data and "ip_address" not in tx_data:
            raise ValueError("DeviceInvestigationAgent requires either 'device_id' or 'ip_address' inside transaction_data.")

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
            "DeviceRecognitionAnalyzer": self.recognition_analyzer,
            "DeviceReputationAnalyzer": self.reputation_analyzer,
            "BrowserAnalyzer": self.browser_analyzer,
            "IPAddressAnalyzer": self.ip_analyzer,
            "VPNProxyAnalyzer": self.vpn_analyzer,
            "GeoConsistencyAnalyzer": self.geo_analyzer,
            "SessionAnalyzer": self.session_analyzer
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
            findings.append("Critical network or device threats identified.")
            recommendations.append("Block transaction")
            recommendations.append("Lock account temporarily")
        elif has_med:
            findings.append("Moderate location or routing anomalies flagged.")
            recommendations.append("Require MFA")
            recommendations.append("Verify device ownership")
        elif unique_evidence:
            findings.append("Minor connection profile changes detected.")
            recommendations.append("Manual review")
        else:
            findings.append("Connection device and location profiles are consistent with baseline.")
            recommendations.append("Verify device ownership")

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
