"""Заготовка типизированных идентификаторов."""
from dataclasses import dataclass


def _require_text(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


@dataclass(frozen=True)
class OrderId:
    value: str

    def __post_init__(self):
        _require_text(self.value, "OrderId")


@dataclass(frozen=True)
class OrderLineId:
    value: str

    def __post_init__(self):
        _require_text(self.value, "OrderLineId")


@dataclass(frozen=True)
class BuyerId:
    value: str

    def __post_init__(self):
        _require_text(self.value, "BuyerId")


@dataclass(frozen=True)
class SellerId:
    value: str

    def __post_init__(self):
        _require_text(self.value, "SellerId")


@dataclass(frozen=True)
class Sku:
    value: str

    def __post_init__(self):
        _require_text(self.value, "Sku")


@dataclass(frozen=True)
class StockItemId:
    value: str

    def __post_init__(self):
        _require_text(self.value, "StockItemId")


@dataclass(frozen=True)
class WarehouseId:
    value: str

    def __post_init__(self):
        _require_text(self.value, "WarehouseId")


@dataclass(frozen=True)
class ReservationId:
    value: str

    def __post_init__(self):
        _require_text(self.value, "ReservationId")