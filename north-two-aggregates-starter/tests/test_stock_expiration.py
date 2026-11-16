# import unittest


# @unittest.skip("Этап 6 ещё не реализован.")
# class StockExpirationTests(unittest.TestCase):
#     def test_due_reservation_expires_and_releases_balance(self) -> None:
#         self.fail("Добавить срок действия резерва.")

import unittest
from datetime import datetime, timedelta

from north_marketplace.domain.identifiers import OrderId, ReservationId, Sku, StockItemId, WarehouseId
from north_marketplace.domain.stock_item import ReservationStatus, StockItem
from north_marketplace.domain.values import Quantity, ReservationDeadline, StockBalance


class StockExpirationTest(unittest.TestCase):
    def setUp(self):
        self.item = StockItem(StockItemId("s1"), WarehouseId("w1"), Sku("SKU-1"), StockBalance(5))

    def test_expire_due_reservation(self):
        past = ReservationDeadline(datetime.now() - timedelta(seconds=1))
        self.item.reserve(ReservationId("r1"), OrderId("o1"), Quantity(2), past)
        self.assertEqual(self.item.expire_reservations(datetime.now()), 1)
        self.assertIs(self.item.reservations()[0].status, ReservationStatus.EXPIRED)
        self.assertEqual(self.item.available_quantity().value, 5)

    def test_future_reservation_stays_active(self):
        future = ReservationDeadline(datetime.now() + timedelta(days=1))
        self.item.reserve(ReservationId("r1"), OrderId("o1"), Quantity(2), future)
        self.assertEqual(self.item.expire_reservations(datetime.now()), 0)
        self.assertIs(self.item.reservations()[0].status, ReservationStatus.ACTIVE)

    def test_released_reservation_not_expired(self):
        past = ReservationDeadline(datetime.now() - timedelta(seconds=1))
        self.item.reserve(ReservationId("r1"), OrderId("o1"), Quantity(2), past)
        self.item.release_reservation(ReservationId("r1"))
        self.assertEqual(self.item.expire_reservations(datetime.now()), 0)
        self.assertIs(self.item.reservations()[0].status, ReservationStatus.RELEASED)


if __name__ == "__main__":
    unittest.main()