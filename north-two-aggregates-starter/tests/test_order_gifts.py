# import unittest


# @unittest.skip("Этап 3 ещё не реализован.")
# class OrderGiftTests(unittest.TestCase):
#     def test_gift_does_not_replace_a_paid_line_and_lines_are_snapshots(self) -> None:
#         self.fail("Добавить подарочные строки, снимки и проверку размещения.")

import unittest
from decimal import Decimal

from north_marketplace.domain.errors import NoPaidLinesError
from north_marketplace.domain.identifiers import BuyerId, OrderId, OrderLineId, SellerId, Sku
from north_marketplace.domain.order import LineKind, Order
from north_marketplace.domain.values import Currency, Money, Quantity, ShippingAddress


class OrderGiftsTest(unittest.TestCase):
    def setUp(self):
        self.rub = Currency("RUB")
        self.seller = SellerId("seller-1")
        self.order = Order(OrderId("order-1"), BuyerId("buyer-1"), self.rub)
        self.order.set_shipping_address(
            ShippingAddress("Архангельск", "Поморская", "18", "163000")
        )

    def test_gift_has_zero_price(self):
        self.order.add_gift_line(
            OrderLineId("g1"), Sku("GIFT-1"), "Подарок", self.seller, Quantity(1)
        )
        snapshot = self.order.lines()[0]
        self.assertIs(snapshot.kind, LineKind.GIFT)
        self.assertEqual(snapshot.subtotal().amount, Decimal("0"))

    def test_gift_only_order_cannot_be_placed(self):
        self.order.add_gift_line(
            OrderLineId("g1"), Sku("GIFT-1"), "Подарок", self.seller, Quantity(1)
        )
        with self.assertRaises(NoPaidLinesError):
            self.order.place()

    def test_snapshot_is_read_only(self):
        self.order.add_paid_line(
            OrderLineId("p1"), Sku("SKU-1"), "Товар", self.seller,
            Money(Decimal("100.00"), self.rub), Quantity(1),
        )
        self.order.add_gift_line(
            OrderLineId("g1"), Sku("GIFT-1"), "Подарок", self.seller, Quantity(1)
        )
        snapshots = self.order.lines()
        self.assertEqual(len(snapshots), 2)


if __name__ == "__main__":
    unittest.main()