from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.deps import get_workspace_id_from_key
from app.models.client import Client
from app.models.project import Project
from app.models.request_log import RequestLog
from app.schemas.ingestion import IngestionEvent, IngestionResponse
from app.services.cost_calculator import calculate_cost
from app.models.budget_rule import BudgetRule
from app.services.budget_engine import check_budget

router = APIRouter(prefix="/v1/ingest", tags=["ingestion"])

@router.post("", response_model=IngestionResponse)
def ingest_event(
    payload: IngestionEvent,
    workspace_id: int = Depends(get_workspace_id_from_key),
    db: Session = Depends(get_db),
):
    if payload.client_id is not None:
        client = db.query(Client).filter(Client.id == payload.client_id, Client.workspace_id == workspace_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found in this workspace")

    if payload.project_id is not None:
        project = db.query(Project).filter(Project.id == payload.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

    cost = calculate_cost(payload.provider, payload.model, payload.tokens_used)

    log = RequestLog(
        workspace_id=workspace_id,
        client_id=payload.client_id,
        project_id=payload.project_id,
        source=payload.source,
        provider=payload.provider,
        model=payload.model,
        tokens_used=payload.tokens_used,
        cost=cost,
        latency=payload.latency,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    
    budget_alert = False
    if payload.client_id is not None:
        rules = db.query(BudgetRule).filter(
            BudgetRule.scope_type == "client", BudgetRule.scope_id == payload.client_id
        ).all()
        for rule in rules:
            _, breached = check_budget(db, rule)
            if breached:
                budget_alert = True

    return IngestionResponse(request_log_id=log.id, cost=cost, budget_alert=budget_alert)