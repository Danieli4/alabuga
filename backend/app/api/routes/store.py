"""Магазин и заказы."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_hr
from app.db.session import get_db
from app.models.store import Order, OrderStatus, StoreItem
from app.models.user import User
from app.schemas.store import OrderCreate, OrderRead, StoreItemRead
from app.services.store import create_order, update_order_status

router = APIRouter(prefix="/api/store", tags=["store"])


@router.get("/items", response_model=list[StoreItemRead], summary="Список товаров")
def list_items(*, db: Session = Depends(get_db)) -> list[StoreItemRead]:
    """Товары магазина."""

    items = db.query(StoreItem).order_by(StoreItem.name).all()
    return [StoreItemRead.model_validate(item) for item in items]


@router.post("/orders", response_model=OrderRead, summary="Создать заказ")
def create_order_endpoint(
    order_in: OrderCreate,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OrderRead:
    """Оформляем заказ пользователя."""

    item = db.query(StoreItem).filter(StoreItem.id == order_in.item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")
    order = create_order(db, current_user, item, order_in.comment)
    db.refresh(order)
    return OrderRead.model_validate(order)


@router.get("/orders", response_model=list[OrderRead], summary="Заказы пользователя")
def list_orders(
    *, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[OrderRead]:
    """Возвращаем заказы пилота."""

    orders = (
        db.query(Order)
        .filter(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )
    return [OrderRead.model_validate(order) for order in orders]


@router.patch(
    "/orders/{order_id}",
    response_model=OrderRead,
    summary="Изменить статус заказа",
)
def patch_order(
    order_id: int,
    status_name: OrderStatus,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr),
) -> OrderRead:
    """HR может подтвердить заказ."""

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден")
    order = update_order_status(db, order, status_name)
    return OrderRead.model_validate(order)
