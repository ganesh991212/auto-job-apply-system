from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
import stripe
import razorpay
import paypalrestsdk
import json

from database import get_db, engine
from models import Base, SubscriptionPlan, UserSubscription, PaymentHistory
from schemas import (
    SubscriptionCreateRequest, SubscriptionResponse, PaymentHistoryResponse,
    WebhookEvent, MessageResponse
)
from auth_middleware import get_current_user, require_role
from config import settings

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Auto Job Apply - Payment Service",
    description="Payment and subscription management service",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize payment providers
stripe.api_key = settings.stripe_secret_key

razorpay_client = razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))

paypalrestsdk.configure({
    "mode": settings.paypal_mode,
    "client_id": settings.paypal_client_id,
    "client_secret": settings.paypal_client_secret
})


@app.get("/plans", response_model=List[dict])
async def get_subscription_plans(db: Session = Depends(get_db)):
    """Get available subscription plans"""
    plans = db.query(SubscriptionPlan).filter(SubscriptionPlan.is_active == True).all()
    
    return [
        {
            "id": str(plan.id),
            "name": plan.name,
            "price": float(plan.price),
            "currency": plan.currency,
            "duration_days": plan.duration_days,
            "job_apply_limit": plan.job_apply_limit,
            "features": plan.features
        }
        for plan in plans
    ]


@app.post("/subscribe", response_model=dict)
async def create_subscription(
    subscription_data: SubscriptionCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new subscription"""
    user_id = current_user["user_id"]
    
    # Get subscription plan
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == subscription_data.plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found"
        )
    
    try:
        if subscription_data.payment_provider == "stripe":
            return await _create_stripe_subscription(user_id, plan, subscription_data, db)
        elif subscription_data.payment_provider == "razorpay":
            return await _create_razorpay_subscription(user_id, plan, subscription_data, db)
        elif subscription_data.payment_provider == "paypal":
            return await _create_paypal_subscription(user_id, plan, subscription_data, db)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported payment provider"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create subscription: {str(e)}"
        )


@app.get("/subscription", response_model=SubscriptionResponse)
async def get_current_subscription(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's current subscription"""
    user_id = current_user["user_id"]
    
    subscription = db.query(UserSubscription).filter(
        UserSubscription.user_id == user_id,
        UserSubscription.status == "active",
        UserSubscription.ends_at > datetime.utcnow()
    ).first()
    
    if not subscription:
        # Return free plan info
        free_plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.name == "Free").first()
        return SubscriptionResponse(
            id="free",
            plan_name="Free",
            status="active",
            starts_at=datetime.utcnow(),
            ends_at=datetime.utcnow() + timedelta(days=365),
            job_apply_limit=5,
            features=free_plan.features if free_plan else ["5 job applications per day"]
        )
    
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == subscription.plan_id).first()
    
    return SubscriptionResponse(
        id=str(subscription.id),
        plan_name=plan.name if plan else "Unknown",
        status=subscription.status,
        starts_at=subscription.starts_at,
        ends_at=subscription.ends_at,
        job_apply_limit=plan.job_apply_limit if plan else None,
        features=plan.features if plan else []
    )


