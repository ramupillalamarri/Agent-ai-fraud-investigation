from typing import Dict, Any, Callable
from app.agents.langgraph.router import (
    route_from_predict,
    route_from_device,
    route_from_network,
    route_from_merchant
)

# Maps node transition functions to node names
EDGES: Dict[str, Callable] = {
    "FraudPrediction": route_from_predict,
    "CustomerInvestigationAgent": lambda state: "DeviceInvestigationAgent",
    "DeviceInvestigationAgent": route_from_device,
    "NetworkRiskAgent": route_from_network,
    "MerchantInvestigationAgent": route_from_merchant,
    "KnowledgeAgent": lambda state: "ReasoningAgent",
    "ReasoningAgent": lambda state: "END"
}
