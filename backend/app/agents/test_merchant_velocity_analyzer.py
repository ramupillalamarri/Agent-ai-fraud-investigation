import sys
import os

# Set pythonpath so we can import app modules correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.agents.models.investigation_context import InvestigationContext
from app.agents.investigators.merchant.config import MerchantAgentConfig
from app.agents.investigators.merchant.analyzers.merchant_velocity_analyzer import MerchantVelocityAnalyzer

def get_base_context(transaction_data: dict) -> InvestigationContext:
    """Helper to instantiate a fresh mock InvestigationContext."""
    return InvestigationContext(
        investigation_id="INV-TEST-005",
        transaction_id="TX-TEST-005",
        transaction_data=transaction_data,
        prediction_result={},
        fraud_probability=0.0,
        risk_score=0,
        priority="LOW"
    )

def test_normal_merchant():
    """Verify normal merchant metrics do not trigger velocity alerts."""
    config = MerchantAgentConfig()
    analyzer = MerchantVelocityAnalyzer(config)
    
    tx_data = {
        "merchant_id": "merch_normal_vel_01",
        "transactions_last_minute": 0,
        "transactions_last_5_minutes": 1,
        "transactions_last_hour": 15,
        "transactions_last_day": 350,
        "average_transactions_per_hour": 20.0,
        "average_transactions_per_day": 400.0,
        "current_transaction_amount": 50.0,
        "average_transaction_amount": 48.0,
        "failed_transactions_last_hour": 0,
        "successful_transactions_last_hour": 15,
        "refunds_last_day": 1,
        "chargebacks_last_week": 0,
        "new_customers_last_hour": 2,
        "repeat_customers_last_hour": 13
    }
    
    context = get_base_context(tx_data)
    res = analyzer.analyze(context)
    
    assert isinstance(res, dict)
    assert len(res["evidence"]) == 0
    assert res["confidence_score"] == 1.0
    assert "Increase monitoring" in res["recommendations"]

    # Legacy mode
    legacy_res = analyzer.analyze(tx_data)
    assert isinstance(legacy_res, list)
    assert len(legacy_res) == 0

def test_flash_sale_merchant():
    """Verify expected velocity spike under flash sale threshold is tolerated."""
    config = MerchantAgentConfig()
    analyzer = MerchantVelocityAnalyzer(config)
    
    tx_data = {
        "merchant_id": "merch_flash_sale_01",
        "transactions_last_5_minutes": 8,   # High count but within flash sale expectations
        "average_transactions_per_hour": 60.0  # expected 5min = 5. Burst threshold is 5 * 5 = 25.
    }
    
    context = get_base_context(tx_data)
    res = analyzer.analyze(context)
    
    evidence_types = [ev["type"] for ev in res["evidence"]]
    assert "MerchantVelocitySpike" not in evidence_types

def test_abnormal_transaction_burst():
    """Verify sudden transaction count burst trigger warnings."""
    config = MerchantAgentConfig()
    analyzer = MerchantVelocityAnalyzer(config)
    
    tx_data = {
        "merchant_id": "merch_burst_01",
        "transactions_last_5_minutes": 55,  # 55 transactions in 5 mins
        "average_transactions_per_hour": 12.0  # expected 5min = 1. Threshold is 5.0 * 1 = 5.
    }
    
    context = get_base_context(tx_data)
    res = analyzer.analyze(context)
    
    evidence_types = [ev["type"] for ev in res["evidence"]]
    assert "MerchantVelocitySpike" in evidence_types
    assert res["confidence_score"] <= 0.90

def test_refund_spike():
    """Verify daily refund counts exceeding thresholds trigger warning."""
    config = MerchantAgentConfig()
    analyzer = MerchantVelocityAnalyzer(config)
    
    tx_data = {
        "merchant_id": "merch_refunds_01",
        "refunds_last_day": 18  # threshold is 10
    }
    
    context = get_base_context(tx_data)
    res = analyzer.analyze(context)
    
    evidence_types = [ev["type"] for ev in res["evidence"]]
    assert "RefundSpikeDetected" in evidence_types
    assert "Temporarily limit transaction volume" in res["recommendations"]

def test_high_failure_rate():
    """Verify hourly failed transaction ratios trigger warnings."""
    config = MerchantAgentConfig()
    analyzer = MerchantVelocityAnalyzer(config)
    
    tx_data = {
        "merchant_id": "merch_failures_01",
        "failed_transactions_last_hour": 8,
        "successful_transactions_last_hour": 12  # failure rate = 8/20 = 40% (threshold is 20%)
    }
    
    context = get_base_context(tx_data)
    res = analyzer.analyze(context)
    
    evidence_types = [ev["type"] for ev in res["evidence"]]
    assert "HighFailedTransactionRate" in evidence_types
    assert "Increase monitoring" in res["recommendations"]

def test_rapid_growth_anomaly():
    """Verify rapid growth multiplier limits trigger warnings."""
    config = MerchantAgentConfig()
    analyzer = MerchantVelocityAnalyzer(config)
    
    tx_data = {
        "merchant_id": "merch_growth_01",
        "transactions_last_day": 1200,
        "average_transactions_per_day": 150.0  # 8x growth (threshold is 4x)
    }
    
    context = get_base_context(tx_data)
    res = analyzer.analyze(context)
    
    evidence_types = [ev["type"] for ev in res["evidence"]]
    assert "RapidMerchantGrowth" in evidence_types
