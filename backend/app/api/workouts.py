import os
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select

from app.api.dependencies import CurrentUser, DbSession
from app.models.workout import Workout

router = APIRouter(prefix="/workouts", tags=["Workouts"])


class WorkoutCreate(BaseModel):
    exercise: str = Field(min_length=2, max_length=40)
    total_reps: int = Field(default=0, ge=0)
    correct_reps: int = Field(default=0, ge=0)
    incorrect_reps: int = Field(default=0, ge=0)
    technique_score: float | None = Field(default=None, ge=0, le=100)
    duration_seconds: int = Field(default=0, ge=0)
    calories_estimate: float | None = Field(default=None, ge=0)
    analysis_video_url: str | None = Field(default=None, max_length=500)


class WorkoutResponse(BaseModel):
    id: int
    exercise: str
    total_reps: int
    correct_reps: int
    incorrect_reps: int
    technique_score: float | None
    duration_seconds: int
    calories_estimate: float | None
    analysis_video_url: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


@router.post(
    "",
    response_model=WorkoutResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_workout(
    workout_data: WorkoutCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    workout = Workout(
        user_id=current_user.id,
        exercise=workout_data.exercise,
        total_reps=workout_data.total_reps,
        correct_reps=workout_data.correct_reps,
        incorrect_reps=workout_data.incorrect_reps,
        technique_score=workout_data.technique_score,
        duration_seconds=workout_data.duration_seconds,
        calories_estimate=workout_data.calories_estimate,
        analysis_video_url=workout_data.analysis_video_url,
    )

    db.add(workout)
    db.commit()
    db.refresh(workout)

    return workout


@router.get("/{workout_id}/video")
def get_saved_workout_video(
    workout_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> FileResponse:
    """Serve a saved analyzed video only to the athlete who owns its workout."""
    workout = db.scalar(select(Workout).where(Workout.id == workout_id, Workout.user_id == current_user.id))
    if workout is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found.")
    if not workout.analysis_video_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No analyzed video is saved for this workout.")
    try:
        video_id = str(UUID(workout.analysis_video_url.rsplit("/", 1)[-1]))
    except (ValueError, IndexError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved video is unavailable.") from exc
    video_path = os.path.join("generated_videos", f"analyzed_{video_id}.mp4")
    if not os.path.exists(video_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved video file is unavailable.")
    return FileResponse(video_path, media_type="video/mp4", filename=f"workout_{workout_id}.mp4", headers={"Content-Disposition": "inline"})


@router.get("", response_model=list[WorkoutResponse])
def get_workouts(
    db: DbSession,
    current_user: CurrentUser,
):
    workouts = db.scalars(
        select(Workout)
        .where(Workout.user_id == current_user.id)
        .order_by(Workout.created_at.desc())
    ).all()

    return workouts


@router.get("/{workout_id}", response_model=WorkoutResponse)
def get_workout(
    workout_id: int,
    db: DbSession,
    current_user: CurrentUser,
):
    workout = db.scalar(
        select(Workout).where(
            Workout.id == workout_id,
            Workout.user_id == current_user.id,
        )
    )

    if workout is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found.",
        )

    return workout


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(
    workout_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    """Delete one workout owned by the authenticated athlete."""
    workout = db.scalar(
        select(Workout).where(
            Workout.id == workout_id,
            Workout.user_id == current_user.id,
        )
    )
    if workout is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found.")
    db.delete(workout)
    db.commit()
