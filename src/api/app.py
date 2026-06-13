from fastapi import FastAPI
from src.api.middleware import audit
from src.api.routes import admin, skills, workflows

app = FastAPI(title="Enterprise Assistant API")

# Register routers
app.include_router(admin.router)
app.include_router(skills.router)
app.include_router(workflows.router)

# Register audit middleware
app.middleware("http")(audit.audit_middleware)

@app.get("/health")
async def health():
    return {"status": "ok"}
