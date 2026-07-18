import sys
import os
from unittest.mock import MagicMock, patch

# Set pythonpath so we can import app modules correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.agents.models.investigation_context import InvestigationContext
from app.agents.investigators.merchant.config import MerchantAgentConfig
from app.agents.investigators.merchant.merchant_agent import MerchantInvestigationAgent

def get_valid_context() -> InvestigationContext:
    """Helper to instantiate a valid, comprehensive mock InvestigationContext."""
    return InvestigationContext(
        investigation_id="INV-INT-001",
        transaction_id="TX-INT-001",
        transaction_data={
            "merchant_id": "MERCH_SAFE_01",
            "merchant_name": "Trusted Store",
            "merchant_country": "US",
            "location_country": "US",
            "customer_country": "US",
            "merchant_category": "grocery",
            "merchant_verified": True,
            "merchant_status": "ACTIVE",
            "amount": 25.0
        },
        prediction_result={"prediction": "Legitimate", "probability": 0.05},
        fraud_probability=0.0,
        risk_score=0,
        priority="LOW"
    )

def test_merchant_agent_all_success():
    """Verify flow when all analyzers execute successfully."""
    config = MerchantAgentConfig()
    agent = MerchantInvestigationAgent(config=config)
    
    # Confirm health check passes
    assert agent.health_check() is True
    
    context = get_valid_context()
    result = agent.execute(context)
    
    assert result.status == "SUCCESS"
    stats = result.metadata["execution_statistics"]
    assert len(stats["successful_analyzers"]) == 6
    assert len(stats["failed_analyzers"]) == 0
    assert len(stats["skipped_analyzers"]) == 0
    assert 0.9 < result.confidence_score <= 1.0

def test_merchant_agent_one_fails():
    """Verify that a single sub-analyzer failure does not halt pipeline execution, returning partial success."""
    config = MerchantAgentConfig()
    agent = MerchantInvestigationAgent(config=config)
    
    # Mock category analyzer to raise an error
    agent.category_analyzer.analyze = MagicMock(side_effect=Exception("Critical Category Provider Timeout"))
    
    context = get_valid_context()
    result = agent.execute(context)
    
    assert result.status == "PARTIAL_SUCCESS"
    stats = result.metadata["execution_statistics"]
    assert "Category" in stats["failed_analyzers"]
    assert "Profile" in stats["successful_analyzers"]
    
    # Check for AnalyzerError in evidence list
    evidence_types = [ev["type"] for ev in result.evidence]
    assert "AnalyzerError" in evidence_types
    assert "Escalate investigation" in result.recommendations

def test_merchant_agent_disabled_analyzers():
    """Verify that skipped/disabled analyzers do not execute and are logged accordingly."""
    config = MerchantAgentConfig(
        enable_velocity=False,
        enable_reputation=False
    )
    agent = MerchantInvestigationAgent(config=config)
    
    context = get_valid_context()
    result = agent.execute(context)
    
    assert result.status == "SUCCESS"
    stats = result.metadata["execution_statistics"]
    assert "Velocity" in stats["skipped_analyzers"]
    assert "Reputation" in stats["skipped_analyzers"]
    assert len(stats["successful_analyzers"]) == 4
