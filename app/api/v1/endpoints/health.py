"""
Health check and root endpoints for the application.
"""
from pathlib import Path
from fastapi import APIRouter, Response, status
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/health", include_in_schema=False)
def health_check(response: Response):
    """Health check endpoint - not included in docs and no logging."""
    response.status_code = status.HTTP_200_OK
    return {"status": "healthy"}

@router.get("/", response_class=HTMLResponse)
def root():
    """Root endpoint that serves the API landing page."""
    # Read the HTML content from the template file
    with open(Path(__file__).parent.parent.parent.parent.parent / "app" / "templates" / "index.html", "r") as f:
        html_content = f.read()
    
    return html_content