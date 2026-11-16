"""Заготовка агрегата складской позиции."""
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple

from .errors import (
    DuplicateReservationIdError,
    InsufficientStockError,
    ReservationNotFoundError,
    ReservationNotActiveError,
)
from .identifiers import OrderId, ReservationId, Sku, StockItemId, WarehouseId
from .values import Quantity, ReservationDeadline, StockBalance


class ReservationStatus(Enum):
    ACTIVE = "ACTIVE"
    RELEASED = "RELEASED"
    EXPIRED = "EXPIRED"


class StockReservation:
    def __init__(
        self,
        reservation_id: ReservationId,
        order_id: OrderId,
        quantity: Quantity,
        deadline: ReservationDeadline,
    ):
        self._id = reservation_id
        self._order_id = order_id
        self._quantity = quantity
        self._deadline = deadline
        self._status = ReservationStatus.ACTIVE

    def id(self) -> ReservationId:
        return self._id

    def order_id(self) -> OrderId:
        return self._order_id

    def quantity(self) -> Quantity:
        return self._quantity

    def deadline(self) -> ReservationDeadline:
        return self._deadline

    def status(self) -> ReservationStatus:
        return self._status

    def _release(self) -> None:
        if self._status is not ReservationStatus.ACTIVE:
            raise ReservationNotActiveError("Only active reservation can be released")
        self._status = ReservationStatus.RELEASED

    def _expire_if_due(self, now) -> bool:
        if self._status is not ReservationStatus.ACTIVE:
            return False
        if self._deadline.has_come(now):
            self._status = ReservationStatus.EXPIRED
            return True
        return False

    def _snapshot(self) -> "ReservationSummary":
        return ReservationSummary(
            _reservation_id=self._id,
            _order_id=self._order_id,
            _quantity=self._quantity,
            _deadline=self._deadline,
            _status=self._status,
        )


@dataclass(frozen=True)
class ReservationSummary:
    _reservation_id: ReservationId
    _order_id: OrderId
    _quantity: Quantity
    _deadline: ReservationDeadline
    _status: ReservationStatus

    @property
    def reservation_id(self) -> ReservationId:
        return self._reservation_id

    @property
    def order_id(self) -> OrderId:
        return self._order_id

    @property
    def quantity(self) -> Quantity:
        return self._quantity

    @property
    def deadline(self) -> ReservationDeadline:
        return self._deadline

    @property
    def status(self) -> ReservationStatus:
        return self._status


class StockItem:
    def __init__(
        self,
        item_id: StockItemId,
        warehouse_id: WarehouseId,
        sku: Sku,
        initial_balance: StockBalance,
    ):
        self._id = item_id
        self._warehouse_id = warehouse_id
        self._sku = sku
        self._physical_balance = initial_balance
        self._reservations: List[StockReservation] = []

    # --- чтение ---
    def id(self) -> StockItemId:
        return self._id

    def warehouse_id(self) -> WarehouseId:
        return self._warehouse_id

    def sku(self) -> Sku:
        return self._sku

    def physical_balance(self) -> StockBalance:
        return self._physical_balance

    def reservations(self) -> Tuple[ReservationSummary, ...]:
        return tuple(r._snapshot() for r in self._reservations)

    def available_quantity(self) -> StockBalance:
        active_total = sum(
            r.quantity().value
            for r in self._reservations
            if r.status() is ReservationStatus.ACTIVE
        )
        return StockBalance(self._physical_balance.value - active_total)

    # --- команды ---
    def receive(self, quantity: Quantity) -> None:
        self._physical_balance = self._physical_balance.increase(quantity)

    def write_off(self, quantity: Quantity) -> None:
        self._physical_balance = self._physical_balance.decrease(quantity)

    def reserve(
        self,
        reservation_id: ReservationId,
        order_id: OrderId,
        quantity: Quantity,
        deadline: ReservationDeadline,
    ) -> None:
        if any(r.id() == reservation_id for r in self._reservations):
            raise DuplicateReservationIdError(
                f"Reservation {reservation_id} already exists"
            )
        if self.available_quantity().value < quantity.value:
            raise InsufficientStockError("Not enough available stock to reserve")
        reservation = StockReservation(reservation_id, order_id, quantity, deadline)
        self._reservations.append(reservation)

    def release_reservation(self, reservation_id: ReservationId) -> None:
        reservation = self._find_reservation(reservation_id)
        reservation._release()

    def expire_reservations(self, now) -> int:
        expired = 0
        for reservation in self._reservations:
            if reservation._expire_if_due(now):
                expired += 1
        return expired

    # --- внутренние проверки ---
    def _find_reservation(self, reservation_id: ReservationId) -> StockReservation:
        for reservation in self._reservations:
            if reservation.id() == reservation_id:
                return reservation
        raise ReservationNotFoundError(f"Reservation {reservation_id} not found")