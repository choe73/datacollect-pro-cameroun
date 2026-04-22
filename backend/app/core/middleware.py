"""Custom middleware for quota checking and subscription validation."""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import date

from app.models.user import Subscription
from app.core.database import AsyncSessionLocal


class SubscriptionQuotaMiddleware(BaseHTTPMiddleware):
    """Middleware to check subscription quotas on analysis endpoints."""

    async def dispatch(self, request: Request, call_next):
        """Check quota before processing request."""
        # Only check for analysis endpoints
        path = request.url.path
        if not path.startswith("/api/v1/analysis") or request.method != "POST":
            return await call_next(request)

        # Get user from token
        auth_header = request.headers.get("authorization", "")
        if not auth_header.startswith("Bearer "):
            # Anonymous user - check if endpoint allows anonymous
            return await call_next(request)

        token = auth_header[7:]

        try:
            from jose import jwt
            from app.core.config import settings

            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            user_id = payload.get("sub")

            if user_id:
                # Check quota
                async with AsyncSessionLocal() as db:
                    has_quota = await self._check_quota(int(user_id), db)
                    if not has_quota:
                        raise HTTPException(
                            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail="Quota exceeded. Please upgrade your subscription.",
                        )
        except Exception as e:
            # If token is invalid, let the endpoint handle it
            pass

        return await call_next(request)

    async def _check_quota(self, user_id: int, db: AsyncSessionLocal) -> bool:
        """Check if user has remaining quota."""
        query = (
            select(Subscription)
            .where(
                and_(
                    Subscription.user_id == user_id,
                    Subscription.status.in_(["active", "pending"]),
                )
            )
            .order_by(Subscription.created_at.desc())
        )

        result = await db.execute(query)
        subscription = result.scalar_one_or_none()

        if not subscription:
            # Free plan - 10 analyses per month
            return True  # Will be tracked after completion

        plan = subscription.plan

        # Reset monthly quota if needed
        today = date.today()
        if subscription.quota_reset_date:
            if today.month != subscription.quota_reset_date.month:
                subscription.analyses_used_this_month = 0
                subscription.quota_reset_date = today
        else:
            subscription.quota_reset_date = today

        await db.commit()

        # Check quota based on plan
        if plan == "free":
            return subscription.analyses_used_this_month < 10
        elif plan == "standard":
            return True  # Unlimited
        elif plan == "premium":
            return True  # Unlimited

        return True


class AnalyticsMiddleware(BaseHTTPMiddleware):
    """Middleware to track page views and requests."""

    async def dispatch(self, request: Request, call_next):
        """Track request and continue."""
        # Skip tracking for static files and health checks
        path = request.url.path
        if any(skip in path for skip in ["/health", "/static", "/assets"]):
            return await call_next(request)

        # Track asynchronously without blocking
        import asyncio

        asyncio.create_task(self._track_request(request))

        return await call_next(request)

    async def _track_request(self, request: Request):
        """Track page view."""
        try:
            from app.core.redis import redis_client

            # Get session ID
            session_id = request.cookies.get("analytics_session", "anonymous")

            # Increment page view counter in Redis
            path = request.url.path
            await redis_client.incr(f"pageviews:{path}:{date.today().isoformat()}")
            await redis_client.expire(
                f"pageviews:{path}:{date.today().isoformat()}", 86400 * 30
            )

        except Exception:
            # Silently fail - analytics should not break the app
            pass
