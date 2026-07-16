from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database import Base

class ToolUsageLog(Base):
    __tablename__ = "tool_usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    tool_id = Column(Integer, ForeignKey("ai_tools.id"), nullable=False)
    used_at = Column(DateTime(timezone=True), server_default=func.now())    