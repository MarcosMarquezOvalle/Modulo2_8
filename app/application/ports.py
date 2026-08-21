from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.entities import Order


class OrderRepository(ABC):
    """Port for persisting and retrieving orders. Implemented by adapters
    such as InMemoryOrderRepository and SqlAlchemyOrderRepository."""

    @abstractmethod
    def add(self, order: Order) -> None:
        ...

    @abstractmethod
    def get(self, order_id: UUID) -> Optional[Order]:
        ...

    @abstractmethod
    def list_by_customer(self, customer_id: str) -> List[Order]:
        ...


class NotificationPort(ABC):
    """Port for notifying external systems that an order was created.
    Implemented by adapters such as HttpNotificationSimulatorAdapter."""

    @abstractmethod
    def notify_order_created(self, order: Order) -> None:
        ...
