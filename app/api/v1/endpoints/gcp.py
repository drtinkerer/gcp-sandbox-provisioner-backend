from fastapi import APIRouter, HTTPException
from app.models.gcp_base_models import SandboxCreate, SandboxExtend
from app.core.config import Config
from app.services.gcp_sandbox import GCPSandboxService
from app.utils.logger import logger
from app.utils.utils import generate_sandbox_id
from datetime import timedelta, datetime, UTC
from google.protobuf.timestamp_pb2 import Timestamp


config = Config()

router = APIRouter()

@router.post("/create")
def create_gcp_sandbox(user_data: SandboxCreate):
    """
    Create a new sandbox environment for a given project.

    This endpoint creates a new sandbox environment for the specified project by provisioning 
    a cloud project and linking it to the appropriate folder. The sandbox includes cloud resources 
    and configurations based on the provided details. Additionally, it may involve adding team members 
    and setting specific access permissions as per the request.

    **Request Body:**
    - `user_email`: The email address of the user initiating the request (e.g., `user@example.com`).
    - `team_name`: The name of the team for which the sandbox environment is being requested.
    - `requested_duration_hours`: The number of hours for which the sandbox environment is requested.
    - `request_description`: A brief description of the request, such as the purpose of the sandbox (e.g., `"POC On XYZ"`).
    - `additional_users`: A list of additional users who need access to the sandbox environment. Default is an empty list.

    **Responses:**
    - `200 Created`: If the sandbox environment was successfully created.
    - `400 Bad Request`: If the request contains invalid data or required fields are missing.
    - `500 Internal Server Error`: If there is an issue with the cloud provider during the sandbox creation process.
    """
    user_email = user_data.user_email
    team_name = user_data.team_name
    requested_duration_hours = int(user_data.requested_duration_hours)
    request_description = user_data.request_description
    folder_id = config.AUTHORIZED_TEAM_FOLDERS[team_name]
    all_users = [user_email] + user_data.additional_users
    user_email_prefix = user_email.split("@")[0].replace(".", "-")

    # Check active sandboxes
    active_projects_count = GCPSandboxService.get_active_projects_count(user_email_prefix, folder_id)
    if active_projects_count >= config.MAX_ALLOWED_PROJECTS_PER_USER:
        logger.error(f"User {user_email} has reached maximum number of allowed active sandbox projects {config.MAX_ALLOWED_PROJECTS_PER_USER}.")
        raise HTTPException(status_code=400, detail=f"ERROR 400: User {user_email} has reached maximum number of allowed active sandbox projects ({config.MAX_ALLOWED_PROJECTS_PER_USER}).")

    request_time = datetime.now(UTC)

    delta = timedelta(hours=requested_duration_hours)
    expiry_timestamp = Timestamp()
    expiry_timestamp.FromDatetime(request_time + delta)

    project_id = generate_sandbox_id(user_email, request_time)

    logger.info(f"Handling sandbox project creation event for {user_email}...")
    create_project_response = GCPSandboxService.create_sandbox_project(project_id, folder_id)
    logger.info(f"Successfuly created project {project_id}.")

    logger.info(f"Linking project {project_id} to billing account...")
    updated_project_billing_response = GCPSandboxService.update_project_billing_info(project_id)
    logger.info(f"Successfuly linked project {project_id} to billing account.")

    logger.info(f"Creating deletion task for Project {project_id} on Google Cloud Tasks queue...")
    create_deletion_task_response = GCPSandboxService.create_deletion_task(project_id, project_id, expiry_timestamp)
    logger.info(f"Successfully created deletion task for Project {project_id} on Google Cloud Tasks queue.")

    logger.info(f"Assigning IAM role for {all_users} to project {project_id}...")
    iam_role_assignment_response = GCPSandboxService.set_sandbox_users_iam_role(all_users,project_id)
    logger.info(f"Successfuly asigned owner role to {all_users} for project {project_id}.")

    return {
        "detail": "Sandbox project provisioned succesfully",
        "user_email": user_email,
        "additional_users": user_data.additional_users,
        "team_name": team_name,
        "project_id": project_id,
        "folder_id": folder_id,
        "request_description": request_description,
        "billing_enabled": updated_project_billing_response.billing_enabled,
        "project_url": f"https://console.cloud.google.com/welcome?project={project_id}",
        "created_at": create_project_response.create_time.strftime("%Y-%d-%m %H:%M:%S UTC"),
        "expires_at": create_deletion_task_response.schedule_time.strftime("%Y-%d-%m %H:%M:%S UTC")
    }

