import time
import logging
from typing import Dict, Any, List
from app.agents.langgraph.state import InvestigationState
from app.agents.models.agent_result import AgentResult
from app.agents.models.investigation_report import InvestigationReport

# Import concrete agents
from app.agents.investigators.customer_agent import CustomerInvestigationAgent
from app.agents.investigators.device.device_agent import DeviceInvestigationAgent
from app.agents.investigators.network.network_agent import NetworkRiskAgent
from app.agents.investigators.merchant.merchant_agent import MerchantInvestigationAgent
from app.agents.investigators.knowledge.knowledge_agent import KnowledgeAgent

logger = logging.getLogger("app.agents.langgraph.nodes")

customer_agent = CustomerInvestigationAgent()
device_agent = DeviceInvestigationAgent()
network_agent = NetworkRiskAgent()
merchant_agent = MerchantInvestigationAgent()
knowledge_agent = KnowledgeAgent()

def run_agent_safely(agent, state: InvestigationState) -> Dict[str, Any]:
    """Helper executing agents safely, tracking telemetry latency and capturing failures."""
    start_time = time.perf_counter()
    node_name = agent.agent_name
    
    # Initialize node entry in metadata
    meta = state.get("execution_metadata", {})
    if "nodes" not in meta:
        meta["nodes"] = {}
    meta["nodes"][node_name] = {"status": "RUNNING", "start_time": start_time}
    
    try:
        agent.validate(state["context"])
        res = agent.execute(state["context"])
        
        latency = int((time.perf_counter() - start_time) * 1000)
        meta["nodes"][node_name] = {
            "status": res.status,
            "latency_ms": latency,
            "error": None
        }
        
        # Merge outputs
        state["agent_results"].append(res)
        state["evidence"].extend(res.evidence)
        state["recommendations"].extend(res.recommendations)
        
    except Exception as e:
        logger.exception("Error executing node agent %s: %s", node_name, str(e))
        latency = int((time.perf_counter() - start_time) * 1000)
        meta["nodes"][node_name] = {
            "status": "FAILED",
            "latency_ms": latency,
            "error": str(e)
        }
        # Append failure result to keep graph sequence running
        state["agent_results"].append(AgentResult(
            agent_name=node_name,
            status="FAILED",
            confidence_score=0.0,
            findings=["Internal agent execution failed."],
            recommendations=["Verify node logs."],
            evidence=[],
            execution_time_ms=latency,
            metadata={"error": str(e)}
        ))
        
    return {
        "agent_results": state["agent_results"],
        "evidence": state["evidence"],
        "recommendations": state["recommendations"],
        "execution_metadata": meta
    }

# Node definitions
def predict_node(state: InvestigationState) -> InvestigationState:
    logger.info("Executing predict_node...")
    # Prediction has already been computed by ML Predict API, verify details
    pred = state["context"].prediction_result or {}
    meta = state.get("execution_metadata", {})
    if "nodes" not in meta:
        meta["nodes"] = {}
    meta["nodes"]["FraudPrediction"] = {
        "status": "SUCCESS",
        "latency_ms": 0,
        "score": pred.get("risk_score", 0)
    }
    state["execution_metadata"] = meta
    return state

def customer_node(state: InvestigationState) -> InvestigationState:
    logger.info("Executing customer_node...")
    run_agent_safely(customer_agent, state)
    return state

def device_node(state: InvestigationState) -> InvestigationState:
    logger.info("Executing device_node...")
    run_agent_safely(device_agent, state)
    return state

def network_node(state: InvestigationState) -> InvestigationState:
    logger.info("Executing network_node...")
    run_agent_safely(network_agent, state)
    return state

def merchant_node(state: InvestigationState) -> InvestigationState:
    logger.info("Executing merchant_node...")
    run_agent_safely(merchant_agent, state)
    return state

def knowledge_node(state: InvestigationState) -> InvestigationState:
    logger.info("Executing knowledge_node...")
    run_agent_safely(knowledge_agent, state)
    return state

def reasoning_node(state: InvestigationState) -> InvestigationState:
    logger.info("Executing reasoning_node...")
    start_time = time.perf_counter()
    
    # Resolve risk score averages and priority triggers
    all_evidence = state["evidence"]
    has_crit = any(ev["severity"] == "CRITICAL" for ev in all_evidence)
    has_high = any(ev["severity"] == "HIGH" for ev in all_evidence)
    has_med = any(ev["severity"] == "MEDIUM" for ev in all_evidence)
    
    # Compute composite overall risk score based on agent outputs
    base_ml_risk = state["context"].prediction_result.get("risk_score", 0.0) if state["context"].prediction_result else 0.0
    agent_risks = [res.confidence_score * 100 for res in state["agent_results"] if res.status == "SUCCESS"]
    
    if agent_risks:
        overall_risk = int(0.4 * base_ml_risk + 0.6 * (sum(agent_risks) / len(agent_risks)))
    else:
        overall_risk = int(base_ml_risk)
        
    overall_risk = max(0, min(100, overall_risk))
    
    priority = "LOW"
    if has_crit or overall_risk >= 80:
        priority = "HIGH"
    elif has_high or has_med or overall_risk >= 50:
        priority = "MEDIUM"

    # Deduplicate findings & recommendations
    unique_findings = list(set([f for res in state["agent_results"] for f in res.findings]))
    unique_recs = list(set(state["recommendations"]))
    if not unique_recs:
        unique_recs = ["No immediate action needed. Monitor user behavior."]

    exec_time_ms = int((time.perf_counter() - start_time) * 1000)
    
    # Store graph execution metadata in execution_metadata
    meta = state.get("execution_metadata", {})
    meta["nodes"]["ReasoningAgent"] = {
        "status": "SUCCESS",
        "latency_ms": exec_time_ms
    }
    
    # Standardize timeline log audits
    if "timeline_events" not in state["context"].metadata:
        state["context"].metadata["timeline_events"] = []
    
    state["context"].metadata["timeline_events"].append({
        "event_type": "REASONING_COMPLETED",
        "event_description": f"Multi-agent LangGraph workflow execution completed with {len(state['agent_results'])} agent outputs.",
        "agent_name": "ReasoningAgent",
        "metadata": meta
    })
    
    # Calculate overall confidence
    valid_confidences = [r.confidence_score for r in state["agent_results"] if r.status == "SUCCESS"]
    overall_confidence = sum(valid_confidences) / len(valid_confidences) if valid_confidences else 1.0

    # Create final InvestigationReport matching model schema
    report = InvestigationReport(
        investigation_id=state["context"].investigation_id,
        transaction_id=state["context"].transaction_id,
        overall_risk=priority,
        overall_confidence=overall_confidence,
        executive_summary=f"Automated multi-agent LangGraph investigation completed with {len(state['agent_results'])} checked nodes. Overall risk index: {overall_risk}%.",
        findings=unique_findings,
        recommendations=unique_recs,
        evidence=state["evidence"],
        executed_agents=[res.agent_name for res in state["agent_results"]]
    )
    
    state["report"] = report
    state["execution_metadata"] = meta
    return state
