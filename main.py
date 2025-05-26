"""
Main application entry point for the Cloud Sandbox Management API.
"""
# Standard library imports
import sys

# Third-party imports
import uvicorn

# Local application imports
from app.core.app_factory import create_app
from app.core.mcp import setup_mcp
from app.core.config import get_config

# Get the singleton config instance
config = get_config()

# Create the FastAPI application
app = create_app()

if __name__ == "__main__":
    # Initialize and mount MCP server
    mcp = setup_mcp(app)
    
    # Check if we're just testing startup time - this exits before running the server
    if "--check-startup-only" in sys.argv:
        print("Startup completed successfully")
        sys.exit(0)
    
    # Run the application
    uvicorn.run(app, host="0.0.0.0", port=8000)