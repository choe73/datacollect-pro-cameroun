"""User feedback endpoints."""

from datetime import datetime
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.user import User, UserFeedback
from app.schemas.user import FeedbackCreate, Feedback
from app.api.endpoints.auth import get_current_active_user, get_current_user

router = APIRouter()


@router.post("", response_model=Feedback)
async def create_feedback(
    feedback: FeedbackCreate,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Submit feedback on an analysis."""
    new_feedback = UserFeedback(
        user_id=current_user.id if current_user else None,
        analysis_id=feedback.analysis_id,
        analysis_type=feedback.analysis_type,
        rating=feedback.rating,
        comment=feedback.comment,
        helpful=feedback.helpful,
    )

    db.add(new_feedback)
    await db.commit()
    await db.refresh(new_feedback)

    return new_feedback


@router.get("/summary")
async def get_feedback_summary(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get feedback summary (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    # Total feedback
    total_query = select(func.count(UserFeedback.id))
    total_result = await db.execute(total_query)
    total_feedback = total_result.scalar()

    # Average rating
    avg_query = select(func.avg(UserFeedback.rating))
    avg_result = await db.execute(avg_query)
    average_rating = avg_result.scalar() or 0

    # Positive feedback (rating >= 4 or helpful=True)
    positive_query = select(func.count(UserFeedback.id)).where(
        (UserFeedback.rating >= 4) | (UserFeedback.helpful == True)
    )
    positive_result = await db.execute(positive_query)
    positive_count = positive_result.scalar()

    positive_pct = (positive_count / total_feedback * 100) if total_feedback > 0 else 0

    # Recent comments
    recent_query = (
        select(UserFeedback).order_by(UserFeedback.created_at.desc()).limit(10)
    )
    recent_result = await db.execute(recent_query)
    recent_comments = recent_result.scalars().all()

    return {
        "total_feedback": total_feedback,
        "average_rating": round(float(average_rating), 2),
        "positive_feedback_pct": round(positive_pct, 2),
        "recent_comments": [
            {
                "id": f.id,
                "rating": f.rating,
                "comment": f.comment,
                "helpful": f.helpful,
                "created_at": f.created_at,
                "analysis_type": f.analysis_type,
            }
            for f in recent_comments
        ],
    }
