from decimal import Decimal

import pytest

from app.domain.entities import Order, OrderItem
from app.infrastructure.notifications.http_simulator import (
    HttpNotificationError,
    HttpNotificationSimulatorAdapter,
)


def make_order() -> Order:
    return Order.new(
        customer_id="cust-1",
        items=[OrderItem(product_id="sku-1", quantity=1, unit_price=Decimal("5.00"))],
    )


@pytest.fixture(params=["http_simulator"])
def notifier(request):
    """Parametrized the same way as the repository contract: adding a new
    NotificationPort adapter (e.g. a real HTTP client, an SQS publisher)
    means adding one entry here."""
    return {"http_simulator": HttpNotificationSimulatorAdapter(failure_rate=0.0)}[
        request.param
    ]


class TestNotificationPortContract:
    def test_successful_notification_records_the_call(self, notifier):
        order = make_order()

        notifier.notify_order_created(order)

        assert len(notifier.sent_requests) == 1
        payload = notifier.sent_requests[0]["payload"]
        assert payload["order_id"] == str(order.id)
        assert payload["event"] == "order.created"
        assert payload["total"] == str(order.total)

    def test_failed_notification_raises_notification_error(self):
        failing_notifier = HttpNotificationSimulatorAdapter(failure_rate=1.0)
        order = make_order()

        with pytest.raises(HttpNotificationError):
            failing_notifier.notify_order_created(order)
