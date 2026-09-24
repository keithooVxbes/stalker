"""
STALKER - API Routes
FastAPI router with all endpoints for the training framework.
"""

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import shortuuid
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_session
from backend.models import (
    User,
    Campaign,
    Participant,
    ConsentLog,
    TrainingEvent,
    LocationEvent,
    BrowserInfo,
    Report,
)

# ── Config ────────────────────────────────────────────────────────────────────

SECRET_KEY = os.getenv("STALKER_SECRET_KEY", "dev-secret-key-change-me")
ALGORITHM = os.getenv("STALKER_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE = int(os.getenv("STALKER_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()


# ── Pydantic Schemas ─────────────────────────────────────────────────────────

class CampaignCreate(BaseModel):
    name: str
    description: str = ""
    duration_hours: int = 24


class CampaignOut(BaseModel):
    id: str
    name: str
    description: str
    status: str
    training_url: str = ""
    created_at: str
    expires_at: str
    participant_count: int = 0


class TokenRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ConsentPayload(BaseModel):
    campaign_id: str
    consent_given: bool
    ip_address: str = ""
    user_agent: str = ""


class LocationPayload(BaseModel):
    participant_id: str
    campaign_id: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    permission_status: str = "DENIED"


class BrowserPayload(BaseModel):
    participant_id: str
    browser: str = ""
    os: str = ""
    screen_resolution: str = ""
    language: str = ""
    timezone: str = ""
    user_agent: str = ""


class EventPayload(BaseModel):
    participant_id: str
    campaign_id: str
    event_type: str
    details: str = ""


class CameraPayload(BaseModel):
    participant_id: str
    campaign_id: str
    permission_status: str = "DENIED"


# ── Auth helpers ──────────────────────────────────────────────────────────────

def _create_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ── Auth routes ───────────────────────────────────────────────────────────────

@router.post("/api/auth/login", response_model=TokenResponse)
async def login(payload: TokenRequest, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(User).where(User.username == payload.username))
    user = result.scalar_one_or_none()
    if not user or not pwd_context.verify(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = _create_token({"sub": user.username, "uid": user.id})
    return TokenResponse(access_token=token)


# ── Campaign CRUD ─────────────────────────────────────────────────────────────

@router.post("/api/campaigns", response_model=dict)
async def create_campaign(payload: CampaignCreate, db: AsyncSession = Depends(get_session)):
    campaign = Campaign(
        name=payload.name,
        description=payload.description,
        status="active",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=payload.duration_hours),
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)

    # Use tunnel URL if available, otherwise local
    public_url = os.getenv("STALKER_PUBLIC_URL", "").rstrip("/")
    if public_url:
        training_url = f"{public_url}/train/{campaign.id}"
    else:
        host = os.getenv("STALKER_HOST", "127.0.0.1")
        port = os.getenv("STALKER_PORT", "8443")
        training_url = f"http://{host}:{port}/train/{campaign.id}"

    return {
        "id": campaign.id,
        "name": campaign.name,
        "description": campaign.description,
        "status": campaign.status,
        "training_url": training_url,
        "created_at": campaign.created_at.isoformat() if campaign.created_at else "",
        "expires_at": campaign.expires_at.isoformat() if campaign.expires_at else "",
    }


@router.get("/api/campaigns")
async def list_campaigns(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Campaign).order_by(Campaign.created_at.desc()))
    campaigns = result.scalars().all()
    out = []
    for c in campaigns:
        out.append({
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "status": c.status,
            "created_at": c.created_at.isoformat() if c.created_at else "",
            "expires_at": c.expires_at.isoformat() if c.expires_at else "",
            "participant_count": len(c.participants) if c.participants else 0,
        })
    return out


@router.get("/api/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {
        "id": campaign.id,
        "name": campaign.name,
        "description": campaign.description,
        "status": campaign.status,
        "created_at": campaign.created_at.isoformat() if campaign.created_at else "",
        "expires_at": campaign.expires_at.isoformat() if campaign.expires_at else "",
        "participant_count": len(campaign.participants) if campaign.participants else 0,
    }


