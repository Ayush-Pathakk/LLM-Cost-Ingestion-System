from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    project_name = Column(String, nullable=False)
    