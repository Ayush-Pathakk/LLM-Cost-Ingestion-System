from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.core.deps import get_workspace_id_from_key
from app.models.client import Client
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectOut

router = APIRouter(prefix="/v1/projects", tags=["projects"])

@router.post("", response_model=ProjectOut)
def create_project(
    payload: ProjectCreate,
    workspace_id: int = Depends(get_workspace_id_from_key),
    db: Session = Depends(get_db),
):
    client = db.query(Client).filter(Client.id == payload.client_id, Client.workspace_id == workspace_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found in this workspace")

    project = Project(client_id=payload.client_id, project_name=payload.project_name)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.get("", response_model=List[ProjectOut])
def list_projects(
    client_id: int,
    workspace_id: int = Depends(get_workspace_id_from_key),
    db: Session = Depends(get_db),
):
    client = db.query(Client).filter(Client.id == client_id, Client.workspace_id == workspace_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found in this workspace")
    return db.query(Project).filter(Project.client_id == client_id).all()