from fastapi import FastAPI

app = FastAPI(
    title="Nexora Agri API",
    version="0.1.0",
    description="AI-powered agricultural decision intelligence platform.",
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "nexora-agri-api",
        "version": "0.1.0",
    }
