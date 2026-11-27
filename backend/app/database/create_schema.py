"""Local development schema bootstrapper.

Use Alembic migrations for production deployments once introduced. This script gives
students a safe, explicit way to initialize their locally configured database.
"""

from app.database.base import Base
from app.database.session import engine
from app.database.schema_upgrade import ensure_schema_compatibility
import app.models  # noqa: F401 - imports all metadata-bearing entities


def main() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_schema_compatibility()
    print("FitMotion database schema is ready.")


if __name__ == "__main__":
    main()
