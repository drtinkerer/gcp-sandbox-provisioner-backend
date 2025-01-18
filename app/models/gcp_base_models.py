from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List
from app.core.config import Config
config = Config()


class SandboxCreate(BaseModel):
    user_email: EmailStr = Field(
        ...,
        description=f"Email address of the user requesting the sandbox. User must belong to {config.AUTHORIZED_DOMAIN_NAMES}"
    )
    team_name: str = Field(
        ...,
        description=f"Name of the team to which the sandbox belongs. Team name must be one in {config.AUTHORIZED_TEAM_FOLDERS.keys()}"
    )
    requested_duration_hours: int = Field(
        2,
        description="Requested duration of the sandbox in hours."
    )
    request_description: str = Field(
        default="POC On ",
        description="Description for sandbox requirement."
    )
    additional_users: List[EmailStr] = Field(
        default=[],
        description="Optional list of additional users to grant access to the sandbox environment."
    )

    @field_validator('user_email')
    @classmethod
    def validate_user_email_domain(cls, validated_email: str) -> str:
        user_email_domain = validated_email.split("@")[1]
        if user_email_domain not in config.AUTHORIZED_DOMAIN_NAMES:
            raise ValueError(f"User {validated_email} doesn't belong to authorized domains {config.AUTHORIZED_DOMAIN_NAMES}")
        return validated_email

    @field_validator('additional_users')
    @classmethod
    def validate_additional_users_domains(cls, validated_emails: List[str]) -> List[str]:
        for email in validated_emails:
            user_email_domain = email.split("@")[1]
            if user_email_domain not in config.AUTHORIZED_DOMAIN_NAMES:
                raise ValueError(f"User {email} doesn't belong to authorized domains {config.AUTHORIZED_DOMAIN_NAMES}")
        return validated_emails

    @field_validator('team_name')
    @classmethod
    def validate_team_name(cls, validated_team_name: str) -> str:
        if validated_team_name not in config.AUTHORIZED_TEAM_FOLDERS.keys():
            raise ValueError(f"Team name {validated_team_name} is invalid. Required value must be one in {config.AUTHORIZED_TEAM_FOLDERS.keys()}")
        return validated_team_name

class SandboxExtend(BaseModel):
    project_id: str = Field(
        ...,
        description="ID of the project to be extended."
    )
    extend_by_hours: int = Field(
        4,
        description="Number of hours by which to extend the sandbox."
    )
