from __future__ import annotations

from decimal import Decimal

import pytest

from app.application.dto import CreateOrderInput
from app.application.dto import CreateOrderItemInput
from app.application.use_cases.create_order import CreateOrderUseCase
from app.domain.entities import OrderStatus
from app.infrastructure.repositories.in_memory import InMemoryOrderRepository


@pytest.fixture
def use_case():
    return CreateOrderUseCase(InMemoryOrderRepository())


def test_creates_order_with_correct_total(use_case):
    input_dto = CreateOrderInput(
        customer_id="cust-1",
        items=[
            CreateOrderItemInput(
                product_id="sku-1",
                quantity=2,
                unit_price=Decimal("10.00"),
            ),
            CreateOrderItemInput(
                product_id="sku-2",
                quantity=1,
                unit_price=Decimal("5.50"),
            ),
        ],
    )

    output = use_case.execute(input_dto)

    assert output.status == OrderStatus.CREATED.value
    assert output.total == Decimal("25.50")
    assert output.customer_id == "cust-1"


def test_rejects_order_with_no_items(use_case):
    input_dto = CreateOrderInput(customer_id="cust-1", items=[])

    with pytest.raises(ValueError):
        use_case.execute(input_dto)


def test_rejects_negative_quantity(use_case):
    input_dto = CreateOrderInput(
        customer_id="cust-1",
        items=[
            CreateOrderItemInput(
                product_id="sku-1",
                quantity=-1,
                unit_price=Decimal("1.00"),
            ),
        ],
    )

    with pytest.raises(ValueError):
        use_case.execute(input_dto)


def test_persists_order_so_it_can_be_retrieved():
    repository = InMemoryOrderRepository()
    use_case = CreateOrderUseCase(repository)
    input_dto = CreateOrderInput(
        customer_id="cust-1",
        items=[
            CreateOrderItemInput(
                product_id="sku-1",
                quantity=1,
                unit_price=Decimal("2.00"),
            ),
        ],
    )

    output = use_case.execute(input_dto)

    assert repository.get(output.order_id) is not None
