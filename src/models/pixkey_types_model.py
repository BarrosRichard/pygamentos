from config.database import db
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime
)

class PixKeyType(db.Model):
    __tablename__ = 'pix_key_type'

    id = Column(Integer, primary_key=True)
    description = Column(String(50), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    def __init__(
        self,
        description
    ):
        self.description = description