# Nion Orchestration Engine - Enhanced L3 Models  
# Defines extraction agent output schemas with gap flags

from typing import Literal, List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


StatusType = Literal["pending", "in_progress", "done", "completed"]
RiskSeverity = Literal["high", "medium", "low"]
RiskLikelihood = Literal["HIGH", "MEDIUM", "LOW"]
RiskImpact = Literal["HIGH", "MEDIUM", "LOW"]
GapFlag = Literal["MISSING_OWNER", "MISSING_DUE_DATE", "MISSING_CONTEXT", "NEEDS_CLARIFICATION"]


class ActionItem(BaseModel):
    """Represents an extracted action item with gap flags"""
    id: Optional[str] = Field(None, description="Action item ID (AI-XXX)")
    action: str = Field(..., description="The action to be taken")
    owner: Optional[str] = Field(None, description="Person responsible for the action")
    deadline: Optional[str] = Field(None, alias="due", description="Due date for the action")
    status: StatusType = Field(default="pending", description="Current status")
    flags: List[GapFlag] = Field(default_factory=list, description="Gap flags for missing info")
    
    def model_post_init(self, __context):
        """Auto-populate flags based on missing data"""
        if self.owner is None or self.owner == "?":
            if "MISSING_OWNER" not in self.flags:
                self.flags.append("MISSING_OWNER")
        if self.deadline is None or self.deadline == "?":
            if "MISSING_DUE_DATE" not in self.flags:
                self.flags.append("MISSING_DUE_DATE")
    
    class Config:
        populate_by_name = True


class ActionItemsResult(BaseModel):
    """Container for extracted action items"""
    items: List[ActionItem] = Field(default_factory=list)
    source_task_id: Optional[str] = Field(None)
    extracted_at: datetime = Field(default_factory=datetime.now)


class Risk(BaseModel):
    """Represents an extracted risk with likelihood/impact"""
    id: Optional[str] = Field(None, description="Risk ID (RISK-XXX)")
    description: str = Field(..., description="Description of the risk")
    severity: RiskSeverity = Field(default="medium", description="Risk severity level")
    likelihood: RiskLikelihood = Field(default="MEDIUM", description="Likelihood of occurrence")
    impact: RiskImpact = Field(default="MEDIUM", description="Impact if occurs")
    mitigation: Optional[str] = Field(None, description="Suggested mitigation strategy")
    owner: Optional[str] = Field(None, description="Person responsible for monitoring")


class RisksResult(BaseModel):
    """Container for extracted risks"""
    items: List[Risk] = Field(default_factory=list)
    source_task_id: Optional[str] = Field(None)
    extracted_at: datetime = Field(default_factory=datetime.now)


class Decision(BaseModel):
    """Represents an extracted decision"""
    id: Optional[str] = Field(None, description="Decision ID (DEC-XXX)")
    decision: str = Field(..., description="The decision that was made or needed")
    rationale: Optional[str] = Field(None, description="Reason for the decision")
    decision_maker: Optional[str] = Field(None, alias="made_by", description="Person or group who decides")
    status: Literal["PENDING", "APPROVED", "REJECTED", "DEFERRED"] = Field(default="PENDING")
    effective_date: Optional[str] = Field(None, description="When the decision takes effect")
    
    class Config:
        populate_by_name = True


class DecisionsResult(BaseModel):
    """Container for extracted decisions"""
    items: List[Decision] = Field(default_factory=list)
    source_task_id: Optional[str] = Field(None)
    extracted_at: datetime = Field(default_factory=datetime.now)


class KnowledgeItem(BaseModel):
    """Represents retrieved project knowledge/context"""
    key: str
    value: str


class KnowledgeResult(BaseModel):
    """Container for knowledge retrieval results"""
    project: Optional[str] = None
    items: Dict[str, Any] = Field(default_factory=dict)
    source_task_id: Optional[str] = Field(None)
    extracted_at: datetime = Field(default_factory=datetime.now)


class QnAResponse(BaseModel):
    """Response from Q&A agent"""
    response: str = Field(..., description="The formulated response")
    what_i_know: List[str] = Field(default_factory=list, description="Known facts")
    what_i_logged: List[str] = Field(default_factory=list, description="Items logged")
    what_i_need: List[str] = Field(default_factory=list, description="Missing information needed")
    source_task_id: Optional[str] = Field(None)


class EvaluationResult(BaseModel):
    """Result of response evaluation"""
    relevance: Literal["PASS", "FAIL"] = "PASS"
    accuracy: Literal["PASS", "FAIL"] = "PASS"
    tone: Literal["PASS", "FAIL"] = "PASS"
    gaps_acknowledged: Literal["PASS", "FAIL"] = "PASS"
    result: Literal["APPROVED", "REJECTED", "NEEDS_REVISION"] = "APPROVED"
    feedback: Optional[str] = None
    source_task_id: Optional[str] = Field(None)


class MessageDeliveryResult(BaseModel):
    """Result of message delivery"""
    channel: str
    recipient: str
    cc: List[str] = Field(default_factory=list)
    delivery_status: Literal["SENT", "PENDING", "FAILED"] = "PENDING"
    source_task_id: Optional[str] = Field(None)


# Union type for any extraction result
ExtractionResult = Union[
    ActionItemsResult,
    RisksResult,
    DecisionsResult,
    KnowledgeResult,
    QnAResponse,
    EvaluationResult,
    MessageDeliveryResult
]
