import sys
import os
import json

# Setup pythonpath so we can import backend packages
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.agents.investigators.network.network_agent import NetworkRiskAgent
from app.agents.models.investigation_context import InvestigationContext

def test_network_agent():
    print("=== Testing NetworkRiskAgent ===")
    
    agent = NetworkRiskAgent()
    
    # ----------------------------------------------------
    # TEST CASE 1: Normal relationship bounds
    # ----------------------------------------------------
    print("\n--- Test Case 1: Normal Relations ---")
    
    # Isolated context data with no sharing
    normal_network = {
        "ip_accounts": {"192.168.1.10": ["acc_1"]},
        "device_accounts": {"DEV-SAFE-99": ["acc_1"]},
        "shared_attributes": {"phone_123": ["acc_1"]},
        "payment_accounts": {"card_1": ["acc_1"]},
        "flagged_merchants": [],
        "fraud_clusters": []
    }
    
    context_normal = InvestigationContext(
        investigation_id="INV-NORM-NET-01",
        transaction_id="TX_NORM_NET_01",
        transaction_data={
            "customer_id": "acc_1",
            "device_id": "DEV-SAFE-99",
            "ip_address": "192.168.1.10",
            "payment_instrument": "card_1",
            "merchant_id": "MERCH-NORMAL"
        },
        prediction_result={"probability": 0.01, "prediction": "Legitimate"},
        fraud_probability=0.01,
        risk_score=1,
        priority="LOW",
        shared_memory={"network_data": normal_network}
    )
    
    result_normal = agent.execute(context_normal)
    
    print(f"Findings: {result_normal.findings}")
    print(f"Evidence: {result_normal.evidence}")
    print(f"Recommendations: {result_normal.recommendations}")
    
    # ----------------------------------------------------
    # TEST CASE 2: Suspicious relationship overlaps
    # ----------------------------------------------------
    print("\n--- Test Case 2: Suspicious Relations ---")
    
    # - Five accounts share the same IP
    # - Three accounts use the same device
    # - Two merchants linked to previous fraud (we are using one flagged merchant in tx_data matching the flagged list)
    # - Shared payment card (three accounts share the card)
    # - Fraud cluster detected
    suspicious_network = {
        "ip_accounts": {
            "198.51.100.22": ["acc_1", "acc_2", "acc_3", "acc_4", "acc_5"]
        },
        "device_accounts": {
            "DEV-SUSP-77": ["acc_1", "acc_2", "acc_3"]
        },
        "shared_attributes": {
            "phone_555": ["acc_1", "acc_2"],
            "address_999": ["acc_1", "acc_3"]
        },
        "payment_accounts": {
            "card_suspicious_88": ["acc_1", "acc_2", "acc_3"]
        },
        "flagged_merchants": ["MERCH_FRAUD_88", "MERCH_BLOCKED_12"],
        "fraud_clusters": [
            ["acc_1", "acc_2", "acc_3", "DEV-SUSP-77", "198.51.100.22"]
        ]
    }
    
    context_suspicious = InvestigationContext(
        investigation_id="INV-SUSP-NET-01",
        transaction_id="TX_SUSP_NET_01",
        transaction_data={
            "customer_id": "acc_1",
            "device_id": "DEV-SUSP-77",
            "ip_address": "198.51.100.22",
            "payment_instrument": "card_suspicious_88",
            "merchant_id": "MERCH_FRAUD_88"
        },
        prediction_result={"probability": 0.96, "prediction": "Fraud"},
        fraud_probability=0.96,
        risk_score=96,
        priority="HIGH",
        shared_memory={"network_data": suspicious_network}
    )
    
    result_suspicious = agent.execute(context_suspicious)
    
    print(f"Findings: {result_suspicious.findings}")
    print(f"Evidence List:")
    for ev in result_suspicious.evidence:
        print(f"  * {ev['type']} (Severity={ev['severity']}, Source={ev['source']})")
        
    print(f"Recommendations: {result_suspicious.recommendations}")
    print(f"Confidence Score: {result_suspicious.confidence_score}")
    
    print("\n=== NetworkRiskAgent Tests Completed ===")

if __name__ == "__main__":
    test_network_agent()
