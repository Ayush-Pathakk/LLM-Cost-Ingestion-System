from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.ai_tool import AITool
from app.models.tool_usage_log import ToolUsageLog
from app.services.quota_engine import get_all_status

router = APIRouter(prefix="/v1/quota", tags=["quota"])

DEFAULT_TOOLS = [
    {"tool_name": "ChatGPT", "quota_limit": 10, "window_hours": 5},
    {"tool_name": "Claude", "quota_limit": 25, "window_hours": 5},
    {"tool_name": "Gemini", "quota_limit": 20, "window_hours": 5},
]

@router.post("/seed")
def seed_tools(db: Session = Depends(get_db)):
    for t in DEFAULT_TOOLS:
        if not db.query(AITool).filter(AITool.tool_name == t["tool_name"]).first():
            db.add(AITool(**t))
    db.commit()
    return {"status": "seeded"}

@router.post("/log/{tool_name}")
def log_use(tool_name: str, db: Session = Depends(get_db)):
    tool = db.query(AITool).filter(AITool.tool_name == tool_name).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found — seed tools first")
    db.add(ToolUsageLog(tool_id=tool.id))
    db.commit()
    return {"status": "logged", "tool": tool_name}

@router.get("/status")
def status(db: Session = Depends(get_db)):
    return get_all_status(db)