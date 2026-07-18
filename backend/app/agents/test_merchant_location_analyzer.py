import sys
import os

# Set pythonpath so we can import app modules correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.agents.models.investigation_context import InvestigationContext
from app.agents.investigators.merchant.config import MerchantAgentConfig
from app.agents.investigators.merchant.analyzers.merchant_location_analyzer import MerchantLocationAnalyzer

def get_base_context(transaction_data: dict) -> InvestigationContext:
    """Helper to instantiate a fresh mock InvestigationContext."""
    return InvestigationContext(
        investigation_id="INV-TEST-004",
        transaction_id="TX-TEST-004",
        transaction_data=transaction_data,
        prediction_result={},
        fraud_probability=0.0,
        risk_score=0,
        priority="LOW"
    )

def test_domestic_merchant():
    """Verify healthy, low-risk domestic location audits."""
    config = MerchantAgentConfig()
    analyzer = MerchantLocationAnalyzer(config)
    
    tx_data = {
        "merchant_id": "merch_domestic_01",
        "merchant_country": "US",
        "location_country": "US",
        "customer_country": "US",
        "customer_latitude": 40.7128,  # NY
        "customer_longitude": -74.0060,
        "merchant_latitude": 42.3601,  # Boston (~300 km)
        "merchant_longitude": -71.0589,
        "customer_timezone": -5.0,
        "merchant_timezone": -5.0
    }
    
    context = get_base_context(tx_data)
    res = analyzer.analyze(context)
    
    assert isinstance(res, dict)
    assert len(res["evidence"]) == 0
    assert res["confidence_score"] == 1.0
    assert "Enhanced monitoring" in res["recommendations"]

    # Legacy mode
    legacy_res = analyzer.analyze(tx_data)
    assert isinstance(legacy_res, list)
    assert len(legacy_res) == 0

def test_cross_border_merchant():
    """Verify cross-border mismatch country alert triggers."""
    config = MerchantAgentConfig()
    analyzer = MerchantLocationAnalyzer(config)
    
    tx_data = {
        "merchant_id": "merch_cross_01",
        "merchant_country": "CA",
        "location_country": "US",
        "customer_country": "US"
    }
    
    context = get_base_context(tx_data)
    res = analyzer.analyze(context)
    
    evidence_types = [ev["type"] for ev in res["evidence"]]
    assert "MerchantLocationMismatch" in evidence_types
    assert res["confidence_score"] <= 0.85

def test_merchant_in_sanctioned_region():
    """Verify sanctioned jurisdiction block and classification warnings."""
    config = MerchantAgentConfig()
    analyzer = MerchantLocationAnalyzer(config)
    
    tx_data = {
        "merchant_id": "merch_sanctioned_01",
        "merchant_country": "KP",
        "location_country": "KP"
    }
    
    context = get_base_context(tx_data)
    res = analyzer.analyze(context)
    
    evidence_types = [ev["type"] for ev in res["evidence"]]
    assert "SanctionedMerchantJurisdiction" in evidence_types
    assert "Block transaction" in res["recommendations"]
    assert res["confidence_score"] <= 0.1  # highly penalized

def test_merchant_outside_operating_region():
    """Verify operating regions constraints alert triggers."""
    config = MerchantAgentConfig()
    analyzer = MerchantLocationAnalyzer(config)
    
    tx_data = {
        "merchant_id": "merch_outside_01",
        "merchant_country": "US",
        "location_country": "GB",  # executing in GB
        "merchant_operating_regions": ["US", "CA"]  # but declared US, CA only
    }
    
    context = get_base_context(tx_data)
    res = analyzer.analyze(context)
    
    evidence_types = [ev["type"] for ev in res["evidence"]]
    assert "MerchantOutsideOperatingRegion" in evidence_types
    assert "Require additional verification" in res["recommendations"]

def test_merchant_with_timezone_inconsistency():
    """Verify timezone offset offset anomalies checks."""
    config = MerchantAgentConfig()
    analyzer = MerchantLocationAnalyzer(config)
    
    tx_data = {
        "merchant_id": "merch_tz_01",
        "merchant_country": "US",
        "location_country": "US",
        "customer_timezone": -5.0,  # EST
        "merchant_timezone": 4.0   # anomalous difference of 9 hours
    }
    
    context = get_base_context(tx_data)
    res = analyzer.analyze(context)
    
    evidence_types = [ev["type"] for ev in res["evidence"]]
    assert "TimezoneMismatch" in evidence_types
    assert res["confidence_score"] <= 0.90