@app.get("/billing-history", response_model=List[PaymentHistoryResponse])
async def get_billing_history(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's billing history"""
    user_id = current_user["user_id"]
    
    payments = db.query(PaymentHistory).filter(
        PaymentHistory.user_id == user_id
    ).order_by(PaymentHistory.created_at.desc()).all()
    
    return [PaymentHistoryResponse.from_orm(payment) for payment in payments]


@app.post("/webhook/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhooks"""
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle the event
    if event['type'] == 'invoice.payment_succeeded':
        await _handle_payment_success(event['data']['object'], "stripe", db)
    elif event['type'] == 'invoice.payment_failed':
        await _handle_payment_failure(event['data']['object'], "stripe", db)
    
    return {"status": "success"}


@app.post("/webhook/razorpay")
async def razorpay_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Razorpay webhooks"""
    payload = await request.body()
    
    try:
        # Verify webhook signature
        razorpay_client.utility.verify_webhook_signature(
            payload.decode(), 
            request.headers.get('x-razorpay-signature'), 
            settings.razorpay_webhook_secret
        )
        
        event = json.loads(payload)
        
        if event['event'] == 'payment.captured':
            await _handle_payment_success(event['payload']['payment']['entity'], "razorpay", db)
        elif event['event'] == 'payment.failed':
            await _handle_payment_failure(event['payload']['payment']['entity'], "razorpay", db)
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook processing failed: {str(e)}")
    
    return {"status": "success"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "payment", "timestamp": datetime.utcnow()}


# Helper functions
async def _create_stripe_subscription(user_id: str, plan: SubscriptionPlan, 
                                    subscription_data: SubscriptionCreateRequest, db: Session):
    """Create Stripe subscription"""
    try:
        # Create Stripe customer
        customer = stripe.Customer.create(
            email=current_user.get("email", ""),
            metadata={"user_id": user_id}
        )
        
        # Create subscription
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{"price": subscription_data.price_id}],
            payment_behavior="default_incomplete",
            expand=["latest_invoice.payment_intent"]
        )
        
        # Store subscription in database
        user_subscription = UserSubscription(
            user_id=user_id,
            plan_id=plan.id,
            payment_provider="stripe",
            subscription_id=subscription.id,
            status="pending",
            starts_at=datetime.utcnow(),
            ends_at=datetime.utcnow() + timedelta(days=plan.duration_days)
        )
        
        db.add(user_subscription)
        db.commit()
        
        return {
            "subscription_id": subscription.id,
            "client_secret": subscription.latest_invoice.payment_intent.client_secret,
            "status": subscription.status
        }
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )


async def _create_razorpay_subscription(user_id: str, plan: SubscriptionPlan,
                                      subscription_data: SubscriptionCreateRequest, db: Session):
    """Create Razorpay subscription"""
    try:
        # Create subscription
        subscription = razorpay_client.subscription.create({
            "plan_id": subscription_data.price_id,
            "customer_notify": 1,
            "total_count": 12,  # 12 months
            "notes": {
                "user_id": user_id,
                "plan_name": plan.name
            }
        })
        
        # Store subscription in database
        user_subscription = UserSubscription(
            user_id=user_id,
            plan_id=plan.id,
            payment_provider="razorpay",
            subscription_id=subscription["id"],
            status="pending",
            starts_at=datetime.utcnow(),
            ends_at=datetime.utcnow() + timedelta(days=plan.duration_days)
        )
        
        db.add(user_subscription)
        db.commit()
        
        return {
            "subscription_id": subscription["id"],
            "status": subscription["status"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Razorpay error: {str(e)}"
        )


async def _create_paypal_subscription(user_id: str, plan: SubscriptionPlan,
                                    subscription_data: SubscriptionCreateRequest, db: Session):
    """Create PayPal subscription"""
    try:
        # Create PayPal subscription (simplified)
        subscription_data_paypal = {
            "plan_id": subscription_data.price_id,
            "start_time": datetime.utcnow().isoformat() + "Z",
            "subscriber": {
                "email_address": current_user.get("email", "")
            },
            "application_context": {
                "brand_name": "Auto Job Apply",
                "user_action": "SUBSCRIBE_NOW",
                "return_url": "http://localhost:3000/payment/success",
                "cancel_url": "http://localhost:3000/payment/cancel"
            }
        }
        
        # This would create actual PayPal subscription
        # For demo purposes, we'll simulate it
        subscription_id = f"paypal_sub_{user_id}_{datetime.utcnow().timestamp()}"
        
        # Store subscription in database
        user_subscription = UserSubscription(
            user_id=user_id,
            plan_id=plan.id,
            payment_provider="paypal",
            subscription_id=subscription_id,
            status="pending",
            starts_at=datetime.utcnow(),
            ends_at=datetime.utcnow() + timedelta(days=plan.duration_days)
        )
        
        db.add(user_subscription)
        db.commit()
        
        return {
            "subscription_id": subscription_id,
            "approval_url": f"https://www.sandbox.paypal.com/webapps/billing/subscriptions/subscribe?ba_token={subscription_id}",
            "status": "pending"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"PayPal error: {str(e)}"
        )


async def _handle_payment_success(payment_data: dict, provider: str, db: Session):
    """Handle successful payment"""
    # Extract subscription ID and update status
    subscription_id = payment_data.get("subscription") or payment_data.get("subscription_id")
    
    if subscription_id:
        subscription = db.query(UserSubscription).filter(
            UserSubscription.subscription_id == subscription_id
        ).first()
        
        if subscription:
            subscription.status = "active"
            
            # Create payment history record
            payment_history = PaymentHistory(
                user_id=subscription.user_id,
                subscription_id=subscription.id,
                amount=payment_data.get("amount", 0) / 100,  # Convert from cents
                currency=payment_data.get("currency", "usd").upper(),
                payment_provider=provider,
                transaction_id=payment_data.get("id"),
                status="completed",
                paid_at=datetime.utcnow()
            )
            
            db.add(payment_history)
            db.commit()


async def _handle_payment_failure(payment_data: dict, provider: str, db: Session):
    """Handle failed payment"""
    subscription_id = payment_data.get("subscription") or payment_data.get("subscription_id")
    
    if subscription_id:
        subscription = db.query(UserSubscription).filter(
            UserSubscription.subscription_id == subscription_id
        ).first()
        
        if subscription:
            subscription.status = "failed"
            
            # Create payment history record
            payment_history = PaymentHistory(
                user_id=subscription.user_id,
                subscription_id=subscription.id,
                amount=payment_data.get("amount", 0) / 100,
                currency=payment_data.get("currency", "usd").upper(),
                payment_provider=provider,
                transaction_id=payment_data.get("id"),
                status="failed",
                paid_at=datetime.utcnow()
            )
            
            db.add(payment_history)
            db.commit()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
