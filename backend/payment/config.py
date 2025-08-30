from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:postgres123@localhost:5432/auto_job_apply"
    
    # Stripe Configuration
    stripe_secret_key: str = "sk_test_your_stripe_secret_key"
    stripe_publishable_key: str = "pk_test_your_stripe_publishable_key"
    stripe_webhook_secret: str = "whsec_your_webhook_secret"
    
    # Razorpay Configuration
    razorpay_key_id: str = "your_razorpay_key_id"
    razorpay_key_secret: str = "your_razorpay_key_secret"
    razorpay_webhook_secret: str = "your_razorpay_webhook_secret"
    
    # PayPal Configuration
    paypal_client_id: str = "your_paypal_client_id"
    paypal_client_secret: str = "your_paypal_client_secret"
    paypal_mode: str = "sandbox"  # sandbox or live
    
    # Currency
    default_currency: str = "USD"
    supported_currencies: list = ["USD", "INR", "EUR"]
    
    # Subscription Plans
    free_plan_id: str = "free"
    premium_plan_id: str = "premium"
    
    # CORS
    cors_origins: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    class Config:
        env_file = ".env"


settings = Settings()
