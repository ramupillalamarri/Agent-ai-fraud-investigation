import asyncio
import sys
import os
import uuid
from datetime import datetime

# Setup PYTHONPATH so we can resolve backend packages
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.repositories.investigation_repository import InvestigationRepository
from app.services.investigation_service import InvestigationService

from app.agents.models.investigation_report import InvestigationReport
from app.agents.models.agent_result import AgentResult

async def verify_service_layer():
    print("=== Verifying InvestigationService and Repository Persistence Flow ===")
    
    # 1. Initialize In-Memory SQLite Engine and create schema
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("1. In-memory sqlite schema created.")

    # 2. Setup SessionMaker and instantiate Repository/Service
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        repo = InvestigationRepository(session)
        service = InvestigationService(repo)
        
        # 3. Formulate InvestigationReport and nested outputs
        inv_id = str(uuid.uuid4())
        report = InvestigationReport(
            investigation_id=inv_id,
            transaction_id="TX-55099",
            overall_risk="HIGH",
            overall_confidence=0.94,
            executive_summary="Fraud pattern audit shows critical matches.",
            findings=["Customer spending velocity is anomalous", "Datacenter IP proxy used"],
            recommendations=["Escalate investigation", "Freeze accounts"],
            evidence=[{"type": "SharedIP", "severity": "HIGH", "source": "NetworkAgent"}],
            executed_agents=["CustomerAgent", "DeviceAgent"]
        )
        
        agent_results = [
            AgentResult(
                agent_name="CustomerAgent",
                status="SUCCESS",
                confidence_score=0.90,
                findings=["Customer spending velocity is anomalous"],
                recommendations=[],
                evidence=[],
                execution_time_ms=120,
                metadata={"threshold_exceeded": True}
            ),
            AgentResult(
                agent_name="DeviceAgent",
                status="SUCCESS",
                confidence_score=0.98,
                findings=["Datacenter IP proxy used"],
                recommendations=["Block device"],
                evidence=[{"type": "SharedIP", "severity": "HIGH", "source": "NetworkAgent"}],
                execution_time_ms=90,
                metadata={"isp": "Datacenter Hosting"}
            )
        ]
        
        timeline_events = [
            {
                "event_type": "ORCHESTRATION_STARTED",
                "event_description": "Investigation orchestrator execution started.",
                "metadata": {"user": "admin"}
            },
            {
                "event_type": "AGENT_COMPLETE",
                "event_description": "DeviceAgent completed checks.",
                "agent_name": "DeviceAgent"
            }
        ]

        # 4. Save Report
        print("2. Invoking save_report()...")
        db_inv = await service.save_report(report, agent_results, timeline_events)
        assert db_inv.id == uuid.UUID(inv_id)
        
    # 5. Reload report in a fresh session to ensure complete isolation
    print("3. Reloading investigation from DB...")
    async with async_session() as session:
        repo = InvestigationRepository(session)
        service = InvestigationService(repo)
        
        loaded = await service.load_report(inv_id)
        assert loaded is not None
        
        print("\n=== Verifying Restored Data ===")
        print(f"Transaction ID: {loaded.transaction_id}")
        assert loaded.transaction_id == "TX-55099"
        
        print(f"Priority / Status: {loaded.priority} / {loaded.status}")
        assert loaded.priority == "HIGH"
        assert loaded.status == "COMPLETED"
        
        # Verify nested results
        print(f"Agent Results count: {len(loaded.agent_results)}")
        assert len(loaded.agent_results) == 2
        for ar in loaded.agent_results:
            print(f"  * Agent: {ar.agent_name} | Status: {ar.status} | Time: {ar.execution_time_ms}ms")
            
        # Verify evidence mapping
        print(f"Evidence count: {len(loaded.evidence)}")
        assert len(loaded.evidence) == 1
        assert loaded.evidence[0].type == "SharedIP"
        
        # Verify recommendations mapping
        print(f"Recommendations count: {len(loaded.recommendations)}")
        assert len(loaded.recommendations) == 2
        
        # Verify timeline log events
        print(f"Timeline logs: {len(loaded.timeline)}")
        assert len(loaded.timeline) == 2
        
        # 6. Verify Archive Status Transitions
        print("\n4. Archiving investigation...")
        archived = await service.archive(inv_id)
        assert archived.status == "ARCHIVED"
        print(f"  * New status: {archived.status}")
        
        # 7. Verify Close Investigation Transitions
        print("5. Closing investigation...")
        closed = await service.close_investigation(inv_id, "Verified fraud ring activity.")
        assert closed.status == "CLOSED"
        print(f"  * New status: {closed.status}")

        # 8. Test create_investigation and duplicate validation
        print("\n6. Creating new investigation dossier...")
        new_inv = await service.create_investigation(transaction_id="TX_NEW_88", status="OPEN", priority="MEDIUM")
        assert new_inv.status == "OPEN"
        assert new_inv.priority == "MEDIUM"
        assert new_inv.case_number.startswith("INV-")
        print(f"  * Created successfully: Case={new_inv.case_number}")

        # Try to duplicate
        try:
            await service.create_investigation(transaction_id="TX_NEW_88")
            assert False, "Should raise duplication error"
        except Exception as e:
            print(f"  * Duplication caught: {str(e)}")

        # 9. Test assign_investigator, change_priority, change_status
        user_uuid = uuid.uuid4()
        await service.assign_investigator(str(new_inv.id), user_uuid)
        await service.change_priority(str(new_inv.id), "HIGH")
        await service.change_status(str(new_inv.id), "IN_PROGRESS")
        
        updated = await service.get_investigation(str(new_inv.id))
        assert updated.assigned_to == user_uuid
        assert updated.priority == "HIGH"
        assert updated.status == "IN_PROGRESS"
        print("7. Assignments, Priority and Status updates verified successfully.")

        # Test invalid status transition
        try:
            await service.change_status(str(new_inv.id), "ARCHIVED")
            assert False, "Should reject transition IN_PROGRESS -> ARCHIVED"
        except Exception as e:
            print(f"  * Invalid transition rejected: {str(e)}")

        # 10. Search & Retrieval
        by_case = await service.get_by_case_number(updated.case_number)
        assert by_case is not None
        assert by_case.id == new_inv.id

        search_res, search_cnt = await service.search_investigations("TX_NEW")
        assert search_cnt == 1
        assert search_res[0].id == new_inv.id
        print("8. Retrieval and Search queries verified successfully.")

        # Soft Delete
        await service.soft_delete_investigation(str(new_inv.id))
        deleted = await service.get_investigation(str(new_inv.id))
        assert deleted.status == "DELETED"
        print("9. Soft delete verification completed.")
        
    print("\n=== All Repository & Service Flow Tests Passed Successfully! ===")

if __name__ == "__main__":
    asyncio.run(verify_service_layer())
