# import unittest


# @unittest.skip("Этап 1 ещё не реализован.")
# class OrderBaselineTests(unittest.TestCase):
#     def test_line_id_changes_quantity_and_place_requires_full_order(self) -> None:
#         self.fail("Реализовать базовый Order, OrderLineId и снимки строк.")

import unittest
from decimal import Decimal

from north_marketplace.domain.errors import (
    EmptyOrderError,
    IncompleteShippingAddressError,
    OrderNotDraftError,
)
from north_marketplace.domain.identifiers import BuyerId, OrderId, OrderLineId, SellerId, Sku
from north_marketplace.domain.order import Order, OrderStatus
from north_marketplace.domain.values import Currency, Money, Quantity, ShippingAddress


class OrderBaselineTest(unittest.TestCase):
    def setUp(self):
        self.rub = Currency("RUB")
        self.seller = SellerId("seller-7")
        self.order = Order(OrderId("order-1"), BuyerId("buyer-1"), self.rub)

    def test_empty_order_cannot_be_placed(self):
        with self.assertRaises(EmptyOrderError):
            self.order.place()

    def test_place_requires_address(self):
        self.order.add_paid_line(
            OrderLineId("l1"), Sku("SKU-1"), "Товар", self.seller,
            Money(Decimal("100.00"), self.rub), Quantity(1),
        )
        with self.assertRaises(IncompleteShippingAddressError):
            self.order.place()

    def test_place_success(self):
        self.order.add_paid_line(
            OrderLineId("l1"), Sku("SKU-1"), "Товар", self.seller,
            Money(Decimal("100.00"), self.rub), Quantity(1),
        )
        self.order.set_shipping_address(
            ShippingAddress("Архангельск", "Поморская", "18", "163000")
        )
        self.order.place()
        self.assertIs(self.order.status(), OrderStatus.PLACED)

    def test_currency_mismatch_rejected(self):
        usd = Currency("USD")
        with self.assertRaises(Exception):
            self.order.add_paid_line(
                OrderLineId("l1"), Sku("SKU-1"), "Товар", self.seller,
                Money(Decimal("100.00"), usd), Quantity(1),
            )

    def test_change_line_quantity_by_id(self):
        self.order.add_paid_line(
            OrderLineId("l1"), Sku("SKU-1"), "Товар", self.seller,
            Money(Decimal("100.00"), self.rub), Quantity(1),
        )
        self.order.change_line_quantity(OrderLineId("l1"), Quantity(3))
        self.assertEqual(self.order.lines()[0].quantity.value, 3)

    def test_immutable_after_place(self):
        self.order.add_paid_line(
            OrderLineId("l1"), Sku("SKU-1"), "Товар", self.seller,
            Money(Decimal("100.00"), self.rub), Quantity(1),
        )
        self.order.set_shipping_address(
            ShippingAddress("Архангельск", "Поморская", "18", "163000")
        )
        self.order.place()
        with self.assertRaises(OrderNotDraftError):
            self.order.change_line_quantity(OrderLineId("l1"), Quantity(2))


if __name__ == "__main__":
    unittest.main()