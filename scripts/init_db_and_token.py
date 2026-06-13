"""Utility: create initial DB and an admin API token"""
import os
from src.db import init_db, SessionLocal
from src.enterprise.models_auth import APIToken
import secrets

if __name__ == '__main__':
    print('Initializing DB...')
    init_db()
    db = SessionLocal()
    token = secrets.token_urlsafe(32)
    t = APIToken(token=token, role='admin', user='system')
    db.add(t)
    db.commit()
    print('Created API token (store this securely):')
    print(token)
    db.close()
