#!/usr/bin/env bash
set -euo pipefail
echo "Generating enterprise-assistant scaffold..."

# Create directories
mkdir -p docs skills/templates skills/examples src/api src/api/routes src/api/middleware src/enterprise logs docker k8s tests

# README.md
cat > README.md <<'EOF'
# enterprise-assistant

Enterprise-grade personal AI assistant with centralized management, skill system, and LLM configuration.

This repository is a starter scaffold that builds on the work-buddy design principles...
EOF

# Minimal core files (you can extend later)
cat > src/api/app.py <<'PY'
from fastapi import FastAPI
from src.api.middleware import audit
from src.api.routes import admin, skills, workflows

app = FastAPI(title="Enterprise Assistant API")
app.include_router(admin.router)
app.include_router(skills.router)
app.include_router(workflows.router)
app.middleware("http")(audit.audit_middleware)

@app.get("/health")
async def health():
    return {"status":"ok"}
PY

# Admin routes
cat > src/api/routes/admin.py <<'PY'
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
PY

# Skills routes
cat > src/api/routes/skills.py <<'PY'
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from pathlib import Path
import yaml
from src.api.middleware.auth import require_api_token

router = APIRouter(prefix="/skills", dependencies=[Depends(require_api_token)])
SKILLS_DIR = Path(__file__).parents[3] / "skills" / "examples"
SKILLS_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/")
def list_skills():
    skills = []
    for p in SKILLS_DIR.glob("*.yaml"):
        with open(p, 'r', encoding='utf-8') as f:
            skills.append(yaml.safe_load(f))
    return {"skills": skills}

class PublishSkillIn(BaseModel):
    filename: str
    content: str

@router.post("/publish")
def publish_skill(payload: PublishSkillIn):
    if ".." in payload.filename or "/" in payload.filename:
        raise HTTPException(status_code=400, detail="invalid filename")
    path = SKILLS_DIR / payload.filename
    path.write_text(payload.content, encoding='utf-8')
    return {"status":"published", "path": str(path)}
PY

# Workflows routes
cat > src/api/routes/workflows.py <<'PY'
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
PY

# Auth middleware
cat > src/api/middleware/auth.py <<'PY'
import os
from typing import Optional
from fastapi import Header, HTTPException

API_TOKEN = os.getenv("EA_API_TOKEN", "devtoken")

async def require_api_token(x_api_token: Optional[str] = Header(None)):
    if x_api_token is None:
        raise HTTPException(status_code=401, detail="Missing X-API-TOKEN header")
    if x_api_token != API_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")
    return True
PY

# Audit middleware
cat > src/api/middleware/audit.py <<'PY'
from fastapi import Request
import time
from pathlib import Path
import json

AUDIT_LOG = Path(__file__).parents[3] / "logs" / "audit.log"
AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)

async def audit_middleware(request: Request, call_next):
    start = time.time()
    resp = await call_next(request)
    end = time.time()
    entry = {"path": str(request.url.path), "method": request.method, "status_code": resp.status_code, "duration_ms": int((end-start)*1000)}
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\\n")
    return resp
PY

# Example skills
cat > skills/examples/client_management.yaml <<'YML'
name: client-management
description: "客户管理示例"
steps:
  - id: collect
    type: code
    description: "收集客户数据"
  - id: analyze
    type: agent
    description: "用LLM分析"
YML

cat > skills/examples/morning_routine.yaml <<'YML'
name: morning-routine
description: "早晨例程"
steps:
  - id: gather
    type: code
    description: "收集上下文"
  - id: plan
    type: agent
    description: "生成日计划"
YML

# config samples
mkdir -p config
cat > config/config.example.yaml <<'CFG'
llm:
  provider: "anthropic"
  api_key: "REPLACE_ME"
  default_model: "claude-2"

enterprise:
  org_name: "ACME Corp"
  admin_contact: "admin@acme.example"
  audit_enabled: true
CFG

echo "Scaffold created."
