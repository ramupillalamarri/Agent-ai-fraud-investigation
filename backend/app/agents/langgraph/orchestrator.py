import time
import logging
from app.agents.orchestrator.orchestrator import InvestigationOrchestrator
from app.agents.orchestrator.registry import AgentRegistry
from app.agents.models.investigation_context import InvestigationContext
from app.agents.models.investigation_report import InvestigationReport
from app.agents.langgraph.graph import build_investigation_graph
from app.agents.langgraph.state import InvestigationState

logger = logging.getLogger("app.agents.langgraph.orchestrator")

class LangGraphOrchestrator(InvestigationOrchestrator):
    """Subclass of InvestigationOrchestrator that implements a dynamic LangGraph-based execution workflow."""

    def __init__(self, registry: AgentRegistry) -> None:
        """Injects registry and compiles the multi-agent execution graph."""
        super().__init__(registry)
        self.graph = build_investigation_graph()
        logger.info("Initialized LangGraphOrchestrator with compiled StateGraph.")

    def run_investigation(self, context: InvestigationContext) -> InvestigationReport:
        """Runs the LangGraph dynamic agent flow instead of the standard sequential orchestrator."""
        start_time = time.perf_counter()
        
        self.before_investigation(context)
        
        # Initialize graph state
        initial_state: InvestigationState = {
            "context": context,
            "report": None,
            "agent_results": [],
            "evidence": [],
            "recommendations": [],
            "execution_metadata": {"nodes": {}},
            "next_node": ""
        }
        
        # Invoke compiled state machine graph
        final_state = self.graph.invoke(initial_state)
        
        # Log to context metadata (required by database service mapping)
        context.metadata["agent_results"] = final_state["agent_results"]
            
        report = final_state["report"]
        if not report:
            raise ValueError("LangGraph multi-agent execution failed to construct a final InvestigationReport.")
            
        # Calculate total latency and append to executive summary
        total_time_ms = int((time.perf_counter() - start_time) * 1000)
        report.executive_summary += f" Total execution time: {total_time_ms} ms."
        
        self.after_investigation(context, report)
        return report
