# Health Assist Backend Service

Flask backend for authentication, chat/history APIs, and ML-model orchestration.

## Project Structure

```text
health-assist-backend-service/
├── run.py
├── app/
│   ├── __init__.py
│   ├── routes/
│   ├── models/
│   └── utils/
├── requirements.txt
├── .gitignore
├── README.md
└── scripts/
    └── preflight_render.sh
```

## Local Setup

```bash
cd health-assist-backend-service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `.env`:

```env
APP_ENV=development
SECRET_KEY=change-me
JWT_SECRET_KEY=change-me-too
MONGO_URI=mongodb://localhost:27017/healthchatbot
ML_MODEL_URL=http://localhost:7860/predict
ML_MODEL_TIMEOUT=45
API_PREFIX=/api
AUTO_CREATE_INDEXES=true
CORS_ORIGINS=*
SHARE_BASE_URL=http://localhost:5173/share/
```

Run locally:

```bash
python run.py
```

Health check:

```bash
curl -i http://localhost:5001/api/health
```

## One-Command Preflight Checks

Run before every deployment push:

```bash
bash scripts/preflight_render.sh
```

This checks:
- required files/dirs exist
- `run.py` exports top-level `app` (for `gunicorn run:app`)
- `/api/health` returns `200` and `{"status":"ok"}`
- Python compile/syntax on `app/` and `run.py`
- full `pytest` suite

## Render Deployment (Free Tier)

Use these exact settings:

- Environment: `Python`
- Branch: `main`
- Root Directory: `health-assist-backend-service`
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn run:app --bind 0.0.0.0:$PORT`
- Health Check Path: `/api/health`

Environment variables:

```env
APP_ENV=production
SECRET_KEY=<strong-secret>
JWT_SECRET_KEY=<strong-secret>
MONGO_URI=<mongodb-atlas-uri>
ML_MODEL_URL=<public-ml-service-url>/predict
ML_MODEL_TIMEOUT=45
API_PREFIX=/api
AUTO_CREATE_INDEXES=true
SHARE_BASE_URL=<frontend-url>/share/
CORS_ORIGINS=<frontend-url>
PYTHONUNBUFFERED=1
```
