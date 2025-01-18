from fastapi import FastAPI
from app.api.v1.endpoints import gcp, aws

from app.core.config import Config
from app.utils.logger import logger

# Create an instance of the Config class
config = Config()

app = FastAPI(
    title="Cloud Sandbox Management API",
    version="1.0.0"
)

# Include routers
app.include_router(gcp.router, prefix="/api/v1/gcp", tags=["GCP"])
app.include_router(aws.router, prefix="/api/v1/aws", tags=["AWS"])


# Root endpoint
@app.get("/")
def root():
    return {"message": "Welcome to the Sandbox API"}
