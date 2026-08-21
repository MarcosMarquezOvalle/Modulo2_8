from __future__ import annotations

from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.application.dto import CreateOrderInput
from app.application.dto import CreateOrderItemInput
from app.application.orchestration.create_order_orchestrator import (
    CreateOrderOrchestrator,
)
from app.infrastructure.notifications.http_simulator import (
    HttpNotificationSimulatorAdapter,
)
from app.infrastructure.repositories.in_memory import InMemoryOrderRepository
from app.infrastructure.repositories.models import Base
from app.infrastructure.repositories.sqlalchemy_repo import SqlAlchemyOrderRepository

repo = InMemoryOrderRepository()
notifier = HttpNotificationSimulatorAdapter(failure_rate=0.0)
orchestrator = CreateOrderOrchestrator(repo, notifier)

result = orchestrator.run(
    CreateOrderInput(
        customer_id="cust-1",
        items=[
            CreateOrderItemInput(
                product_id="sku-1",
                quantity=2,
                unit_price=Decimal("19.99"),
            ),
        ],
    ),
)

# CreateOrderOutput(order_id=..., total=Decimal('39.98'), ...)
print(result)
# the simulated "webhook" payload that was sent
print(notifier.sent_requests)

print("\n--- Now using a real database ---\n")

engine = create_engine("sqlite:///orders.db")  # or a real Postgres URL
Base.metadata.create_all(engine)
session = sessionmaker(bind=engine)()
repo = SqlAlchemyOrderRepository(session)
notifier = HttpNotificationSimulatorAdapter(failure_rate=0.0)
orchestrator = CreateOrderOrchestrator(repo, notifier)

result = orchestrator.run(
    CreateOrderInput(
        customer_id="cust-1",
        items=[
            CreateOrderItemInput(
                product_id="sku-1",
                quantity=2,
                unit_price=Decimal("19.99"),
            ),
        ],
    ),
)

# CreateOrderOutput(order_id=..., total=Decimal('39.98'), ...)
print(result)
# the simulated "webhook" payload that was sent
print(notifier.sent_requests)
