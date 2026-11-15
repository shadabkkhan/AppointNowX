from fastapi import FastAPI

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