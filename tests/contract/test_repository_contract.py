from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.domain.entities import Order, OrderItem
from app.infrastructure.repositories.in_memory import InMemoryOrderRepository
from app.infrastructure.repositories.models import Base
from app.infrastructure.repositories.sqlalchemy_repo import SqlAlchemyOrderRepository


def make_order(customer_id: str = "cust-1") -> Order:
    return Order.new(
        customer_id=customer_id,
        items=[OrderItem(product_id="sku-1", quantity=2, unit_price=Decimal("9.99"))],
    )


@pytest.fixture
def in_memory_repo():
    return InMemoryOrderRepository()


@pytest.fixture
def sqlalchemy_repo():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    yield SqlAlchemyOrderRepository(session)
    session.close()


@pytest.fixture(params=["in_memory", "sqlalchemy"])
def repository(request, in_memory_repo, sqlalchemy_repo):
    """Parametrized fixture: every test in this module runs once per
    adapter. Adding a new OrderRepository adapter means adding one line
    here — the whole contract is re-verified against it automatically."""
    return {"in_memory": in_memory_repo, "sqlalchemy": sqlalchemy_repo}[request.param]


class TestOrderRepositoryContract:
    """
    Behavioral contract shared by every OrderRepository implementation.
    Any adapter that does not pass all of these does not satisfy the
    OrderRepository port and must not be used behind it.
    """

    def test_add_then_get_returns_equivalent_order(self, repository):
        order = make_order()
        repository.add(order)

        fetched = repository.get(order.id)

        assert fetched is not None
        assert fetched.id == order.id
        assert fetched.customer_id == order.customer_id
        assert fetched.status == order.status
        assert fetched.total == order.total
        assert len(fetched.items) == len(order.items)
        assert fetched.items[0].product_id == order.items[0].product_id

    def test_get_unknown_id_returns_none(self, repository):
        assert repository.get(uuid4()) is None

    def test_list_by_customer_filters_correctly(self, repository):
        order_a1 = make_order(customer_id="cust-A")
        order_a2 = make_order(customer_id="cust-A")
        order_b1 = make_order(customer_id="cust-B")

        repository.add(order_a1)
        repository.add(order_a2)
        repository.add(order_b1)

        result = repository.list_by_customer("cust-A")

        assert {o.id for o in result} == {order_a1.id, order_a2.id}

    def test_list_by_customer_with_no_orders_returns_empty(self, repository):
        assert repository.list_by_customer("nobody") == []
