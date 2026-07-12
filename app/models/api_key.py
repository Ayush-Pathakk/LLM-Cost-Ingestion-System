from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from app.database import Base

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    key_type = Column(String, nullable=False)   # "proxy" | "ingestion"
    key_value = Column(String, unique=True, index=True, nullable=False)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    