import sys
import os
import json
from datetime import datetime, timedelta

# Reconfigure stdout to support UTF-8 on Windows environments for printing checkmarks/cross symbols
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Setup pythonpath so we can import backend packages
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.agents.investigators.customer_agent import CustomerInvestigationAgent
from app.agents.models.investigation_context import InvestigationContext

def test_customer_agent():
    print("=== Testing CustomerInvestigationAgent ===")
    
    agent = CustomerInvestigationAgent()
    
    # ----------------------------------------------------
    # TEST CASE 1: Normal spending behaviors
    # ----------------------------------------------------
    print("\n--- Test Case 1: Normal Spending ---")
    
    # Use a fixed normal time (Wednesday 2:00 PM) for test reliability
    normal_time = datetime(2026, 7, 15, 14, 0, 0)
    normal_history = [
        {"amount": 500, "timestamp": (normal_time - timedelta(days=7)).isoformat()},
        {"amount": 700, "timestamp": (normal_time - timedelta(days=6)).isoformat()},
        {"amount": 600, "timestamp": (normal_time - timedelta(days=5)).isoformat()},
        {"amount": 800, "timestamp": (normal_time - timedelta(days=4)).isoformat()},
    ]
    
    context_normal = InvestigationContext(
        investigation_id="INV-NORMAL-01",
        transaction_id="TX_NORM_01",
        transaction_data={"customer_id": "CUST-1001", "amount": 650, "timestamp": normal_time.isoformat()},
        prediction_result={"probability": 0.02, "prediction": "Legitimate"},
        fraud_probability=0.02,
        risk_score=2,
        priority="LOW",
        shared_memory={"customer_history": normal_history}
    )
    
    result_normal = agent.execute(context_normal)
    
    print(f"Findings: {result_normal.findings}")
    print(f"Evidence: {result_normal.evidence}")
    print(f"Recommendations: {result_normal.recommendations}")
    print(f"Confidence Score: {result_normal.confidence_score}")
    
    # ----------------------------------------------------
    # TEST CASE 2: Suspicious spending deviations
    # ----------------------------------------------------
    print("\n--- Test Case 2: Suspicious Spending ---")
    
    # Customer history: 900, 1200, 850
    # Current transaction: 95,000
    # Also trigger:
    # - Time Anomaly (transacting at 2:00 AM)
    # - Velocity Anomaly (two history transactions in the last hour)
    now = datetime(2026, 7, 15, 2, 0, 0)
    suspicious_history = [
        {"amount": 900, "timestamp": (now - timedelta(days=3)).isoformat()},
        {"amount": 1200, "timestamp": (now - timedelta(minutes=15)).isoformat()}, # Velocity count 1
        {"amount": 850, "timestamp": (now - timedelta(minutes=5)).isoformat()},  # Velocity count 2
    ]
    
    # 2:00 AM unusual hour timestamp
    unusual_time = datetime(2026, 7, 15, 2, 0, 0)
    
    context_suspicious = InvestigationContext(
        investigation_id="INV-SUSP-01",
        transaction_id="TX_SUSP_01",
        transaction_data={
            "customer_id": "CUST-2002",
            "amount": 95000,
            "timestamp": unusual_time.isoformat()
        },
        prediction_result={"probability": 0.95, "prediction": "Fraud"},
        fraud_probability=0.95,
        risk_score=95,
        priority="HIGH",
        shared_memory={"customer_history": suspicious_history}
    )
    
    result_suspicious = agent.execute(context_suspicious)
    
    print(f"Findings: {result_suspicious.findings}")
    print(f"Evidence List:")
    for ev in result_suspicious.evidence:
        print(f"  * {ev['type']} (Severity={ev['severity']}, Confidence={ev['confidence']})")
        
    print(f"Recommendations: {result_suspicious.recommendations}")
    print(f"Confidence Score: {result_suspicious.confidence_score}")
    
    print("\n=== CustomerInvestigationAgent Tests Completed ===")

if __name__ == "__main__":
    test_customer_agent()
