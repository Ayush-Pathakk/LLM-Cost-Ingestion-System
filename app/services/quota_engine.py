from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.tool_usage_log import ToolUsageLog
from app.models.ai_tool import AITool

def get_usage_in_window(db: Session, tool: AITool) -> int:
    since = datetime.utcnow() - timedelta(hours=tool.window_hours)
    return db.query(func.count(ToolUsageLog.id)).filter(
        ToolUsageLog.tool_id == tool.id, ToolUsageLog.used_at >= since
    ).scalar()

def get_all_status(db: Session):
    tools = db.query(AITool).all()
    results = []
    for tool in tools:
        used = get_usage_in_window(db, tool)
        pct = min(100, round((used / tool.quota_limit) * 100)) if tool.quota_limit else 0
        results.append({
            "tool_name": tool.tool_name,
            "used": used,
            "quota_limit": tool.quota_limit,
            "window_hours": tool.window_hours,
            "pct_used": pct,
            "remaining": max(0, tool.quota_limit - used),
        })
    return results