@router.delete("/delete/{project_id}")
def delete_gcp_sandbox(project_id: str):
    """
    Delete the sandbox environment for a given project.

    This endpoint will delete the sandbox environment associated with the specified project.
    It involves removing the cloud project and associated resources, as well as disassociating 
    any billing or folder information linked to the project.

    **Parameters:**
    - `project_id`: The ID of the project whose sandbox environment needs to be deleted.

    **Responses:**
    - `200 OK`: If the sandbox environment was successfully deleted.
    - `400 Bad Request`: If the project_id is invalid or the project cannot be found.
    - `500 Internal Server Error`: If there is an issue with the cloud provider during the deletion process.
    """

    logger.info(f"Unlinking project {project_id} from associated billing account...")
    GCPSandboxService.unlink_project_billing_info(project_id)
    logger.info(f"Handling sandbox project deletion event for {project_id}")
    delete_sandbox_project_response = GCPSandboxService.delete_sandbox_project(project_id)
    logger.info(f"Succssfully deleted Project {project_id}.")

    return {
        "detail": "Sandbox project deleted succesfully",
        "project_id": project_id,
        "deleted_at": delete_sandbox_project_response.delete_time.strftime("%Y-%d-%m %H:%M:%S UTC")
    }


@router.post("/extend")
def extend_gcp_sandbox(user_data: SandboxExtend):
    """
    Extends the duration of an active sandbox project.

    This endpoint allows users to extend the deletion/expiry of an active sandbox project by a specified number of hours. 
    It should be triggered before the original scheduled expiry time to prevent automatic deletion.

    **Request Body:**
    - `project_id`: The ID of the project for which the sandbox duration needs to be extended.
    - `extend_by_hours`: The number of hours by which to extend the sandbox project’s expiry time.

    **Response:**
    - `200 OK`: A dictionary containing the project details, including the project ID and the new expiry time after extension.
    - `400 Bad Request`: If the request data is invalid or missing required fields.
    - `500 Internal Server Error`: If there is a server error while processing the extension.
    """

    project_id = user_data.project_id
    extend_by_hours = user_data.extend_by_hours
    cloud_tasks_queue_id = config.CLOUD_TASKS_DELETION_QUEUE_ID
    try:
        task_id = GCPSandboxService.list_cloud_tasks(project_id)
    except:
        task_id = f"{cloud_tasks_queue_id}/tasks/{project_id}"

    new_expiry_timestamp_proto = Timestamp()
    current_expiry_timestamp = GCPSandboxService.get_cloud_task_expiry_time(task_id)
    new_expiry_timestamp_proto.FromSeconds(current_expiry_timestamp + (3600 * extend_by_hours))

    # Delete old task
    logger.info("Deleting task")
    GCPSandboxService.delete_cloud_task(task_id)
    logger.info("Deleting task success")

    # Create new task with updated expiry time
    logger.info("Creating updated task with new expiry")
    random_suffix = int(datetime.now(UTC).timestamp())
    updated_task_name = f"{project_id}-extended-{random_suffix}"
    create_deletion_task_response = GCPSandboxService.create_deletion_task(project_id, updated_task_name, new_expiry_timestamp_proto)
    logger.info("Creating updated task with new expiry success")
    logger.info(create_deletion_task_response)

    return {
        "detail": f"Sandbox project expiry extended by {extend_by_hours} hours succesfully",
        "project_id": project_id,
        "new_expiry": create_deletion_task_response.schedule_time.strftime("%Y-%d-%m %H:%M:%S UTC")
    }
