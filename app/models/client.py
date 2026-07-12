from sqlalchemy import Column, Integer, String, ForeignKey, Float
from app.database import Base

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    client_name = Column(String, nullable=False)
    markup_percentage = Column(Float, default=0.0)
    