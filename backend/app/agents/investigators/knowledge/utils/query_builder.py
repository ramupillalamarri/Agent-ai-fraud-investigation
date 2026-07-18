import logging
from typing import Dict, Any, List
from app.agents.models.investigation_context import InvestigationContext

logger = logging.getLogger("app.agents.investigators.knowledge.utils.query_builder")

class QueryBuilder:
    """Builds search queries dynamically from InvestigationContext, including transaction attributes and child agent findings."""

    def build_queries(self, context: InvestigationContext) -> List[str]:
        """Constructs search query strings target-tailored to matching compliance rules or playbooks."""
        queries = []

        # 1. Base query from transaction amount and priority
        tx_data = context.transaction_data or {}
        amount = tx_data.get("amount", 0.0)
        currency = tx_data.get("currency", "USD")
        category = tx_data.get("category", "")
        
        base_query = f"Verify rules for transaction amount {amount} {currency} in business category {category}."
        queries.append(base_query.strip())

        # 2. Add queries from child agent findings inside context evidence
        for evidence in context.collected_evidence:
            agent = evidence.get("agent_name", "")
            finding = evidence.get("key_finding", "")
            details = str(evidence.get("details", ""))
            
            if "Merchant" in agent or "merchant" in agent.lower():
                queries.append(f"Merchant risk guidelines: {finding}. {details}")
            elif "Customer" in agent or "customer" in agent.lower():
                queries.append(f"Customer verification procedures: {finding}. {details}")
            elif "Device" in agent or "device" in agent.lower():
                queries.append(f"Device fingerprint anomalies: {finding}. {details}")
            elif "Network" in agent or "network" in agent.lower():
                queries.append(f"IP address proxy velocity: {finding}. {details}")

        # Remove empty items or duplicates
        unique_queries = list(dict.fromkeys(q.strip() for q in queries if q.strip()))
        
        logger.info("Generated %d search queries from investigation context", len(unique_queries))
        return unique_queries
export_builder = QueryBuilder
