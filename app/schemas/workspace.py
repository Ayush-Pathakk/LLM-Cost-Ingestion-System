from pydantic import BaseModel
from app.schemas.user import UserOut

class WorkspaceOut(BaseModel):
    id: int
    workspace_name: str

    class Config:
        from_attributes = True

class APIKeyOut(BaseModel):
    id: int
    key_type: str
    key_value: str

    class Config:
        from_attributes = True

class RegisterResponse(BaseModel):
    user: UserOut = None
    workspace: WorkspaceOut
    ingestion_key: str

RegisterResponse.model_rebuild()