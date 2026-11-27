from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.workout import Workout


class ExerciseAnalysis(Base):
    __tablename__ = "exercise_analysis"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    workout_id: Mapped[int] = mapped_column(ForeignKey("workouts.id", ondelete="CASCADE"), unique=True, nullable=False)
    pose_accuracy: Mapped[float | None] = mapped_column(Float)
    average_knee_angle: Mapped[float | None] = mapped_column(Float)
    average_hip_angle: Mapped[float | None] = mapped_column(Float)
    average_elbow_angle: Mapped[float | None] = mapped_column(Float)
    movement_quality: Mapped[str | None] = mapped_column(String(40))
    feedback: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    workout: Mapped["Workout"] = relationship(back_populates="analysis")
