from database.configs.base import Base
from sqlalchemy import text, Column, String, Integer, select, update, delete, Boolean, TIMESTAMP

class UserModel(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    accepts_communications = Column(Boolean, nullable=False, default=False)
    phone_number = Column(String, nullable=False)
    created_at = Column(TIMESTAMP)
    # updated_at = Column(TIMESTAMP)