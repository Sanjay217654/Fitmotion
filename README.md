# FitMotion

AI-Powered Fitness & Movement Analytics

AI-Powered Sports Performance & Fitness Analytics

**Train Smarter. Move Better. Perform Better.**

## Phase 1 status

This repository now contains the production-oriented foundation: a FastAPI service, SQLAlchemy entities, MySQL container, secure environment configuration pattern, frontend/ML module locations, and architecture/setup documentation. Authentication, Alembic migrations, frontend pages, pose processing, and analysis workflows are implemented in the following phases.

## Repository layout

- `backend/` — FastAPI API, relational entities, migrations, services, and tests.
- `frontend/` — React application and design system.
- `ml/` — privacy-aware pose-sequence data, training, models, and evaluation.
- `docs/` — architecture, API, and local setup notes.

## Database design

The initial relational design contains `users`, `workouts`, `exercise_analysis`, and `performance_history` with foreign keys and cascade cleanup. Password hashes are stored only in `users.password_hash` and are never exposed through response schemas (to be added with authentication).

Use the Windows commands in [docs/setup.md](docs/setup.md) to bring up MySQL and verify the API.

## Phase 2 status

Athlete accounts now use Argon2 password hashing, short-lived access tokens, refresh-token rotation, and server-side token revocation at logout. The protected profile API supports reading and editing profile fields, changing passwords, and uploading a JPG, PNG, or WebP profile image up to 5 MB.

## Important limitations

The future technique score is a project-defined coaching indicator, not a medical or independently validated assessment. The separate LSTM/TCN module will not report accuracy or quality metrics until a labeled, leakage-controlled dataset is trained and evaluated.
