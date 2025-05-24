from pydantic_settings import BaseSettings
import json
from typing import Optional


class Config(BaseSettings):
    MAX_ALLOWED_PROJECTS_PER_USER: int
    AUTHORIZED_TEAM_FOLDERS: str
    BILLING_ACCOUNT_ID: str
    AUTHORIZED_DOMAIN_NAMES: str
    LOCATION: str
    SERVICE_ACCOUNT_EMAIL: str
    ORGANIZATION_ID: str
    CLOUD_TASKS_DELETION_QUEUE_ID: str
    CLOUDRUN_SERVICE_ID: str
    ENABLE_GCP_PROVISIONER: bool
    ENABLE_AWS_PROVISIONER: bool
    ENABLE_AZURE_PROVISIONER: bool
    
    _parsed_team_folders: Optional[dict] = None
    
    class Config:
        # env_file = None
        # For local development, point this to custom .env file
        # If ENVIRONMENT Variables are not present in system OS,
        # then config will get picked up from .env file
        # Recommended way is to use docker for development and mount .env
        env_file = [".env", "../.env"]  # Try both current directory and parent directory

    def __init__(self, **kwargs):
        """
        Initialize the config object.

        Note: Config values are loaded from environment variables. If a variable
        is not set, it will be loaded from the .env file if present.
        """
        super().__init__(**kwargs)
        # Cache the parsed JSON to avoid repeated parsing
        if self._parsed_team_folders is None:
            self._parsed_team_folders = json.loads(self.AUTHORIZED_TEAM_FOLDERS)
    
    @property
    def parsed_team_folders(self) -> dict:
        """Get parsed team folders, using cached version if available."""
        if self._parsed_team_folders is None:
            self._parsed_team_folders = json.loads(self.AUTHORIZED_TEAM_FOLDERS)
        return self._parsed_team_folders


# Singleton pattern to prevent multiple instantiations
_config_instance: Optional[Config] = None

def get_config() -> Config:
    """Get the singleton config instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
        # Replace the string with parsed dict to avoid repeated JSON parsing
        _config_instance.AUTHORIZED_TEAM_FOLDERS = _config_instance.parsed_team_folders
    return _config_instance
