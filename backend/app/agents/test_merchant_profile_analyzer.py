import sys
import os
from datetime import datetime, date, timedelta

# Set pythonpath so we can import app modules correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.agents.models.investigation_context import InvestigationContext
from app.agents.investigators.merchant.config import MerchantAgentConfig
from app.agents.investigators.merchant.analyzers.merchant_profile_analyzer import MerchantProfileAnalyzer

def get_base_context(transaction_data: dict) -> InvestigationContext:
    """Helper to instantiate a fresh mock InvestigationContext."""
    return InvestigationContext(
        investigation_id="INV-TEST-001",
        transaction_id="TX-TEST-001",
        transaction_data=transaction_data,
        prediction_result={},
        fraud_probability=0.0,
        risk_score=0,
        priority="LOW"
    )

def test_normal_merchant():
    """Verify that a fully populated, verified, established, and active merchant generates no alerts."""
    config = MerchantAgentConfig()
    analyzer = MerchantProfileAnalyzer(config)
    
    profile = {
        "merchant_id": "merch_normal_01",
        "merchant_name": "Standard Retail Corp",
        "merchant_country": "US",
        "merchant_city": "New York",
        "merchant_registration_date": (date.today() - timedelta(days=365)).isoformat(),
        "merchant_category": "Apparel",
        "merchant_verified": True,
        "merchant_status": "ACTIVE",
        "merchant_type": "CORPORATION"
    }
    
    # Test InvestigationContext mode
    context = get_base_context(profile)
    res = analyzer.analyze(context)
    
    assert isinstance(res, dict)
    assert len(res["evidence"]) == 0
    assert res["confidence_score"] == 1.0
    assert "Verify merchant profile" in res["recommendations"]

    # Test legacy/dictionary mode
    legacy_res = analyzer.analyze(profile)
    assert isinstance(legacy_res, list)
    assert len(legacy_res) == 0

def test_new_merchant():
    """Verify recently registered merchant profile flag."""
    config = MerchantAgentConfig()
    analyzer = MerchantProfileAnalyzer(config)
    
    profile = {
        "merchant_id": "merch_new_01",
        "merchant_name": "New Shop",
        "merchant_country": "CA",
        "merchant_registration_date": (date.today() - timedelta(days=10)).isoformat(),
        "merchant_category": "electronics",
        "merchant_verified": True,
        "merchant_status": "ACTIVE",
        "merchant_type": "SOLE_PROPRIETORSHIP"
    }
    
    context = get_base_context(profile)
    res = analyzer.analyze(context)
    
    evidence_types = [ev["type"] for ev in res["evidence"]]
    assert "NewMerchantProfile" in evidence_types
    assert "HighRiskMerchantCategory" in evidence_types
    assert "Review merchant onboarding" in res["recommendations"]

def test_unverified_merchant():
    """Verify unverified status flags."""
    config = MerchantAgentConfig()
    analyzer = MerchantProfileAnalyzer(config)
    
    profile = {
        "merchant_id": "merch_unverified_01",
        "merchant_name": "Unverified Shop",
        "merchant_country": "US",
        "merchant_registration_date": (date.today() - timedelta(days=100)).isoformat(),
        "merchant_category": "Apparel",
        "merchant_verified": False,
        "merchant_status": "ACTIVE",
        "merchant_type": "SOLE_PROPRIETORSHIP"
    }
    
    context = get_base_context(profile)
    res = analyzer.analyze(context)
    
    evidence_types = [ev["type"] for ev in res["evidence"]]
    assert "UnverifiedMerchantProfile" in evidence_types
    assert "Require additional KYC" in res["recommendations"]
    assert res["confidence_score"] < 0.6  # confidence should be penalized due to verification status

def test_incomplete_merchant():
    """Verify completeness checks for missing fields."""
    config = MerchantAgentConfig()
    analyzer = MerchantProfileAnalyzer(config)
    
    # Missing required field 'merchant_country' and important field 'merchant_category'
    profile = {
        "merchant_id": "merch_incomplete_01",
        "merchant_name": "Half Shop",
        "merchant_registration_date": (date.today() - timedelta(days=200)).isoformat(),
        "merchant_verified": True,
        "merchant_status": "ACTIVE",
        "merchant_type": "SOLE_PROPRIETORSHIP"
    }
    
    context = get_base_context(profile)
    res = analyzer.analyze(context)
    
    evidence_types = [ev["type"] for ev in res["evidence"]]
    assert "MissingRequiredMerchantFields" in evidence_types
    assert "MissingImportantMerchantFields" in evidence_types
    assert "merchant_country" in res["metadata"]["missing_required"]
    assert "merchant_category" in res["metadata"]["missing_important"]

def test_inactive_and_inconsistent_merchant():
    """Verify status checks, country inconsistency, and business type inconsistency."""
    config = MerchantAgentConfig()
    analyzer = MerchantProfileAnalyzer(config)
    
    profile = {
        "merchant_id": "merch_inconsistent_01",
        "merchant_name": "Suspicious Sole-Proprietorship Exchange",
        "merchant_country": "US",  # Registry is US
        "merchant_registration_date": (date.today() - timedelta(days=50)).isoformat(),
        "merchant_category": "crypto_exchange",  # High-risk
        "merchant_verified": True,
        "merchant_status": "SUSPENDED",  # Inactive
        "merchant_type": "SOLE_PROPRIETORSHIP",  # Sole-proprietorship operating crypto exchange
        "location_country": "CA"  # Transaction country is CA (not US)
    }
    
    context = get_base_context(profile)
    res = analyzer.analyze(context)
    
    evidence_types = [ev["type"] for ev in res["evidence"]]
    assert "InactiveMerchantStatus" in evidence_types
    assert "CountryInconsistency" in evidence_types
    assert "BusinessTypeInconsistency" in evidence_types
    assert "HighRiskMerchantCategory" in evidence_types
    
    assert "Manual verification" in res["recommendations"]
    assert res["confidence_score"] <= 0.3  # confidence penalized by active status checks
