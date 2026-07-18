import uuid
import time
import logging
import functools
from datetime import datetime, timezone
from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.api.deps import ActiveSession, has_permission, get_current_active_user
from app.models.user import User
from app.repositories.investigation_repository import InvestigationRepository
from app.services.investigation_service import InvestigationService, InvestigationServiceException
from app.schemas.investigation import (
    InvestigationRunRequest,
    InvestigationResponse,
    InvestigationListResponse,
    TimelineResponse,
    InvestigationReportResponse,
    EvidenceResponse,
    RecommendationResponse,
    AgentResultResponse,
    UpdateInvestigationRequest
)

# Import default concrete investigators to register them in orchestrator
from app.agents.orchestrator.registry import AgentRegistry
from app.agents.orchestrator.orchestrator import InvestigationOrchestrator
from app.agents.langgraph.orchestrator import LangGraphOrchestrator
from app.agents.investigators.customer_agent import CustomerInvestigationAgent
from app.agents.investigators.device.device_agent import DeviceInvestigationAgent
from app.agents.investigators.network.network_agent import NetworkRiskAgent
from app.agents.investigators.merchant.merchant_agent import MerchantInvestigationAgent
from app.agents.investigators.knowledge.knowledge_agent import KnowledgeAgent

from ml.inference.predict import PredictionEngine

logger = logging.getLogger("app.api.v1.investigations")

router = APIRouter()

# Dependency Injection Helpers

def get_investigation_service(db: ActiveSession) -> InvestigationService:
    """Dependency provider for InvestigationService."""
    repo = InvestigationRepository(db)
    return InvestigationService(repo)

@functools.lru_cache()
def get_agent_registry() -> AgentRegistry:
    """Dependency provider singleton for AgentRegistry."""
    registry = AgentRegistry()
    registry.register(CustomerInvestigationAgent())
    registry.register(DeviceInvestigationAgent())
    registry.register(NetworkRiskAgent())
    registry.register(MerchantInvestigationAgent())
    registry.register(KnowledgeAgent())
    return registry

def get_orchestrator(registry: AgentRegistry = Depends(get_agent_registry)) -> InvestigationOrchestrator:
    """Dependency provider for InvestigationOrchestrator returning compiled LangGraph execution engines."""
    return LangGraphOrchestrator(registry)

@functools.lru_cache()
def get_prediction_engine() -> PredictionEngine:
    """Dependency provider singleton for ML PredictionEngine."""
    return PredictionEngine()


# REST Endpoints

@router.post(
    "/run",
    response_model=InvestigationReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Run real-time multi-agent fraud investigation",
    dependencies=[has_permission("investigation:write")]
)
async def run_investigation(
    payload: InvestigationRunRequest,
    db: ActiveSession,
    current_user: User = Depends(get_current_active_user),
    service: InvestigationService = Depends(get_investigation_service),
    orchestrator: InvestigationOrchestrator = Depends(get_orchestrator),
    prediction_engine: PredictionEngine = Depends(get_prediction_engine)
) -> dict:
    """Executes automated real-time transaction ingestion, ML classification inference,
    multi-agent reasoning node orchestration, and persists audit reports to database.
    """
    logger.info("REST request to run investigation by user %s for TX: %s", current_user.email, payload.transaction_id)
    start_time = time.perf_counter()
    
    # 1. Execute ML Model Prediction
    try:
        # Pre-populate and map default fields for pipeline compatibility
        payload_dict = payload.model_dump()
        add_data = payload_dict.pop("additional_data", None) or {}
        payload_dict["user_id"] = payload_dict.get("customer_id")
        payload_dict["transaction_timestamp"] = payload_dict.get("timestamp") or datetime.now(timezone.utc)
        payload_dict["user_age"] = add_data.get("user_age", 35)
        payload_dict["account_balance"] = add_data.get("account_balance", 2000.0)
        payload_dict["device_type"] = add_data.get("device_type", "mobile")
        payload_dict["location_country"] = add_data.get("location_country", "US")

        pred_results = prediction_engine.predict(payload_dict)
        if not pred_results:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ML prediction returned empty dataset results."
            )
        pred_res = pred_results[0]
        prob = pred_res["prediction"]["fraud_probability"]
        risk = pred_res["prediction"]["risk_score"]
        priority = pred_res["investigation_context"]["priority"]
        logger.info("Prediction generated. Risk: %d | Probability: %.4f | Priority: %s", risk, prob, priority)
    except Exception as e:
        logger.error("ML Prediction calculation crashed: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ML Prediction calculation failed: {str(e)}"
        )

    # 2. Construct InvestigationContext
    from app.agents.models.investigation_context import InvestigationContext
    investigation_uuid = uuid.uuid4()
    
    context = InvestigationContext(
        investigation_id=str(investigation_uuid),
        transaction_id=payload.transaction_id,
        transaction_data=payload.model_dump(),
        prediction_result=pred_res["prediction"],
        fraud_probability=prob,
        risk_score=risk,
        priority=priority,
        shared_memory={}
    )
    
    # Pre-populate relational node boundaries for NetworkRiskAgent
    context.shared_memory["network_data"] = {
        "ip_accounts": {payload.ip_address: [payload.customer_id]},
        "device_accounts": {payload.device_id: [payload.customer_id]},
        "shared_attributes": {},
        "payment_accounts": {payload.payment_instrument: [payload.customer_id]},
        "flagged_merchants": ["MERCH_FRAUD_88"],
        "fraud_clusters": []
    }
    
    # 3. Execute InvestigationOrchestrator
    try:
        report = orchestrator.run_investigation(context)
        logger.info("Investigation completed. Executed agents: %s", report.executed_agents)
    except Exception as e:
        logger.error("Investigation orchestration crashed: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Investigation orchestration failed: {str(e)}"
        )
        
    # 4. Persist to PostgreSQL database
    try:
        db_inv = await service.save_report(
            report=report,
            agent_results=context.metadata.get("agent_results"),
            timeline_events=context.metadata.get("timeline_events")
        )
        # Link user who triggered the run
        db_inv.created_by = current_user.id
        await service.repository.update_investigation(db_inv)
        logger.info("Successfully persisted investigation ID: %s", investigation_uuid)
    except InvestigationServiceException as err:
        logger.error("Failed to save report: %s", str(err))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database persistence failure: {str(err)}"
        )
        
    execution_time_ms = int((time.perf_counter() - start_time) * 1000)
    logger.info("POST /run successfully completed in %d ms.", execution_time_ms)
    
    return {
        "id": investigation_uuid,
        "investigation_id": investigation_uuid,
        "transaction_id": report.transaction_id,
        "overall_risk": report.overall_risk,
        "overall_confidence": report.overall_confidence,
        "executive_summary": report.executive_summary,
        "findings": report.findings,
        "recommendations": [r.get("text") if isinstance(r, dict) else str(r) for r in report.recommendations],
        "evidence": report.evidence,
        "executed_agents": report.executed_agents,
        "generated_at": report.generated_at
    }

