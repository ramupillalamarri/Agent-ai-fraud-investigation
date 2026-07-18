import sys
import time
import json
import logging
from typing import Dict, Any, List, Optional

# Reconfigure stdout to support UTF-8 on Windows environments for printing checkmarks/cross symbols
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from app.agents.models.investigation_context import InvestigationContext
from app.agents.models.agent_result import AgentResult
from app.agents.models.investigation_report import InvestigationReport
from app.agents.base.base_agent import BaseAgent
from app.agents.orchestrator.registry import AgentRegistry

logger = logging.getLogger("app.agents.orchestrator.orchestrator")

class InvestigationOrchestrator:
    """Orchestrates the priority-ordered execution of registered AI investigation agents,
    accumulating metrics, capturing exceptions, aggregating evidence, and compiling the final report.
    """

    def __init__(self, registry: AgentRegistry) -> None:
        """Initializes the orchestrator with an agent registry injection.
        
        Args:
            registry: The AgentRegistry instance.
        """
        self.registry = registry

    def health_check(self) -> bool:
        """Verifies the health check states of all registered agents (including the KnowledgeAgent and its RAG subsystems)."""
        logger.info("InvestigationOrchestrator health check started")
        try:
            for agent in self.registry.get_all_agents():
                logger.info("Checking agent health: %s", agent.agent_name)
                if not agent.health_check():
                    logger.error("Health check failed for agent: %s", agent.agent_name)
                    return False
            logger.info("InvestigationOrchestrator health check completed successfully.")
            return True
        except Exception as e:
            logger.error("Health check failed with exception: %s", str(e), exc_info=True)
            return False

    def before_investigation(self, context: InvestigationContext) -> None:

        """Lifecycle hook: Invoked before the orchestration workflow starts."""
        print("Investigation Started\n")
        logger.info("Orchestrator starting investigation ID: %s", context.investigation_id)

    def after_investigation(self, context: InvestigationContext, report: InvestigationReport) -> None:
        """Lifecycle hook: Invoked after the orchestration report is generated."""
        print("Investigation Completed")
        logger.info("Orchestrator completed investigation ID: %s", context.investigation_id)

    def before_agent_execution(self, agent: BaseAgent, context: InvestigationContext) -> None:
        """Lifecycle hook: Invoked before a single agent execution starts."""
        print(f"Executing {agent.agent_name}")
        logger.info("Starting agent: %s", agent.agent_name)

    def _safe_print(self, text: str) -> None:
        """Robust console printer with safe fallback formatting for non-UTF8 terminals."""
        try:
            print(text)
        except UnicodeEncodeError:
            fallback = text.replace("✓", "✓ Success").replace("✗", "✗ Failed").replace("⚠", "⚠ Skipped")
            # If CP1252 still raises, strip unicode characters entirely
            clean_text = fallback.encode("ascii", errors="replace").decode("ascii")
            # Replace question marks with human readable statuses
            clean_text = clean_text.replace("?", "")
            print(clean_text)

    def after_agent_execution(self, agent: BaseAgent, result: AgentResult, context: InvestigationContext) -> None:
        """Lifecycle hook: Invoked after an agent execution completes successfully (including skipped)."""
        if result.status == "SUCCESS":
            self._safe_print("✓ Success\n")
        elif result.status == "SKIPPED":
            self._safe_print("⚠ Skipped\n")
        logger.info("Finished agent: %s with status %s", agent.agent_name, result.status)

    def on_agent_failure(self, agent: BaseAgent, exception: Exception, context: InvestigationContext) -> None:
        """Lifecycle hook: Invoked when an agent execution fails due to a validation error or runtime crash."""
        self._safe_print("✗ Failed\n")
        self._safe_print("Continuing Investigation...\n")
        logger.error("Failed agent: %s | Error: %s", agent.agent_name, str(exception))

    def run_investigation(self, context: InvestigationContext) -> InvestigationReport:
        """Validates incoming context, runs all enabled agents sequentially, and compiles the InvestigationReport.
        
        Args:
            context: The shared InvestigationContext.
            
        Returns:
            InvestigationReport: The aggregated report.
        """
        # 1. Validate Context instance
        if not isinstance(context, InvestigationContext):
            raise ValueError("Invalid InvestigationContext: must be an instance of InvestigationContext")
            
        start_time = time.perf_counter()
        self.before_investigation(context)
        
        # 2. Get enabled agents from registry (registry already handles priority ordering)
        enabled_agents = self.registry.get_enabled_agents()
        
        agent_results = []
        
        # 3. Execute each agent sequentially
        for agent in enabled_agents:
            is_knowledge = agent.agent_name == "KnowledgeAgent"
            if is_knowledge:
                logger.info("KnowledgeAgent started")

            self.before_agent_execution(agent, context)
            
            try:
                # Trigger agent execution
                result = agent.execute(context)
                
                # Check for runtime skipped or validation fail results returned by execute wrapper
                if result.status in ("FAILED", "FAILED_VALIDATION"):
                    self.on_agent_failure(agent, ValueError(result.metadata.get("error_message", "Agent execute failed.")), context)
                    if is_knowledge:
                        logger.error("KnowledgeAgent failed execution")
                else:
                    self.after_agent_execution(agent, result, context)
                    if is_knowledge:
                        logger.info("Knowledge retrieved")
                        logger.info("Knowledge merged")
                    
                if is_knowledge:
                    logger.info("KnowledgeAgent completed")

                agent_results.append(result)
                
            except Exception as e:
                # Capture unhandled edge-case exceptions from agent.execute wrapper
                self.on_agent_failure(agent, e, context)
                if is_knowledge:
                    logger.error("KnowledgeAgent failed execution: %s", str(e))
                    logger.info("KnowledgeAgent completed")
                exec_time_ms = int((time.perf_counter() - start_time) * 1000)
                
                failed_res = AgentResult(
                    agent_name=agent.agent_name,
                    status="FAILED",
                    confidence_score=0.0,
                    findings=[f"Unhandled exception during execution: {str(e)}"],
                    recommendations=["Inspect code execution logs for diagnostics."],
                    evidence=[],
                    execution_time_ms=0,
                    metadata={"error_message": str(e)}
                )
                agent_results.append(failed_res)

                
        # 4. Aggregations
        print("Aggregating Evidence\n")
        
        seen_evidence = set()
        aggregated_evidence = []
        for res in agent_results:
            for item in res.evidence:
                # stable string serialization for deduplication
                serialized = json.dumps(item, sort_keys=True)
                if serialized not in seen_evidence:
                    seen_evidence.add(serialized)
                    aggregated_evidence.append(item)
                    
        # Update context collected evidence with full deduplicated list
        context.collected_evidence = aggregated_evidence
        
        # Recommendations deduplication
        seen_recs = set()
        aggregated_recs = []
        severity_rank = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        
        for res in agent_results:
            for rec in res.recommendations:
                if isinstance(rec, dict):
                    rec_text = rec.get("text", "")
                    rec_sev = str(rec.get("severity", "MEDIUM")).upper()
                    key = (rec_text, rec_sev)
                    if key not in seen_recs:
                        seen_recs.add(key)
                        aggregated_recs.append(rec)
                else:
                    if rec not in seen_recs:
                        seen_recs.add(rec)
                        aggregated_recs.append(rec)
                        
        # Sort recommendations if they are dicts with severity
        if all(isinstance(r, dict) and "severity" in r for r in aggregated_recs):
            aggregated_recs.sort(key=lambda r: severity_rank.get(str(r.get("severity", "MEDIUM")).upper(), 99))
            
        print("Generating Investigation Report\n")
        
        # Calculate overall metrics
        end_time = time.perf_counter()
        total_time_ms = int((end_time - start_time) * 1000)
        
        success_agents = [r.agent_name for r in agent_results if r.status == "SUCCESS"]
        failed_agents = [r.agent_name for r in agent_results if r.status in ("FAILED", "FAILED_VALIDATION")]
        skipped_agents = [r.agent_name for r in agent_results if r.status == "SKIPPED"]
        execution_times = {r.agent_name: r.execution_time_ms for r in agent_results}
        
        metrics = {
            "total_investigation_time_ms": total_time_ms,
            "successful_agents": success_agents,
            "failed_agents": failed_agents,
            "skipped_agents": skipped_agents,
            "agent_execution_times_ms": execution_times
        }
        
        # Calculate aggregate confidence score
        valid_confidences = [r.confidence_score for r in agent_results if r.status == "SUCCESS"]
        overall_confidence = sum(valid_confidences) / len(valid_confidences) if valid_confidences else 0.0
        
        # 5. Build Final Report
        report = InvestigationReport(
            investigation_id=context.investigation_id,
            transaction_id=context.transaction_id,
            overall_risk=context.priority,
            overall_confidence=overall_confidence,
            executive_summary=f"Automated multi-agent investigation completed with {len(success_agents)} successful checks and {len(failed_agents)} failures.",
            findings=[finding for r in agent_results for finding in r.findings if r.status == "SUCCESS"],
            recommendations=aggregated_recs,
            evidence=aggregated_evidence,
            executed_agents=context.executed_agents
        )
        
        # Embed metrics in report metadata list or generate metadata dict
        report.executive_summary += f" Total execution time: {total_time_ms} ms."
        
        # Store metrics on report metadata if requested
        # Wait, report.model_dump() doesn't have a direct metadata field, but we can store it in execution history or context metadata
        context.metadata["orchestrator_metrics"] = metrics
        context.metadata["agent_results"] = agent_results
        
        self.after_investigation(context, report)
        
        return report

