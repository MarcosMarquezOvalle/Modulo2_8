import logging
import random
import time
from dataclasses import dataclass
from typing import List

from app.application.ports import NotificationPort
from app.domain.entities import Order

logger = logging.getLogger(__name__)


@dataclass
class SimulatedHttpResponse:
    status_code: int
    payload: dict


class HttpNotificationError(Exception):
    """Raised when the simulated HTTP notification 'call' fails."""

    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code


class HttpNotificationSimulatorAdapter(NotificationPort):
    """
    Simulates an outbound HTTP call to a notification service (e.g. a
    webhook or messaging gateway) without doing real network I/O. Useful
    for local development, unit tests, and contract tests, and can be
    swapped 1:1 for a real `requests`/`httpx`-based adapter later since
    both implement the same NotificationPort.
    """

    def __init__(
        self,
        endpoint: str = "https://notifications.example.com/webhooks/orders",
        failure_rate: float = 0.0,
        simulated_latency_seconds: float = 0.0,
    ):
        self._endpoint = endpoint
        self._failure_rate = failure_rate
        self._latency = simulated_latency_seconds
        self.sent_requests: List[dict] = []

    def notify_order_created(self, order: Order) -> None:
        payload = {
            "event": "order.created",
            "order_id": str(order.id),
            "customer_id": order.customer_id,
            "status": order.status.value,
            "total": str(order.total),
            "items": [
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": str(item.unit_price),
                }
                for item in order.items
            ],
        }

        if self._latency:
            time.sleep(self._latency)

        response = self._simulate_post(payload)
        self.sent_requests.append({"endpoint": self._endpoint, "payload": payload})

        if response.status_code >= 400:
            raise HttpNotificationError(
                response.status_code,
                f"Simulated notification POST to {self._endpoint} failed "
                f"with status {response.status_code}",
            )

        logger.info(
            "Simulated notification sent to %s for order %s (status=%s)",
            self._endpoint,
            order.id,
            response.status_code,
        )

    def _simulate_post(self, payload: dict) -> SimulatedHttpResponse:
        if random.random() < self._failure_rate:
            return SimulatedHttpResponse(status_code=500, payload=payload)
        return SimulatedHttpResponse(status_code=200, payload={"received": True})
