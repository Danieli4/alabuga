"""Схемы магазина."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.store import OrderStatus


class StoreItemRead(BaseModel):
    """Товар магазина."""

    id: int
    name: str
    description: str
    cost_mana: int
    stock: int

    class Config:
        from_attributes = True


class OrderRead(BaseModel):
    """Информация о заказе."""

    id: int
    item: StoreItemRead
    status: OrderStatus
    comment: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    """Запрос на создание заказа."""

    item_id: int
    comment: Optional[str] = None
