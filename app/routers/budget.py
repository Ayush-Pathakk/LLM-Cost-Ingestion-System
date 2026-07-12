from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.core.deps import get_workspace_id_from_key
from app.models.budget_rule import BudgetRule
from app.schemas.budget_rule import BudgetRuleCreate, BudgetRuleOut, BudgetStatusOut
from app.services.budget_engine import check_budget

router = APIRouter(prefix="/v1/budget", tags=["budget"])

@router.post("", response_model=BudgetRuleOut)
def create_rule(payload: BudgetRuleCreate, db: Session = Depends(get_db)):
    if payload.scope_type not in ("client", "project"):
        raise HTTPException(status_code=400, detail="scope_type must be 'client' or 'project'")
    if payload.period not in ("daily", "monthly"):
        raise HTTPException(status_code=400, detail="period must be 'daily' or 'monthly'")

    rule = BudgetRule(**payload.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule

@router.get("", response_model=List[BudgetRuleOut])
def list_rules(db: Session = Depends(get_db)):
    return db.query(BudgetRule).all()

@router.get("/status", response_model=List[BudgetStatusOut])
def budget_status(db: Session = Depends(get_db)):
    rules = db.query(BudgetRule).all()
    results = []
    for rule in rules:
        spend, breached = check_budget(db, rule)
        results.append(BudgetStatusOut(
            scope_type=rule.scope_type,
            scope_id=rule.scope_id,
            budget_amount=rule.budget_amount,
            period=rule.period,
            current_spend=spend,
            is_breached=breached,
        ))
    return results