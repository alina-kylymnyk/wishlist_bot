from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    """User model"""
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    is_public = Column(Boolean, default=True)  # Public or private wishlist 
    created_at = Column(DateTime, default=datetime.utcnow)

    wishes = relationship('Wish', back_populates='user', cascade='all, delete-orphan')
    
    # Index for searching by username
    __table_args__ = (
         Index('idx_users_username', 'username'),
   ) 
    def __repr__(self):
                return f"<User(user_id={self.user_id}, username={self.username})>"


class Wish(Base):
    """Wish model"""
    __tablename__ = 'wishes'
    
    wish_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String(500), nullable=True)
    price = Column(String(100), nullable=True)  # Save as text for flexibility 
    image_file_id = Column(String(255), nullable=True)  # file_id from Telegram
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Connection(relation) with user
    user = relationship('User', back_populates='wishes')

    __table_args__ = (
        Index ('idx_user_created', 'user_id', 'created_at'), # To sort user preferences 
        Index ('idx_user_id', 'user_id')  # Для пошуку всіх бажань користувача 
    )
    
    def __repr__(self):
        return f"<Wish(wish_id={self.wish_id}, title={self.title}, user_id={self.user_id})>"