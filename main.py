"""
Main application entry point for the Cloud Sandbox Management API.
"""
# Standard library imports
import logging
import sys
from pathlib import Path

# Third-party imports
import uvicorn
from fastapi import FastAPI, Response, status
from fastapi.responses import HTMLResponse
from fastapi_mcp import FastApiMCP

# Local application imports
from app.core.config import get_config
from app.utils.logger import get_logger

# Initialize logger
logger = get_logger()

# Get the singleton config instance
config = get_config()

# Create FastAPI application
app = FastAPI(
    title="Cloud Sandbox Management API",
    version="1.0.0"
)

class EndpointFilter(logging.Filter):
    """Filter to remove health check endpoint logs to prevent log spam."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        return (
            record.args  # type: ignore
            and len(record.args) >= 3
            and record.args[2] not in ["/health", "/health-no-log"]  # type: ignore
        )

# Register the log filter to prevent health endpoint logging
logging.getLogger("uvicorn.access").addFilter(EndpointFilter())

def setup_routers():
    """Lazy load and setup routers based on configuration."""
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

# Setup routers immediately after app creation
setup_routers()

# Health check endpoint - not included in docs and no logging
@app.get("/health", include_in_schema=False)
def health_check(response: Response):
    response.status_code = status.HTTP_200_OK
    return {"status": "healthy"}

# Root endpoint
@app.get("/", response_class=HTMLResponse)
def root():
    """Root endpoint that serves the API landing page."""
    # Read the HTML content from the template file
    with open(Path(__file__).parent / "app" / "templates" / "index.html", "r") as f:
        html_content = f.read()
    
    return html_content

if __name__ == "__main__":
    # Initialize and mount MCP server
    mcp = FastApiMCP(
        app,
        name="My API MCP",
        description="Very cool MCP server",
        include_operations=["create_gcp_sandbox", "extend_gcp_sandbox"]
    )
    mcp.mount()
    
    # Check if we're just testing startup time - this exits before running the server
    if "--check-startup-only" in sys.argv:
        print("Startup completed successfully")
        sys.exit(0)
    
    # Run the application
    uvicorn.run(app, host="0.0.0.0", port=8000)