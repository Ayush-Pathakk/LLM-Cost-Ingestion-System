from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.request_log import RequestLog
from app.models.budget_rule import BudgetRule

def _period_start(period: str) -> datetime:
    now = datetime.utcnow()
    if period == "daily":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    if period == "monthly":
        return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    raise ValueError(f"Unknown period: {period}")

def get_spend(db: Session, scope_type: str, scope_id: int, period: str) -> float:
    since = _period_start(period)
    query = db.query(func.coalesce(func.sum(RequestLog.cost), 0.0)).filter(RequestLog.timestamp >= since)

    if scope_type == "client":
        query = query.filter(RequestLog.client_id == scope_id)
    elif scope_type == "project":
        query = query.filter(RequestLog.project_id == scope_id)
    else:
        raise ValueError(f"Unknown scope_type: {scope_type}")

    return float(query.scalar())

def check_budget(db: Session, rule: BudgetRule) -> tuple[float, bool]:
    spend = get_spend(db, rule.scope_type, rule.scope_id, rule.period)
    is_breached = spend >= rule.budget_amount
    return spend, is_breached

def get_active_breached_rule(db: Session, scope_type: str, scope_id: int) -> BudgetRule | None:
    """Returns the first breached, non-alert-only rule for this scope, or None."""
    rules = db.query(BudgetRule).filter(
        BudgetRule.scope_type == scope_type, BudgetRule.scope_id == scope_id
    ).all()
    for rule in rules:
        spend, breached = check_budget(db, rule)
        if breached and rule.action != "alert_only":
            return rule
    return None