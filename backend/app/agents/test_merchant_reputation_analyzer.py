import sys
import os

# Set pythonpath so we can import app modules correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.agents.models.investigation_context import InvestigationContext
from app.agents.investigators.merchant.config import MerchantAgentConfig
from app.agents.investigators.merchant.analyzers.merchant_reputation_analyzer import MerchantReputationAnalyzer

def get_base_context(transaction_data: dict) -> InvestigationContext:
    """Helper to instantiate a fresh mock InvestigationContext."""
    return InvestigationContext(
        investigation_id="INV-TEST-006",
        transaction_id="TX-TEST-006",
        transaction_data=transaction_data,
        prediction_result={},
        fraud_probability=0.0,
        risk_score=0,
        priority="LOW"
    )

def test_trusted_merchant():
    """Verify whitelisted / trusted merchant exemption checks."""
    config = MerchantAgentConfig()
    analyzer = MerchantReputationAnalyzer(config)
    
    tx_data = {
        "merchant_id": "MERCH_SAFE_01",
        "merchant_whitelisted": True,
        "merchant_trust_score": 0.95
    }
    
    context = get_base_context(tx_data)
    res = analyzer.analyze(context)
    
    assert isinstance(res, dict)
    evidence_types = [ev["type"] for ev in res["evidence"]]
    assert "WhitelistedMerchantExemption" in evidence_types
    assert res["confidence_score"] == 1.0
    assert "Approve merchant" in res["recommendations"]

    # Legacy mode
    legacy_res = analyzer.analyze(tx_data)
    assert isinstance(legacy_res, list)
    assert len(legacy_res) > 0

def test_blacklisted_merchant():
    """Verify system blacklist matches block and flag warnings."""
    config = MerchantAgentConfig()
    analyzer = MerchantReputationAnalyzer(config)
    
    tx_data = {
        "merchant_id": "MERCH_FRAUD_99",
        "merchant_blacklisted": True
    }
    
    context = get_base_context(tx_data)
    res = analyzer.analyze(context)
    
    evidence_types = [ev["type"] for ev in res["evidence"]]
    assert "BlacklistedMerchant" in evidence_types
    assert "Suspend merchant" in res["recommendations"]
    assert res["confidence_score"] <= 0.1

def test_watchlisted_merchant():
    """Verify watchlist match alert triggers."""
    config = MerchantAgentConfig()
    analyzer = MerchantReputationAnalyzer(config)
    
    tx_data = {
        "merchant_id": "MERCH_WATCH_01",
        "merchant_watchlisted": True
    }
    
    context = get_base_context(tx_data)
    res = analyzer.analyze(context)
    
    evidence_types = [ev["type"] for ev in res["evidence"]]
    assert "WatchlistedMerchant" in evidence_types
    assert "Manual compliance review" in res["recommendations"]
    assert res["confidence_score"] <= 0.60

def test_compliance_violations_merchant():
    """Verify compliance status failure triggers warning."""
    config = MerchantAgentConfig()
    analyzer = MerchantReputationAnalyzer(config)
    
    tx_data = {
        "merchant_id": "merch_noncompliant_01",
        "merchant_compliance_status": "NON_COMPLIANT"
    }
    
    context = get_base_context(tx_data)
    res = analyzer.analyze(context)
    
    evidence_types = [ev["type"] for ev in res["evidence"]]
    assert "RegulatoryComplianceViolation" in evidence_types
    assert "Manual compliance review" in res["recommendations"]

def test_under_investigation_merchant():
    """Verify prior investigations flag triggers."""
    config = MerchantAgentConfig()
    analyzer = MerchantReputationAnalyzer(config)
    
    tx_data = {
        "merchant_id": "merch_investigated_01",
        "merchant_previous_investigations": 4
    }
    
    context = get_base_context(tx_data)
    res = analyzer.analyze(context)
    
    evidence_types = [ev["type"] for ev in res["evidence"]]
    assert "PreviousFraudInvolvement" in evidence_types

def test_sanctions_match_merchant():
    """Verify critical sanctions mismatch flags block transaction."""
    config = MerchantAgentConfig()
    analyzer = MerchantReputationAnalyzer(config)
    
    tx_data = {
        "merchant_id": "merch_sanctioned_entity_01",
        "merchant_sanctions_match": True
    }
    
    context = get_base_context(tx_data)
    res = analyzer.analyze(context)
    
    evidence_types = [ev["type"] for ev in res["evidence"]]
    assert "SanctionsRegistryMatch" in evidence_types
    assert "Suspend merchant" in res["recommendations"]
    assert res["confidence_score"] <= 0.1
