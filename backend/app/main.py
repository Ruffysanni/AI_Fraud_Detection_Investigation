
from fastapi import FastAPI

app = FastAPI(
    title="Fraud Detection and Investigation API",
    description="API for transaction fraud detection and investigation.",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "The API is running successfully.",
    }
