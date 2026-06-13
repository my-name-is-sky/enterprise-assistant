from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from pathlib import Path
import json
from src.api.middleware.auth import require_api_token

router = APIRouter(prefix="/admin", dependencies=[Depends(require_api_token)])
CLIENTS_FILE = Path(__file__).parents[3] / "config" / "clients.json"
CLIENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
if not CLIENTS_FILE.exists():
    CLIENTS_FILE.write_text(json.dumps({"clients": []}, indent=2))

class RegisterClientIn(BaseModel):
    client_id: str
    name: str
    metadata: dict = {}

@router.post("/clients/register")
def register_client(payload: RegisterClientIn):
    data = json.loads(CLIENTS_FILE.read_text())
    for c in data["clients"]:
        if c["client_id"] == payload.client_id:
            raise HTTPException(status_code=409, detail="client exists")
    entry = {"client_id": payload.client_id, "name": payload.name, "metadata": payload.metadata}
    data["clients"].append(entry)
    CLIENTS_FILE.write_text(json.dumps(data, indent=2))
    return {"status":"registered","client":entry}

@router.get("/clients")
def list_clients():
    data = json.loads(CLIENTS_FILE.read_text())
    return {"clients": data["clients"]}
