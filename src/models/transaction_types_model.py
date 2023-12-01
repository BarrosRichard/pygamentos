from config.database import db
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Float
)

class TransactionTypes(db.Model):
    __tablename__ = 'transaction_types'

    id = Column(Integer, primary_key=True)
    description = Column(String(40), nullable=False)
    tax = Column(Float, default=0.0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    deleted_at = Column(DateTime)

    def __init__(
        self,
        description,
        tax
    ):
        self.description = description
        self.tax = tax