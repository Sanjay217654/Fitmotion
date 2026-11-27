# Local setup (Windows)

## Prerequisites

Install Python 3.11+, Node.js 20+, Docker Desktop (recommended for MySQL), and Git.

## Phase 1 backend check

```powershell
cd C:\FitMotion
Copy-Item .env.example .env
docker compose up -d mysql
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/health`. Swagger documentation will be available at `http://127.0.0.1:8000/docs` as API routes are added.

The local schema bootstrap command below creates the SQLAlchemy-defined tables. Alembic migrations will be added before production deployment. Database credentials in `.env` are local-development values only and must be replaced for any shared deployment.

## Initialize the database and start Phase 2

With MySQL running and the virtual environment activated:

```powershell
python -m app.database.create_schema
python -m uvicorn app.main:app --reload
python -m pytest -q
```

Use `http://127.0.0.1:8000/docs` to register an athlete and exercise the protected API. Click **Authorize** and enter `Bearer <access_token>` for endpoints that require a session.
