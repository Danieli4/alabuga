"""Магазин и заказы."""

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from sqlalchemy import Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class OrderStatus(str, Enum):
    """Статусы заказа в магазине."""

    CREATED = "created"
    APPROVED = "approved"
    REJECTED = "rejected"
    DELIVERED = "delivered"


class StoreItem(Base, TimestampMixin):
    """Товар, который можно приобрести за ману."""

    __tablename__ = "store_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    cost_mana: Mapped[int] = mapped_column(Integer, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(512))

    orders: Mapped[List["Order"]] = relationship("Order", back_populates="item")


class Order(Base, TimestampMixin):
    """Заказ пользователя."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    item_id: Mapped[int] = mapped_column(ForeignKey("store_items.id"), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(OrderStatus), default=OrderStatus.CREATED, nullable=False
    )
    comment: Mapped[Optional[str]] = mapped_column(Text)

    user = relationship("User", back_populates="orders")
    item = relationship("StoreItem", back_populates="orders")
