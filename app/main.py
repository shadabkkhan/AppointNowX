from fastapi import FastAPI
from app.core.config import settings
from app.routers.auth import router as auth_router

app = FastAPI(
    title="AppointNowX",
    description="AppointNowX - An Agentic AI dental appointment booking platform",
    version="1.0.0"
)

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "ok"
    }

app.include_router(
    auth_router,
    prefix=settings.api_v1_prefix,
)