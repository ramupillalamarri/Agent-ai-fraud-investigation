import sys
import os
import json
from datetime import datetime, timedelta

# Setup pythonpath so we can import backend packages
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.agents.investigators.device.device_agent import DeviceInvestigationAgent
from app.agents.models.investigation_context import InvestigationContext

def test_device_agent():
    print("=== Testing DeviceInvestigationAgent ===")
    
    agent = DeviceInvestigationAgent()
    
    # ----------------------------------------------------
    # TEST CASE 1: Normal connection behaviors
    # ----------------------------------------------------
    print("\n--- Test Case 1: Normal Connection ---")
    
    normal_time = datetime(2026, 7, 15, 14, 0, 0)
    normal_history = [
        {
            "device_id": "DEV-SAFE-99",
            "ip_address": "192.168.1.10",
            "country": "US",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "timestamp": (normal_time - timedelta(days=2)).isoformat()
        }
    ]
    
    context_normal = InvestigationContext(
        investigation_id="INV-NORM-DEV-01",
        transaction_id="TX_NORM_DEV_01",
        transaction_data={
            "device_id": "DEV-SAFE-99",
            "browser": "chrome",
            "ip_address": "192.168.1.10",
            "ip_type": "residential",
            "vpn_detected": False,
            "proxy_detected": False,
            "tor_detected": False,
            "latitude": 37.7749,
            "longitude": -122.4194,
            "timestamp": normal_time.isoformat()
        },
        prediction_result={"probability": 0.01, "prediction": "Legitimate"},
        fraud_probability=0.01,
        risk_score=1,
        priority="LOW",
        shared_memory={"customer_history": normal_history}
    )
    
    result_normal = agent.execute(context_normal)
    
    print(f"Findings: {result_normal.findings}")
    print(f"Evidence: {result_normal.evidence}")
    print(f"Recommendations: {result_normal.recommendations}")
    
    # ----------------------------------------------------
    # TEST CASE 2: Suspicious connection behaviors
    # ----------------------------------------------------
    print("\n--- Test Case 2: Suspicious Connection ---")
    
    # Customer history in US (SF) 15 minutes ago
    suspicious_history = [
        {
            "device_id": "DEV-SAFE-99",
            "ip_address": "192.168.1.10",
            "country": "US",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "timestamp": (normal_time - timedelta(minutes=15)).isoformat()
        }
    ]
    
    # New laptop, VPN enabled, New country (UK, London), Datacenter IP, Headless browser
    # Travel from SF to London (8700 km) in 15 minutes is impossible travel!
    context_suspicious = InvestigationContext(
        investigation_id="INV-SUSP-DEV-01",
        transaction_id="TX_SUSP_DEV_01",
        transaction_data={
            "device_id": "DEV-NEW-LAPTOP-55",
            "previous_device_id": "DEV-SAFE-99",
            "browser": "headlesschrome",
            "user_agent": "headless chrome agent bot",
            "ip_address": "198.51.100.22",
            "ip_type": "datacenter",
            "vpn_detected": True,
            "proxy_detected": False,
            "tor_detected": False,
            "country": "UK",
            "latitude": 51.5074,
            "longitude": -0.1278,
            "timestamp": normal_time.isoformat()
        },
        prediction_result={"probability": 0.98, "prediction": "Fraud"},
        fraud_probability=0.98,
        risk_score=98,
        priority="HIGH",
        shared_memory={"customer_history": suspicious_history}
    )
    
    result_suspicious = agent.execute(context_suspicious)
    
    print(f"Findings: {result_suspicious.findings}")
    print(f"Evidence List:")
    for ev in result_suspicious.evidence:
        print(f"  * {ev['type']} (Severity={ev['severity']}, Source={ev['source']})")
        
    print(f"Recommendations: {result_suspicious.recommendations}")
    print(f"Confidence Score: {result_suspicious.confidence_score}")
    
    print("\n=== DeviceInvestigationAgent Tests Completed ===")

if __name__ == "__main__":
    test_device_agent()