# ── Consent ───────────────────────────────────────────────────────────────────

@router.post("/api/consent")
async def record_consent(payload: ConsentPayload, request: Request, db: AsyncSession = Depends(get_session)):
    # Validate campaign
    result = await db.execute(select(Campaign).where(Campaign.id == payload.campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    ip = payload.ip_address or request.client.host if request.client else "unknown"

    # Create participant
    participant = Participant(campaign_id=payload.campaign_id, ip_address=ip)
    db.add(participant)
    await db.flush()

    # Log consent
    consent = ConsentLog(
        participant_id=participant.id,
        consent_given=payload.consent_given,
    )
    db.add(consent)

    # Log event
    event_type = "CONSENT_ACCEPTED" if payload.consent_given else "CONSENT_DECLINED"
    event = TrainingEvent(
        participant_id=participant.id,
        campaign_id=payload.campaign_id,
        event_type=event_type,
    )
    db.add(event)
    await db.commit()

    return {
        "participant_id": participant.id,
        "consent": event_type,
        "campaign_id": payload.campaign_id,
    }


# ── Events ────────────────────────────────────────────────────────────────────

@router.post("/api/events")
async def record_event(payload: EventPayload, db: AsyncSession = Depends(get_session)):
    event = TrainingEvent(
        participant_id=payload.participant_id,
        campaign_id=payload.campaign_id,
        event_type=payload.event_type,
        details=payload.details,
    )
    db.add(event)
    await db.commit()
    return {"status": "ok"}


@router.get("/api/events")
async def list_events(db: AsyncSession = Depends(get_session)):
    result = await db.execute(
        select(TrainingEvent).order_by(TrainingEvent.timestamp.desc()).limit(200)
    )
    events = result.scalars().all()
    return [
        {
            "id": e.id,
            "participant_id": e.participant_id,
            "campaign_id": e.campaign_id,
            "event_type": e.event_type,
            "details": e.details,
            "timestamp": e.timestamp.isoformat() if e.timestamp else "",
        }
        for e in events
    ]


# ── Location ──────────────────────────────────────────────────────────────────

@router.post("/api/location")
async def record_location(payload: LocationPayload, db: AsyncSession = Depends(get_session)):
    loc = LocationEvent(
        participant_id=payload.participant_id,
        campaign_id=payload.campaign_id,
        latitude=payload.latitude,
        longitude=payload.longitude,
        permission_status=payload.permission_status,
    )
    db.add(loc)

    event = TrainingEvent(
        participant_id=payload.participant_id,
        campaign_id=payload.campaign_id,
        event_type=f"LOCATION_{payload.permission_status}",
    )
    db.add(event)
    await db.commit()
    return {"status": "ok", "permission_status": payload.permission_status}


@router.get("/api/locations")
async def list_locations(db: AsyncSession = Depends(get_session)):
    result = await db.execute(
        select(LocationEvent).order_by(LocationEvent.timestamp.desc()).limit(200)
    )
    locations = result.scalars().all()
    return [
        {
            "id": loc.id,
            "participant_id": loc.participant_id,
            "campaign_id": loc.campaign_id,
            "latitude": loc.latitude,
            "longitude": loc.longitude,
            "permission_status": loc.permission_status,
            "timestamp": loc.timestamp.isoformat() if loc.timestamp else "",
        }
        for loc in locations
    ]


# ── Browser Info ──────────────────────────────────────────────────────────────

@router.post("/api/browser-info")
async def record_browser_info(payload: BrowserPayload, db: AsyncSession = Depends(get_session)):
    info = BrowserInfo(
        participant_id=payload.participant_id,
        browser=payload.browser,
        os=payload.os,
        screen_resolution=payload.screen_resolution,
        language=payload.language,
        timezone=payload.timezone,
        user_agent=payload.user_agent,
    )
    db.add(info)
    await db.commit()
    return {"status": "ok"}


@router.get("/api/browser-info")
async def list_browser_info(db: AsyncSession = Depends(get_session)):
    result = await db.execute(
        select(BrowserInfo).order_by(BrowserInfo.timestamp.desc()).limit(200)
    )
    items = result.scalars().all()
    return [
        {
            "id": b.id,
            "participant_id": b.participant_id,
            "browser": b.browser,
            "os": b.os,
            "screen_resolution": b.screen_resolution,
            "language": b.language,
            "timezone": b.timezone,
            "user_agent": b.user_agent,
            "timestamp": b.timestamp.isoformat() if b.timestamp else "",
        }
        for b in items
    ]


# ── Camera permission event ──────────────────────────────────────────────────

@router.post("/api/camera")
async def record_camera(payload: CameraPayload, db: AsyncSession = Depends(get_session)):
    event = TrainingEvent(
        participant_id=payload.participant_id,
        campaign_id=payload.campaign_id,
        event_type=f"CAMERA_{payload.permission_status}",
    )
    db.add(event)
    await db.commit()
    return {"status": "ok", "permission_status": payload.permission_status}


# ── Reports ───────────────────────────────────────────────────────────────────

@router.get("/api/reports/{campaign_id}")
async def generate_report(campaign_id: str, format: str = "html", db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    participants = campaign.participants or []
    total = len(participants)

    # Location stats
    loc_result = await db.execute(
        select(LocationEvent).where(LocationEvent.campaign_id == campaign_id)
    )
    locations = loc_result.scalars().all()
    loc_granted = sum(1 for l in locations if l.permission_status == "GRANTED")
    loc_denied = sum(1 for l in locations if l.permission_status == "DENIED")

    # Camera stats
    cam_result = await db.execute(
        select(TrainingEvent).where(
            TrainingEvent.campaign_id == campaign_id,
            TrainingEvent.event_type.in_(["CAMERA_GRANTED", "CAMERA_DENIED"]),
        )
    )
    cam_events = cam_result.scalars().all()
    cam_granted = sum(1 for e in cam_events if e.event_type == "CAMERA_GRANTED")
    cam_denied = sum(1 for e in cam_events if e.event_type == "CAMERA_DENIED")

    # Awareness score: % of participants who denied at least one permission
    denied_count = loc_denied + cam_denied
    total_decisions = loc_granted + loc_denied + cam_granted + cam_denied
    awareness_score = round((denied_count / total_decisions * 100) if total_decisions else 0)

    report_data = {
        "campaign": {
            "id": campaign.id,
            "name": campaign.name,
            "description": campaign.description,
            "status": campaign.status,
            "created_at": campaign.created_at.isoformat() if campaign.created_at else "",
            "expires_at": campaign.expires_at.isoformat() if campaign.expires_at else "",
        },
        "statistics": {
            "total_participants": total,
            "location_granted": loc_granted,
            "location_denied": loc_denied,
            "camera_granted": cam_granted,
            "camera_denied": cam_denied,
            "awareness_score": awareness_score,
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    if format == "json":
        return report_data

    # HTML report
    html = _render_html_report(report_data)

    # Persist
    report = Report(
        campaign_id=campaign_id,
        format=format,
        content=html if format == "html" else json.dumps(report_data),
    )
    db.add(report)
    await db.commit()

    return {"html": html}


# ── Dashboard stats (for React admin) ────────────────────────────────────────

@router.get("/api/dashboard/stats")
async def dashboard_stats(db: AsyncSession = Depends(get_session)):
    campaigns = (await db.execute(select(Campaign))).scalars().all()
    participants = (await db.execute(select(Participant))).scalars().all()
    locations = (await db.execute(select(LocationEvent))).scalars().all()
    events = (await db.execute(select(TrainingEvent))).scalars().all()

    loc_granted = sum(1 for l in locations if l.permission_status == "GRANTED")
    loc_denied = sum(1 for l in locations if l.permission_status == "DENIED")

    cam_granted = sum(1 for e in events if e.event_type == "CAMERA_GRANTED")
    cam_denied = sum(1 for e in events if e.event_type == "CAMERA_DENIED")

    return {
        "active_campaigns": sum(1 for c in campaigns if c.status == "active"),
        "total_campaigns": len(campaigns),
        "total_participants": len(participants),
        "location_granted": loc_granted,
        "location_denied": loc_denied,
        "camera_granted": cam_granted,
        "camera_denied": cam_denied,
        "recent_events": [
            {
                "event_type": e.event_type,
                "participant_id": e.participant_id[:8],
                "campaign_id": e.campaign_id[:8],
                "timestamp": e.timestamp.isoformat() if e.timestamp else "",
            }
            for e in sorted(events, key=lambda x: x.timestamp or datetime.min.replace(tzinfo=timezone.utc), reverse=True)[:20]
        ],
    }


# ── HTML report renderer ─────────────────────────────────────────────────────

def _render_html_report(data: dict) -> str:
    c = data["campaign"]
    s = data["statistics"]
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>STALKER Report – {c['name']}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:#0a0a0f;color:#e0e0e0;padding:40px}}
.container{{max-width:800px;margin:0 auto}}
h1{{color:#c084fc;font-size:2rem;margin-bottom:8px}}
h2{{color:#a855f7;margin:32px 0 16px;font-size:1.3rem}}
.subtitle{{color:#888;margin-bottom:32px}}
.card{{background:#161622;border:1px solid #2a2a3e;border-radius:12px;padding:24px;margin-bottom:20px}}
.stat-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px}}
.stat{{background:#1e1e30;border-radius:10px;padding:20px;text-align:center}}
.stat .value{{font-size:2rem;font-weight:700;color:#c084fc}}
.stat .label{{color:#999;margin-top:4px;font-size:.85rem}}
.score{{font-size:3rem;font-weight:800;color:#22c55e;text-align:center;padding:24px}}
.footer{{text-align:center;color:#555;margin-top:40px;font-size:.8rem}}
.badge{{display:inline-block;padding:4px 12px;border-radius:20px;font-size:.75rem;font-weight:600}}
.badge-granted{{background:#22c55e22;color:#22c55e}}
.badge-denied{{background:#ef444422;color:#ef4444}}
</style>
</head>
<body>
<div class="container">
  <h1>🔒 STALKER Security Awareness Report</h1>
  <p class="subtitle">Generated {data['generated_at'][:19]}</p>

  <div class="card">
    <h2>Campaign Details</h2>
    <p><strong>Name:</strong> {c['name']}</p>
    <p><strong>Description:</strong> {c['description']}</p>
    <p><strong>Status:</strong> {c['status']}</p>
    <p><strong>Created:</strong> {c['created_at'][:19]}</p>
    <p><strong>Expires:</strong> {c['expires_at'][:19]}</p>
  </div>

  <div class="card">
    <h2>Participant Statistics</h2>
    <div class="stat-grid">
      <div class="stat">
        <div class="value">{s['total_participants']}</div>
        <div class="label">Total Participants</div>
      </div>
      <div class="stat">
        <div class="value">{s['location_granted']}</div>
        <div class="label">Location <span class="badge badge-granted">GRANTED</span></div>
      </div>
      <div class="stat">
        <div class="value">{s['location_denied']}</div>
        <div class="label">Location <span class="badge badge-denied">DENIED</span></div>
      </div>
      <div class="stat">
        <div class="value">{s['camera_granted']}</div>
        <div class="label">Camera <span class="badge badge-granted">GRANTED</span></div>
      </div>
      <div class="stat">
        <div class="value">{s['camera_denied']}</div>
        <div class="label">Camera <span class="badge badge-denied">DENIED</span></div>
      </div>
    </div>
  </div>

  <div class="card">
    <h2>Awareness Score</h2>
    <div class="score">{s['awareness_score']}%</div>
    <p style="text-align:center;color:#999">Percentage of permission requests denied by participants</p>
  </div>

  <div class="footer">
    STALKER Framework v1.0.0 &middot; 0xPurpleMiaw16<br>
    For authorized cybersecurity training only.
  </div>
</div>
</body>
</html>"""
