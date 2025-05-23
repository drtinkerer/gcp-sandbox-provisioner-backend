from fastapi import FastAPI, Response, status
from fastapi.responses import HTMLResponse
from app.core.config import Config
from app.utils.logger import logger
import uvicorn
import logging

# Create an instance of the Config class
config = Config()

app = FastAPI(
    title="Cloud Sandbox Management API",
    version="1.0.0"
)

def register_log_filter() -> None:
    """
    Removes logs from health check endpoints to prevent log spam
    """
    class EndpointFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            return (
                record.args  # type: ignore
                and len(record.args) >= 3
                and record.args[2] not in ["/health", "/health-no-log"]  # type: ignore
            )

    logging.getLogger("uvicorn.access").addFilter(EndpointFilter())

# Register the log filter to prevent health endpoint logging
register_log_filter()

# Include routers
if config.ENABLE_GCP_PROVISIONER:
    from app.api.v1.endpoints import gcp
    app.include_router(gcp.router, prefix="/api/v1/gcp", tags=["Google Cloud Platform"])

if config.ENABLE_AWS_PROVISIONER:
    from app.api.v1.endpoints import aws
    app.include_router(aws.router, prefix="/api/v1/aws", tags=["Amazon Web Services"])

if config.ENABLE_AZURE_PROVISIONER:
    from app.api.v1.endpoints import azure
    app.include_router(azure.router, prefix="/api/v1/azure", tags=["Microsoft Azure"])

# Health check endpoint - not included in docs and no logging
@app.get("/health", include_in_schema=False)
def health_check(response: Response):
    response.status_code = status.HTTP_200_OK
    return {"status": "healthy"}


# Root endpoint
@app.get("/", response_class=HTMLResponse)
def root():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Cloud Sandbox Management API</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                color: #333;
            }
            h1 {
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }
            .card {
                background-color: #f9f9f9;
                border-left: 4px solid #3498db;
                padding: 15px;
                margin-bottom: 20px;
                border-radius: 4px;
            }
            a {
                color: #3498db;
                text-decoration: none;
                font-weight: bold;
            }
            a:hover {
                text-decoration: underline;
            }
            .links {
                margin-top: 30px;
            }
            .links a {
                display: inline-block;
                margin-right: 20px;
                background-color: #3498db;
                color: white;
                padding: 10px 15px;
                border-radius: 4px;
                transition: background-color 0.3s;
            }
            .links a:hover {
                background-color: #2980b9;
                text-decoration: none;
            }
        </style>
    </head>
    <body>
        <h1>Welcome to the Cloud Sandbox Management API</h1>
        
        <div class="card">
            <p>This API provides endpoints for managing cloud sandbox environments across multiple providers:</p>
            <ul>
                <li><strong>Google Cloud Platform</strong> - Create, manage, and delete GCP sandbox projects</li>
                <li><strong>Amazon Web Services</strong> - Manage AWS sandbox accounts</li>
                <li><strong>Microsoft Azure</strong> - Provision and control Azure sandbox resources</li>
            </ul>
        </div>
        
        <div class="links">
            <a href="/docs">API Documentation</a>
            <a href="/openapi.json">OpenAPI Schema</a>
        </div>
    </body>
    </html>
    """
    return html_content


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)