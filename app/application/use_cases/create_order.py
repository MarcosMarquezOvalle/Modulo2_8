from app.application.dto import CreateOrderInput, CreateOrderOutput
from app.application.ports import OrderRepository
from app.domain.entities import Order, OrderItem


class CreateOrderUseCase:
    """Pure business use case: validate input, build the Order aggregate,
    and persist it. Has no knowledge of HTTP, notifications, or any other
    infrastructure concern — only depends on the OrderRepository port."""

    def __init__(self, repository: OrderRepository):
        self._repository = repository

    def execute(self, input_dto: CreateOrderInput) -> CreateOrderOutput:
        items = [
            OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in input_dto.items
        ]
        order = Order.new(customer_id=input_dto.customer_id, items=items)
        self._repository.add(order)

        return CreateOrderOutput(
            order_id=order.id,
            customer_id=order.customer_id,
            status=order.status.value,
            total=order.total,
        )
