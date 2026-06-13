from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from src.db import Base

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    metadata = Column(JSON, nullable=True)
    models = relationship("ClientModel", back_populates="client")

class ClientModel(Base):
    __tablename__ = "client_models"
    id = Column(Integer, primary_key=True, index=True)
    client_id_fk = Column(Integer, ForeignKey("clients.id"), nullable=False)
    model_id = Column(String, nullable=False)
    policy = Column(JSON, nullable=True)
    client = relationship("Client", back_populates="models")
