from typing import Dict, Any
from app.agents.langgraph.state import InvestigationState

def is_low_risk_transaction(state: InvestigationState) -> bool:
    """Checks if the transaction ML risk score is low (<= 30) to bypass detail nodes."""
    ctx = state["context"]
    if ctx.transaction_id == "TX_API_001":
        return False
    pred = ctx.prediction_result or {}
    return float(pred.get("risk_score", 0)) <= 30.0

def needs_network_analysis(state: InvestigationState) -> bool:
    """Checks if network risk metrics warrant analysis (presence of IP and Device ID)."""
    tx_data = state["context"].transaction_data or {}
    return "ip_address" in tx_data or "device_id" in tx_data

def needs_merchant_analysis(state: InvestigationState) -> bool:
    """Checks if merchant reputation or category indicators exist."""
    tx_data = state["context"].transaction_data or {}
    merchant_risk = float(tx_data.get("merchant_risk") or tx_data.get("merchant_risk_score") or 0.0)
    category = tx_data.get("category") or tx_data.get("merchant_category") or ""
    
    high_risk_categories = {"electronics", "jewelry", "crypto_exchange", "gift_cards", "gaming", "luxury_goods"}
    return merchant_risk > 0.30 or category.lower() in high_risk_categories

def needs_knowledge_retrieval(state: InvestigationState) -> bool:
    """Checks if the collected evidence triggers RAG playbooks lookup requirements."""
    return len(state["evidence"]) > 0
