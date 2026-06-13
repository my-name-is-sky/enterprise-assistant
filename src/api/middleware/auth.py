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
