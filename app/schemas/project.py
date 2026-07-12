from pydantic import BaseModel

class ProjectCreate(BaseModel):
    client_id: int
    project_name: str

class ProjectOut(BaseModel):
    id: int
    client_id: int
    project_name: str

    class Config:
        from_attributes = True