"""
STALKER - Database Models
All SQLAlchemy ORM models for the framework.
"""

import shortuuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    Float,
    Boolean,
    Integer,
    ForeignKey,
    Enum as SAEnum,
)
from sqlalchemy.orm import relationship
from backend.database import Base


def _generate_id() -> str:
    return shortuuid.uuid()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ── User (admin) ──────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(String(22), primary_key=True, default=_generate_id)
    username = Column(String(120), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow)


# ── Campaign ──────────────────────────────────────────────────────────────────

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(String(22), primary_key=True, default=_generate_id)
    name = Column(String(255), nullable=False)
    description = Column(Text, default="")
    status = Column(String(20), default="active")  # active | paused | expired
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    participants = relationship("Participant", back_populates="campaign", lazy="selectin")
    events = relationship("TrainingEvent", back_populates="campaign", lazy="selectin")
    locations = relationship("LocationEvent", back_populates="campaign", lazy="selectin")
    reports = relationship("Report", back_populates="campaign", lazy="selectin")


# ── Participant ───────────────────────────────────────────────────────────────

class Participant(Base):
    __tablename__ = "participants"

    id = Column(String(22), primary_key=True, default=_generate_id)
    campaign_id = Column(String(22), ForeignKey("campaigns.id"), nullable=False)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    campaign = relationship("Campaign", back_populates="participants")
    consent = relationship("ConsentLog", back_populates="participant", uselist=False, lazy="selectin")
    events = relationship("TrainingEvent", back_populates="participant", lazy="selectin")
    location = relationship("LocationEvent", back_populates="participant", uselist=False, lazy="selectin")
    browser_info = relationship("BrowserInfo", back_populates="participant", uselist=False, lazy="selectin")


# ── ConsentLog ────────────────────────────────────────────────────────────────

class ConsentLog(Base):
    __tablename__ = "consent_logs"

    id = Column(String(22), primary_key=True, default=_generate_id)
    participant_id = Column(String(22), ForeignKey("participants.id"), nullable=False)
    consent_given = Column(Boolean, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=_utcnow)

    participant = relationship("Participant", back_populates="consent")


# ── TrainingEvent ─────────────────────────────────────────────────────────────

class TrainingEvent(Base):
    __tablename__ = "training_events"

    id = Column(String(22), primary_key=True, default=_generate_id)
    participant_id = Column(String(22), ForeignKey("participants.id"), nullable=False)
    campaign_id = Column(String(22), ForeignKey("campaigns.id"), nullable=False)
    event_type = Column(String(50), nullable=False)  # PAGE_VIEW, SPIN, CONSENT_ACCEPTED, etc.
    details = Column(Text, default="")
    timestamp = Column(DateTime(timezone=True), default=_utcnow)

    participant = relationship("Participant", back_populates="events")
    campaign = relationship("Campaign", back_populates="events")


# ── LocationEvent ─────────────────────────────────────────────────────────────

class LocationEvent(Base):
    __tablename__ = "location_events"

    id = Column(String(22), primary_key=True, default=_generate_id)
    participant_id = Column(String(22), ForeignKey("participants.id"), nullable=False)
    campaign_id = Column(String(22), ForeignKey("campaigns.id"), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    permission_status = Column(String(30), default="PENDING")  # GRANTED | DENIED | PENDING
    timestamp = Column(DateTime(timezone=True), default=_utcnow)

    participant = relationship("Participant", back_populates="location")
    campaign = relationship("Campaign", back_populates="locations")


# ── BrowserInfo ───────────────────────────────────────────────────────────────

class BrowserInfo(Base):
    __tablename__ = "browser_info"

    id = Column(String(22), primary_key=True, default=_generate_id)
    participant_id = Column(String(22), ForeignKey("participants.id"), nullable=False)
    browser = Column(String(100), default="")
    os = Column(String(100), default="")
    screen_resolution = Column(String(30), default="")
    language = Column(String(20), default="")
    timezone = Column(String(80), default="")
    user_agent = Column(Text, default="")
    timestamp = Column(DateTime(timezone=True), default=_utcnow)

    participant = relationship("Participant", back_populates="browser_info")


# ── Report ────────────────────────────────────────────────────────────────────

class Report(Base):
    __tablename__ = "reports"

    id = Column(String(22), primary_key=True, default=_generate_id)
    campaign_id = Column(String(22), ForeignKey("campaigns.id"), nullable=False)
    format = Column(String(10), default="html")
    content = Column(Text, default="")
    generated_at = Column(DateTime(timezone=True), default=_utcnow)

    campaign = relationship("Campaign", back_populates="reports")
