from pydantic import BaseModel
from typing import Optional

class ProxyRequest(BaseModel):
    provider: str
    model: str
    prompt: str
    client_id: Optional[int] = None
    project_id: Optional[int] = None

class ProxyResponse(BaseModel):
    response_text: str
    tokens_used: int
    cost: float
    request_log_id: int
    budget_alert: bool = False