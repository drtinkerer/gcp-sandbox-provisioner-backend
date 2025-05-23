from fastapi import APIRouter

router = APIRouter()

@router.post("/create")
def create_azure_sandbox():
    """
    Creates a sandbox environment in AZURE.
    """
    return {"message": "AZURE sandbox provisioner is work in progress."}

@router.delete("/delete")
def delete_azure_sandbox():
    """
    Deletes a sandbox environment in AZURE.
    """
    return {"message":"AZURE sandbox provisioner is work in progress."}
