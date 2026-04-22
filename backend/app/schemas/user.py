"""User and subscription schemas."""

from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel, EmailStr, Field, validator


# User Schemas
class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user registration."""

    password: str = Field(..., min_length=8)

    @validator("password")
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserUpdate(BaseModel):
    """Schema for user update."""

    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class User(UserBase):
    """Complete user schema."""

    id: int
    role: str = "user"
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserInDB(User):
    """User schema with internal fields."""

    hashed_password: str


# Auth Schemas
class Token(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes


class TokenPayload(BaseModel):
    """Token payload schema."""

    sub: Optional[int] = None  # user_id
    exp: Optional[datetime] = None
    type: str = "access"


class LoginRequest(BaseModel):
    """Login request schema."""

    email: EmailStr
    password: str


class PasswordReset(BaseModel):
    """Password reset schema."""

    email: EmailStr


class PasswordChange(BaseModel):
    """Password change schema."""

    current_password: str
    new_password: str = Field(..., min_length=8)


# Subscription Schemas
class SubscriptionBase(BaseModel):
    """Base subscription schema."""

    plan: str  # free, standard, premium


class SubscriptionCreate(SubscriptionBase):
    """Schema for creating subscription."""

    payment_method: str  # paypal, mtn, orange


class Subscription(SubscriptionBase):
    """Complete subscription schema."""

    id: int
    user_id: int
    status: str
    start_date: Optional[date]
    end_date: Optional[date]
    payment_provider: Optional[str]
    analyses_used_this_month: int = 0
    api_calls_used_this_month: int = 0
    exports_used_this_month: int = 0
    quota_reset_date: Optional[date]
    created_at: datetime

    class Config:
        from_attributes = True


class SubscriptionPlan(BaseModel):
    """Subscription plan details."""

    id: str
    name: str
    price_monthly: int  # FCFA
    price_yearly: Optional[int] = None
    analyses_limit: int
    api_calls_limit: int
    exports_limit: int
    features: List[str]


class SubscriptionPlansResponse(BaseModel):
    """Response with all subscription plans."""

    plans: List[SubscriptionPlan]


class SubscriptionQuota(BaseModel):
    """User's current quota usage."""

    plan: str
    analyses_used: int
    analyses_limit: int
    api_calls_used: int
    api_calls_limit: int
    exports_used: int
    exports_limit: int
    reset_date: date


# Analytics Schemas
class AnalyticsEventCreate(BaseModel):
    """Schema for creating analytics event."""

    event_type: str
    event_data: Optional[dict] = None
    page_url: Optional[str] = None
    session_id: Optional[str] = None


class AnalyticsEvent(AnalyticsEventCreate):
    """Complete analytics event schema."""

    id: int
    user_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class AnalyticsSummary(BaseModel):
    """Analytics summary for admin dashboard."""

    total_events: int
    unique_users: int
    top_pages: List[dict]
    top_analyses: List[dict]
    error_rate: float
    period: str


# Consent Schemas
class ConsentStatus(BaseModel):
    """User consent status."""

    cookie_consent: bool
    analytics_consent: bool
    marketing_consent: bool
    consented_at: Optional[datetime]
    consent_version: str


class ConsentUpdate(BaseModel):
    """Update user consent."""

    cookie_consent: bool
    analytics_consent: bool
    marketing_consent: Optional[bool] = False


# Feedback Schemas
class FeedbackCreate(BaseModel):
    """Schema for creating feedback."""

    analysis_id: Optional[int] = None
    analysis_type: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None
    helpful: Optional[bool] = None


class Feedback(FeedbackCreate):
    """Complete feedback schema."""

    id: int
    user_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class FeedbackSummary(BaseModel):
    """Summary of feedback for admin."""

    total_feedback: int
    average_rating: float
    positive_feedback_pct: float
    recent_comments: List[Feedback]
