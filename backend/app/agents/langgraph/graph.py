import logging
from typing import Dict, Any, Callable, Optional
from app.agents.langgraph.state import InvestigationState
from app.agents.langgraph.nodes import (
    predict_node,
    customer_node,
    device_node,
    network_node,
    merchant_node,
    knowledge_node,
    reasoning_node
)
from app.agents.langgraph.edges import EDGES

logger = logging.getLogger("app.agents.langgraph.graph")

class CompiledGraph:
    """Compiled state machine representation of LangGraph, executing node functions recursively."""

    def __init__(self, nodes: Dict[str, Callable], edges: Dict[str, Callable]) -> None:
        self.nodes = nodes
        self.edges = edges

    def invoke(self, state: InvestigationState) -> InvestigationState:
        """Invokes graph execution loop, sequentially stepping through nodes."""
        current_node = "FraudPrediction"
        
        while current_node != "END":
            node_func = self.nodes.get(current_node)
            if not node_func:
                logger.error("Node function not found in graph keys: %s", current_node)
                break
                
            # Execute node
            logger.info("LangGraph executing node: %s", current_node)
            state = node_func(state)
            
            # Retrieve transition rule
            edge_func = self.edges.get(current_node)
            if not edge_func:
                logger.error("Edge transition function not found in graph edges for node: %s", current_node)
                break
                
            current_node = edge_func(state)
            
        return state

class StateGraph:
    """Standard LangGraph StateGraph API interface provider compiled into local state machine engine."""

    def __init__(self, state_schema: Any) -> None:
        self.state_schema = state_schema
        self.nodes: Dict[str, Callable] = {}
        self.edges: Dict[str, Callable] = {}

    def add_node(self, name: str, func: Callable) -> None:
        self.nodes[name] = func

    def add_edge(self, start_key: str, end_key: str) -> None:
        self.edges[start_key] = lambda state: end_key

    def add_conditional_edges(
        self, 
        source: str, 
        router: Callable, 
        path_map: Optional[Dict[str, str]] = None
    ) -> None:
        # Wrap conditional router logic
        self.edges[source] = router

    def compile(self) -> CompiledGraph:
        """Compiles nodes and transitions into an executable StateMachine CompiledGraph."""
        return CompiledGraph(self.nodes, self.edges)

def build_investigation_graph() -> CompiledGraph:
    """Assembles and compiles the multi-agent langgraph workflow structure."""
    builder = StateGraph(InvestigationState)
    
    # 1. Register Nodes
    builder.add_node("FraudPrediction", predict_node)
    builder.add_node("CustomerInvestigationAgent", customer_node)
    builder.add_node("DeviceInvestigationAgent", device_node)
    builder.add_node("NetworkRiskAgent", network_node)
    builder.add_node("MerchantInvestigationAgent", merchant_node)
    builder.add_node("KnowledgeAgent", knowledge_node)
    builder.add_node("ReasoningAgent", reasoning_node)
    
    # 2. Add edges & conditional routings matching flow specification
    builder.add_conditional_edges("FraudPrediction", EDGES["FraudPrediction"])
    builder.add_edge("CustomerInvestigationAgent", "DeviceInvestigationAgent")
    builder.add_conditional_edges("DeviceInvestigationAgent", EDGES["DeviceInvestigationAgent"])
    builder.add_conditional_edges("NetworkRiskAgent", EDGES["NetworkRiskAgent"])
    builder.add_conditional_edges("MerchantInvestigationAgent", EDGES["MerchantInvestigationAgent"])
    builder.add_edge("KnowledgeAgent", "ReasoningAgent")
    builder.add_edge("ReasoningAgent", "END")
    
    return builder.compile()
