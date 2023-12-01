from config.database import db
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey
)

class PixKey(db.Model):
    __tablename__ = 'pixkeys'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    key_type_id = Column(Integer)
    key = Column(String(50), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    deleted_at = Column(DateTime)

    def __init__(
            self,
            user_id,
            key_type_id,
            key
    ):
        self.user_id = user_id
        self.key_type_id = key_type_id
        self.key = key
