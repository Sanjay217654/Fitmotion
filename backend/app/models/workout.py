from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.analysis import ExerciseAnalysis
    from app.models.user import User


class Workout(Base):
    __tablename__ = "workouts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    exercise: Mapped[str] = mapped_column(String(40), nullable=False)
    total_reps: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    correct_reps: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    incorrect_reps: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    technique_score: Mapped[float | None] = mapped_column(Float)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    calories_estimate: Mapped[float | None] = mapped_column(Float)
    analysis_video_url: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    user: Mapped["User"] = relationship(back_populates="workouts")
    analysis: Mapped["ExerciseAnalysis | None"] = relationship(back_populates="workout", cascade="all, delete-orphan", uselist=False)
