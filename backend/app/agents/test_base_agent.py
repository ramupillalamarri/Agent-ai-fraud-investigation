import sys
import os
import logging
from typing import Dict, Any, List

# Set pythonpath so we can import app modules correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Configure base logging to print to stdout so we can verify logs are outputted
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s")

from app.agents.base.base_agent import BaseAgent
from app.agents.models.investigation_context import InvestigationContext
from app.agents.models.agent_result import AgentResult

# 1. Define concrete subclass DummyAgent to test BaseAgent implementation contracts
class DummyAgent(BaseAgent):
    """A minimal mock implementation of BaseAgent for testing execution lifecycles."""
    
    def validate(self, context: InvestigationContext) -> None:
        """Validate input payload properties."""
        if context.transaction_data.get("amount", 0) <= 0:
            raise ValueError("Transaction amount must be positive.")
            
    def health_check(self) -> bool:
        """Indicate component health status."""
        return True
        
    def _execute(self, context: InvestigationContext) -> AgentResult:
        """Execute core business checks and return result."""
        # Log via utility method helper
        self.log_info("DummyAgent processing transaction id: %s", context.transaction_id)
        
        # Access context values
        amount = context.transaction_data.get("amount", 0)
        findings = [f"Transaction amount of ${amount} is under verification limits."]
        recs = ["No flags raised by DummyAgent."]
        
        # Mock evidence collection
        evidence = [{"inspected_amount": amount, "status": "verified"}]
        context.add_evidence(self.agent_name, "Inspected amount verify bounds", evidence)
        
        # Update context shared memory
        context.update_shared_memory("dummy_checked", True)
        
        return self.create_success_result(
            findings=findings,
            recommendations=recs,
            evidence=evidence,
            confidence_score=0.98
        )

def run_test():
    print("=== Testing Abstract BaseAgent and Lifecycle ===")
    
    # 2. Setup Context
    context = InvestigationContext(
        investigation_id="INV-00123",
        transaction_id="TX_9999",
        transaction_data={"amount": 450.0},
        prediction_result={"probability": 0.05, "prediction": "Legitimate"},
        fraud_probability=0.05,
        risk_score=5,
        priority="LOW"
    )
    
    # 3. Instantiate DummyAgent
    agent = DummyAgent(
        agent_id="dummy-agent-01",
        agent_name="DummyAgent",
        description="A verification agent to validate BaseAgent lifecycles",
        version="1.0.0",
        execution_priority=1
    )
    
    # Verify properties
    print(f"Agent ID: {agent.agent_id}")
    print(f"Agent Name: {agent.agent_name}")
    print(f"Priority: {agent.execution_priority}")
    print(f"Health Check Status: {agent.health_check()}")
    
    # 4. Execute Lifecycle
    print("\nExecuting agent...")
    result = agent.execute(context)
    
    # 5. Assertions and print outputs
    print("\nExecution Complete. Validating outputs:")
    print(f"Execution Status: {result.status}")
    print(f"Execution Time: {result.execution_time_ms} ms")
    print(f"Findings: {result.findings}")
    print(f"Recommendations: {result.recommendations}")
    print(f"Context Executed Agents: {context.executed_agents}")
    print(f"Context Shared Memory: {context.shared_memory}")
    
    # 6. Test Context Validation Error Path
    print("\nTesting context validation error handling...")
    invalid_context = InvestigationContext(
        investigation_id="INV-00123",
        transaction_id="TX_9999",
        transaction_data={"amount": -10.0},  # Triggers ValueError
        prediction_result={"probability": 0.05, "prediction": "Legitimate"},
        fraud_probability=0.05,
        risk_score=5,
        priority="LOW"
    )
    fail_result = agent.execute(invalid_context)
    print(f"Validation Fail Status: {fail_result.status}")
    print(f"Validation Fail Error: {fail_result.metadata.get('error_message')}")
    
    print("\n=== BaseAgent Verification Succeeded! ===")

if __name__ == "__main__":
    run_test()
