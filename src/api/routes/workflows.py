from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api.middleware.auth import require_api_token
from typing import Dict

router = APIRouter(prefix="/workflows", dependencies=[Depends(require_api_token)])

class RunWorkflowIn(BaseModel):
    workflow_id: str
    params: Dict = {}

@router.post("/run")
def run_workflow(payload: RunWorkflowIn):
    return {"status":"started", "workflow_id": payload.workflow_id}
