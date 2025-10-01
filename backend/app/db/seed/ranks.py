"""Seed ranks data."""

from sqlalchemy.orm import Session

from app.models.rank import Rank


def seed_ranks(session: Session) -> list[Rank]:
    """Create and return ranks."""
    ranks = [
        Rank(title="Искатель", description="Первое знакомство с космофлотом", required_xp=0),
        Rank(title="Пилот-кандидат", description="Готовится к старту", required_xp=200),
        Rank(title="Член экипажа", description="Активно выполняет миссии", required_xp=500),
    ]
    session.add_all(ranks)
    session.flush()
    return ranks
