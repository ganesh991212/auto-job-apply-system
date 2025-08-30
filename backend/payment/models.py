from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer, DECIMAL, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    price = Column(DECIMAL(10,2), nullable=False)
    currency = Column(String(3), default='USD')
    duration_days = Column(Integer, nullable=False)
    job_apply_limit = Column(Integer)  # NULL for unlimited
    features = Column(ARRAY(String))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    subscriptions = relationship("UserSubscription", back_populates="plan")


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)  # Foreign key to auth service
    plan_id = Column(UUID(as_uuid=True), ForeignKey("subscription_plans.id"))
    payment_provider = Column(String(50))  # 'stripe', 'razorpay', 'paypal'
    subscription_id = Column(String(255))  # Provider's subscription ID
    status = Column(String(50), default='active')
    starts_at = Column(DateTime, nullable=False)
    ends_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
    payments = relationship("PaymentHistory", back_populates="subscription")


class PaymentHistory(Base):
    __tablename__ = "payment_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("user_subscriptions.id"))
    amount = Column(DECIMAL(10,2), nullable=False)
    currency = Column(String(3), default='USD')
    payment_provider = Column(String(50))
    transaction_id = Column(String(255))
    status = Column(String(50), default='pending')
    paid_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    subscription = relationship("UserSubscription", back_populates="payments")
