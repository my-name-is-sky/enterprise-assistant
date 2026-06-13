from fastapi import Request, Depends, HTTPException
from src.db import SessionLocal
from src.enterprise.models import APIToken
from typing import Optional

async def get_api_token(x_api_token: Optional[str] = None):
    if not x_api_token:
        raise HTTPException(status_code=401, detail="Missing X-API-TOKEN header")
    db = SessionLocal()
    try:
        t = db.query(APIToken).filter(APIToken.token == x_api_token).first()
        if not t:
            raise HTTPException(status_code=403, detail="Invalid token")
        return t
    finally:
        db.close()

async def require_api_token(token=Depends(get_api_token), request: Request = None):
    request.state.api_token = token
    request.state.role = token.role
    request.state.user = token.user
    return True

def require_role(allowed_roles):
    def _checker(request: Request = None):
        role = getattr(request.state, 'role', None)
        if role not in allowed_roles:
            raise HTTPException(status_code=403, detail='Forbidden')
        return True
    return _checker
