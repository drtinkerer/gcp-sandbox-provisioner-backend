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
if config.ENABLE_GCP_PROVISIONER:
    app.include_router(gcp.router, prefix="/api/v1/gcp", tags=["Google Cloud Platform"])

if config.ENABLE_AWS_PROVISIONER:
    app.include_router(aws.router, prefix="/api/v1/aws", tags=["Amazon Web Services"])

if config.ENABLE_AZURE_PROVISIONER:
    app.include_router(aws.router, prefix="/api/v1/azure", tags=["Microsoft Azure"])


# Root endpoint
@app.get("/")
def root():
    return {"message": "Welcome to the Sandbox API"}
