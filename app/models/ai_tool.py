from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class AITool(Base):
    __tablename__ = "ai_tools"

    id = Column(Integer, primary_key=True, index=True)
    tool_name = Column(String, unique=True, nullable=False)   # "ChatGPT", "Claude", "Gemini"
    quota_limit = Column(Integer, nullable=False)              # approx messages per window
    window_hours = Column(Integer, default=5)                  # rolling window length