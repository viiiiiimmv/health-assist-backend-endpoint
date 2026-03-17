# HealthAssist — Backend API

> Flask backend powering authentication, chat APIs, mood tracking, and ML model orchestration for HealthAssist.

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=flat-square&logo=mongodb&logoColor=white)](https://mongodb.com/)
[![JWT](https://img.shields.io/badge/JWT-000000?style=flat-square&logo=jsonwebtokens&logoColor=white)](https://jwt.io/)
[![Render](https://img.shields.io/badge/Render-46E3B7?style=flat-square&logo=render&logoColor=black)](https://render.com/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue?style=flat-square)](LICENSE)

**Frontend Repo →** [health-assist-frontend-service](https://github.com/viiiiiimmv/health-assist-frontend-service)  
**Live Frontend →** [health-assist-chatbot-viiiiiimmv.vercel.app](https://health-assist-chatbot-viiiiiimmv.vercel.app)

---

## About

This is the backend service for HealthAssist — an AI-powered health chatbot platform. It handles user authentication via JWT, exposes REST APIs for chat flow and mood tracking, manages session-based history, and orchestrates calls to an external ML model for NLP-based responses and sentiment analysis.

---

## Features

- **JWT Authentication** — Secure register, login, and token-based session management
- **Chat API** — REST endpoints for sending messages and receiving ML-powered chatbot responses
- **ML Model Orchestration** — Proxies requests to an external NLP model service with configurable timeout
- **Mood Tracking** — Log and retrieve daily mood entries per user
- **Chat History** — Persistent, session-based conversation storage and retrieval
- **Sentiment Analysis** — Mood classification integrated via ML model pipeline
- **Health Check Endpoint** — `/api/health` for deployment monitoring and uptime checks
- **CORS Configuration** — Supports cross-origin requests from the Vercel frontend
- **Preflight Checks** — Shell script to validate deployment readiness before every push

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python |
| Framework | Flask |
| Database | MongoDB Atlas |
| Auth | JWT (Flask-JWT-Extended) |
| Production Server | Gunicorn |
| Deployment | Render |
| ML Integration | External NLP Model via HTTP |

---

## Project Structure

```
health-assist-backend-endpoint/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── routes/              # Blueprint route definitions
│   ├── models/              # MongoDB document models
│   └── utils/               # Helper functions
├── docs/                    # API documentation
├── scripts/
│   └── preflight_render.sh  # Pre-deployment validation script
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
├── routes.txt               # Route reference sheet
└── project_structure.sh     # Structure documentation script
```

---

## Getting Started

### Prerequisites
- Python 3.9+
- MongoDB URI (local or Atlas)
- ML model service URL (local or hosted)

### Installation

```bash
# Clone the repository
git clone https://github.com/viiiiiimmv/health-assist-backend-endpoint.git
cd health-assist-backend-endpoint

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the root:

```env
APP_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
MONGO_URI=mongodb://localhost:27017/healthchatbot
MONGO_DB_NAME=healthchatbot
ML_MODEL_URL=http://localhost:7860/predict
ML_MODEL_TIMEOUT=45
API_PREFIX=/api
AUTO_CREATE_INDEXES=true
CORS_ORIGINS=*
SHARE_BASE_URL=http://localhost:5173/share/
```

### Run Locally

```bash
python run.py
```

API available at [http://localhost:5001](http://localhost:5001)

### Health Check

```bash
curl -i http://localhost:5001/api/health
```

Expected response: `{"status": "ok"}`

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check — confirms API is live |
| `POST` | `/api/auth/register` | Register a new user |
| `POST` | `/api/auth/login` | Login and receive JWT token |
| `POST` | `/api/chat` | Send message, receive ML-powered response |
| `GET` | `/api/history/:userId` | Fetch chat history for a user |
| `POST` | `/api/mood` | Log a mood entry |
| `GET` | `/api/mood/:userId` | Retrieve mood history for a user |

---

## Pre-Deployment Checks

Run before every deployment push:

```bash
bash scripts/preflight_render.sh
```

This validates:
- Required files and directories exist
- `run.py` exports top-level `app` (for `gunicorn run:app`)
- `/api/health` returns `200` and `{"status":"ok"}`
- Python syntax across `app/` and `run.py`
- Full `pytest` test suite passes

---

## Deployment

Deployed on **Render** (Free Tier) with **MongoDB Atlas**.

**Render settings:**

| Field | Value |
|---|---|
| Environment | Python |
| Branch | main |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn run:app --bind 0.0.0.0:$PORT` |
| Health Check Path | `/api/health` |

**Production environment variables:**

```env
APP_ENV=production
SECRET_KEY=<strong-secret>
JWT_SECRET_KEY=<strong-secret>
MONGO_URI=<mongodb-atlas-uri>
MONGO_DB_NAME=healthchatbot
ML_MODEL_URL=<public-ml-service-url>/predict
ML_MODEL_TIMEOUT=45
API_PREFIX=/api
AUTO_CREATE_INDEXES=true
CORS_ORIGINS=<frontend-vercel-url>
SHARE_BASE_URL=<frontend-vercel-url>/share/
PYTHONUNBUFFERED=1
```

> Note: `MONGO_DB_NAME` is used as a fallback when `MONGO_URI` does not include a default database segment.

---

## Related

- **Frontend Client** → [health-assist-frontend-service](https://github.com/viiiiiimmv/health-assist-frontend-service)

---

## Author

**Shiv Chauhan**

[![Portfolio](https://img.shields.io/badge/Portfolio-000000?style=flat-square&logo=vercel&logoColor=white)](https://shivchauhan835.netlify.app)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://linkedin.com/in/shivchauhan)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/viiiiiimmv)

---

## License

This project is licensed under the [Apache 2.0 License](LICENSE).
