from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.application.ports import OrderRepository
from app.domain.entities import Order
from app.domain.entities import OrderItem
from app.domain.entities import OrderStatus
from app.infrastructure.repositories.models import OrderItemModel
from app.infrastructure.repositories.models import OrderModel


class SqlAlchemyOrderRepository(OrderRepository):
    """SQLAlchemy implementation of OrderRepository. Works against any
    SQLAlchemy-supported database (SQLite for tests, Postgres/MySQL in
    production) via the injected Session."""

    def __init__(self, session: Session):
        self._session = session

    def add(self, order: Order) -> None:
        model = OrderModel(
            id=order.id,
            customer_id=order.customer_id,
            status=order.status.value,
            created_at=order.created_at,
            items=[
                OrderItemModel(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )
                for item in order.items
            ],
        )
        self._session.add(model)
        self._session.commit()

    def get(self, order_id: UUID) -> Order | None:
        model = self._session.get(OrderModel, order_id)
        if model is None:
            return None
        return self._to_domain(model)

    def list_by_customer(self, customer_id: str) -> list[Order]:
        models = (
            self._session.query(OrderModel)
            .filter(OrderModel.customer_id == customer_id)
            .all()
        )
        return [self._to_domain(m) for m in models]

    @staticmethod
    def _to_domain(model: OrderModel) -> Order:
        return Order(
            id=model.id,
            customer_id=model.customer_id,
            items=[
                OrderItem(
                    product_id=i.product_id,
                    quantity=i.quantity,
                    unit_price=i.unit_price,
                )
                for i in model.items
            ],
            status=OrderStatus(model.status),
            created_at=model.created_at,
        )
