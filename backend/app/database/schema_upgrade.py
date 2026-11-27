"""Small, idempotent local-development schema upgrades."""

from sqlalchemy import inspect, text

from app.database.session import engine


def ensure_schema_compatibility() -> None:
    """Add additive columns needed by newer local versions of FitMotion."""
    inspector = inspect(engine)
    if "workouts" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("workouts")}
    if "analysis_video_url" not in columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE workouts ADD COLUMN analysis_video_url VARCHAR(500)"))
