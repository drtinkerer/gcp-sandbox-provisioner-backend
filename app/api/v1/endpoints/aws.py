from fastapi import APIRouter

router = APIRouter()

@router.post("/create")
def create_aws_sandbox():
    """
    Creates a sandbox environment in AWS.
    """
    return {"message": "AWS sandbox provisioner is work in progress."}

@router.delete("/delete")
def delete_aws_sandbox():
    """
    Deletes a sandbox environment in AWS.
    """
    return {"message":"AWS sandbox provisioner is work in progress."}