@router.get(
    "/{investigation_id}",
    response_model=InvestigationResponse,
    summary="Get complete investigation dossier",
    dependencies=[has_permission("investigation:read")]
)
async def get_investigation(
    investigation_id: uuid.UUID,
    service: InvestigationService = Depends(get_investigation_service)
) -> InvestigationResponse:
    """Fetch complete profile detail logs of a single fraud audit investigation by primary key UUID."""
    try:
        inv = await service.load_report(str(investigation_id))
        if not inv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Investigation not found for ID: {investigation_id}"
            )
        return inv
    except InvestigationServiceException as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(err)
        )

@router.get(
    "",
    response_model=InvestigationListResponse,
    summary="List, search and filter investigations",
    dependencies=[has_permission("investigation:read")]
)
async def list_investigations(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    min_risk_score: Optional[int] = Query(None, ge=0, le=100),
    max_risk_score: Optional[int] = Query(None, ge=0, le=100),
    min_fraud_prob: Optional[float] = Query(None, ge=0.0, le=1.0),
    max_fraud_prob: Optional[float] = Query(None, ge=0.0, le=1.0),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    sort_by: str = "created_at",
    sort_desc: bool = True,
    service: InvestigationService = Depends(get_investigation_service)
) -> dict:
    """Retrieve paginated and filtered list of investigation audits."""
    try:
        results, total = await service.search(
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
        return {"investigations": results, "total": total}
    except InvestigationServiceException as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(err)
        )

@router.get(
    "/{investigation_id}/timeline",
    response_model=TimelineResponse,
    summary="Get timeline audit events",
    dependencies=[has_permission("investigation:read")]
)
async def get_timeline(
    investigation_id: uuid.UUID,
    service: InvestigationService = Depends(get_investigation_service)
) -> dict:
    """Fetch complete list of transaction log audit history occurred for a single investigation."""
    try:
        inv = await service.load_report(str(investigation_id))
        if not inv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Investigation not found for ID: {investigation_id}"
            )
        return {
            "investigation_id": inv.id,
            "timeline": inv.timeline
        }
    except InvestigationServiceException as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(err)
        )

