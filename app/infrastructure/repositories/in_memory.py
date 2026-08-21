from threading import Lock
from typing import Dict, List, Optional
from uuid import UUID

from app.application.ports import OrderRepository
from app.domain.entities import Order


class InMemoryOrderRepository(OrderRepository):
    """Thread-safe in-memory implementation of OrderRepository. Useful for
    unit tests, local development, and contract testing."""

    def __init__(self):
        self._orders: Dict[UUID, Order] = {}
        self._lock = Lock()

    def add(self, order: Order) -> None:
        with self._lock:
            self._orders[order.id] = order

    def get(self, order_id: UUID) -> Optional[Order]:
        return self._orders.get(order_id)

    def list_by_customer(self, customer_id: str) -> List[Order]:
        return [o for o in self._orders.values() if o.customer_id == customer_id]
