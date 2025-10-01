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
            image_url="/store/excursion-alabuga.svg",
        ),
        StoreItem(
            name="Мерч экипажа",
            description="Футболка с эмблемой миссии",
            cost_mana=150,
            stock=10,
            image_url="/store/alabuga-crew-shirt.svg",
        ),
    ]
    session.add_all(items)
    session.flush()
    return items