@router.get(
    "/{investigation_id}/report",
    response_model=InvestigationReportResponse,
    summary="Get compiled investigation report",
    dependencies=[has_permission("investigation:read")]
)
async def get_report(
    investigation_id: uuid.UUID,
    service: InvestigationService = Depends(get_investigation_service)
) -> dict:
    """Fetch compiled final summary report overview from the persisted database."""
    try:
        inv = await service.load_report(str(investigation_id))
        if not inv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Investigation not found for ID: {investigation_id}"
            )
        
        # Build InvestigationReportResponse from DB entity
        findings = [finding for ar in inv.agent_results for finding in ar.additional_metadata.get("findings", [])]
        recommendations = [r.recommendation for r in inv.recommendations]
        evidence = []
        for ev in inv.evidence:
            evidence.append({
                "type": ev.type,
                "severity": ev.severity,
                "confidence": ev.confidence,
                "description": ev.description,
                "source": ev.source,
                "metadata": ev.additional_metadata
            })
        executed_agents = [ar.agent_name for ar in inv.agent_results]
        
        return {
            "investigation_id": inv.id,
            "transaction_id": inv.transaction_id,
            "overall_risk": inv.priority,
            "overall_confidence": inv.overall_confidence,
            "executive_summary": inv.additional_metadata.get("executive_summary", ""),
            "findings": findings,
            "recommendations": recommendations,
            "evidence": evidence,
            "executed_agents": executed_agents,
            "generated_at": inv.created_at
        }
    except InvestigationServiceException as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(err)
        )

@router.delete(
    "/{investigation_id}",
    response_model=InvestigationResponse,
    summary="Soft delete investigation audit",
    dependencies=[has_permission("investigation:delete")]
)
async def delete_investigation(
    investigation_id: uuid.UUID,
    service: InvestigationService = Depends(get_investigation_service)
) -> InvestigationResponse:
    """Performs soft-delete mapping for target investigation primary ID (updates status to DELETED)."""
    try:
        inv = await service.load_report(str(investigation_id))
        if not inv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Investigation not found for ID: {investigation_id}"
            )
            
        deleted_inv = await service.delete_investigation(str(investigation_id))
        return deleted_inv
    except InvestigationServiceException as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(err)
        )

@router.get(
    "/{investigation_id}/evidence",
    response_model=EvidenceResponse,
    summary="Get case evidence items",
    dependencies=[has_permission("investigation:read")]
)
async def get_evidence(
    investigation_id: uuid.UUID,
    service: InvestigationService = Depends(get_investigation_service)
) -> dict:
    """Fetch complete list of audit evidence items collected for a single investigation."""
    try:
        inv = await service.load_report(str(investigation_id))
        if not inv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Investigation not found for ID: {investigation_id}"
            )
        return {
            "investigation_id": inv.id,
            "evidence": inv.evidence
        }
    except InvestigationServiceException as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(err)
        )

@router.get(
    "/{investigation_id}/recommendations",
    response_model=RecommendationResponse,
    summary="Get case recommendations",
    dependencies=[has_permission("investigation:read")]
)
async def get_recommendations(
    investigation_id: uuid.UUID,
    service: InvestigationService = Depends(get_investigation_service)
) -> dict:
    """Fetch complete list of mitigation recommendations mapped for a single investigation."""
    try:
        inv = await service.load_report(str(investigation_id))
        if not inv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Investigation not found for ID: {investigation_id}"
            )
        return {
            "investigation_id": inv.id,
            "recommendations": inv.recommendations
        }
    except InvestigationServiceException as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(err)
        )

@router.get(
    "/{investigation_id}/agent-results",
    response_model=AgentResultResponse,
    summary="Get individual agent execution results",
    dependencies=[has_permission("investigation:read")]
)
async def get_agent_results(
    investigation_id: uuid.UUID,
    service: InvestigationService = Depends(get_investigation_service)
) -> dict:
    """Fetch execution parameters and outputs of all agents executed for a single investigation."""
    try:
        inv = await service.load_report(str(investigation_id))
        if not inv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Investigation not found for ID: {investigation_id}"
            )
        return {
            "investigation_id": inv.id,
            "agent_results": inv.agent_results
        }
    except InvestigationServiceException as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(err)
        )

@router.patch(
    "/{investigation_id}",
    response_model=InvestigationResponse,
    summary="Update investigation attributes",
    dependencies=[has_permission("investigation:update")]
)
async def update_investigation(
    investigation_id: uuid.UUID,
    payload: UpdateInvestigationRequest,
    service: InvestigationService = Depends(get_investigation_service)
) -> Any:
    """Partially updates investigation priority, status, or assignee attributes."""
    try:
        inv = await service.load_report(str(investigation_id))
        if not inv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Investigation not found for ID: {investigation_id}"
            )
            
        if payload.status is not None:
            await service.change_status(str(investigation_id), payload.status)
        if payload.priority is not None:
            await service.change_priority(str(investigation_id), payload.priority)
        if payload.assigned_to is not None:
            await service.assign_investigator(str(investigation_id), payload.assigned_to)
            
        return await service.load_report(str(investigation_id))
    except InvestigationServiceException as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err)
        )
