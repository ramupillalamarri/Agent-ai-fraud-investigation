import asyncio
import sys
import os
from datetime import datetime, timezone
import uuid

# Setup PYTHONPATH so we can resolve backend packages
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.investigation import Investigation
from app.models.agent_result import AgentResult
from app.models.evidence import Evidence
from app.models.recommendation import Recommendation
from app.models.timeline_event import TimelineEvent

from app.repositories.investigation_repository import InvestigationRepository
from app.repositories.agent_result_repository import AgentResultRepository
from app.repositories.evidence_repository import EvidenceRepository
from app.repositories.recommendation_repository import RecommendationRepository
from app.repositories.timeline_repository import TimelineRepository

import pytest

@pytest.mark.asyncio
async def test_all_repositories():
    print("=== Testing Async SQLAlchemy 2.0 Repositories ===")
    
    # 1. Initialize In-Memory SQLite Engine
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("1. In-memory schema initialized.")

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Create Repository instances
        inv_repo = InvestigationRepository(session)
        ar_repo = AgentResultRepository(session)
        ev_repo = EvidenceRepository(session)
        rec_repo = RecommendationRepository(session)
        tl_repo = TimelineRepository(session)

        # 2. Test InvestigationRepository.create()
        inv = Investigation(
            transaction_id="TX_REP_99",
            status="PENDING",
            priority="HIGH",
            fraud_probability=0.75,
            risk_score=80,
            overall_confidence=0.85
        )
        inv = await inv_repo.create(inv)
        inv_id = inv.id
        print(f"2. Created Investigation: ID={inv_id}, Case={inv.case_number}")

        # 3. Test AgentResultRepository.create()
        ar = AgentResult(
            investigation_id=inv_id,
            agent_name="NetworkRiskAgent",
            status="SUCCESS",
            confidence_score=0.9,
            execution_time_ms=120,
            summary="Checked related transactions."
        )
        ar = await ar_repo.create(ar)
        ar_id = ar.id
        print(f"3. Created AgentResult: ID={ar_id}")

        # 4. Test EvidenceRepository.create()
        ev = Evidence(
            investigation_id=inv_id,
            agent_result_id=ar_id,
            type="SharedDevice",
            severity="HIGH",
            confidence=0.9,
            title="Shared Hardware ID",
            description="Same hardware signature used across 3 separate client accounts.",
            source="DeviceInvestigationAgent"
        )
        ev = await ev_repo.create(ev)
        print(f"4. Created Evidence: ID={ev.id}")

        # 5. Test RecommendationRepository.create()
        rec = Recommendation(
            investigation_id=inv_id,
            title="Block Device",
            description="Add this device to blacklist",
            priority="HIGH",
            generated_by="DeviceInvestigationAgent",
            status="PENDING"
        )
        rec = await rec_repo.create(rec)
        print(f"5. Created Recommendation: ID={rec.id}")

        # 6. Test TimelineRepository.create()
        tl = TimelineEvent(
            investigation_id=inv_id,
            event_type="CUSTOMER_AGENT",
            title="Customer Profile Analysis",
            description="Analyzed account registry records and billing mismatch parameters.",
            status="SUCCESS",
            duration_ms=45
        )
        tl = await tl_repo.create(tl)
        print(f"6. Created TimelineEvent: ID={tl.id}")

    # 7. Test Retrieval, Filtering, and Listing
    async with async_session() as session:
        inv_repo = InvestigationRepository(session)
        ar_repo = AgentResultRepository(session)
        ev_repo = EvidenceRepository(session)
        rec_repo = RecommendationRepository(session)
        tl_repo = TimelineRepository(session)

        # Get Investigation
        loaded_inv = await inv_repo.get(inv_id)
        assert loaded_inv is not None
        print("7. Retrieved investigation record successfully.")
        
        # Test get_by_case_number
        by_case = await inv_repo.get_by_case_number(loaded_inv.case_number)
        assert by_case is not None
        assert by_case.id == inv_id
        
        # Test get_by_transaction
        by_tx = await inv_repo.get_by_transaction("TX_REP_99")
        assert by_tx is not None
        assert by_tx.id == inv_id

        # Test list_by_investigation in child repositories
        ar_list = await ar_repo.list_by_investigation(inv_id)
        assert len(ar_list) == 1
        assert ar_list[0].agent_name == "NetworkRiskAgent"
        print("  * AgentResults listed successfully.")

        ev_list = await ev_repo.list_by_investigation(inv_id)
        assert len(ev_list) == 1
        assert ev_list[0].type == "SharedDevice"
        print("  * Evidence listed successfully.")

        ev_by_agent = await ev_repo.list_by_agent(ar_id)
        assert len(ev_by_agent) == 1

        ev_by_sev = await ev_repo.list_by_severity("HIGH")
        assert len(ev_by_sev) == 1

        rec_list = await rec_repo.list_by_investigation(inv_id)
        assert len(rec_list) == 1
        assert rec_list[0].description == "Add this device to blacklist"
        print("  * Recommendations listed successfully.")

        tl_list = await tl_repo.list_by_investigation(inv_id)
        assert len(tl_list) == 1
        assert tl_list[0].event_type == "CUSTOMER_AGENT"
        print("  * TimelineEvents listed successfully.")

        # Test filter, pagination, sorting in list()
        items, count = await inv_repo.list(status="PENDING", priority="HIGH", page=1, page_size=10)
        assert count == 1
        assert items[0].id == inv_id

        # Test search
        search_items, search_count = await inv_repo.search("TX_REP")
        assert search_count == 1
        assert search_items[0].id == inv_id
        print("8. Search & filter queries ran successfully.")

        # Test Soft Delete
        await inv_repo.soft_delete(inv_id)
        deleted_inv = await inv_repo.get(inv_id)
        assert deleted_inv.status == "DELETED"
        print("9. Soft Delete test succeeded.")

        # Test Cascade Delete
        await inv_repo.delete(inv_id)
        check_deleted = await inv_repo.get(inv_id)
        assert check_deleted is None

        # Verify children deleted
        assert len(await ar_repo.list_by_investigation(inv_id)) == 0
        assert len(await ev_repo.list_by_investigation(inv_id)) == 0
        assert len(await rec_repo.list_by_investigation(inv_id)) == 0
        assert len(await tl_repo.list_by_investigation(inv_id)) == 0
        print("10. Hard Delete & Cascades tests succeeded.")

    print("=== All Repository Tests Passed Successfully! ===")

if __name__ == "__main__":
    asyncio.run(test_all_repositories())
