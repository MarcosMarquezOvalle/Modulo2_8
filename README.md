# CreateOrder — Use Case, Orchestration & Adapters

A small hexagonal-architecture (ports & adapters) project built around a
single use case, `CreateOrder`, showing how to keep business logic,
orchestration, and infrastructure cleanly separated and independently
testable.

## Layout

```
app/
  domain/
    entities.py          Order, OrderItem, OrderStatus (business rules live here)
    exceptions.py
  application/
    dto.py                Input/Output DTOs for the use case
    ports.py               OrderRepository and NotificationPort interfaces
    use_cases/
      create_order.py      CreateOrderUseCase — pure business logic
    orchestration/
      create_order_orchestrator.py   Coordinates the use case + side effects
  infrastructure/
    repositories/
      in_memory.py          InMemoryOrderRepository adapter
      sqlalchemy_repo.py     SqlAlchemyOrderRepository adapter
      models.py               SQLAlchemy ORM models
    notifications/
      http_simulator.py     HttpNotificationSimulatorAdapter (simulates an
                             outbound webhook call, no real network I/O)
tests/
  unit/                    Tests against the use case and orchestrator directly
  contract/                Same test suite run against every adapter of a port
```

## Design notes

- **Use case vs. orchestrator.** `CreateOrderUseCase` only knows about the
  domain and the `OrderRepository` port — no notifications, no logging
  policy. `CreateOrderOrchestrator` wraps it and adds the side effect
  (notifying an external system) without leaking that concern into the
  business logic. This makes the use case trivial to test and reuse (e.g.
  from a CLI, a batch job, or an HTTP endpoint) without dragging along
  notification behavior.
- **Ports & adapters.** `OrderRepository` and `NotificationPort` are
  abstract interfaces defined in `application/ports.py`. Nothing in
  `domain/` or `application/` imports SQLAlchemy or any HTTP library —
  only `infrastructure/` adapters do. Swapping `InMemoryOrderRepository`
  for `SqlAlchemyOrderRepository`, or the HTTP simulator for a real HTTP
  client, requires no change to the use case or orchestrator.
- **Notification failures don't roll back order creation.** The order is
  already durably persisted by the time the orchestrator notifies; a
  notification failure is logged, not raised, so a flaky downstream
  webhook can never make order creation appear to fail. A production
  version would likely replace the `try/except` with an outbox pattern.

## Contract testing

`tests/contract/` holds one test suite per port (`OrderRepository`,
`NotificationPort`), each parametrized over every adapter that implements
it. This guarantees that `InMemoryOrderRepository` and
`SqlAlchemyOrderRepository` behave identically from the use case's point
of view — the whole point of depending on a port instead of a concrete
class. Adding a new adapter (e.g. a Postgres-specific repository, a real
HTTP notifier) means adding one line to the relevant fixture; the full
contract is then re-verified against it automatically.

## Running

```bash
pip install -r requirements.txt
pytest
```

Run just the contract suite:

```bash
pytest tests/contract -v
```
