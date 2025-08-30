from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from decimal import Decimal


class SubscriptionCreateRequest(BaseModel):
    plan_id: str
    payment_provider: str  # 'stripe', 'razorpay', 'paypal'
    price_id: str  # Provider's price/plan ID


class SubscriptionResponse(BaseModel):
    id: str
    plan_name: str
    status: str
    starts_at: datetime
    ends_at: datetime
    job_apply_limit: Optional[int]
    features: List[str]


class PaymentHistoryResponse(BaseModel):
    id: str
    amount: Decimal
    currency: str
    payment_provider: str
    transaction_id: Optional[str]
    status: str
    paid_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class WebhookEvent(BaseModel):
    event_type: str
    data: dict


class MessageResponse(BaseModel):
    message: str
