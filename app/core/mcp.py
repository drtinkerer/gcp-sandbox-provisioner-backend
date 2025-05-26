"""
Model Context Protocol (MCP) server setup for the application.
"""
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

def setup_mcp(app: FastAPI):
    """Initialize and mount MCP server."""
    mcp = FastApiMCP(
        app,
        name="My API MCP",
        description="Very cool MCP server",
        include_operations=["create_gcp_sandbox", "extend_gcp_sandbox"]
    )
    mcp.mount()
    return mcp