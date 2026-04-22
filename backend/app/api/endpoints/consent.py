"""Consent management endpoints."""

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.user import User, UserConsent
from app.schemas.user import ConsentStatus, ConsentUpdate
from app.api.endpoints.auth import get_current_active_user
from app.core.redis import redis_client

router = APIRouter()


@router.get("/status", response_model=ConsentStatus)
async def get_consent_status(
    request: Request,
    current_user: Optional[User] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get current consent status for user or session."""
    user_id = current_user.id if current_user else None
    session_id = request.cookies.get("analytics_session")
    
    # Try to get from database if user is logged in
    if user_id:
        query = select(UserConsent).where(UserConsent.user_id == user_id)
        result = await db.execute(query)
        consent = result.scalar_one_or_none()
        
        if consent:
            return ConsentStatus(
                cookie_consent=consent.cookie_consent,
                analytics_consent=consent.analytics_consent,
                marketing_consent=consent.marketing_consent,
                consented_at=consent.consented_at,
                consent_version=consent.consent_version
            )
    
    # Try to get from Redis (for anonymous users)
    if session_id:
        cache_key = f"consent:{session_id}"
        cached = await redis_client.get(cache_key)
        if cached:
            try:
                import json
                data = json.loads(cached)
                return ConsentStatus(
                    cookie_consent=data.get("cookie_consent", False),
                    analytics_consent=data.get("analytics_consent", False),
                    marketing_consent=data.get("marketing_consent", False),
                    consented_at=datetime.fromisoformat(data.get("consented_at")) if data.get("consented_at") else None,
                    consent_version=data.get("consent_version", "1.0")
                )
            except:
                pass
    
    # Return default (no consent)
    return ConsentStatus(
        cookie_consent=False,
        analytics_consent=False,
        marketing_consent=False,
        consented_at=None,
        consent_version="1.0"
    )


@router.post("/update")
async def update_consent(
    consent: ConsentUpdate,
    request: Request,
    response: Response,
    current_user: Optional[User] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Update consent preferences."""
    user_id = current_user.id if current_user else None
    session_id = request.cookies.get("analytics_session")
    
    # Create session if not exists
    if not session_id:
        import uuid
        session_id = str(uuid.uuid4())
        response.set_cookie(
            key="analytics_session",
            value=session_id,
            max_age=86400 * 180,  # 6 months
            httponly=True,
            secure=True,
            samesite="lax"
        )
    
    # Update in database if user is logged in
    if user_id:
        query = select(UserConsent).where(UserConsent.user_id == user_id)
        result = await db.execute(query)
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.cookie_consent = consent.cookie_consent
            existing.analytics_consent = consent.analytics_consent
            existing.marketing_consent = consent.marketing_consent or False
            existing.updated_at = datetime.utcnow()
        else:
            new_consent = UserConsent(
                user_id=user_id,
                cookie_consent=consent.cookie_consent,
                analytics_consent=consent.analytics_consent,
                marketing_consent=consent.marketing_consent or False
            )
            db.add(new_consent)
        
        await db.commit()
    
    # Store in Redis for quick access
    cache_key = f"consent:{user_id or session_id}"
    import json
    await redis_client.set(
        cache_key,
        json.dumps({
            "cookie_consent": consent.cookie_consent,
            "analytics_consent": consent.analytics_consent,
            "marketing_consent": consent.marketing_consent or False,
            "consented_at": datetime.utcnow().isoformat(),
            "consent_version": "1.0"
        }),
        expire=86400 * 180  # 6 months
    )
    
    # Set consent cookie
    response.set_cookie(
        key="analytics_consent",
        value="true" if consent.analytics_consent else "false",
        max_age=86400 * 180,  # 6 months
        httponly=False,  # Must be accessible by JS
        secure=True,
        samesite="lax"
    )
    
    return {"status": "updated"}


@router.post("/withdraw")
async def withdraw_consent(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Withdraw all consent (GDPR right to withdraw)."""
    user_id = current_user.id
    
    # Update in database
    query = select(UserConsent).where(UserConsent.user_id == user_id)
    result = await db.execute(query)
    consent = result.scalar_one_or_none()
    
    if consent:
        consent.cookie_consent = False
        consent.analytics_consent = False
        consent.marketing_consent = False
        consent.updated_at = datetime.utcnow()
        await db.commit()
    
    # Clear from Redis
    cache_key = f"consent:{user_id}"
    await redis_client.delete(cache_key)
    
    # Clear cookies
    response.delete_cookie("analytics_consent")
    response.delete_cookie("analytics_session")
    
    return {"status": "withdrawn", "message": "All consent withdrawn successfully"}
