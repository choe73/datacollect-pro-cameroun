"""User model for authentication and subscription management."""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Date, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    """User model for authentication."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=True)
    role = Column(String(20), default="user")
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="user", lazy="selectin")
    analytics_events = relationship("AnalyticsEvent", back_populates="user", lazy="selectin")
    feedbacks = relationship("UserFeedback", back_populates="user", lazy="selectin")
    consents = relationship("UserConsent", back_populates="user", lazy="selectin", uselist=False)


class Subscription(Base):
    """Subscription model for monetization."""
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan = Column(String(20), nullable=False)  # free, standard, premium
    status = Column(String(20), default="active")  # active, expired, cancelled, pending
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    payment_provider = Column(String(50), nullable=True)  # paypal, mtn, orange
    provider_subscription_id = Column(String(255), nullable=True)
    amount_paid = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(3), default="XAF")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    
    # Quota tracking
    analyses_used_this_month = Column(Integer, default=0)
    api_calls_used_this_month = Column(Integer, default=0)
    exports_used_this_month = Column(Integer, default=0)
    quota_reset_date = Column(Date, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")


class AnalyticsEvent(Base):
    """Analytics events for tracking user behavior."""
    __tablename__ = "analytics_events"
    
    # Note: This table should be partitioned by created_at for performance
    __table_args__ = {
        'postgresql_partition_by': 'RANGE (created_at)',
    }

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # NULL for anonymous
    event_type = Column(String(50), nullable=False, index=True)
    event_data = Column(Text, nullable=True)  # JSON stored as text
    session_id = Column(String(255), nullable=True, index=True)
    page_url = Column(String(500), nullable=True)
    user_agent = Column(String(500), nullable=True)
    ip_hash = Column(String(64), nullable=True)  # Hashed IP with salt
    created_at = Column(DateTime(timezone=True), server_default=func.now(), primary_key=True)
    
    # Relationships
    user = relationship("User", back_populates="analytics_events")


class UserConsent(Base):
    """User consent for cookies and analytics."""
    __tablename__ = "user_consents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    cookie_consent = Column(Boolean, default=False)
    analytics_consent = Column(Boolean, default=False)
    marketing_consent = Column(Boolean, default=False)
    consented_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    consent_version = Column(String(10), default="1.0")
    
    # Relationships
    user = relationship("User", back_populates="consents")


class UserFeedback(Base):
    """User feedback on analysis results."""
    __tablename__ = "user_feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    analysis_id = Column(Integer, ForeignKey("analysis_results.id"), nullable=True)
    analysis_type = Column(String(50), nullable=True)
    rating = Column(Integer, nullable=True)  # 1-5 scale
    comment = Column(Text, nullable=True)
    helpful = Column(Boolean, nullable=True)  # Thumbs up/down
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="feedbacks")
    analysis = relationship("AnalysisResult")
