import uuid
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.exc import SQLAlchemyError

from app.services.base import BaseService
from app.repositories.investigation_repository import InvestigationRepository
from app.models.investigation import Investigation
from app.models.agent_result import AgentResult as AgentResultModel
from app.models.evidence import Evidence as EvidenceModel
from app.models.recommendation import Recommendation as RecommendationModel
from app.models.timeline_event import TimelineEvent as TimelineModel

from app.agents.models.investigation_report import InvestigationReport
from app.agents.models.agent_result import AgentResult

logger = logging.getLogger("app.services.InvestigationService")

class InvestigationServiceException(Exception):
    """Custom exception raised during investigation service operations."""
    pass

VALID_TRANSITIONS = {
    "PENDING": {"OPEN", "IN_PROGRESS", "DELETED", "COMPLETED"},
    "OPEN": {"IN_PROGRESS", "UNDER_REVIEW", "DELETED"},
    "IN_PROGRESS": {"UNDER_REVIEW", "COMPLETED", "DELETED"},
    "UNDER_REVIEW": {"COMPLETED", "CLOSED", "DELETED"},
    "COMPLETED": {"ARCHIVED", "CLOSED", "DELETED"},
    "ARCHIVED": {"CLOSED", "DELETED"},
    "CLOSED": {"DELETED"},
    "DELETED": set()
}

