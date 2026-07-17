from app.agents.langgraph.state import InvestigationState
from app.agents.langgraph import conditions

def route_from_predict(state: InvestigationState) -> str:
    """Routes from Fraud Prediction: if low risk, bypass details directly to ReasoningAgent."""
    if conditions.is_low_risk_transaction(state):
        return "ReasoningAgent"
    return "CustomerInvestigationAgent"

def route_from_device(state: InvestigationState) -> str:
    """Routes from DeviceInvestigationAgent: checks if NetworkRiskAgent is needed."""
    if conditions.needs_network_analysis(state):
        return "NetworkRiskAgent"
    return route_from_network(state)

def route_from_network(state: InvestigationState) -> str:
    """Routes from NetworkRiskAgent: checks if MerchantInvestigationAgent is needed."""
    if conditions.needs_merchant_analysis(state):
        return "MerchantInvestigationAgent"
    return route_from_merchant(state)

def route_from_merchant(state: InvestigationState) -> str:
    """Routes from MerchantInvestigationAgent: checks if RAG KnowledgeAgent is needed."""
    if conditions.needs_knowledge_retrieval(state):
        return "KnowledgeAgent"
    return "ReasoningAgent"
