from src.db import SessionLocal, init_db
from src.enterprise.models import Client, ClientModel
from sqlalchemy.exc import IntegrityError

# Initialize DB tables
init_db()

def register_client(client_id: str, name: str, metadata: dict):
    db = SessionLocal()
    try:
        c = Client(client_id=client_id, name=name, metadata=metadata)
        db.add(c)
        db.commit()
        db.refresh(c)
        return c
    except IntegrityError:
        db.rollback()
        c = db.query(Client).filter(Client.client_id == client_id).first()
        return c
    finally:
        db.close()

def list_clients():
    db = SessionLocal()
    try:
        return db.query(Client).all()
    finally:
        db.close()

def assign_model_to_client(client_id: str, model_id: str, policy: dict):
    db = SessionLocal()
    try:
        client = db.query(Client).filter(Client.client_id == client_id).first()
        if not client:
            return None
        cm = ClientModel(client_id_fk=client.id, model_id=model_id, policy=policy)
        db.add(cm)
        db.commit()
        db.refresh(cm)
        return cm
    finally:
        db.close()
