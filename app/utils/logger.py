import logging
import json
from datetime import datetime

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

# Create a logger object
logger = logging.getLogger(__name__)

# Set up the console handler with the JSON formatter
console_handler = logging.StreamHandler()
console_handler.setFormatter(JsonFormatter())

# Add the console handler to the logger
logger.addHandler(console_handler)

# Set the log level to INFO
logger.setLevel(logging.DEBUG)
