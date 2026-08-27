from fastapi import FastAPI

from app.api.organizations import router as organizations_router


app = FastAPI(
    title="Nexora Agri API",
    version="0.1.0",
    description="AI-powered agricultural decision intelligence platform.",
)


app.include_router(
    organizations_router,
    prefix="/api/v1",
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "nexora-agri-api",
        "version": "0.1.0",
    }
