from google.cloud import resourcemanager_v3, billing_v1, tasks_v2, run_v2
from app.core.config import Config
config = Config()


class GCPSandboxService:
    @staticmethod
    def create_sandbox_project(project_id, folder_id):
        """
        Creates a new Google Cloud Sandbox project with the given project_id and folder_id.

        Args:
            project_id (str): The ID of the project to be created.
            folder_id (str): The ID of the folder in which the project should be created.

        Returns:
            resourcemanager_v3.types.Operation: The operation object returned from the API.
        """
        client = resourcemanager_v3.ProjectsClient()

        project_request = resourcemanager_v3.CreateProjectRequest(
            project=resourcemanager_v3.Project(
                project_id=project_id,
                parent=folder_id,
                display_name=project_id
            )
        )

        operation = client.create_project(request=project_request)
        response = operation.result()

        # Handle the response
        return response

    @staticmethod
    def update_project_billing_info(project_id):
        """
        Links a Google Cloud Project with the given project_id to a billing account.

        Args:
            project_id (str): The ID of the project to be linked to a billing account.

        Returns:
            billing_v1.types.Operation: The operation object returned from the API.
        """
        billing_account_id = config.BILLING_ACCOUNT_ID
        client = billing_v1.CloudBillingClient()

        # Initialize request argument(s)
        request = billing_v1.UpdateProjectBillingInfoRequest(
            name=f"projects/{project_id}",
            project_billing_info=billing_v1.ProjectBillingInfo(
                billing_account_name=f"billingAccounts/{billing_account_id}"
            )
        )

        # Make the request
        response = client.update_project_billing_info(request=request)
        return response

    @staticmethod
    def unlink_project_billing_info(project_id):
        """
        Unlinks a Google Cloud Project with the given project_id from its associated billing account.

        Args:
            project_id (str): The ID of the project to be unlinked from its billing account.

        Returns:
            billing_v1.types.Operation: The operation object returned from the API.
        """
        client = billing_v1.CloudBillingClient()

        # Initialize request argument(s)
        request = billing_v1.UpdateProjectBillingInfoRequest(
            name=f"projects/{project_id}",
            project_billing_info=billing_v1.ProjectBillingInfo(
                billing_account_name=""
            )
        )

        # Make the request to unlink the billing account
        response = client.update_project_billing_info(request=request)
        return response

    @staticmethod
    def delete_sandbox_project(project_id):
        """
        Deletes a Google Cloud Project with the given project_id.

        Args:
            project_id (str): The ID of the project to be deleted.

        Returns:
            resourcemanager_v3.types.Operation: The operation object returned from the API.
        """
        client = resourcemanager_v3.ProjectsClient()

        # Initialize request argument(s)
        request = resourcemanager_v3.DeleteProjectRequest(
            name=f"projects/{project_id}"
        )

        # Make the request
        operation = client.delete_project(request=request)
        response = operation.result()

        # Handle the response
        return response

    @staticmethod
    def create_deletion_task(project_id, task_name, expiry_timestamp):
        """
        Creates a Cloud Task that will trigger the deletion of a sandbox project after a given duration.

        Args:
            project_id (str): The ID of the project to be deleted.
            task_name (str): The name of the task to be created.
            expiry_timestamp (google.protobuf.timestamp_pb2.Timestamp): The timestamp at which the task should be triggered.

        Returns:
            tasks_v2.types.Task: The task object returned from the API.
        """
        client = tasks_v2.CloudTasksClient()

        cloud_run_client = run_v2.ServicesClient()
        cloud_run_service_url = cloud_run_client.get_service(
            request=run_v2.GetServiceRequest(name=config.CLOUDRUN_SERVICE_ID)).uri

        cloud_tasks_queue_id = config.CLOUD_TASKS_DELETION_QUEUE_ID

        task_object = tasks_v2.Task(
            name=f"{cloud_tasks_queue_id}/tasks/{task_name}",
            http_request=tasks_v2.HttpRequest(
                url=f"{cloud_run_service_url}/api/v1/gcp/delete/{project_id}",
                http_method="DELETE",
                headers=[("Content-Type", "application/json")],
                oidc_token=tasks_v2.OidcToken(
                    service_account_email=config.SERVICE_ACCOUNT_EMAIL
                )
            ),
            schedule_time=expiry_timestamp
        )

        # Initialize request argument(s)
        request = tasks_v2.CreateTaskRequest(
            parent=cloud_tasks_queue_id,
            task=task_object
        )

        # Make the request
        response = client.create_task(request=request)

        # Handle the response
        return response

    @staticmethod
    def get_active_projects_count(user_email_prefix, folder_id):
        """
        Counts the number of active projects in a given folder belonging to a specific user.

        Args:
            user_email_prefix (str): The prefix of the user's email address.
            folder_id (str): The ID of the folder to search for projects.

        Returns:
            int: The number of active projects in the given folder belonging to the given user.
        """
        client = resourcemanager_v3.ProjectsClient()

        # Initialize request argument(s)
        request = resourcemanager_v3.ListProjectsRequest(
            parent=folder_id,
        )

        # Make the request
        page_result = client.list_projects(request=request)

        project_list = [response.project_id for response in page_result]

        count = 0
        for project in project_list:
            if user_email_prefix in project:
                count += 1
        return count

    @staticmethod
    def get_cloud_task_expiry_time(task_id):
        # Create a client
        """
        Retrieves the scheduled time of a Cloud Task.

        Args:
            task_id (str): The ID of the task to retrieve the schedule time for.

        Returns:
            int: The scheduled time of the task as a Unix timestamp.
        """
        client = tasks_v2.CloudTasksClient()

        # Initialize request argument(s)
        request = tasks_v2.GetTaskRequest(
            name=task_id
        )

        # Make the request
        response = client.get_task(request=request)

        # Handle the response
        return int(response.schedule_time.timestamp())

    @staticmethod
    def delete_cloud_task(task_id):
        """
        Deletes a Cloud Task with the given task_id.

        Args:
            task_id (str): The ID of the task to be deleted.

        Returns:
            tasks_v2.types.Task: The deleted task object returned from the API.
        """
        client = tasks_v2.CloudTasksClient()

        # Initialize request argument(s)
        request = tasks_v2.DeleteTaskRequest(
            name=task_id,
        )

        # Make the request
        response = client.delete_task(request=request)

        return response

    @staticmethod
    def list_cloud_tasks(project_id):
        """
        Retrieves the Cloud Task ID of a task scheduled to delete a sandbox project
        with the given project_id.

        Args:
            project_id (str): The ID of the project to retrieve the Cloud Task ID for.

        Returns:
            str: The ID of the Cloud Task scheduled to delete the project.
        """
        client = tasks_v2.CloudTasksClient()
        cloud_tasks_queue_id = config.CLOUD_TASKS_DELETION_QUEUE_ID

        # Initialize request argument(s)
        request = tasks_v2.ListTasksRequest(
            parent=cloud_tasks_queue_id
        )

        # Make the request
        page_result = client.list_tasks(request=request)

        # Handle the response
        for response in page_result:
            if project_id in response.name:
                return response.name
