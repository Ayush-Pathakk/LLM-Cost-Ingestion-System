from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class BudgetRule(Base):
    __tablename__ = "budget_rules"

    id = Column(Integer, primary_key=True, index=True)
    scope_type = Column(String, nullable=False)   # "client" | "project"
    scope_id = Column(Integer, nullable=False)
    budget_amount = Column(Float, nullable=False)
    period = Column(String, nullable=False)       # "daily" | "monthly"
    action = Column(String, default="alert_only")
    fallback_model = Column(String, nullable=True)