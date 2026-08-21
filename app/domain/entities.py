from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List
from uuid import UUID, uuid4


class OrderStatus(str, Enum):
    CREATED = "CREATED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class OrderItem:
    product_id: str
    quantity: int
    unit_price: Decimal

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("quantity must be greater than zero")
        if self.unit_price < 0:
            raise ValueError("unit_price cannot be negative")

    @property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity


@dataclass
class Order:
    id: UUID
    customer_id: str
    items: List[OrderItem]
    status: OrderStatus = OrderStatus.CREATED
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if not self.items:
            raise ValueError("order must contain at least one item")

    @property
    def total(self) -> Decimal:
        return sum((item.subtotal for item in self.items), Decimal("0"))

    @classmethod
    def new(cls, customer_id: str, items: List[OrderItem]) -> "Order":
        return cls(id=uuid4(), customer_id=customer_id, items=items)
