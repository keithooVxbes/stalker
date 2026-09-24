"""
STALKER - FastAPI Application
Main entry point for the backend server.
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy import select

from backend.database import init_db, async_session
from backend.models import User
from backend.routes import router

# ── Rate limiter ──────────────────────────────────────────────────────────────

limiter = Limiter(key_func=get_remote_address)

# ── Lifespan ──────────────────────────────────────────────────────────────────

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables & seed admin
    await init_db()
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.username == os.getenv("STALKER_ADMIN_USERNAME", "admin"))
        )
        if not result.scalar_one_or_none():
            admin = User(
                username=os.getenv("STALKER_ADMIN_USERNAME", "admin"),
                hashed_password=pwd_context.hash(
                    os.getenv("STALKER_ADMIN_PASSWORD", "changeme")
                ),
            )
            session.add(admin)
            await session.commit()
    # Ensure reports dir
    Path("reports").mkdir(exist_ok=True)
    yield


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="STALKER Framework",
    description="Security Tracking Awareness & Learning Knowledge Education Research",
    version="1.0.0",
    lifespan=lifespan,
)

# Security middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
origins = os.getenv("STALKER_CORS_ORIGINS", '["*"]')
import json as _json

app.add_middleware(
    CORSMiddleware,
    allow_origins=_json.loads(origins) if origins.startswith("[") else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Secure headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


# Include API routes
app.include_router(router)

# ── Serve training landing page ───────────────────────────────────────────────

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates" / "awareness_pages"


@app.get("/train/{campaign_id}", response_class=HTMLResponse)
async def serve_training_page(campaign_id: str):
    """Serve the awareness training landing page."""
    template = TEMPLATES_DIR / "index.html"
    if not template.exists():
        return HTMLResponse("<h1>Training page not found.</h1>", status_code=404)
    html = template.read_text().replace("{{CAMPAIGN_ID}}", campaign_id)
    return HTMLResponse(html)


# ── Serve static assets from templates ────────────────────────────────────────

STATIC_DIR = Path(__file__).resolve().parent.parent / "templates" / "awareness_pages" / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
