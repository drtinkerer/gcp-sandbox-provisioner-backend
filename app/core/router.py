"""
Router setup for the application.
"""
from fastapi import FastAPI
from app.core.config import get_config

# Get the singleton config instance
config = get_config()

def setup_routers(app: FastAPI):
    """Lazy load and setup routers based on configuration."""
    # Include health router
    from app.api.v1.endpoints import health
    app.include_router(health.router)
    
    # Include routers only when needed
    if config.ENABLE_GCP_PROVISIONER:
        from app.api.v1.endpoints import gcp
        app.include_router(gcp.router, prefix="/api/v1/gcp", tags=["Google Cloud Platform"])

    if config.ENABLE_AWS_PROVISIONER:
        from app.api.v1.endpoints import aws
        app.include_router(aws.router, prefix="/api/v1/aws", tags=["Amazon Web Services"])

    if config.ENABLE_AZURE_PROVISIONER:
        from app.api.v1.endpoints import azure
        app.include_router(azure.router, prefix="/api/v1/azure", tags=["Microsoft Azure"])