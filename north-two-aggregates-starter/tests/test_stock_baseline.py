# import unittest


# @unittest.skip("Этап 4 ещё не реализован.")
# class StockBaselineTests(unittest.TestCase):
#     def test_physical_balance_never_becomes_negative(self) -> None:
#         self.fail("Реализовать базовый агрегат StockItem.")
import unittest

from north_marketplace.domain.errors import NegativeStockError
from north_marketplace.domain.identifiers import Sku, StockItemId, WarehouseId
from north_marketplace.domain.stock_item import StockItem
from north_marketplace.domain.values import Quantity, StockBalance


class StockBaselineTest(unittest.TestCase):
    def test_receive(self):
        item = StockItem(StockItemId("s1"), WarehouseId("w1"), Sku("SKU-1"), StockBalance(0))
        item.receive(Quantity(5))
        self.assertEqual(item.physical_balance().value, 5)

    def test_write_off(self):
        item = StockItem(StockItemId("s1"), WarehouseId("w1"), Sku("SKU-1"), StockBalance(5))
        item.write_off(Quantity(3))
        self.assertEqual(item.physical_balance().value, 2)

    def test_write_off_below_zero_rejected(self):
        item = StockItem(StockItemId("s1"), WarehouseId("w1"), Sku("SKU-1"), StockBalance(1))
        with self.assertRaises(NegativeStockError):
            item.write_off(Quantity(2))


if __name__ == "__main__":
    unittest.main()