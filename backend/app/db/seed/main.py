"""Main seed orchestrator."""

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal

from .artifacts import seed_artifacts
from .branches import seed_branches
from .competencies import seed_competencies
from .missions import seed_missions
from .onboarding import seed_onboarding_slides
from .ranks import seed_ranks
from .store import seed_store_items
from .users import seed_users

DATA_SENTINEL = settings.sqlite_path.parent / ".seeded"


def seed() -> None:
    """Main seeding function that orchestrates all seed modules.
    """
    if DATA_SENTINEL.exists():
        print("Database already seeded, skipping")
        return

    session: Session = SessionLocal()
    try:
        print("Starting database seeding...")
        
        # Seed in dependency order
        print("  - Seeding competencies...")
        competencies = seed_competencies(session)
        
        print("  - Seeding ranks...")
        ranks = seed_ranks(session)
        
        print("  - Seeding artifacts...")
        artifacts = seed_artifacts(session)
        
        print("  - Seeding branches...")
        branches = seed_branches(session)
        
        print("  - Seeding missions...")
        missions = seed_missions(session, branches, ranks, artifacts, competencies)
        
        print("  - Seeding store items...")
        seed_store_items(session)
        
        print("  - Seeding users...")
        seed_users(session, ranks, competencies, artifacts, missions)
        
        print("  - Seeding onboarding slides...")
        seed_onboarding_slides(session)
        
        session.commit()
        DATA_SENTINEL.write_text("seeded")
        print("Database seeding completed successfully!")
    except Exception as e:
        session.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed()
