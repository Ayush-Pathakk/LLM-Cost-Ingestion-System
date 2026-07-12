from fastapi import FastAPI
from app.database import Base, engine
from app.routers import auth, clients, projects, ingest
from app.routers import auth, clients, projects, ingest, budget
from app import models  # noqa: F401
from app.routers import auth, clients, projects
from app.routers import auth, clients, projects, ingest, budget, proxy

app = FastAPI(title="LCIS", version="0.1.0")

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(projects.router)
app.include_router(ingest.router)
app.include_router(budget.router)
app.include_router(proxy.router)
