# import unittest


# @unittest.skip("Этап 5 ещё не реализован.")
# class StockReservationTests(unittest.TestCase):
#     def test_active_reservations_do_not_exceed_available_balance(self) -> None:
#         self.fail("Добавить внутреннюю сущность резерва.")

import unittest
from datetime import datetime, timedelta

from north_marketplace.domain.errors import InsufficientStockError
from north_marketplace.domain.identifiers import OrderId, ReservationId, Sku, StockItemId, WarehouseId
from north_marketplace.domain.stock_item import ReservationStatus, StockItem
from north_marketplace.domain.values import Quantity, ReservationDeadline, StockBalance


class StockReservationsTest(unittest.TestCase):
    def setUp(self):
        self.item = StockItem(StockItemId("s1"), WarehouseId("w1"), Sku("SKU-1"), StockBalance(5))
        self.deadline = ReservationDeadline(datetime.now() + timedelta(days=1))

    def test_reserve_reduces_available(self):
        self.item.reserve(ReservationId("r1"), OrderId("o1"), Quantity(2), self.deadline)
        self.assertEqual(self.item.physical_balance().value, 5)
        self.assertEqual(self.item.available_quantity().value, 3)

    def test_reserve_above_available_rejected(self):
        with self.assertRaises(InsufficientStockError):
            self.item.reserve(ReservationId("r1"), OrderId("o1"), Quantity(6), self.deadline)

    def test_release_returns_stock(self):
        self.item.reserve(ReservationId("r1"), OrderId("o1"), Quantity(2), self.deadline)
        self.item.release_reservation(ReservationId("r1"))
        self.assertEqual(self.item.available_quantity().value, 5)
        self.assertIs(self.item.reservations()[0].status, ReservationStatus.RELEASED)


if __name__ == "__main__":
    unittest.main()