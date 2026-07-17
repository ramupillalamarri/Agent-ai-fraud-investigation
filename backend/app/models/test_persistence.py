import asyncio
import sys
import os
from datetime import datetime

# Setup PYTHONPATH so we can resolve backend packages
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.investigation import Investigation
from app.models.agent_result import AgentResult
from app.models.evidence import Evidence
from app.models.recommendation import Recommendation
from app.models.investigation_timeline import InvestigationTimeline

async def verify_persistence_layer():
    print("=== Verifying Async SQLAlchemy 2.0 Persistence Layer ===")
    
    # 1. Initialize In-Memory SQLite Engine
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    # Create all tables defined in metadata (including newly registered investigation models)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("1. In-memory schema initialized successfully.")

    # 2. Configure SessionMaker
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # 3. Create Investigation
        investigation = Investigation(
            transaction_id="TX-10022",
            status="PENDING",
            priority="HIGH",
            fraud_probability=0.88,
            risk_score=90,
            overall_confidence=0.92,
            additional_metadata={"source": "Real-time Gateway"}
        )
        session.add(investigation)
        await session.flush()  # Populates UUIDs
        
        investigation_id = investigation.id
        print(f"2. Investigation created. ID: {investigation_id}")

        # 4. Create AgentResult
        agent_result = AgentResult(
            investigation_id=investigation_id,
            agent_name="NetworkRiskAgent",
            status="SUCCESS",
            confidence_score=0.95,
            execution_time_ms=250,
            additional_metadata={"rule_version": "1.0.0"}
        )
        session.add(agent_result)
        await session.flush()
        
        agent_result_id = agent_result.id
        print(f"3. AgentResult created. ID: {agent_result_id}")

        # 5. Create Evidence
        evidence = Evidence(
            investigation_id=investigation_id,
            agent_result_id=agent_result_id,
            type="SharedIP",
            severity="HIGH",
            confidence=0.95,
            description="IP shared across 5 accounts",
            source="IPRelationshipAnalyzer"
        )
        session.add(evidence)
        await session.flush()
        print(f"4. Evidence created. ID: {evidence.id}")

        # 6. Create Recommendation and Timeline events
        rec = Recommendation(
            investigation_id=investigation_id,
            recommendation="Freeze related accounts",
            priority="HIGH",
            generated_by="NetworkRiskAgent",
            status="PENDING"
        )
        timeline = InvestigationTimeline(
            investigation_id=investigation_id,
            event_type="AGENT_EXECUTION_COMPLETED",
            event_description="NetworkRiskAgent execution finished reporting 1 high alert.",
            agent_name="NetworkRiskAgent"
        )
        session.add_all([rec, timeline])
        await session.commit()
        print("5. Recommendation and Timeline events committed.")

    # 7. Query and Verify Relationships & Cascades
    async with async_session() as session:
        # Load the investigation and verify relations
        q = await session.get(Investigation, investigation_id)
        assert q is not None
        print(f"\nVerifying relations for Transaction ID: {q.transaction_id}")
        
        print(f"  * Associated Agent Results count: {len(q.agent_results)}")
        assert len(q.agent_results) == 1
        assert q.agent_results[0].agent_name == "NetworkRiskAgent"
        
        print(f"  * Associated Evidence count: {len(q.evidence)}")
        assert len(q.evidence) == 1
        assert q.evidence[0].type == "SharedIP"
        assert q.evidence[0].agent_result_id == agent_result_id
        
        print(f"  * Associated Recommendations count: {len(q.recommendations)}")
        assert len(q.recommendations) == 1
        
        print(f"  * Associated Timeline events count: {len(q.timeline)}")
        assert len(q.timeline) == 1

        # Test Cascade Delete
        print("\n6. Triggering Cascade Delete...")
        await session.delete(q)
        await session.commit()
        
        # Verify children are deleted from database
        check_ar = await session.get(AgentResult, agent_result_id)
        check_ev = await session.get(Evidence, evidence.id)
        check_rec = await session.get(Recommendation, rec.id)
        check_tl = await session.get(InvestigationTimeline, timeline.id)
        
        assert check_ar is None
        assert check_ev is None
        assert check_rec is None
        assert check_tl is None
        
        print("  * Verification Succeeded: Cascade deletes verified successfully.")

    print("\n=== All Persistence Layer Tests Passed! ===")

if __name__ == "__main__":
    asyncio.run(verify_persistence_layer())
