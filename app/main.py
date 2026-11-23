
from app.core.config import settings
from app.routers.auth import router as auth_router

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI(
    title="AppointNowX",
    description="AppointNowX - An Agentic AI dental appointment booking platform",
    version="1.0.0"
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    sanitized_errors = [
        {
            "type": error["type"],
            "loc": error["loc"],
            "msg": error["msg"],
        }
        for error in exc.errors()
    ]

    return JSONResponse(
        status_code=422,
        content={"detail": sanitized_errors},
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
