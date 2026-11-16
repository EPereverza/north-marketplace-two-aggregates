"""Заготовка агрегата заказа."""
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple

from .errors import (
    CurrencyMismatchError,
    DuplicateOrderLineIdError,
    EmptyOrderError,
    IncompleteShippingAddressError,
    NoPaidLinesError,
    OrderLineNotFoundError,
    OrderNotDraftError,
    SellerMismatchError,
)
from .identifiers import BuyerId, OrderId, OrderLineId, SellerId, Sku
from .values import Currency, Money, Quantity, ShippingAddress


class OrderStatus(Enum):
    DRAFT = "DRAFT"
    PLACED = "PLACED"
    CANCELLED = "CANCELLED"


class LineKind(Enum):
    PAID = "PAID"
    GIFT = "GIFT"


@dataclass
class OrderLine:
    _id: OrderLineId
    _sku: Sku
    _title: str
    _seller_id: SellerId
    _unit_price: Money
    _quantity: Quantity
    _kind: LineKind

    def subtotal(self) -> Money:
        return self._unit_price * self._quantity.value

    def _change_quantity(self, quantity: Quantity) -> None:
        self._quantity = quantity

    def _snapshot(self) -> "OrderLineSnapshot":
        return OrderLineSnapshot(
            _id=self._id,
            _sku=self._sku,
            _title=self._title,
            _seller_id=self._seller_id,
            _unit_price=self._unit_price,
            _quantity=self._quantity,
            _kind=self._kind,
        )

    @property
    def kind(self) -> LineKind:
        return self._kind

    @property
    def seller_id(self) -> SellerId:
        return self._seller_id


@dataclass(frozen=True)
class OrderLineSnapshot:
    _id: OrderLineId
    _sku: Sku
    _title: str
    _seller_id: SellerId
    _unit_price: Money
    _quantity: Quantity
    _kind: LineKind

    @property
    def id(self) -> OrderLineId:
        return self._id

    @property
    def sku(self) -> Sku:
        return self._sku

    @property
    def quantity(self) -> Quantity:
        return self._quantity

    @property
    def kind(self) -> LineKind:
        return self._kind

    def subtotal(self) -> Money:
        return self._unit_price * self._quantity.value


class Order:
    def __init__(self, order_id: OrderId, buyer_id: BuyerId, currency: Currency):
        self._id = order_id
        self._buyer_id = buyer_id
        self._currency = currency
        self._status = OrderStatus.DRAFT
        self._seller_id: Optional[SellerId] = None
        self._lines: List[OrderLine] = []
        self._shipping_address: Optional[ShippingAddress] = None

    # --- чтение ---
    def id(self) -> OrderId:
        return self._id

    def buyer_id(self) -> BuyerId:
        return self._buyer_id

    def currency(self) -> Currency:
        return self._currency

    def status(self) -> OrderStatus:
        return self._status

    def seller_id(self) -> Optional[SellerId]:
        return self._seller_id

    def shipping_address(self) -> Optional[ShippingAddress]:
        return self._shipping_address

    def lines(self) -> Tuple[OrderLineSnapshot, ...]:
        return tuple(line._snapshot() for line in self._lines)

    def total(self) -> Money:
        total = Money(amount=0, currency=self._currency)
        for line in self._lines:
            total = total + line.subtotal()
        return total

    # --- команды ---
    def add_paid_line(
        self,
        line_id: OrderLineId,
        sku: Sku,
        title: str,
        seller_id: SellerId,
        price: Money,
        quantity: Quantity,
    ) -> None:
        self._ensure_draft()
        if not price.is_positive():
            raise ValueError("Paid line price must be positive")
        self._ensure_line_id_unique(line_id)
        self._ensure_seller_matches(seller_id)
        self._ensure_currency_matches(price)
        line = OrderLine(
            _id=line_id,
            _sku=sku,
            _title=title,
            _seller_id=seller_id,
            _unit_price=price,
            _quantity=quantity,
            _kind=LineKind.PAID,
        )
        self._attach_line(line)

    def add_gift_line(
        self,
        line_id: OrderLineId,
        sku: Sku,
        title: str,
        seller_id: SellerId,
        quantity: Quantity,
    ) -> None:
        self._ensure_draft()
        self._ensure_line_id_unique(line_id)
        self._ensure_seller_matches(seller_id)
        line = OrderLine(
            _id=line_id,
            _sku=sku,
            _title=title,
            _seller_id=seller_id,
            _unit_price=Money(amount=0, currency=self._currency),
            _quantity=quantity,
            _kind=LineKind.GIFT,
        )
        self._attach_line(line)

    def change_line_quantity(self, line_id: OrderLineId, quantity: Quantity) -> None:
        self._ensure_draft()
        line = self._find_line(line_id)
        line._change_quantity(quantity)

    def set_shipping_address(self, address: ShippingAddress) -> None:
        self._ensure_draft()
        if not address.is_complete():
            raise IncompleteShippingAddressError("Address must be complete")
        self._shipping_address = address

    def place(self) -> None:
        self._ensure_draft()
        if not self._lines:
            raise EmptyOrderError("Cannot place an empty order")
        if self._shipping_address is None or not self._shipping_address.is_complete():
            raise IncompleteShippingAddressError("Address is required to place")
        if not any(line.kind is LineKind.PAID for line in self._lines):
            raise NoPaidLinesError("Order must contain at least one paid line")
        if not self.total().is_positive():
            raise EmptyOrderError("Order total must be positive")
        self._status = OrderStatus.PLACED

    def cancel(self) -> None:
        if self._status is OrderStatus.CANCELLED:
            raise OrderNotDraftError("Order already cancelled")
        self._status = OrderStatus.CANCELLED

    # --- внутренние проверки ---
    def _ensure_draft(self) -> None:
        if self._status is not OrderStatus.DRAFT:
            raise OrderNotDraftError("Order is not in DRAFT status")

    def _ensure_line_id_unique(self, line_id: OrderLineId) -> None:
        if any(line._id == line_id for line in self._lines):
            raise DuplicateOrderLineIdError(f"Line {line_id} already exists")

    def _ensure_seller_matches(self, seller_id: SellerId) -> None:
        if self._seller_id is None:
            return
        if self._seller_id != seller_id:
            raise SellerMismatchError("All lines must belong to the same seller")

    def _ensure_currency_matches(self, price: Money) -> None:
        if price.currency != self._currency:
            raise CurrencyMismatchError("Line currency must match order currency")

    def _find_line(self, line_id: OrderLineId) -> OrderLine:
        for line in self._lines:
            if line._id == line_id:
                return line
        raise OrderLineNotFoundError(f"Line {line_id} not found")

    def _attach_line(self, line: OrderLine) -> None:
        # проверки уже выполнены до вызова
        if self._seller_id is None:
            self._seller_id = line._seller_id
        self._lines.append(line)