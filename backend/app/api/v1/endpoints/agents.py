from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import has_permission
from app.schemas.agent import AgentResponse, AgentUpdate
from app.api.v1.investigations import get_agent_registry
from app.agents.orchestrator.registry import AgentRegistry

router = APIRouter()

@router.get(
    "",
    response_model=List[AgentResponse],
    summary="List all registered AI investigation agents",
    dependencies=[has_permission("dashboard:view")]
)
async def list_agents(
    registry: AgentRegistry = Depends(get_agent_registry)
) -> List[dict]:
    """Retrieves all registered agents with their details and health status."""
    agents = registry.get_all_agents()
    response = []
    for agent in agents:
        try:
            health = agent.health_check()
        except Exception:
            health = False
            
        response.append({
            "id": agent.agent_id,
            "name": agent.agent_name,
            "description": agent.description,
            "version": agent.version,
            "priority": agent.execution_priority,
            "enabled": agent.enabled,
            "type": agent.supported_features[0] if agent.supported_features else "General",
            "health_status": health
        })
    return response

@router.patch(
    "/{agent_id}",
    response_model=AgentResponse,
    summary="Update a registered AI agent configuration",
    dependencies=[has_permission("users:create")]
)
async def update_agent(
    agent_id: str,
    payload: AgentUpdate,
    registry: AgentRegistry = Depends(get_agent_registry)
) -> dict:
    """Partially updates enabled state or execution order of the targeted agent."""
    try:
        agent = registry.get_agent(agent_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID '{agent_id}' not found."
        )

    if payload.enabled is not None:
        agent.enabled = payload.enabled
        
    priority_val = payload.priority if payload.priority is not None else payload.execution_priority
    if priority_val is not None:
        agent.execution_priority = priority_val

    try:
        health = agent.health_check()
    except Exception:
        health = False

    return {
        "id": agent.agent_id,
        "name": agent.agent_name,
        "description": agent.description,
        "version": agent.version,
        "priority": agent.execution_priority,
        "enabled": agent.enabled,
        "type": agent.supported_features[0] if agent.supported_features else "General",
        "health_status": health
    }
