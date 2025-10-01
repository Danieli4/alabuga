"""Seed store items data."""

from sqlalchemy.orm import Session

from app.models.store import StoreItem


def seed_store_items(session: Session) -> list[StoreItem]:
    """Create and return store items."""
    items = [
        StoreItem(
            name="Экскурсия по космодрому",
            description="Личный тур по цехам Алабуги",
            cost_mana=200,
            stock=5,
        ),
        StoreItem(
            name="Мерч экипажа",
            description="Футболка с эмблемой миссии",
            cost_mана=150,
            stock=10,
        ),
    ]
    session.add_all(items)
    session.flush()
    return items
