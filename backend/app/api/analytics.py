from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import select

from app.api.dependencies import CurrentUser, DbSession
from app.models.workout import Workout

router = APIRouter(prefix="/analytics", tags=["Analytics"])


class RecentWorkout(BaseModel):
    id: int
    exercise: str
    total_reps: int
    technique_score: float | None
    duration_seconds: int
    created_at: datetime
    has_analyzed_video: bool
    correct_reps: int
    incorrect_reps: int

    model_config = {"from_attributes": True}


class AnalyticsSummary(BaseModel):
    total_workouts: int
    total_reps: int
    average_technique_score: float | None
    best_technique_score: float | None
    total_duration_seconds: int
    exercise_counts: dict[str, int]
    recent_workouts: list[RecentWorkout]


@router.get("/summary", response_model=AnalyticsSummary)
def get_summary(db: DbSession, current_user: CurrentUser) -> AnalyticsSummary:
    workouts = db.scalars(
        select(Workout)
        .where(Workout.user_id == current_user.id)
        .order_by(Workout.created_at.desc())
    ).all()
    scores = [workout.technique_score for workout in workouts if workout.technique_score is not None]
    exercise_counts: dict[str, int] = {}
    for workout in workouts:
        exercise_counts[workout.exercise] = exercise_counts.get(workout.exercise, 0) + 1

    return AnalyticsSummary(
        total_workouts=len(workouts),
        total_reps=sum(workout.total_reps for workout in workouts),
        average_technique_score=round(sum(scores) / len(scores), 1) if scores else None,
        best_technique_score=round(max(scores), 1) if scores else None,
        total_duration_seconds=sum(workout.duration_seconds for workout in workouts),
        exercise_counts=exercise_counts,
        recent_workouts=[
            RecentWorkout(
                id=workout.id,
                exercise=workout.exercise,
                total_reps=workout.total_reps,
                technique_score=workout.technique_score,
                duration_seconds=workout.duration_seconds,
                created_at=workout.created_at,
                has_analyzed_video=bool(workout.analysis_video_url),
                correct_reps=workout.correct_reps,
                incorrect_reps=workout.incorrect_reps,
            )
            for workout in workouts[:5]
        ],
    )
