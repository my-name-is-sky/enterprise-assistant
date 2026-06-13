from fastapi import Request
import time
from pathlib import Path
import json
from src.db import SessionLocal
from src.enterprise.models import AuditLog

AUDIT_LOG = Path(__file__).parents[4] / 'logs' / 'audit.log'
AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)

async def audit_middleware(request: Request, call_next):
    start = time.time()
    try:
        resp = await call_next(request)
    except Exception as e:
        duration = int((time.time() - start)*1000)
        entry = {
            'path': str(request.url.path),
            'method': request.method,
            'status_code': 500,
            'duration_ms': duration,
            'error': str(e)
        }
        try:
            with open(AUDIT_LOG, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
            db = SessionLocal()
            db.add(AuditLog(path=entry['path'], method=entry['method'], status_code=entry['status_code'], duration_ms=entry['duration_ms'], user=getattr(request.state, 'user', None), role=getattr(request.state, 'role', None)))
            db.commit()
        except Exception:
            pass
        finally:
            try:
                db.close()
            except Exception:
                pass
        raise

    end = time.time()
    duration = int((end - start)*1000)
    entry = {
        'path': str(request.url.path),
        'method': request.method,
        'status_code': resp.status_code,
        'duration_ms': duration
    }
    try:
        with open(AUDIT_LOG, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    except Exception:
        pass

    try:
        db = SessionLocal()
        db.add(AuditLog(path=entry['path'], method=entry['method'], status_code=entry['status_code'], duration_ms=entry['duration_ms'], user=getattr(request.state, 'user', None), role=getattr(request.state, 'role', None)))
        db.commit()
    except Exception:
        pass
    finally:
        try:
            db.close()
        except Exception:
            pass

    return resp
