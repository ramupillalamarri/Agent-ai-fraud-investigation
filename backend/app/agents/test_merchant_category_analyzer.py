import sys
import os

# Set pythonpath so we can import app modules correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.agents.models.investigation_context import InvestigationContext
from app.agents.investigators.merchant.config import MerchantAgentConfig
from app.agents.investigators.merchant.analyzers.merchant_category_analyzer import MerchantCategoryAnalyzer

def get_base_context(transaction_data: dict, history: list = None) -> InvestigationContext:
    """Helper to instantiate a fresh mock InvestigationContext with optional history."""
    ctx = InvestigationContext(
        investigation_id="INV-TEST-003",
        transaction_id="TX-TEST-003",
        transaction_data=transaction_data,
        prediction_result={},
        fraud_probability=0.0,
        risk_score=0,
        priority="LOW"
    )
    if history:
        ctx.update_shared_memory("customer_history", history)
    return ctx

def test_normal_grocery_merchant():
    """Verify healthy, low-risk category checks (grocery)."""
    config = MerchantAgentConfig()
    analyzer = MerchantCategoryAnalyzer(config)
    
    tx_data = {
        "category": "grocery",
        "amount": 45.0,
        "merchant_country": "US",
        "location_country": "US"
    }
    history = [{"category": "grocery", "status": "SUCCESS"}]
    
    context = get_base_context(tx_data, history)
    res = analyzer.analyze(context)
    
    assert isinstance(res, dict)
    assert len(res["evidence"]) == 0
    assert res["confidence_score"] == 1.0

def test_travel_merchant():
    """Verify medium-risk category classification (travel)."""
    config = MerchantAgentConfig()
    analyzer = MerchantCategoryAnalyzer(config)
    
    tx_data = {
        "category": "travel",
        "amount": 1500.0,  # below typical 3000 norm
        "merchant_country": "US",
        "location_country": "US"
    }
    
    context = get_base_context(tx_data)
    res = analyzer.analyze(context)
    
    evidence_types = [ev["type"] for ev in res["evidence"]]
    assert "MediumRiskMerchantCategory" in evidence_types
    assert res["confidence_score"] <= 0.75

def test_crypto_exchange_merchant():
    """Verify high-risk category, amount norm limit, and cross-border risk flags."""
    config = MerchantAgentConfig()
    analyzer = MerchantCategoryAnalyzer(config)
    
    tx_data = {
        "category": "crypto_exchange",
        "amount": 1500.0,  # abovetypical 1000 limit
        "merchant_country": "CA",
        "location_country": "US"  # cross-border mismatch
    }
    
    context = get_base_context(tx_data)
    res = analyzer.analyze(context)
    
    evidence_types = [ev["type"] for ev in res["evidence"]]
    assert "HighRiskMerchantCategory" in evidence_types
    assert "AbnormalCategoryAmount" in evidence_types
    assert "CrossBorderCategoryRisk" in evidence_types
    assert res["confidence_score"] < 0.4  # trust heavily reduced

def test_gift_card_seller():
    """Verify high-risk category for gift_cards."""
    config = MerchantAgentConfig()
    analyzer = MerchantCategoryAnalyzer(config)
    
    tx_data = {
        "category": "gift_cards",
        "amount": 100.0
    }
    
    context = get_base_context(tx_data)
    res = analyzer.analyze(context)
    
    evidence_types = [ev["type"] for ev in res["evidence"]]
    assert "HighRiskMerchantCategory" in evidence_types

def test_online_gaming_platform():
    """Verify high-risk category for gaming."""
    config = MerchantAgentConfig()
    analyzer = MerchantCategoryAnalyzer(config)
    
    tx_data = {
        "category": "gaming",
        "amount": 50.0
    }
    
    context = get_base_context(tx_data)
    res = analyzer.analyze(context)
    
    evidence_types = [ev["type"] for ev in res["evidence"]]
    assert "HighRiskMerchantCategory" in evidence_types

def test_marketplace_seller():
    """Verify medium-risk category for marketplace."""
    config = MerchantAgentConfig()
    analyzer = MerchantCategoryAnalyzer(config)
    
    tx_data = {
        "category": "marketplace",
        "amount": 120.0
    }
    
    context = get_base_context(tx_data)
    res = analyzer.analyze(context)
    
    evidence_types = [ev["type"] for ev in res["evidence"]]
    assert "MediumRiskMerchantCategory" in evidence_types
