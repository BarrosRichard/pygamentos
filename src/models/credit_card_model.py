from config.database import db
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey
)

class CreditCard(db.Model):
    __tablename__ = 'credit_card'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    number = Column(String(16), nullable=False)
    validate = Column(String(7), nullable=False)
    cvv = Column(String(3), nullable=False)
    description = Column(String(60))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    deleted_at = Column(DateTime)

    def __init__(
        self,
        user_id,
        number,
        validate,
        cvv,
        description
    ):
        self.user_id = user_id
        self.number = number
        self.validate = validate
        self.cvv = cvv
        self.description = description