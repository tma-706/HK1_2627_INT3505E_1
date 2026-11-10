from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..extensions import db

if TYPE_CHECKING:
    from .product import Product

class Order(db.Model):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(
        primary_key=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )
    @property
    def total_cents(self) -> int:
        return sum(
            item.line_total_cents
            for item in self.items
        )

class OrderItem(db.Model):
    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="ck_order_items_quantity_positive",
        ),
        CheckConstraint(
            "unit_price_cents >= 0",
            name="ck_order_items_price_non_negative",
        ),
        UniqueConstraint(
            "order_id",
            "product_id",
            name="uq_order_items_order_product",
        ),
    )
    id: Mapped[int] = mapped_column(
        primary_key=True,
    )
    order_id: Mapped[int] = mapped_column(
        ForeignKey(
            "orders.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    # Lưu giá tại thời điểm đặt hàng.
    unit_price_cents: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    order: Mapped["Order"] = relationship(
        back_populates="items",
    )
    product: Mapped["Product"] = relationship(
        back_populates="order_items",
    )

    @property
    def line_total_cents(self) -> int:
        return self.quantity * self.unit_price_cents