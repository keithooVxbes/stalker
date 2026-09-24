# STALKER Framework v1.0.0

```
███████╗████████╗ █████╗ ██╗     ██╗  ██╗███████╗██████╗
██╔════╝╚══██╔══╝██╔══██╗██║     ██║ ██╔╝██╔════╝██╔══██╗
███████╗   ██║   ███████║██║     █████╔╝ █████╗  ██████╔╝
╚════██║   ██║   ██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
███████║   ██║   ██║  ██║███████╗██║  ██╗███████╗██║  ██║
╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
```

**Security Tracking Awareness & Learning Knowledge Education Research**

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [CLI Usage](#cli-usage)
- [Training Scenarios](#training-scenarios)
- [Admin Dashboard](#admin-dashboard)
- [API Documentation](#api-documentation)
- [Docker Deployment](#docker-deployment)
- [Ethical Usage Guidelines](#ethical-usage-guidelines)
- [License](#license)

---

## Overview

STALKER is a professional cybersecurity awareness framework designed for **authorized training labs** only. It enables security educators to create realistic social engineering awareness campaigns that demonstrate:

- **Social engineering attack patterns** – fake rewards, urgency triggers, curiosity manipulation
- **Browser permission risks** – geolocation, camera, notifications
- **Browser fingerprinting concepts** – user agent, screen resolution, timezone exposure
- **Privacy exposure awareness** – how much data websites can collect with user consent

### Important Security Notice

This framework is **strictly for authorized cybersecurity training**. It is **NOT** designed for:

- Hidden tracking or surveillance
- Permission bypass or stealth collection
- Credential harvesting or real phishing
- Impersonation of real companies
- Any unauthorized activity

**All data collection requires explicit participant consent.**

---

## Features

| Module | Description |
|--------|-------------|
| Campaign Generator | Create & manage training campaigns with unique URLs |
| 🌐 Training Landing Pages | Social engineering awareness pages with interactive elements |
| 🔐 Consent System | Mandatory consent modal before any data collection |
| 📍 Geolocation Awareness | Demonstrate browser location permission risks |
| 📷 Camera Awareness | Optional camera permission demonstration |
| 🔍 Browser Analysis | Collect educational browser fingerprinting data |
| Reporting Engine | Generate HTML & JSON security awareness reports |
| SOC Dashboard | React-based admin dashboard with analytics |
| Security | JWT auth, bcrypt hashing, rate limiting, CSRF protection |

---

## Architecture

```
stalker/
├── stalker.py              # CLI entry point
├── cli/
│   ├── banner.py           # ASCII art & system info
│   ├── menu.py             # Interactive menu system
│   └── campaign.py         # Campaign management commands
├── backend/
│   ├── main.py             # FastAPI application
│   ├── database.py         # SQLAlchemy async engine
│   ├── models.py           # ORM models
│   └── routes.py           # API routes
├── frontend/               # React + TypeScript admin dashboard
│   └── src/
│       ├── components/     # Layout, StatCard
│       ├── pages/          # Login, Dashboard, Campaigns, Reports
│       └── services/       # API client
├── templates/
│   └── awareness_pages/    # Training landing page templates
│       └── index.html      # Spin wheel awareness page
├── reports/                # Generated reports
├── docker-compose.yml
├── Dockerfile.backend
├── requirements.txt
└── .env
```

### Tech Stack

| Layer | Technology |
|-------|-----------|
| CLI | Python 3.12, Rich, Typer, Click |
| Backend | FastAPI, SQLAlchemy, SQLite/PostgreSQL |
| Frontend | React, TypeScript, TailwindCSS v4, Recharts |
| Auth | JWT (python-jose), bcrypt (passlib) |
| Security | slowapi rate limiter, secure headers, CORS |
| Deployment | Docker, docker-compose, nginx |
| Tunneling | Built-in Cloudflare quick-tunnel (cloudflared) |

---

## Installation

### Prerequisites

- Python 3.12+
- Node.js 18+ (for admin dashboard)
- pip

### Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/stalker.git
cd stalker

# Install Python dependencies
pip install -r requirements.txt

# Configure environment
cp .env .env.local  # Edit as needed

# Run the CLI
python stalker.py
```

### Frontend Setup (Admin Dashboard)

```bash
cd frontend
npm install
npm run dev
```

The admin dashboard will be available at `http://localhost:5173`.

---

## CLI Usage

### Launch the Framework

```bash
python stalker.py
```

### Main Menu Options

| Option | Description |
|--------|-------------|
| `[01]` | Create a new training campaign |
| `[02]` | Generate a shareable awareness link |
| `[03]` | Start the FastAPI training server |
| `[04]` | List & manage existing campaigns |
| `[05]` | View participant training events |
| `[06]` | View location permission reports |
| `[07]` | View collected browser information |
| `[08]` | Generate HTML/JSON security reports |
| `[09]` | View current configuration |
| `[00]` | Exit |

### Typical Workflow

```
1. Start the server (with Tunnel) → Option [03]
2. Create a campaign              → Option [01]
3. Share the HTTPS URL            → Option [02]
4. Monitor events                 → Option [05]
5. View location reports          → Option [06]
6. Generate final report          → Option [08]
```

### Cloudflare Tunnel (Remote Access)

STALKER includes built-in support for Cloudflare quick-tunnels. When you start the server (`[03]`), you'll be asked:
`Start HTTPS tunnel for remote participants? (y/n)`

Answering `y` will automatically:
1. Start `cloudflared` in the background
2. Generate a secure HTTPS URL (e.g., `https://random-words.trycloudflare.com`)
3. Use this HTTPS URL for all generated campaign links

**Why is this important?**
Modern browsers **require HTTPS** to request Camera and Geolocation permissions. If you send an `http://0.0.0.0` link to a target, the browser will automatically deny the permissions without prompting. The Cloudflare tunnel solves this by providing a secure, public HTTPS endpoint.

---

## Training Scenarios

### Scenario 1: Prize Scam Awareness

**Objective:** Demonstrate how social engineering attacks manipulate user behavior using fake reward mechanics.

1. Create a campaign named "Prize Scam Awareness Training"
2. Share the training URL with participants
3. Participants encounter a "Congratulations! Spin the wheel!" page
4. Before any interaction, a **consent modal** explains the exercise
5. After consent, the system records browser info and requests location permission
6. Review results: how many participants granted location/camera access

### Scenario 2: Permission Awareness Lab

**Objective:** Educate participants about browser permission risks.

1. Create a campaign focused on permission awareness
2. The landing page demonstrates geolocation and camera permission requests
3. Participants learn how easily websites can request sensitive permissions
4. Generate a report showing permission grant/deny ratios

---

## Admin Dashboard

The SOC-style admin dashboard provides:

- **Dashboard** – Real-time stats, pie charts for permission ratios, recent events
- **Campaigns** – Create, view, and manage training campaigns
- **Campaign Detail** – Per-campaign stats, location events with Google Maps links
- **Reports** – Generate and download HTML/JSON reports

### Login

Default credentials (change in `.env`):

```
Username: admin
Password: changeme
```

---

## API Documentation

The FastAPI backend provides auto-generated API docs at:

- **Swagger UI:** `http://localhost:8443/docs`
- **ReDoc:** `http://localhost:8443/redoc`

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/login` | Authenticate & get JWT token |
| `POST` | `/api/campaigns` | Create a new campaign |
| `GET` | `/api/campaigns` | List all campaigns |
| `GET` | `/api/campaigns/:id` | Get campaign details |
| `POST` | `/api/consent` | Record participant consent |
| `POST` | `/api/events` | Log a training event |
| `POST` | `/api/location` | Record location permission result |
| `POST` | `/api/browser-info` | Record browser information |
| `POST` | `/api/camera` | Record camera permission result |
| `GET` | `/api/events` | List all training events |
| `GET` | `/api/locations` | List all location events |
| `GET` | `/api/browser-info` | List browser info records |
| `GET` | `/api/reports/:id` | Generate campaign report |
| `GET` | `/api/dashboard/stats` | Dashboard statistics |
| `GET` | `/train/:campaign_id` | Serve training landing page |

---

## Docker Deployment

### Using docker-compose

```bash
docker-compose up -d
```

This starts:

- **Backend** on port `8443`
- **Frontend** on port `3000`

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `STALKER_SECRET_KEY` | `change-me-...` | JWT signing key |
| `STALKER_DATABASE_URL` | `sqlite+aiosqlite:///./stalker.db` | Database connection |
| `STALKER_HOST` | `0.0.0.0` | Server bind address |
| `STALKER_PORT` | `8443` | Server port |
| `STALKER_ADMIN_USERNAME` | `admin` | Default admin user |
| `STALKER_ADMIN_PASSWORD` | `changeme` | Default admin password |
| `STALKER_CORS_ORIGINS` | `["*"]` | Allowed CORS origins |

---

## Ethical Usage Guidelines

### Authorized Use

- Corporate security awareness training
- Educational cybersecurity labs
- Penetration testing training (with authorization)
- Security research (with proper ethics approval)
- Conference demonstrations (with audience consent)

### Prohibited Use

- Unauthorized tracking or surveillance
- Real phishing campaigns
- Credential harvesting
- Privacy violations
- Any illegal activity
- Impersonation of real organizations

### Consent Requirements

- **All participants must be informed** that they are part of a security exercise
- **Explicit consent is required** before any data collection
- **Location data is only collected** when the browser permission is granted by the participant
- **All data should be deleted** after the training exercise is completed

---

## Database Models

| Model | Purpose |
|-------|---------|
| `User` | Admin accounts with bcrypt-hashed passwords |
| `Campaign` | Training campaign metadata & status |
| `Participant` | Individual training session records |
| `ConsentLog` | Consent acceptance/decline records |
| `TrainingEvent` | Activity event log (page views, spins, permissions) |
| `LocationEvent` | Geolocation permission results & coordinates |
| `BrowserInfo` | Browser fingerprinting data |
| `Report` | Generated report storage |

---

## Security Features

- **JWT Authentication** – Secure admin access with expiring tokens
- **Password Hashing** – bcrypt via passlib
- **Secure Headers** – X-Content-Type-Options, X-Frame-Options, XSS protection
- **Rate Limiting** – slowapi to prevent abuse
- **CORS Control** – Configurable allowed origins
- **Input Validation** – Pydantic model validation
- **Audit Logging** – All events recorded with timestamps
- **Environment Variables** – Sensitive config via `.env`

---

## License

This project is for **authorized cybersecurity training purposes only**.

Created by **0xPurpleMiaw16** — STALKER Framework v1.0.0

---

> *"The best defense is understanding the offense."*
