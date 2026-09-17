from fastapi import FastAPI

from app.routes.device_routes import router as device_router
from app.routes.loan_routes import history_router, router as loan_router
from app.routes.user_routes import router as user_router

app = FastAPI(
    title="device_systems",
    description="API para gestionar usuarios, dispositivos y préstamos con FastAPI, SQLAlchemy y Alembic.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(device_router, prefix="/devices", tags=["Devices"])
app.include_router(loan_router, prefix="/loans", tags=["Loans"])
app.include_router(history_router, tags=["Loans"])


@app.get("/health")
def health_check():
    return {"status": "ok"}
