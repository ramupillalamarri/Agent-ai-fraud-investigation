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
        merchant_id = (
            tx_data.get("merchant_id") 
            or tx_data.get("merchant") 
            or (tx_data.get("merchant_profile") or {}).get("merchant_id")
        )
        if not merchant_id:
            raise ValueError("MerchantInvestigationAgent requires either 'merchant_id' or 'merchant' inside transaction_data.")

    def health_check(self) -> bool:
        """Verifies configuration integrity, child dependency analyzers availability, and system readiness."""
        try:
            # 1. Config check
            if not isinstance(self.config, MerchantAgentConfig):
                logger.error("Health check failed: Invalid config instance type.")
                return False
            
            # 2. Child analyzers instantiation check
            analyzers = [
                self.profile_analyzer,
                self.history_analyzer,
                self.category_analyzer,
                self.location_analyzer,
                self.velocity_analyzer,
                self.reputation_analyzer
            ]
            for idx, analyzer in enumerate(analyzers):
                if analyzer is None:
                    logger.error("Health check failed: Analyzer at index %d is not initialized.", idx)
                    return False
                    
            logger.info("Health check passed: MerchantInvestigationAgent is healthy and ready.")
            return True
        except Exception as e:
            logger.exception("Health check encountered unhandled exception: %s", str(e))
            return False

    def _execute(self, context: InvestigationContext) -> AgentResult:
        """Executes the integrated analysis pipeline by routing context to enabled sub-analyzers sequentially."""
        import time
        logger.info("Merchant Agent started")
        
        # 1. Validation
        self.validate(context)

        # 2. Map analyzers in execution order with their toggle configurations
        pipeline = [
            ("Profile", self.profile_analyzer, getattr(self.config, "enable_profile", True)),
            ("History", self.history_analyzer, getattr(self.config, "enable_history", True)),
            ("Category", self.category_analyzer, getattr(self.config, "enable_category", True)),
            ("Location", self.location_analyzer, getattr(self.config, "enable_location", True)),
            ("Velocity", self.velocity_analyzer, getattr(self.config, "enable_velocity", True)),
            ("Reputation", self.reputation_analyzer, getattr(self.config, "enable_reputation", True)),
        ]

        evidence_list: List[Dict[str, Any]] = []
        recommendations_list: List[str] = []
        confidence_scores: List[float] = []
        metadata_breakdown: Dict[str, Any] = {}
        
        # Metrics and execution stats
        analyzer_latencies: Dict[str, float] = {}
        successful_analyzers: List[str] = []
        failed_analyzers: List[str] = []
        skipped_analyzers: List[str] = []
        
        start_total_time = time.perf_counter()
        
        logger.info("Analyzer execution started")

        for name, analyzer, is_enabled in pipeline:
            if not is_enabled:
                logger.info("Analyzer %s is skipped (disabled by config)", name)
                skipped_analyzers.append(name)
                continue
                
            start_analyzer_time = time.perf_counter()
            try:
                logger.info("Executing analyzer sub-module: %s", name)
                
                # Execute analyzer using full context payload
                res = analyzer.analyze(context)
                
                # Record latency
                latency_ms = (time.perf_counter() - start_analyzer_time) * 1000.0
                analyzer_latencies[name] = latency_ms
                
                if isinstance(res, dict):
                    # Structured context mode return format
                    evidence_list.extend(res.get("evidence") or [])
                    recommendations_list.extend(res.get("recommendations") or [])
                    confidence_scores.append(res.get("confidence_score", 1.0))
                    metadata_breakdown[name] = res.get("metadata") or {}
                else:
                    # Legacy dict mode fallback returning flat list of evidence dicts
                    evidence_list.extend(res or [])
                    confidence_scores.append(1.0) # default confidence
                    
                successful_analyzers.append(name)
                logger.info("Analyzer completed: %s in %.2fms", name, latency_ms)
                
            except Exception as e:
                # Capture failures gracefully, log them, and keep executing the pipeline
                latency_ms = (time.perf_counter() - start_analyzer_time) * 1000.0
                analyzer_latencies[name] = latency_ms
                failed_analyzers.append(name)
                
                logger.error("Analyzer failed: %s after %.2fms with error: %s", name, latency_ms, str(e), exc_info=True)
                
                evidence_list.append({
                    "type": "AnalyzerError",
                    "severity": "HIGH",
                    "title": f"Sub-module Execution Crash: {name}",
                    "description": f"Internal crash during sub-module execution in {name} analyzer: {str(e)}",
                    "confidence": 0.0,
                    "source": f"Merchant{name}Analyzer",
                    "metadata": {"error": str(e), "latency_ms": latency_ms}
                })
                recommendations_list.append("Escalate investigation")

        total_execution_time = (time.perf_counter() - start_total_time) * 1000.0
        logger.info("Aggregation completed")

        # Deduplicate evidence list
        seen_evidence = set()
        unique_evidence = []
        for ev in evidence_list:
            key = (ev.get("type"), ev.get("severity"), ev.get("source"), ev.get("description"))
            if key not in seen_evidence:
                seen_evidence.add(key)
                unique_evidence.append(ev)

        # Deduplicate recommendations list
        unique_recommendations = list(set(recommendations_list))

        # Calculate overall trust confidence score
        if confidence_scores:
            overall_confidence = sum(confidence_scores) / len(confidence_scores)
        else:
            overall_confidence = 1.0

        # Generate summary findings
        findings: List[str] = []
        has_crit = any(ev.get("severity") == "CRITICAL" for ev in unique_evidence)
        has_high = any(ev.get("severity") == "HIGH" for ev in unique_evidence)
        has_med = any(ev.get("severity") == "MEDIUM" for ev in unique_evidence)
        
        merchant_id = (
            (context.transaction_data or {}).get("merchant_id")
            or (context.transaction_data or {}).get("merchant")
            or ((context.transaction_data or {}).get("merchant_profile") or {}).get("merchant_id")
        )

        if has_crit or has_high:
            findings.append(f"High risk factors flagged for merchant '{merchant_id}' checks.")
            if "Block transaction" not in unique_recommendations:
                unique_recommendations.append("Block transaction")
            if "Flag merchant for manual compliance review" not in unique_recommendations:
                unique_recommendations.append("Flag merchant for manual compliance review")
        elif has_med:
            findings.append(f"Moderate risk merchant category/velocity spike flagged for merchant '{merchant_id}'.")
            if "Flag transaction for manual review" not in unique_recommendations:
                unique_recommendations.append("Flag transaction for manual review")
        else:
            findings.append(f"Merchant '{merchant_id}' risk parameters are optimal.")
            if not unique_recommendations or unique_recommendations == ["Increase monitoring"]:
                unique_recommendations = ["Approve merchant"]

        # Final metadata construction
        metadata = {
            "execution_statistics": {
                "total_execution_time_ms": total_execution_time,
                "analyzer_latencies_ms": analyzer_latencies,
                "successful_analyzers": successful_analyzers,
                "failed_analyzers": failed_analyzers,
                "skipped_analyzers": skipped_analyzers
            },
            "analyzers_executed": successful_analyzers + failed_analyzers,
            "confidence_breakdown": metadata_breakdown,
            "triggered_rules": list(set(ev.get("type") for ev in unique_evidence))
        }

        logger.info("Merchant Agent completed in %.2fms", total_execution_time)

        return AgentResult(
            agent_name=self.agent_name,
            status="SUCCESS" if not failed_analyzers else "PARTIAL_SUCCESS",
            confidence_score=overall_confidence,
            findings=findings,
            recommendations=unique_recommendations,
            evidence=unique_evidence,
            execution_time_ms=int(total_execution_time),
            metadata=metadata
        )
