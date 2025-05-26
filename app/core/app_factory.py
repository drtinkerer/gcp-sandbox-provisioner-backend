"""
Application factory for creating and configuring the FastAPI application.
"""
from fastapi import FastAPI
from app.core.config import get_config
from app.utils.logging_utils import setup_logging
from app.core.router import setup_routers

# Get the singleton config instance
config = get_config()


def create_app() -> FastAPI:
    """
    Create and configure a FastAPI application instance.

    Returns:
        FastAPI: The configured FastAPI application.
    """
    # Create FastAPI application
    app = FastAPI(
        title="Cloud Sandbox Management API",
        version="1.0.0"
    )

    # Setup logging
    setup_logging()

    # Setup routers
    setup_routers(app)

    return app
