from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.core.deps import get_workspace_id_from_key
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientOut

router = APIRouter(prefix="/v1/clients", tags=["clients"])

@router.post("", response_model=ClientOut)
def create_client(
    payload: ClientCreate,
    workspace_id: int = Depends(get_workspace_id_from_key),
    db: Session = Depends(get_db),
):
    client = Client(workspace_id=workspace_id, client_name=payload.client_name, markup_percentage=payload.markup_percentage)
    db.add(client)
    db.commit()
    db.refresh(client)
    return client

@router.get("", response_model=List[ClientOut])
def list_clients(
    workspace_id: int = Depends(get_workspace_id_from_key),
    db: Session = Depends(get_db),
):
    return db.query(Client).filter(Client.workspace_id == workspace_id).all()