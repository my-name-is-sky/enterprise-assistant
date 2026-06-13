from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from src.api.middleware.auth import require_api_token
from src.enterprise import control_panel

router = APIRouter(prefix="/admin", dependencies=[Depends(require_api_token)])

class RegisterClientIn(BaseModel):
    client_id: str
    name: str
    metadata: Dict[str, Any] = {}

@router.post("/clients/register")
def register_client(payload: RegisterClientIn):
    c = control_panel.register_client(payload.client_id, payload.name, payload.metadata)
    return {"status": "registered", "client_id": c.client_id, "name": c.name}

@router.get("/clients")
def list_clients():
    clients = control_panel.list_clients()
    result = [{"client_id": c.client_id, "name": c.name, "metadata": c.metadata} for c in clients]
    return {"clients": result}

class DistributeModelIn(BaseModel):
    client_id: str
    model_id: str
    policy: Dict[str, Any] = {}

@router.post("/clients/distribute-model")
def distribute_model(payload: DistributeModelIn):
    cm = control_panel.assign_model_to_client(payload.client_id, payload.model_id, payload.policy)
    if cm is None:
        raise HTTPException(status_code=404, detail="client not found")
    return {"status": "ok", "model_assignment_id": cm.id}
