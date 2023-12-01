from config.database import db
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey
)

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    user_dest = Column(Integer, nullable=False)
    transaction_type_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(80), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    deleted_at = Column(DateTime)

    def __init__(self, user_id, user_dest, transaction_type_id, amount, description):
        self.user_id = user_id
        self.user_dest = user_dest
        self.transaction_type_id = transaction_type_id
        self.amount = amount
        self.description = description
