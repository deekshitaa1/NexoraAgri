from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.farms import router as farms_router
from app.api.fields import router as fields_router
from app.api.observations import router as observations_router
from app.api.organizations import router as organizations_router
from app.api.predictions import router as predictions_router


app = FastAPI(
    title="Nexora Agri API",
    version="0.1.0",
    description="AI-powered agricultural decision intelligence platform.",
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:5177",
        "http://localhost:5178",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:5176",
        "http://127.0.0.1:5177",
        "http://127.0.0.1:5178",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# API ROUTES
# ---------------------------------------------------------

app.include_router(
    organizations_router,
    prefix="/api/v1",
)

app.include_router(
    farms_router,
    prefix="/api/v1",
)

app.include_router(
    fields_router,
    prefix="/api/v1",
)

app.include_router(
    observations_router,
    prefix="/api/v1",
)

app.include_router(
    predictions_router,
    prefix="/api/v1",
)


# ---------------------------------------------------------
# HEALTH
# ---------------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "nexora-agri-api",
        "version": "0.1.0",
    }
