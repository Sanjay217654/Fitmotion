# FitMotion Architecture

FitMotion is a React + FastAPI monorepo with a modular computer-vision and ML layer.

```text
React web app ──HTTP/JWT──> FastAPI API ──SQLAlchemy/Alembic──> MySQL
                                 │
                                 ├─ Pose adapter (MediaPipe first; MoveNet/RTMPose later)
                                 ├─ Rule-based analysis (angles, rep state machines, feedback)
                                 └─ Sequence-model adapter (LSTM/TCN training and evaluation)
```

The browser owns camera permission and sends frames/video to authenticated analysis endpoints. The API makes reliability explicit: when landmarks, confidence, angle, or processing-rate checks fail, it returns an unreliable status instead of a technique score. Workout persistence is always linked to the authenticated `users.id`; analytics are aggregated only from that user's workouts.

## Core data relationships

```text
users 1 ── * workouts 1 ── 0..1 exercise_analysis
  │
  └────── * performance_history
```

`workouts` stores completed-session summaries. `exercise_analysis` retains the associated joint and feedback summary. `performance_history` is an analytics-friendly time series; it is created transactionally when a workout is saved in Phase 8.

## Extension boundaries

- `services/pose_service.py`: provider interface for MediaPipe and future pose backends.
- `services/rep_counter.py`: exercise-specific state machines with configurable thresholds.
- `services/technique_service.py`: rule baseline and score decomposition.
- `services/ai_model.py`: separately versioned, trained sequence models; no unvalidated outputs are represented as facts.
