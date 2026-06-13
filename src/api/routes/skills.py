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
