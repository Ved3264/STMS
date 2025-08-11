from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False) 
    email = Column(String(100), nullable=False, unique=True) 
    password = Column(String(100), nullable=False)  
    is_active = Column(Boolean,default=True)
    is_admin = Column(Boolean,default=False)
    created_at = Column(DateTime, default=datetime.utcnow)  
    last_active = Column(DateTime, nullable=True) 
