from fastapi import FastAPI
from app.routes import user_routes

app = FastAPI(
    title="Device Systems Users API",
    description="API REST enfocada en la gestión del recurso usuarios.",
    version="1.0.0"
)

app.include_router(user_routes.router)

@app.get("/")
def read_root():
    return {"Mensaje": "Bienvenido a la API device_systems"}
