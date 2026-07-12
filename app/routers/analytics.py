from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.core.deps import get_workspace_id_from_key
from app.models.request_log import RequestLog
from app.models.client import Client

router = APIRouter(prefix="/v1/analytics", tags=["analytics"])

@router.get("/summary")
def summary(workspace_id: int = Depends(get_workspace_id_from_key), db: Session = Depends(get_db)):
    total_cost = db.query(func.coalesce(func.sum(RequestLog.cost), 0.0)).filter(RequestLog.workspace_id == workspace_id).scalar()
    total_requests = db.query(func.count(RequestLog.id)).filter(RequestLog.workspace_id == workspace_id).scalar()
    total_tokens = db.query(func.coalesce(func.sum(RequestLog.tokens_used), 0)).filter(RequestLog.workspace_id == workspace_id).scalar()
    return {"total_cost": round(total_cost, 6), "total_requests": total_requests, "total_tokens": total_tokens}

@router.get("/cost-by-client")
def cost_by_client(workspace_id: int = Depends(get_workspace_id_from_key), db: Session = Depends(get_db)):
    rows = (
        db.query(Client.id, Client.client_name, Client.markup_percentage,
                  func.coalesce(func.sum(RequestLog.cost), 0.0).label("cost"))
        .outerjoin(RequestLog, RequestLog.client_id == Client.id)
        .filter(Client.workspace_id == workspace_id)
        .group_by(Client.id)
        .all()
    )
    return [{"client_id": r[0], "client_name": r[1], "markup": r[2], "cost": round(r[3], 6)} for r in rows]

@router.get("/cost-by-model")
def cost_by_model(workspace_id: int = Depends(get_workspace_id_from_key), db: Session = Depends(get_db)):
    rows = (
        db.query(RequestLog.provider, RequestLog.model,
                  func.sum(RequestLog.cost).label("cost"), func.sum(RequestLog.tokens_used).label("tokens"))
        .filter(RequestLog.workspace_id == workspace_id)
        .group_by(RequestLog.provider, RequestLog.model)
        .all()
    )
    return [{"provider": r[0], "model": r[1], "cost": round(r[2], 6), "tokens": r[3]} for r in rows]

@router.get("/logs")
def recent_logs(limit: int = 50, workspace_id: int = Depends(get_workspace_id_from_key), db: Session = Depends(get_db)):
    logs = (
        db.query(RequestLog)
        .filter(RequestLog.workspace_id == workspace_id)
        .order_by(RequestLog.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [{
        "id": l.id, "source": l.source, "provider": l.provider, "model": l.model,
        "tokens_used": l.tokens_used, "cost": l.cost, "client_id": l.client_id,
        "timestamp": l.timestamp.isoformat() if l.timestamp else None,
    } for l in logs]