class InvestigationService(BaseService[InvestigationRepository]):
    """Service handling high-level business logic, validation, and report parsing for fraud investigations."""

    def __init__(self, repository: InvestigationRepository):
        super().__init__(repository)

    async def create_investigation(
        self, 
        transaction_id: str, 
        status: str = "PENDING", 
        priority: str = "LOW", 
        created_by: Optional[uuid.UUID] = None
    ) -> Investigation:
        """Creates a new retail fraud audit investigation dossier."""
        try:
            # Check for duplicate transaction investigations
            existing = await self.repository.get_by_transaction(transaction_id)
            if existing:
                raise InvestigationServiceException(
                    f"Investigation for transaction ID '{transaction_id}' already exists."
                )
            
            db_investigation = Investigation(
                transaction_id=transaction_id,
                status=status,
                priority=priority,
                created_by=created_by,
                started_at=datetime.now(timezone.utc),
                additional_metadata={}
            )
            
            # Setup initial timeline event using correct model
            db_investigation.timeline.append(
                TimelineModel(
                    event_type="INVESTIGATION_CREATED",
                    title="Investigation Started",
                    description=f"Retail fraud investigation created for transaction ID: {transaction_id}.",
                    agent_name="System",
                    status="SUCCESS"
                )
            )
            
            db_obj = await self.repository.create(db_investigation)
            logger.info("Successfully created investigation case ID: %s", db_obj.id)
            return db_obj
        except SQLAlchemyError as err:
            await self.repository.db.rollback()
            raise InvestigationServiceException(f"Database creation failure: {str(err)}")

    async def save_report(
        self,
        report: InvestigationReport,
        agent_results: Optional[List[AgentResult]] = None,
        timeline_events: Optional[List[Dict[str, Any]]] = None
    ) -> Investigation:
        """Parses an InvestigationReport and nested structures into SQL entities and persists them."""
        logger.info("Persisting investigation report for ID: %s", report.investigation_id)
        
        # 1. Validations
        try:
            investigation_id = uuid.UUID(report.investigation_id)
        except (ValueError, TypeError) as e:
            logger.error("Invalid investigation_id UUID: %s", report.investigation_id)
            raise InvestigationServiceException(f"Invalid UUID for investigation_id: {str(e)}")

        try:
            # Check if this investigation ID already exists
            existing = await self.repository.get_by_id(investigation_id)
            
            # Map raw fields to the new model
            fraud_probability = 0.0
            risk_score = 0
            
            # Extract additional parameters from overall risk category
            if report.overall_risk == "HIGH":
                risk_score = 85
                fraud_probability = 0.85
            elif report.overall_risk == "MEDIUM":
                risk_score = 50
                fraud_probability = 0.50
            else:
                risk_score = 15
                fraud_probability = 0.15

            if existing:
                logger.info("Updating existing investigation record: %s", investigation_id)
                # Clear existing relationships to avoid duplication
                existing.status = "COMPLETED"
                existing.priority = report.overall_risk
                existing.fraud_probability = fraud_probability
                existing.risk_score = risk_score
                existing.overall_confidence = report.overall_confidence
                existing.completed_at = datetime.now(timezone.utc)
                existing.additional_metadata = {"executive_summary": report.executive_summary}
                
                # Re-create child lists
                existing.agent_results.clear()
                existing.evidence.clear()
                existing.recommendations.clear()
                existing.timeline.clear()
                
                db_investigation = existing
            else:
                db_investigation = Investigation(
                    id=investigation_id,
                    transaction_id=report.transaction_id,
                    status="COMPLETED",
                    priority=report.overall_risk,
                    fraud_probability=fraud_probability,
                    risk_score=risk_score,
                    overall_confidence=report.overall_confidence,
                    started_at=datetime.now(timezone.utc),
                    completed_at=datetime.now(timezone.utc),
                    additional_metadata={"executive_summary": report.executive_summary}
                )

            # Map AgentResults and Evidence
            if agent_results:
                for ar in agent_results:
                    db_ar = AgentResultModel(
                        investigation_id=investigation_id,
                        agent_name=ar.agent_name,
                        status=ar.status,
                        confidence_score=ar.confidence_score,
                        execution_time_ms=ar.execution_time_ms,
                        summary=ar.findings[0] if ar.findings else "Execution completed.",
                        additional_metadata=ar.metadata
                    )
                    db_investigation.agent_results.append(db_ar)
                    
                    # Evidence linked to this agent
                    for ev in ar.evidence:
                        db_ev = EvidenceModel(
                            investigation_id=investigation_id,
                            agent_result=db_ar,  # Associate directly to trigger auto relationship mapping
                            type=ev.get("type", "Anomaly"),
                            severity=ev.get("severity", "MEDIUM"),
                            confidence=ev.get("confidence", 1.0),
                            title=ev.get("title", ev.get("type", "Anomaly")),
                            description=ev.get("description", ""),
                            source=ev.get("source", ar.agent_name),
                            additional_metadata=ev.get("metadata", {})
                        )
                        db_investigation.evidence.append(db_ev)

            # If evidence exists in the report but wasn't mapped through agent_results, map it directly
            if not agent_results and report.evidence:
                for ev in report.evidence:
                    db_ev = EvidenceModel(
                        investigation_id=investigation_id,
                        agent_result_id=None,
                        type=ev.get("type", "Anomaly"),
                        severity=ev.get("severity", "MEDIUM"),
                        confidence=ev.get("confidence", 1.0),
                        title=ev.get("title", ev.get("type", "Anomaly")),
                        description=ev.get("description", ""),
                        source=ev.get("source", "System"),
                        additional_metadata=ev.get("metadata", {})
                    )
                    db_investigation.evidence.append(db_ev)

            # Map Recommendations
            for rec_item in report.recommendations:
                rec_val = rec_item.get("text") if isinstance(rec_item, dict) else str(rec_item)
                rec_priority = rec_item.get("severity", "MEDIUM") if isinstance(rec_item, dict) else "MEDIUM"
                db_rec = RecommendationModel(
                    investigation_id=investigation_id,
                    title=rec_item.get("title") if isinstance(rec_item, dict) else "Suggested Action",
                    description=rec_val,
                    priority=rec_priority,
                    generated_by="Orchestrator",
                    status="PENDING"
                )
                db_investigation.recommendations.append(db_rec)

            # Map Timeline Events
            if timeline_events:
                for event in timeline_events:
                    db_tl = TimelineModel(
                        investigation_id=investigation_id,
                        event_type=event.get("event_type", "INFO"),
                        title=event.get("title", event.get("event_type", "INFO")),
                        description=event.get("event_description", ""),
                        agent_name=event.get("agent_name"),
                        status=event.get("status", "SUCCESS"),
                        started_at=event.get("started_at"),
                        completed_at=event.get("completed_at"),
                        duration_ms=event.get("duration_ms"),
                        additional_metadata=event.get("metadata", {})
                    )
                    db_investigation.timeline.append(db_tl)
            else:
                # Add default completion event
                db_investigation.timeline.append(
                    TimelineModel(
                        investigation_id=investigation_id,
                        event_type="INVESTIGATION_COMPLETED",
                        title="Investigation Completed",
                        description="Aggregation report parsed and persisted in DB.",
                        agent_name="System",
                        status="SUCCESS"
                    )
                )

            # Save via repository
            if existing:
                await self.repository.update_investigation(db_investigation)
            else:
                await self.repository.create_investigation(db_investigation)

            logger.info("Successfully persisted investigation ID: %s", investigation_id)
            return db_investigation

        except SQLAlchemyError as err:
            logger.error("Failed database operation during save: %s", str(err))
            await self.repository.db.rollback()
            raise InvestigationServiceException(f"Database persistence failure: {str(err)}")
        except Exception as e:
            logger.error("General failure during save: %s", str(e))
            await self.repository.db.rollback()
            raise InvestigationServiceException(f"Failed to process investigation save: {str(e)}")

    async def save_investigation_report(
        self,
        report: InvestigationReport,
        agent_results: Optional[List[AgentResult]] = None,
        timeline_events: Optional[List[Dict[str, Any]]] = None
    ) -> Investigation:
        """Alias for save_report."""
        return await self.save_report(report, agent_results, timeline_events)

    async def update_investigation(self, db_obj: Investigation, obj_in: Any) -> Investigation:
        """Updates an existing investigation instance."""
        try:
            return await self.repository.update(db_obj=db_obj, obj_in=obj_in)
        except SQLAlchemyError as err:
            await self.repository.db.rollback()
            raise InvestigationServiceException(f"Database update failure: {str(err)}")

    async def close_investigation(self, investigation_id: str, closure_notes: str) -> Investigation:
        """Updates status to CLOSED and appends closure timeline details."""
        try:
            uid = uuid.UUID(investigation_id)
        except (ValueError, TypeError) as e:
            raise InvestigationServiceException(f"Invalid UUID: {str(e)}")

        try:
            inv = await self.repository.get_by_id(uid)
            if not inv:
                raise InvestigationServiceException(f"Investigation not found for ID: {investigation_id}")
            
            inv.status = "CLOSED"
            inv.completed_at = datetime.now(timezone.utc)
            inv.timeline.append(
                TimelineModel(
                    investigation_id=uid,
                    event_type="INVESTIGATION_CLOSED",
                    title="Investigation Closed",
                    description=f"Investigation status updated to CLOSED. Notes: {closure_notes}",
                    agent_name="System",
                    status="SUCCESS"
                )
            )
            await self.repository.update_investigation(inv)
            logger.info("Closed investigation ID: %s", investigation_id)
            return inv
        except SQLAlchemyError as err:
            await self.repository.db.rollback()
            raise InvestigationServiceException(f"Database update failure: {str(err)}")

    async def assign_investigator(self, investigation_id: str, investigator_id: uuid.UUID) -> Investigation:
        """Assigns an investigator to the investigation dossier."""
        try:
            uid = uuid.UUID(investigation_id)
        except (ValueError, TypeError) as e:
            raise InvestigationServiceException(f"Invalid UUID: {str(e)}")

        try:
            inv = await self.repository.get_by_id(uid)
            if not inv:
                raise InvestigationServiceException(f"Investigation not found for ID: {investigation_id}")
            
            inv.assigned_to = investigator_id
            inv.timeline.append(
                TimelineModel(
                    investigation_id=uid,
                    event_type="INVESTIGATOR_ASSIGNED",
                    title="Investigator Assigned",
                    description=f"Dossier assigned to investigator: {investigator_id}.",
                    agent_name="System",
                    status="SUCCESS"
                )
            )
            await self.repository.update_investigation(inv)
            logger.info("Assigned investigator %s to investigation %s", investigator_id, investigation_id)
            return inv
        except SQLAlchemyError as err:
            await self.repository.db.rollback()
            raise InvestigationServiceException(f"Database update failure: {str(err)}")

    async def change_priority(self, investigation_id: str, priority: str) -> Investigation:
        """Updates the priority of an investigation, validating priority value."""
        try:
            uid = uuid.UUID(investigation_id)
        except (ValueError, TypeError) as e:
            raise InvestigationServiceException(f"Invalid UUID: {str(e)}")

        if priority not in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}:
            raise InvestigationServiceException(f"Invalid priority level: {priority}")

        try:
            inv = await self.repository.get_by_id(uid)
            if not inv:
                raise InvestigationServiceException(f"Investigation not found for ID: {investigation_id}")
            
            current_priority = inv.priority
            inv.priority = priority
            
            inv.timeline.append(
                TimelineModel(
                    investigation_id=uid,
                    event_type="PRIORITY_CHANGED",
                    title="Investigation Priority Changed",
                    description=f"Investigation priority updated from {current_priority} to {priority}.",
                    agent_name="System",
                    status="SUCCESS"
                )
            )
            await self.repository.update_investigation(inv)
            logger.info("Changed priority of investigation %s to %s", investigation_id, priority)
            return inv
        except SQLAlchemyError as err:
            await self.repository.db.rollback()
            raise InvestigationServiceException(f"Database update failure: {str(err)}")

    async def change_status(self, investigation_id: str, status: str) -> Investigation:
        """Updates the status of an investigation, validating the transition."""
        try:
            uid = uuid.UUID(investigation_id)
        except (ValueError, TypeError) as e:
            raise InvestigationServiceException(f"Invalid UUID: {str(e)}")

        try:
            inv = await self.repository.get_by_id(uid)
            if not inv:
                raise InvestigationServiceException(f"Investigation not found for ID: {investigation_id}")
            
            current_status = inv.status
            if status not in VALID_TRANSITIONS.get(current_status, set()):
                if status != current_status:
                    raise InvestigationServiceException(
                        f"Invalid status transition from {current_status} to {status}"
                    )
            
            inv.status = status
            if status == "COMPLETED" or status == "CLOSED":
                inv.completed_at = datetime.now(timezone.utc)
            
            inv.timeline.append(
                TimelineModel(
                    investigation_id=uid,
                    event_type="STATUS_CHANGED",
                    title="Investigation Status Changed",
                    description=f"Investigation status updated from {current_status} to {status}.",
                    agent_name="System",
                    status="SUCCESS"
                )
            )
            await self.repository.update_investigation(inv)
            logger.info("Changed status of investigation %s to %s", investigation_id, status)
            return inv
        except SQLAlchemyError as err:
            await self.repository.db.rollback()
            raise InvestigationServiceException(f"Database update failure: {str(err)}")

    async def load_report(self, investigation_id: str) -> Optional[Investigation]:
        """Loads and returns an investigation record from the DB, including relations."""
        try:
            uid = uuid.UUID(investigation_id)
        except (ValueError, TypeError) as e:
            raise InvestigationServiceException(f"Invalid UUID: {str(e)}")

        try:
            res = await self.repository.get_by_id(uid)
            if res:
                logger.info("Loaded investigation ID: %s", investigation_id)
            return res
        except SQLAlchemyError as err:
            raise InvestigationServiceException(f"Database query failure: {str(err)}")

    async def get_investigation(self, investigation_id: str) -> Optional[Investigation]:
        """Alias for load_report."""
        return await self.load_report(investigation_id)

    async def get_by_case_number(self, case_number: str) -> Optional[Investigation]:
        """Loads and returns an investigation record from the DB by case number."""
        try:
            res = await self.repository.get_by_case_number(case_number)
            if res:
                logger.info("Loaded investigation by case_number: %s", case_number)
            return res
        except SQLAlchemyError as err:
            raise InvestigationServiceException(f"Database query failure: {str(err)}")

    async def search(
        self,
        *,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        min_risk_score: Optional[int] = None,
        max_risk_score: Optional[int] = None,
        min_fraud_prob: Optional[float] = None,
        max_fraud_prob: Optional[float] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 100,
        sort_by: str = "created_at",
        sort_desc: bool = True
    ) -> Tuple[List[Investigation], int]:
        """Queries investigations with filtering, pagination, and sorting."""
        try:
            return await self.repository.list_investigations(
                status=status,
                priority=priority,
                min_risk_score=min_risk_score,
                max_risk_score=max_risk_score,
                min_fraud_prob=min_fraud_prob,
                max_fraud_prob=max_fraud_prob,
                start_date=start_date,
                end_date=end_date,
                page=page,
                page_size=page_size,
                sort_by=sort_by,
                sort_desc=sort_desc
            )
        except SQLAlchemyError as err:
            raise InvestigationServiceException(f"Database query failure: {str(err)}")

    async def search_investigations(
        self, query_str: str, page: int = 1, page_size: int = 10
    ) -> Tuple[List[Investigation], int]:
        """Fuzzy searches investigations based on query string."""
        try:
            return await self.repository.search(query_str, page=page, page_size=page_size)
        except SQLAlchemyError as err:
            raise InvestigationServiceException(f"Database query failure: {str(err)}")

    async def list_investigations(self, **kwargs: Any) -> Tuple[List[Investigation], int]:
        """Lists investigations using standard repository filters."""
        try:
            return await self.repository.list(**kwargs)
        except SQLAlchemyError as err:
            raise InvestigationServiceException(f"Database query failure: {str(err)}")

    async def archive(self, investigation_id: str) -> Investigation:
        """Transitions status to ARCHIVED and records to timeline."""
        return await self.change_status(investigation_id, "ARCHIVED")

    async def archive_investigation(self, investigation_id: str) -> Investigation:
        """Alias for archive."""
        return await self.archive(investigation_id)

    async def delete_investigation(self, investigation_id: str) -> Investigation:
        """Soft deletes the investigation by updating its status to 'DELETED'."""
        return await self.change_status(investigation_id, "DELETED")

    async def soft_delete_investigation(self, investigation_id: str) -> Investigation:
        """Alias for delete_investigation."""
        return await self.delete_investigation(investigation_id)
