from pydantic import BaseModel

class ClientCreate(BaseModel):
    client_name: str
    markup_percentage: float = 0.0

class ClientOut(BaseModel):
    id: int
    client_name: str
    markup_percentage: float

    class Config:
        from_attributes = True