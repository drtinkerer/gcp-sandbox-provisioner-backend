import logging
import json
from datetime import datetime
from typing import Optional

# Custom JSON Formatter class
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_message = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name
        }
        return json.dumps(log_message)

# Global logger instance
_logger_instance: Optional[logging.Logger] = None

def get_logger() -> logging.Logger:
    """Get the configured logger instance with lazy initialization."""
    global _logger_instance
    if _logger_instance is None:
        # Create a logger object
        _logger_instance = logging.getLogger(__name__)
        
        # Set up the console handler with the JSON formatter
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(JsonFormatter())
        
        # Add the console handler to the logger
        _logger_instance.addHandler(console_handler)
        
        # Set the log level to DEBUG
        _logger_instance.setLevel(logging.DEBUG)
    
    return _logger_instance

# For backward compatibility, provide the logger instance
logger = get_logger()
