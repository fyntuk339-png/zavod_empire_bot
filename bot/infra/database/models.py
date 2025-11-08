# bot/infra/database/models.py

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=True, index=True)
    first_name = Column(String(255))
    last_name = Column(String(255), nullable=True)
    language = Column(String(5), default="ru")
    
    # Реферальная система
    referral_code = Column(String(16), unique=True, index=True)
    invited_by_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    
    # Завод
    factory_level = Column(Integer, default=1)
    factory_capacity = Column(Integer, default=10)
    workers_count = Column(Integer, default=0)
    
    # Валюта
    soft_currency = Column(Integer, default=0)  # Мягкая валюта
    hard_currency = Column(Integer, default=0)  # Твёрдая валюта
    
    # Статистика
    total_referrals = Column(Integer, default=0)
    total_purchases = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    
    # Флаги
    is_premium = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Отношения
    referrals = relationship("User", remote_side=[invited_by_id], backref="inviter")
    auctions = relationship("Auction", back_populates="creator")
    purchases = relationship("Purchase", back_populates="user")

class Auction(Base):
    """Модель аукциона"""
    __tablename__ = "auctions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    creator_id = Column(Integer, ForeignKey("users.user_id"), index=True)
    
    # Данные карточки
    photo_file_id = Column(String(255), nullable=True)
    description = Column(Text)
    characteristics = Column(JSON, default=dict)  # {"strength": 5, "charm": 3, ...}
    
    # Цена и статус
    base_price = Column(Integer, default=100)
    current_price = Column(Integer, default=100)
    times_purchased = Column(Integer, default=0)  # Для формулы цены
    
    # Статус
    is_active = Column(Boolean, default=True, index=True)
    is_sold_out = Column(Boolean, default=False)
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    creator = relationship("User", back_populates="auctions")
    purchases = relationship("Purchase", back_populates="auction")

class Purchase(Base):
    """Модель покупки"""
    __tablename__ = "purchases"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.user_id"), index=True)
    auction_id = Column(String(36), ForeignKey("auctions.id"), index=True)
    
    # Данные
    price_paid = Column(Integer)
    idempotency_key = Column(String(64), unique=True, index=True)  # Защита от дупликатов
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    user = relationship("User", back_populates="purchases")
    auction = relationship("Auction", back_populates="purchases")

class ABTest(Base):
    """Модель A/B теста"""
    __tablename__ = "ab_tests"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    experiment_key = Column(String(64), unique=True, index=True)
    
    # Варианты
    variant_a_name = Column(String(255))
    variant_b_name = Column(String(255))
    
    # Статус
    is_active = Column(Boolean, default=True)
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    
    exposures = relationship("ABTestExposure", back_populates="test")

class ABTestExposure(Base):
    """Воздействие A/B теста"""
    __tablename__ = "ab_test_exposures"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    test_id = Column(String(36), ForeignKey("ab_tests.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), index=True)
    
    # Вариант
    variant = Column(String(1))  # 'A' или 'B'
    
    # Конверсия
    converted = Column(Boolean, default=False)
    conversion_value = Column(Float, nullable=True)
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    test = relationship("ABTest", back_populates="exposures")
