"""Analytics and tracking endpoints."""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.dialects.postgresql import insert

from app.core.database import get_db
from app.models.user import User, AnalyticsEvent
from app.schemas.user import AnalyticsEventCreate, AnalyticsSummary
from app.api.endpoints.auth import get_current_active_user
from app.core.redis import redis_client

router = APIRouter()


async def get_analytics_consent(user_id: Optional[int] = None, session_id: Optional[str] = None) -> bool:
    """Check if user has given analytics consent."""
    if not user_id and not session_id:
        return False
    
    # Check Redis cache for consent
    cache_key = f"consent:{user_id or session_id}"
    cached = await redis_client.get(cache_key)
    if cached:
        return cached == "true"
    
    return False


@router.post("/event")
async def track_event(
    event: AnalyticsEventCreate,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Track an analytics event."""
    # Get session ID from cookie or create new one
    session_id = request.cookies.get("analytics_session")
    if not session_id:
        import uuid
        session_id = str(uuid.uuid4())
        response.set_cookie(
            key="analytics_session",
            value=session_id,
            max_age=86400,  # 24 hours
            httponly=True,
            secure=True,
            samesite="lax"
        )
    
    # Check consent (for now, track anonymous events too with limited data)
    # In production, should check consent before tracking
    
    # Hash IP with rotating salt for pseudonymization
    ip_salt = datetime.utcnow().strftime("%Y%m")  # Rotating monthly salt
    ip_hash = None
    if request.client:
        ip_hash = hashlib.sha256(
            f"{request.client.host}{ip_salt}".encode()
        ).hexdigest()
    
    # Get user agent (truncate for privacy)
    user_agent = request.headers.get("user-agent", "")[:200]
    
    # Store event
    analytics_event = AnalyticsEvent(
        event_type=event.event_type,
        event_data=json.dumps(event.event_data) if event.event_data else None,
        session_id=session_id,
        page_url=event.page_url,
        user_agent=user_agent,
        ip_hash=ip_hash
    )
    
    # Try to get user_id from session if authenticated
    try:
        from jose import jwt
        from app.core.config import settings
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            if user_id:
                analytics_event.user_id = int(user_id)
                # Check user consent
                consent_query = select(User).where(User.id == int(user_id))
                result = await db.execute(consent_query)
                user = result.scalar_one_or_none()
                if user and user.consents:
                    if not user.consents.analytics_consent:
                        # Skip tracking if no consent
                        return {"status": "skipped", "reason": "no_consent"}
    except Exception:
        pass
    
    db.add(analytics_event)
    await db.commit()
    
    return {"status": "tracked"}


@router.get("/admin/analytics", response_model=AnalyticsSummary)
async def get_analytics_summary(
    period: str = "7d",
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get analytics summary for admin dashboard."""
    # Check admin role
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Calculate date range
    days = int(period[:-1]) if period.endswith("d") else 7
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Total events
    total_query = select(func.count(AnalyticsEvent.id)).where(
        AnalyticsEvent.created_at >= start_date
    )
    total_result = await db.execute(total_query)
    total_events = total_result.scalar()
    
    # Unique users
    unique_query = select(func.count(func.distinct(AnalyticsEvent.user_id))).where(
        and_(
            AnalyticsEvent.created_at >= start_date,
            AnalyticsEvent.user_id.isnot(None)
        )
    )
    unique_result = await db.execute(unique_query)
    unique_users = unique_result.scalar()
    
    # Top pages
    pages_query = select(
        AnalyticsEvent.page_url,
        func.count(AnalyticsEvent.id).label("count")
    ).where(
        AnalyticsEvent.created_at >= start_date
    ).group_by(AnalyticsEvent.page_url).order_by(func.count(AnalyticsEvent.id).desc()).limit(10)
    
    pages_result = await db.execute(pages_query)
    top_pages = [
        {"url": url, "count": count}
        for url, count in pages_result.all()
    ]
    
    # Top analysis types
    analyses_query = select(
        AnalyticsEvent.event_data,
        func.count(AnalyticsEvent.id).label("count")
    ).where(
        and_(
            AnalyticsEvent.created_at >= start_date,
            AnalyticsEvent.event_type == "analysis_run"
        )
    ).group_by(AnalyticsEvent.event_data).order_by(func.count(AnalyticsEvent.id).desc()).limit(10)
    
    analyses_result = await db.execute(analyses_query)
    top_analyses = []
    for data, count in analyses_result.all():
        try:
            parsed = json.loads(data) if data else {}
            top_analyses.append({
                "type": parsed.get("analysis_type", "unknown"),
                "count": count
            })
        except:
            top_analyses.append({"type": "unknown", "count": count})
    
    # Error rate
    error_query = select(func.count(AnalyticsEvent.id)).where(
        and_(
            AnalyticsEvent.created_at >= start_date,
            AnalyticsEvent.event_type == "error_encountered"
        )
    )
    error_result = await db.execute(error_query)
    error_count = error_result.scalar()
    error_rate = error_count / total_events if total_events > 0 else 0
    
    return AnalyticsSummary(
        total_events=total_events,
        unique_users=unique_users,
        top_pages=top_pages,
        top_analyses=top_analyses,
        error_rate=error_rate,
        period=period
    )
