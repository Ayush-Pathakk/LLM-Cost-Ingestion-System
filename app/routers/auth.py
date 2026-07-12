from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.workspace import Workspace
from app.models.api_key import APIKey
from app.schemas.user import UserRegister
from app.schemas.workspace import RegisterResponse
from app.core.security import hash_password, generate_api_key

router = APIRouter(prefix="/v1/auth", tags=["auth"])

@router.post("/register", response_model=RegisterResponse)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(name=payload.name, email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    workspace = Workspace(owner_user_id=user.id, workspace_name=payload.workspace_name)
    db.add(workspace)
    db.commit()
    db.refresh(workspace)

    key = APIKey(workspace_id=workspace.id, key_type="ingestion", key_value=generate_api_key())
    db.add(key)
    db.commit()
    db.refresh(key)

    return RegisterResponse(user=user, workspace=workspace, ingestion_key=key.key_value)