"""Заготовка доменных ошибок."""
class DomainError(Exception):
    """Базовый класс доменных ошибок."""


class EmptyOrderError(DomainError):
    pass


class IncompleteShippingAddressError(DomainError):
    pass


class OrderNotDraftError(DomainError):
    pass


class DuplicateOrderLineIdError(DomainError):
    pass


class OrderLineNotFoundError(DomainError):
    pass


class CurrencyMismatchError(DomainError):
    pass


class SellerMismatchError(DomainError):
    pass


class NoPaidLinesError(DomainError):
    pass


class InvalidQuantityError(DomainError):
    pass


class NegativeStockError(DomainError):
    pass


class InsufficientStockError(DomainError):
    pass


class DuplicateReservationIdError(DomainError):
    pass


class ReservationNotFoundError(DomainError):
    pass


class ReservationNotActiveError(DomainError):
    pass