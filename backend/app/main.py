from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import init_db
from app.modules.firefly.router import router as firefly_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.transactions.router import router as transactions_router
from app.modules.assets.router import router as assets_router
from app.modules.liabilities.router import router as liabilities_router

app = FastAPI(title="Firefly Brain API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3010", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup() -> None:
    init_db()

@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "firefly-brain-api", "env": settings.app_env}

app.include_router(firefly_router, prefix="/api/firefly", tags=["Firefly III"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(transactions_router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(assets_router, prefix="/api/assets", tags=["Assets"])
app.include_router(liabilities_router, prefix="/api/liabilities", tags=["Liabilities"])
