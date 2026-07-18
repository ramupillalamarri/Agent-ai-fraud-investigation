import sys
import os
from datetime import datetime, date, timedelta

# Set pythonpath so we can import app modules correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.agents.models.investigation_context import InvestigationContext
from app.agents.investigators.merchant.config import MerchantAgentConfig
from app.agents.investigators.merchant.analyzers.merchant_history_analyzer import MerchantHistoryAnalyzer

def get_base_context(transaction_data: dict) -> InvestigationContext:
    """Helper to instantiate a fresh mock InvestigationContext."""
    return InvestigationContext(
        investigation_id="INV-TEST-002",
        transaction_id="TX-TEST-002",
        transaction_data=transaction_data,
        prediction_result={},
        fraud_probability=0.0,
        risk_score=0,
        priority="LOW"
    )

def test_healthy_merchant_history():
    """Verify that an established, low-dispute, active history merchant generates no alerts."""
    config = MerchantAgentConfig()
    analyzer = MerchantHistoryAnalyzer(config)
    
    history_payload = {
        "merchant_id": "merch_healthy_hist_01",
        "total_transactions": 5000,
        "successful_transactions": 4980,
        "failed_transactions": 20,
        "chargebacks": 2,          # 0.04% chargeback rate
        "refunds": 45,             # 0.9% refund rate
        "fraud_cases": 0,
        "customer_disputes": 5,    # 0.1% dispute rate
        "daily_transaction_volume": 12000.0,
        "monthly_transaction_volume": 350000.0,
        "last_transaction_date": (date.today() - timedelta(days=1)).isoformat()
    }
    
    # Context mode
    context = get_base_context(history_payload)
    res = analyzer.analyze(context)
    
    assert isinstance(res, dict)
    assert len(res["evidence"]) == 0
    assert res["confidence_score"] == 1.0
    assert "Increase monitoring" in res["recommendations"]

    # Legacy mode
    legacy_res = analyzer.analyze(history_payload)
    assert isinstance(legacy_res, list)
    assert len(legacy_res) == 0

def test_excessive_chargebacks_merchant():
    """Verify high chargeback rate threshold alert triggers."""
    config = MerchantAgentConfig()
    analyzer = MerchantHistoryAnalyzer(config)
    
    history_payload = {
        "merchant_id": "merch_high_cb_01",
        "total_transactions": 200,
        "successful_transactions": 190,
        "failed_transactions": 10,
        "chargebacks": 10,         # 5% chargeback rate (threshold is 2%)
        "refunds": 10,
        "fraud_cases": 0,
        "customer_disputes": 2
    }
    
    context = get_base_context(history_payload)
    res = analyzer.analyze(context)
    
    evidence_types = [ev["type"] for ev in res["evidence"]]
    assert "HighMerchantChargebackRate" in evidence_types
    assert "Reduce transaction limits" in res["recommendations"]
    assert "Require manual review" in res["recommendations"]
    assert res["confidence_score"] <= 0.5  # Penalized for high chargebacks

def test_fraud_history_merchant():
    """Verify previous fraud cases/investigations alerts."""
    config = MerchantAgentConfig()
    analyzer = MerchantHistoryAnalyzer(config)
    
    history_payload = {
        "merchant_id": "merch_fraud_hist_01",
        "total_transactions": 1000,
        "successful_transactions": 980,
        "failed_transactions": 20,
        "chargebacks": 1,
        "refunds": 20,
        "fraud_cases": 3,          # Explicit previous fraud cases
        "customer_disputes": 4
    }
    
    context = get_base_context(history_payload)
    res = analyzer.analyze(context)
    
    evidence_types = [ev["type"] for ev in res["evidence"]]
    assert "HighMerchantFraudRate" in evidence_types
    assert "Temporary merchant verification" in res["recommendations"]
    assert res["confidence_score"] <= 0.4  # Penalized heavily for fraud history

def test_abnormal_refund_ratio_merchant():
    """Verify abnormal refund rates trigger alerts."""
    config = MerchantAgentConfig()
    analyzer = MerchantHistoryAnalyzer(config)
    
    history_payload = {
        "merchant_id": "merch_high_refund_01",
        "total_transactions": 150,
        "successful_transactions": 110,
        "failed_transactions": 40,
        "chargebacks": 0,
        "refunds": 30,             # 20% refund rate (threshold is 15%)
        "fraud_cases": 0,
        "customer_disputes": 1
    }
    
    context = get_base_context(history_payload)
    res = analyzer.analyze(context)
    
    evidence_types = [ev["type"] for ev in res["evidence"]]
    assert "HighMerchantRefundRate" in evidence_types
    assert "Increase monitoring" in res["recommendations"]
    assert res["confidence_score"] <= 0.7  # Penalized for high refunds
