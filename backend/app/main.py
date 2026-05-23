from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import SessionLocal, init_db
from app.memory_guard import seed_default_rules
from app.routes import routers

app = FastAPI(title="Thesis Agent MVP", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_db()
    db = SessionLocal()
    seed_default_rules(db)
    db.close()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "Thesis Agent MVP"}


for router in routers:
    app.include_router(router)
