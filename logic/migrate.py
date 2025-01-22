import sys
from pathlib import Path
from settings import settings

print("settings.DATABASE_URL", settings.DATABASE_URL)

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from alembic import command
from alembic.config import Config

def run_migrations(script_location: str = "migrations"):
    """Run database migrations."""
    # Create Alembic configuration
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("script_location", script_location)
    alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

    try:
        print("Running database migrations...")
        command.upgrade(alembic_cfg, "head")
        print("Migrations completed successfully!")
    except Exception as e:
        print(f"Error running migrations: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_migrations()