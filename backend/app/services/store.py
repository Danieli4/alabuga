"""Сервис магазина."""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.journal import JournalEventType
from app.models.store import Order, OrderStatus, StoreItem
from app.models.user import User
from app.services.journal import log_event
from app.schemas.store import StoreItemRead


def build_store_image_url(relative_path: str | None) -> str | None:
    """Преобразуем относительный путь в публичный URL."""

    if not relative_path:
        return None
    normalized = relative_path.lstrip("/")
    return f"/uploads/{normalized}"


def store_item_to_read(item: StoreItem) -> StoreItemRead:
    """Готовим схему товара с публичным URL изображения."""

    return StoreItemRead(
        id=item.id,
        name=item.name,
        description=item.description,
        cost_mana=item.cost_mana,
        stock=item.stock,
        image_url=build_store_image_url(item.image_url),
    )


def create_order(db: Session, user: User, item: StoreItem, comment: str | None) -> Order:
    """Пытаемся списать ману и создать заказ."""

    if item.stock <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Товар закончился")
    if user.mana < item.cost_mana:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Недостаточно маны")

    user.mana -= item.cost_mana
    item.stock -= 1

    order = Order(user_id=user.id, item_id=item.id, comment=comment)
    db.add_all([user, item, order])
    db.commit()
    db.refresh(order)

    log_event(
        db,
        user_id=user.id,
        event_type=JournalEventType.ORDER_CREATED,
        title=f"Заказ «{item.name}» оформлен",
        description="Команда HR подтвердит и передаст приз.",
        payload={"order_id": order.id, "item_id": item.id},
        mana_delta=-item.cost_mana,
    )

    return order


def update_order_status(db: Session, order: Order, status_: OrderStatus) -> Order:
    """Обновляем статус заказа."""

    order.status = status_
    db.add(order)
    db.commit()
    db.refresh(order)

    if status_ == OrderStatus.APPROVED:
        log_event(
            db,
            user_id=order.user_id,
            event_type=JournalEventType.ORDER_APPROVED,
            title=f"Заказ «{order.item.name}» одобрен",
            description="Скоро мы свяжемся для вручения.",
            payload={"order_id": order.id},
        )

    return order
