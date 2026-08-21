from decimal import Decimal

from app.application.dto import CreateOrderInput, CreateOrderItemInput
from app.application.orchestration.create_order_orchestrator import (
    CreateOrderOrchestrator,
)
from app.infrastructure.notifications.http_simulator import (
    HttpNotificationSimulatorAdapter,
)
from app.infrastructure.repositories.in_memory import InMemoryOrderRepository

repo = InMemoryOrderRepository()
notifier = HttpNotificationSimulatorAdapter(failure_rate=0.0)
orchestrator = CreateOrderOrchestrator(repo, notifier)

result = orchestrator.run(CreateOrderInput(
    customer_id="cust-1",
    items=[CreateOrderItemInput(product_id="sku-1", quantity=2, unit_price=Decimal("19.99"))],
))

print(result)                     # CreateOrderOutput(order_id=..., total=Decimal('39.98'), ...)
print(notifier.sent_requests)     # the simulated "webhook" payload that was sent