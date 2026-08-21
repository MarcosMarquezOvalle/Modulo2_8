import logging

from app.application.dto import CreateOrderInput, CreateOrderOutput
from app.application.ports import NotificationPort, OrderRepository
from app.application.use_cases.create_order import CreateOrderUseCase

logger = logging.getLogger(__name__)


class CreateOrderOrchestrator:
    """
    Coordinates the CreateOrder use case with side-effecting adapters
    (notifications today; logging/event-publishing tomorrow) without
    polluting the pure use case with infrastructure concerns.

    Design choice: a notification failure does NOT roll back or fail the
    order creation — the order was already persisted successfully by the
    use case. The failure is logged so it can be retried/alerted on by
    infrastructure outside this orchestrator (e.g. an outbox/retry worker).
    """

    def __init__(self, repository: OrderRepository, notifier: NotificationPort):
        self._use_case = CreateOrderUseCase(repository)
        self._repository = repository
        self._notifier = notifier

    def run(self, input_dto: CreateOrderInput) -> CreateOrderOutput:
        output = self._use_case.execute(input_dto)

        order = self._repository.get(output.order_id)
        assert order is not None  # just persisted by the use case above

        try:
            self._notifier.notify_order_created(order)
        except Exception:
            logger.exception(
                "Failed to send notification for order %s; the order was "
                "created successfully and this failure does not affect it.",
                output.order_id,
            )

        return output
