from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api.middleware.auth import require_api_token

router = APIRouter(prefix="/workflows", dependencies=[Depends(require_api_token)])

class RunWorkflowIn(BaseModel):
    workflow_id: str
    params: dict = {}

@router.post("/run")
def run_workflow(payload: RunWorkflowIn):
    # TODO: enqueue to background worker
    return {"status": "started", "workflow_id": payload.workflow_id}
