from pydantic_settings import BaseSettings
import json


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
    class Config:
        # env_file = None
        # For local development, point this to custom .env file
        # If ENVIRONMENT Variables are not present in system OS,
        # then config will get picked up from .env file
        # Recommended way is to use docker for development and mount .env
        env_file = ".env"

    def __init__(self, **kwargs):
        """
        Initialize the config object.

        Note: Config values are loaded from environment variables. If a variable
        is not set, it will be loaded from the .env file if present.
        """
        super().__init__(**kwargs)
        # Load the AUTHORIZED_TEAM_FOLDERS from json string
        self.AUTHORIZED_TEAM_FOLDERS = json.loads(self.AUTHORIZED_TEAM_FOLDERS)
