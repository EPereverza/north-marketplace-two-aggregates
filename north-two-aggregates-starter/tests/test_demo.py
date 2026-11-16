import unittest


# @unittest.skip("Демонстрационный сценарий создаётся после завершения этапа 6.")
# class DemoTests(unittest.TestCase):
#     def test_cli_coordinates_order_and_stock_item_through_order_id(self) -> None:
#         self.fail("Собрать детерминированный прикладной сценарий.")

import unittest

from north_marketplace.application import run_demo


class DemoTest(unittest.TestCase):
    def test_demo_scenario(self):
        text = run_demo()
        self.assertIn("PLACED", text)
        self.assertIn("order-100", text)
        self.assertIn("reservation-900", text)
        self.assertIn("8", text)
        self.assertIn("7", text)


if __name__ == "__main__":
    unittest.main()