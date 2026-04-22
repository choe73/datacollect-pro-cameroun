"""Subscription and monetization endpoints."""

from datetime import datetime, timedelta, date
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User, Subscription
from app.schemas.user import (
    SubscriptionCreate, Subscription, SubscriptionPlan,
    SubscriptionPlansResponse, SubscriptionQuota
)
from app.api.endpoints.auth import get_current_active_user

router = APIRouter()


# Subscription plan definitions
PLANS = {
    "free": SubscriptionPlan(
        id="free",
        name="Gratuit",
        price_monthly=0,
        price_yearly=0,
        analyses_limit=10,
        api_calls_limit=0,
        exports_limit=5,
        features=[
            "10 analyses par mois",
            "Exports limites (CSV 100 lignes)",
            "Watermark sur graphiques",
            "Support communautaire"
        ]
    ),
    "standard": SubscriptionPlan(
        id="standard",
        name="Standard",
        price_monthly=9900,
        price_yearly=99000,
        analyses_limit=-1,  # unlimited
        api_calls_limit=100,
        exports_limit=-1,  # unlimited
        features=[
            "Analyses illimites",
            "Exports complets",
            "Acces API (100 req/jour)",
            "Support email",
            "Sans watermark"
        ]
    ),
    "premium": SubscriptionPlan(
        id="premium",
        name="Premium",
        price_monthly=29900,
        price_yearly=299000,
        analyses_limit=-1,
        api_calls_limit=1000,
        exports_limit=-1,
        features=[
            "Tout le plan Standard",
            "Modeles personnalises",
            "Donnees historiques completes",
            "Support prioritaire",
            "API (1000 req/jour)",
            "Rapports automatiques"
        ]
    )
}


@router.get("/plans", response_model=SubscriptionPlansResponse)
async def get_plans() -> Any:
    """Get all available subscription plans."""
    return SubscriptionPlansResponse(plans=list(PLANS.values()))


@router.get("/current", response_model=Subscription)
async def get_current_subscription(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get current user's active subscription."""
    query = select(Subscription).where(
        and_(
            Subscription.user_id == current_user.id,
            Subscription.status.in_(["active", "pending"])
        )
    ).order_by(Subscription.created_at.desc())
    
    result = await db.execute(query)
    subscription = result.scalar_one_or_none()
    
    # If no subscription, create free plan
    if not subscription:
        subscription = Subscription(
            user_id=current_user.id,
            plan="free",
            status="active",
            analyses_used_this_month=0,
            api_calls_used_this_month=0,
            exports_used_this_month=0
        )
        db.add(subscription)
        await db.commit()
        await db.refresh(subscription)
    
    return subscription


@router.get("/quota", response_model=SubscriptionQuota)
async def get_quota(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get current quota usage."""
    subscription = await get_current_subscription(current_user, db)
    plan = PLANS.get(subscription.plan, PLANS["free"])
    
    # Check if quota needs reset (monthly)
    today = date.today()
    if subscription.quota_reset_date:
        if today.month != subscription.quota_reset_date.month or today.year != subscription.quota_reset_date.year:
            subscription.analyses_used_this_month = 0
            subscription.api_calls_used_this_month = 0
            subscription.exports_used_this_month = 0
            subscription.quota_reset_date = today
            await db.commit()
    else:
        subscription.quota_reset_date = today
        await db.commit()
    
    return SubscriptionQuota(
        plan=subscription.plan,
        analyses_used=subscription.analyses_used_this_month,
        analyses_limit=plan.analyses_limit,
        api_calls_used=subscription.api_calls_used_this_month,
        api_calls_limit=plan.api_calls_limit,
        exports_used=subscription.exports_used_this_month,
        exports_limit=plan.exports_limit,
        reset_date=subscription.quota_reset_date or today
    )


@router.post("/create")
async def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Create a new subscription (initiates payment)."""
    plan = PLANS.get(subscription_data.plan)
    if not plan:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    if subscription_data.plan == "free":
        raise HTTPException(status_code=400, detail="Cannot subscribe to free plan")
    
    # Cancel any existing active subscription
    query = select(Subscription).where(
        and_(
            Subscription.user_id == current_user.id,
            Subscription.status == "active"
        )
    )
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing:
        existing.status = "cancelled"
        existing.cancelled_at = datetime.utcnow()
        existing.cancellation_reason = "Upgraded to new plan"
    
    # Create new subscription (pending payment)
    subscription = Subscription(
        user_id=current_user.id,
        plan=subscription_data.plan,
        status="pending",
        payment_provider=subscription_data.payment_method
    )
    db.add(subscription)
    await db.commit()
    await db.refresh(subscription)
    
    # TODO: Integrate with PayPal or mobile money API
    # For now, return payment URL placeholder
    return {
        "subscription_id": subscription.id,
        "status": "pending_payment",
        "payment_url": f"/api/v1/payments/{subscription_data.payment_method}/checkout?subscription_id={subscription.id}",
        "plan": subscription_data.plan,
        "amount": plan.price_monthly
    }


@router.post("/webhook")
async def payment_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Webhook for payment provider notifications."""
    # TODO: Verify webhook signature from payment provider
    payload = await request.json()
    
    subscription_id = payload.get("subscription_id")
    status = payload.get("status")
    
    query = select(Subscription).where(Subscription.id == subscription_id)
    result = await db.execute(query)
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    if status == "completed":
        subscription.status = "active"
        subscription.start_date = date.today()
        subscription.end_date = date.today() + timedelta(days=30)
        subscription.amount_paid = payload.get("amount")
        subscription.provider_subscription_id = payload.get("provider_id")
    elif status == "failed":
        subscription.status = "cancelled"
    
    await db.commit()
    return {"status": "processed"}


@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Cancel current subscription."""
    query = select(Subscription).where(
        and_(
            Subscription.user_id == current_user.id,
            Subscription.status == "active"
        )
    )
    result = await db.execute(query)
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription found")
    
    subscription.status = "cancelled"
    subscription.cancelled_at = datetime.utcnow()
    subscription.cancellation_reason = "User cancelled"
    
    await db.commit()
    
    return {"message": "Subscription cancelled successfully"}