if __name__ == "__main__":
    import sys
    import os
    
    # Setup path so standard imports work when executed directly
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
    
    # Define DummyAgents representing Customer, Device, and Behavior
    class CustomerDummyAgent(BaseAgent):
        def _execute(self, context: InvestigationContext) -> AgentResult:
            context.add_evidence(self.agent_name, "Verified customer balance is positive", {"balance": 5000})
            return self.create_success_result(
                findings=["Customer balance verified."],
                recommendations=["No customer flags."],
                evidence=[{"balance": 5000}]
            )
        def validate(self, context: InvestigationContext) -> None:
            pass
        def health_check(self) -> bool:
            return True

    class DeviceDummyAgent(BaseAgent):
        def _execute(self, context: InvestigationContext) -> AgentResult:
            # Throw runtime exception
            raise RuntimeError("Failed to resolve device geolocation server.")
        def validate(self, context: InvestigationContext) -> None:
            pass
        def health_check(self) -> bool:
            return True

    class BehaviorDummyAgent(BaseAgent):
        def _execute(self, context: InvestigationContext) -> AgentResult:
            context.add_evidence(self.agent_name, "Transaction behavior pattern matches historical baselines", {"pattern": "normal"})
            return self.create_success_result(
                findings=["Behavior matches baseline."],
                recommendations=["No behavioral flags."],
                evidence=[{"pattern": "normal"}]
            )
        def validate(self, context: InvestigationContext) -> None:
            pass
        def health_check(self) -> bool:
            return True

    # Setup Registry and register all three
    registry = AgentRegistry()
    
    customer = CustomerDummyAgent("cust-01", "CustomerDummyAgent", "Customer checks", "1.0", execution_priority=1)
    device = DeviceDummyAgent("dev-01", "DeviceDummyAgent", "Device checks", "1.0", execution_priority=2)
    behavior = BehaviorDummyAgent("beh-01", "BehaviorDummyAgent", "Behavior checks", "1.0", execution_priority=3)
    
    registry.register(customer)
    registry.register(device)
    registry.register(behavior)
    
    # Setup Context
    context = InvestigationContext(
        investigation_id="INV-TEST-ORCH",
        transaction_id="TX_TEST_ORCH",
        transaction_data={"amount": 100.0},
        prediction_result={"probability": 0.1, "prediction": "Legitimate"},
        fraud_probability=0.1,
        risk_score=10,
        priority="MEDIUM"
    )
    
    # Instantiate Orchestrator and run
    orchestrator = InvestigationOrchestrator(registry)
    report = orchestrator.run_investigation(context)
