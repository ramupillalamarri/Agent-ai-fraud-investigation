import sys
import os
import json
from datetime import datetime

# Set pythonpath so we can import app modules correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.agents.models.investigation_context import InvestigationContext
from app.agents.models.agent_result import AgentResult
from app.agents.models.investigation_report import InvestigationReport

def test_models_flow():
    print("=== Testing Shared AI Agent Models ===")
    
    # 1. Initialize InvestigationContext
    context = InvestigationContext(
        investigation_id="INV-9988",
        transaction_id="TX_1001",
        transaction_data={"amount": 1500.0, "location": "US", "payment_method": "credit"},
        prediction_result={"prediction": "Fraud", "probability": 0.92},
        fraud_probability=0.92,
        risk_score=92,
        priority="HIGH",
        metadata={"triggered_by": "XGBoost-Model"}
    )
    print("1. InvestigationContext created successfully.")
    
    # 2. Add some evidence to Context
    context.add_evidence(
        agent_name="IPGeolocatorAgent",
        key_finding="IP address belongs to a known proxy subnet.",
        details={"ip": "192.168.1.99", "subnet": "proxy-net-01"},
        confidence=0.95
    )
    context.update_shared_memory(key="proxy_detected", value=True)
    context.mark_agent_executed("IPGeolocatorAgent")
    print("2. Evidence and memory updated in InvestigationContext.")
    
    # 3. Create an AgentResult
    agent_result = AgentResult(
        agent_name="IPGeolocatorAgent",
        status="SUCCESS",
        confidence_score=0.95,
        findings=["Anomalous IP proxy detected.", "Subnet match on proxy blocklist."],
        recommendations=["Flag IP for future transactions.", "Require secondary MFA verification."],
        evidence=context.collected_evidence,
        execution_time_ms=120,
        metadata={"cache_hit": False}
    )
    print("3. AgentResult instantiated.")
    
    # 4. Initialize InvestigationReport and add AgentResult
    report = InvestigationReport(
        investigation_id=context.investigation_id,
        transaction_id=context.transaction_id,
        overall_risk=context.priority,
        overall_confidence=0.92
    )
    report.generate_summary("Executive Summary: Autonomous multi-agent verification has flagged transaction TX_1001 due to proxy subnet activity.")
    report.add_agent_result(agent_result)
    print("4. AgentResult added to InvestigationReport.")
    
    # 5. Export and Print Serialized Report
    report_dict = report.export_dict()
    print("\n5. Serialized Executive Investigation Report:")
    print(json.dumps(report_dict, indent=4))
    
    print("\n=== Models Verification Succeeded! ===")

if __name__ == "__main__":
    test_models_flow()
