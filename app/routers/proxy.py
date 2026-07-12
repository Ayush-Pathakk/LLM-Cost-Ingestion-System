from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import time
from app.database import get_db
from app.core.deps import get_workspace_id_from_key
from app.models.client import Client
from app.models.project import Project
from app.models.request_log import RequestLog
from app.models.budget_rule import BudgetRule
from app.schemas.proxy import ProxyRequest, ProxyResponse
from app.services.llm_providers import call_llm
from app.services.cost_calculator import calculate_cost
from app.services.budget_engine import check_budget
from app.services.budget_engine import check_budget, get_active_breached_rule

router = APIRouter(prefix="/v1/proxy", tags=["proxy"])


@router.post("", response_model=ProxyResponse)
def proxy_call(
    payload: ProxyRequest,
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

    actual_model = payload.model
    downgraded = False

    # Pre-flight budget check (only client-scoped rules can block a proxy call for now)
    if payload.client_id is not None:
        breached_rule = get_active_breached_rule(db, "client", payload.client_id)
        if breached_rule:
            if breached_rule.action == "block":
                raise HTTPException(
                    status_code=402,
                    detail=f"Budget exceeded for client {payload.client_id} ({breached_rule.period} limit ${breached_rule.budget_amount}). Request blocked."
                )
            elif breached_rule.action == "auto_downgrade":
                if not breached_rule.fallback_model:
                    raise HTTPException(status_code=500, detail="auto_downgrade rule has no fallback_model configured")
                actual_model = breached_rule.fallback_model
                downgraded = True

    try:
        start = time.time()
        response_text, tokens_used = call_llm(payload.provider, actual_model, payload.prompt)
        latency = round(time.time() - start, 3)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Provider call failed: {str(e)}")

    cost = calculate_cost(payload.provider, actual_model, tokens_used)

    log = RequestLog(
        workspace_id=workspace_id,
        client_id=payload.client_id,
        project_id=payload.project_id,
        source="proxy",
        provider=payload.provider,
        model=actual_model,
        tokens_used=tokens_used,
        cost=cost,
        latency=latency,
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    budget_alert = downgraded
    if payload.client_id is not None:
        rules = db.query(BudgetRule).filter(
            BudgetRule.scope_type == "client", BudgetRule.scope_id == payload.client_id
        ).all()
        for rule in rules:
            _, breached = check_budget(db, rule)
            if breached:
                budget_alert = True

    return ProxyResponse(
        response_text=response_text + (f"\n\n[Auto-downgraded to {actual_model} due to budget limit]" if downgraded else ""),
        tokens_used=tokens_used,
        cost=cost,
        request_log_id=log.id,
        budget_alert=budget_alert,
    )