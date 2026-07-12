from pydantic import BaseModel
from typing import Optional

class BudgetRuleCreate(BaseModel):
    scope_type: str          # "client" | "project"
    scope_id: int
    budget_amount: float
    period: str               # "daily" | "monthly"
    action: str = "alert_only"
    fallback_model: Optional[str] = None

class BudgetRuleOut(BaseModel):
    id: int
    scope_type: str
    scope_id: int
    budget_amount: float
    period: str
    action: str

    class Config:
        from_attributes = True

class BudgetStatusOut(BaseModel):
    scope_type: str
    scope_id: int
    budget_amount: float
    period: str
    current_spend: float
    is_breached: bool