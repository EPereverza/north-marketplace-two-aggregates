"""Заготовка объектов-значений и перечислений."""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from .errors import InvalidQuantityError, NegativeStockError


@dataclass(frozen=True)
class Currency:
    code: str

    def __post_init__(self):
        if not isinstance(self.code, str) or len(self.code) != 3:
            raise ValueError("Currency code must be 3 letters")
        if not self.code.isalpha():
            raise ValueError("Currency code must be alphabetic")
        object.__setattr__(self, "code", self.code.upper())

    def __str__(self) -> str:
        return self.code


@dataclass(frozen=True)
class Quantity:
    value: int

    def __post_init__(self):
        if not isinstance(self.value, int) or self.value <= 0:
            raise InvalidQuantityError("Quantity must be a positive integer")


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: Currency

    def __post_init__(self):
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, "amount", Decimal(self.amount))
        if self.amount < 0:
            raise ValueError("Money amount must be non-negative")

    def __add__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, factor: int) -> "Money":
        if not isinstance(factor, int) or factor < 0:
            raise ValueError("Factor must be a non-negative integer")
        return Money(self.amount * factor, self.currency)

    def is_positive(self) -> bool:
        return self.amount > 0

    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency}"


@dataclass(frozen=True)
class ShippingAddress:
    city: str
    street: str
    building: str
    postal_code: str

    def __post_init__(self):
        for field_name in ("city", "street", "building", "postal_code"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"ShippingAddress.{field_name} must be non-empty")

    def is_complete(self) -> bool:
        return all(
            getattr(self, f).strip()
            for f in ("city", "street", "building", "postal_code")
        )


@dataclass(frozen=True)
class StockBalance:
    value: int

    def __post_init__(self):
        if not isinstance(self.value, int) or self.value < 0:
            raise NegativeStockError("StockBalance cannot be negative")

    def increase(self, quantity: Quantity) -> "StockBalance":
        return StockBalance(self.value + quantity.value)

    def decrease(self, quantity: Quantity) -> "StockBalance":
        if quantity.value > self.value:
            raise NegativeStockError("Cannot write off more than available")
        return StockBalance(self.value - quantity.value)

    def __sub__(self, other: "StockBalance") -> "StockBalance":
        return StockBalance(self.value - other.value)


@dataclass(frozen=True)
class ReservationDeadline:
    value: datetime

    def __post_init__(self):
        if not isinstance(self.value, datetime):
            raise ValueError("ReservationDeadline must be a datetime")

    def has_come(self, now: datetime) -> bool:
        return now >= self.value