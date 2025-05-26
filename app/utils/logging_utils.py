"""
Logging utilities for the application.
"""
import logging

class EndpointFilter(logging.Filter):
    """Filter to remove health check endpoint logs to prevent log spam."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        return (
            record.args  # type: ignore
            and len(record.args) >= 3
            and record.args[2] not in ["/health", "/health-no-log"]  # type: ignore
        )

def setup_logging():
    """Configure logging for the application."""
    # Register the log filter to prevent health endpoint logging
    logging.getLogger("uvicorn.access").addFilter(EndpointFilter())