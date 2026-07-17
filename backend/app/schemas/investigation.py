import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, Field

class InvestigationRunRequest(BaseModel):
    """Schema representing inputs required to execute real-time multi-agent fraud investigation audits."""
    model_config = ConfigDict(extra="ignore")

    transaction_id: str = Field(..., description="Unique code identifying the retail transaction.")
    customer_id: str = Field(..., description="Unique customer/user profile ID.")
    amount: float = Field(..., gt=0.0, description="Transaction monetary amount.")
    currency: str = Field(default="USD", min_length=3, max_length=3, description="Currency code (e.g. USD).")
    payment_method: str = Field(default="credit_card", description="The channel utilized (e.g. credit_card, paypal).")
    payment_instrument: str = Field(default="card_1", description="Credit card ID or bank account identifier.")
    device_id: str = Field(default="DEV-SAFE-99", description="Hardware terminal/device ID.")
    ip_address: str = Field(default="127.0.0.1", description="Client IP connection origin.")
    merchant_id: str = Field(default="MERCH-NORMAL", description="Store/Merchant profile identifier.")
    merchant_category: str = Field(default="retail", description="Merchant business category.")
    shipping_address: Optional[str] = Field(default="", description="Target delivery physical location.")
    billing_address: Optional[str] = Field(default="", description="Authorized financial billing address.")
    phone_number: Optional[str] = Field(default="", description="Associated contact number.")
    email: Optional[str] = Field(default="", description="Associated account email address.")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Time event recorded.")
    additional_data: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary custom key-value metadata.")

class AgentResultSchema(BaseModel):
    """Schema representing execution results from individual agents."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    agent_name: str
    status: str
    confidence_score: float
    execution_time_ms: int
    summary: Optional[str] = None
    additional_metadata: Dict[str, Any] = Field(default_factory=dict)

class EvidenceSchema(BaseModel):
    """Schema representing captured evidence data points."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    agent_result_id: Optional[uuid.UUID] = None
    type: str
    severity: str
    confidence: float
    title: Optional[str] = None
    description: str
    source: str
    additional_metadata: Dict[str, Any] = Field(default_factory=dict)

class RecommendationSchema(BaseModel):
    """Schema representing mitigation suggestions."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: Optional[str] = None
    description: str
    recommendation: str
    priority: str
    generated_by: str
    status: str

class TimelineSchema(BaseModel):
    """Schema representing timeline audits."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    event_type: str
    title: Optional[str] = None
    event_description: str
    agent_name: Optional[str] = None
    status: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    timestamp: datetime
    additional_metadata: Dict[str, Any] = Field(default_factory=dict)

class InvestigationResponse(BaseModel):
    """Schema representing a complete Investigation record database details."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    transaction_id: str
    case_number: str
    status: str
    priority: str
    fraud_probability: float
    risk_score: int
    overall_confidence: float
    prediction: Optional[str] = None
    summary: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    created_by: Optional[uuid.UUID] = None
    assigned_to: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    additional_metadata: Dict[str, Any] = Field(default_factory=dict)

    agent_results: List[AgentResultSchema] = Field(default_factory=list)
    evidence: List[EvidenceSchema] = Field(default_factory=list)
    recommendations: List[RecommendationSchema] = Field(default_factory=list)
    timeline: List[TimelineSchema] = Field(default_factory=list)

class InvestigationListResponse(BaseModel):
    """Schema representing paginated listing results."""
    investigations: List[InvestigationResponse]
    total: int

class TimelineResponse(BaseModel):
    """Schema representing a timeline of investigation audit logs."""
    investigation_id: uuid.UUID
    timeline: List[TimelineSchema]

class EvidenceResponse(BaseModel):
    """Schema representing evidence items for a case."""
    investigation_id: uuid.UUID
    evidence: List[EvidenceSchema]

class RecommendationResponse(BaseModel):
    """Schema representing recommendations for a case."""
    investigation_id: uuid.UUID
    recommendations: List[RecommendationSchema]

class AgentResultResponse(BaseModel):
    """Schema representing agent result items for a case."""
    investigation_id: uuid.UUID
    agent_results: List[AgentResultSchema]

class UpdateInvestigationRequest(BaseModel):
    """Schema for updating status, priority, or assignment on an investigation."""
    status: Optional[str] = Field(None, description="Updated status of the investigation.")
    priority: Optional[str] = Field(None, description="Updated priority level.")
    assigned_to: Optional[uuid.UUID] = Field(None, description="Investigator UUID assigned to this case.")

class InvestigationReportResponse(BaseModel):
    """Schema representing a parsed and aggregated summary Report output."""
    investigation_id: uuid.UUID
    transaction_id: str
    overall_risk: str
    overall_confidence: float
    executive_summary: str
    findings: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    executed_agents: List[str] = Field(default_factory=list)
    generated_at: datetime
