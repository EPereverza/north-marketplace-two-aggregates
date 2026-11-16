# import unittest


# @unittest.skip("Этап 2 ещё не реализован.")
# class OrderSellerTests(unittest.TestCase):
#     def test_line_id_is_unique_and_first_seller_rejects_another_seller(self) -> None:
#         self.fail("Добавить правило одного продавца и уникальность OrderLineId.")

import unittest
from decimal import Decimal

from north_marketplace.domain.errors import DuplicateOrderLineIdError, SellerMismatchError
from north_marketplace.domain.identifiers import BuyerId, OrderId, OrderLineId, SellerId, Sku
from north_marketplace.domain.order import Order
from north_marketplace.domain.values import Currency, Money, Quantity


class OrderSellerTest(unittest.TestCase):
    def setUp(self):
        self.rub = Currency("RUB")
        self.order = Order(OrderId("order-1"), BuyerId("buyer-1"), self.rub)

    def test_second_seller_rejected_without_changes(self):
        first = SellerId("seller-1")
        second = SellerId("seller-2")
        self.order.add_paid_line(
            OrderLineId("l1"), Sku("SKU-1"), "Товар", first,
            Money(Decimal("100.00"), self.rub), Quantity(1),
        )
        before = len(self.order.lines())
        with self.assertRaises(SellerMismatchError):
            self.order.add_paid_line(
                OrderLineId("l2"), Sku("SKU-2"), "Товар", second,
                Money(Decimal("50.00"), self.rub), Quantity(1),
            )
        self.assertEqual(len(self.order.lines()), before)
        self.assertEqual(self.order.seller_id(), first)

    def test_duplicate_line_id_rejected(self):
        seller = SellerId("seller-1")
        self.order.add_paid_line(
            OrderLineId("l1"), Sku("SKU-1"), "Товар", seller,
            Money(Decimal("100.00"), self.rub), Quantity(1),
        )
        with self.assertRaises(DuplicateOrderLineIdError):
            self.order.add_paid_line(
                OrderLineId("l1"), Sku("SKU-2"), "Товар", seller,
                Money(Decimal("50.00"), self.rub), Quantity(1),
            )


if __name__ == "__main__":
    unittest.main()