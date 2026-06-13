from fastapi import Request
import time
from pathlib import Path
import json

AUDIT_LOG = Path(__file__).parents[4] / "logs" / "audit.log"
AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)

async def audit_middleware(request: Request, call_next):
    start = time.time()
    resp = await call_next(request)
    end = time.time()
    entry = {
        "path": str(request.url.path),
        "method": request.method,
        "status_code": resp.status_code,
        "duration_ms": int((end - start)*1000)
    }
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return resp
