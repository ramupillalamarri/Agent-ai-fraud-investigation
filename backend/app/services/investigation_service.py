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
from app.models.investigation_timeline import InvestigationTimeline as TimelineModel

from app.agents.models.investigation_report import InvestigationReport
from app.agents.models.agent_result import AgentResult

logger = logging.getLogger("app.services.InvestigationService")

class InvestigationServiceException(Exception):
    """Custom exception raised during investigation service operations."""
    pass

class InvestigationService(BaseService[InvestigationRepository]):
    """Service handling high-level business logic, validation, and report parsing for fraud investigations."""

    def __init__(self, repository: InvestigationRepository):
        super().__init__(repository)

    async def save_report(
        self,
        report: InvestigationReport,
        agent_results: Optional[List[AgentResult]] = None,
        timeline_events: Optional[List[Dict[str, Any]]] = None
    ) -> Investigation:
        """Parses an InvestigationReport and nested structures into SQL entities and persists them.
        
        Args:
            report: Pydantic model representation of the InvestigationReport.
            agent_results: List of execution outputs of agents to persist.
            timeline_events: List of raw timeline event dicts to log.
            
        Returns:
            Investigation: The persisted database model.
        """
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
                    recommendation=rec_val,
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
                        event_description=event.get("event_description", ""),
                        agent_name=event.get("agent_name"),
                        additional_metadata=event.get("metadata", {})
                    )
                    db_investigation.timeline.append(db_tl)
            else:
                # Add default completion event
                db_investigation.timeline.append(
                    TimelineModel(
                        investigation_id=investigation_id,
                        event_type="INVESTIGATION_COMPLETED",
                        event_description="Aggregation report parsed and persisted in DB.",
                        agent_name="System"
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

    async def load_report(self, investigation_id: str) -> Optional[Investigation]:
        """Loads and returns an investigation record from the DB, including relations.
        
        Args:
            investigation_id: String representation of UUID.
            
        Returns:
            Optional[Investigation]: Persisted DB entity if found.
        """
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

    async def archive(self, investigation_id: str) -> Investigation:
        """Transitions status to ARCHIVED and records to timeline."""
        try:
            uid = uuid.UUID(investigation_id)
        except (ValueError, TypeError) as e:
            raise InvestigationServiceException(f"Invalid UUID: {str(e)}")

        try:
            inv = await self.repository.get_by_id(uid)
            if not inv:
                raise InvestigationServiceException(f"Investigation not found for ID: {investigation_id}")
            
            inv.status = "ARCHIVED"
            inv.timeline.append(
                TimelineModel(
                    investigation_id=uid,
                    event_type="INVESTIGATION_ARCHIVED",
                    event_description="Investigation status updated to ARCHIVED.",
                    agent_name="System"
                )
            )
            await self.repository.update_investigation(inv)
            logger.info("Archived investigation ID: %s", investigation_id)
            return inv
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
                    event_description=f"Investigation status updated to CLOSED. Notes: {closure_notes}",
                    agent_name="System"
                )
            )
            await self.repository.update_investigation(inv)
            logger.info("Closed investigation ID: %s", investigation_id)
            return inv
        except SQLAlchemyError as err:
            await self.repository.db.rollback()
            raise InvestigationServiceException(f"Database update failure: {str(err)}")

    async def delete_investigation(self, investigation_id: str) -> Investigation:
        """Soft deletes the investigation by updating its status to 'DELETED'."""
        try:
            uid = uuid.UUID(investigation_id)
        except (ValueError, TypeError) as e:
            raise InvestigationServiceException(f"Invalid UUID: {str(e)}")

        try:
            inv = await self.repository.get_by_id(uid)
            if not inv:
                raise InvestigationServiceException(f"Investigation not found for ID: {investigation_id}")
            
            inv.status = "DELETED"
            inv.timeline.append(
                TimelineModel(
                    investigation_id=uid,
                    event_type="INVESTIGATION_DELETED",
                    event_description="Investigation soft-deleted (status set to DELETED).",
                    agent_name="System"
                )
            )
            await self.repository.update_investigation(inv)
            logger.info("Soft-deleted investigation ID: %s", investigation_id)
            return inv
        except SQLAlchemyError as err:
            await self.repository.db.rollback()
            raise InvestigationServiceException(f"Database update failure: {str(err)}")
