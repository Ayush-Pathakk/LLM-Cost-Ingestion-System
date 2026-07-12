from pydantic import BaseModel
from typing import Optional

class IngestionEvent(BaseModel):
    provider: str
    model: str
    tokens_used: int
    latency: Optional[float] = None
    client_id: Optional[int] = None
    project_id: Optional[int] = None
    source: str = "ingestion:manual"  # e.g. "ingestion:litellm"

class IngestionResponse(BaseModel):
    request_log_id: int
    cost: float

    class Config:
        from_attributes = True

class IngestionResponse(BaseModel):
    request_log_id: int
    cost: float
    budget_alert: bool = False

    class Config:
        from_attributes = True