from datetime import datetime

from pydantic import BaseModel, Field


class AIAnalysis(BaseModel):
    summary: str = Field(min_length=1)
    suggested_category: str = Field(min_length=1)
    suggested_priority: str = Field(min_length=1)
    suggested_response: str = Field(min_length=1)

    detected_issue: str = Field(min_length=1)
    recommended_action: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    human_escalation: bool
    customer_response: str = Field(min_length=1)


class AIAnalysisResponse(AIAnalysis):
    id: int
    ticket_id: int
    model_name: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }