class DomainError(Exception):
    """Base class for all domain-level errors."""


class OrderNotFoundError(DomainError):
    """Raised when an order cannot be found by its identifier."""


class InvalidOrderError(DomainError):
    """Raised when an order fails a domain invariant."""
