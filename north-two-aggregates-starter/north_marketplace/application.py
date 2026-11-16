"""Неинтерактивная заглушка прикладного сценария."""

# def main() -> int:
#     print("Каркас практикума готов к последовательной реализации агрегатов.")
#     return 0
from datetime import datetime, timedelta
from decimal import Decimal

from .domain.identifiers import (
    BuyerId,
    OrderId,
    OrderLineId,
    ReservationId,
    SellerId,
    Sku,
    StockItemId,
    WarehouseId,
)
from .domain.order import Order, OrderStatus
from .domain.stock_item import StockItem
from .domain.values import (
    Currency,
    Money,
    Quantity,
    ReservationDeadline,
    ShippingAddress,
    StockBalance,
)


def run_demo() -> str:
    rub = Currency("RUB")
    order = Order(OrderId("order-100"), BuyerId("buyer-20"), rub)
    seller_id = SellerId("seller-7")

    order.add_paid_line(
        OrderLineId("line-1"),
        Sku("BOOK-001"),
        "Книга о Севере",
        seller_id,
        Money(Decimal("1290.00"), rub),
        Quantity(1),
    )
    order.add_gift_line(
        OrderLineId("line-2"),
        Sku("BOOKMARK-001"),
        "Закладка",
        seller_id,
        Quantity(1),
    )
    order.change_line_quantity(OrderLineId("line-1"), Quantity(2))
    order.set_shipping_address(
        ShippingAddress("Архангельск", "Поморская", "18", "163000")
    )
    order.place()

    stock_item = StockItem(
        StockItemId("stock-400"),
        WarehouseId("warehouse-ark"),
        Sku("BOOK-001"),
        StockBalance(8),
    )
    deadline = ReservationDeadline(datetime.now() + timedelta(days=1))
    stock_item.reserve(
        ReservationId("reservation-900"),
        order.id(),
        Quantity(1),
        deadline,
    )

    assert order.status() is OrderStatus.PLACED
    assert str(order.total()) == "2580.00 RUB"
    assert stock_item.physical_balance().value == 8
    assert stock_item.available_quantity().value == 7

    return (
        f"Заказ {order.id().value}: {order.status().value}, "
        f"сумма {order.total()}; "
        f"склад {stock_item.id().value}: физический остаток "
        f"{stock_item.physical_balance().value}, доступно "
        f"{stock_item.available_quantity().value}; "
        f"резерв {ReservationId('reservation-900').value} по заказу "
        f"{order.id().value}"
    )

def main() -> None:
    print(run_demo())