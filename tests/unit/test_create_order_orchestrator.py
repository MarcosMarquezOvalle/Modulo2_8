from decimal import Decimal

from app.application.dto import CreateOrderInput, CreateOrderItemInput
from app.application.orchestration.create_order_orchestrator import (
    CreateOrderOrchestrator,
)
from app.infrastructure.notifications.http_simulator import (
    HttpNotificationSimulatorAdapter,
)
from app.infrastructure.repositories.in_memory import InMemoryOrderRepository


def build_input() -> CreateOrderInput:
    return CreateOrderInput(
        customer_id="cust-1",
        items=[CreateOrderItemInput(product_id="sku-1", quantity=1, unit_price=Decimal("3.00"))],
    )


def test_orchestrator_persists_order_and_sends_notification():
    repository = InMemoryOrderRepository()
    notifier = HttpNotificationSimulatorAdapter(failure_rate=0.0)
    orchestrator = CreateOrderOrchestrator(repository, notifier)

    output = orchestrator.run(build_input())

    assert repository.get(output.order_id) is not None
    assert len(notifier.sent_requests) == 1
    assert notifier.sent_requests[0]["payload"]["order_id"] == str(output.order_id)


def test_orchestrator_still_returns_output_when_notification_fails():
    repository = InMemoryOrderRepository()
    notifier = HttpNotificationSimulatorAdapter(failure_rate=1.0)
    orchestrator = CreateOrderOrchestrator(repository, notifier)

    output = orchestrator.run(build_input())

    # Order creation succeeds even though the notification "call" failed.
    assert repository.get(output.order_id) is not None
