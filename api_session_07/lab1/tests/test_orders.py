from sqlalchemy import event

from product_api.extensions import db
from product_api.models import Order, OrderItem, Product


def seed_orders(app):
    with app.app_context():
        laptop = Product(
            sku="LAPTOP-TEST",
            name="Test Laptop",
            description=None,
            price_cents=15000000,
            qty_in_stock=10,
        )

        mouse = Product(
            sku="MOUSE-TEST",
            name="Test Mouse",
            description=None,
            price_cents=300000,
            qty_in_stock=20,
        )

        db.session.add_all([laptop, mouse])
        db.session.flush()

        # Tạo nhiều Order để kiểm tra N+1.
        for _ in range(3):
            order = Order(status="pending")

            order.items.extend(
                [
                    OrderItem(
                        product=laptop,
                        quantity=1,
                        unit_price_cents=laptop.price_cents,
                    ),
                    OrderItem(
                        product=mouse,
                        quantity=2,
                        unit_price_cents=mouse.price_cents,
                    ),
                ]
            )

            db.session.add(order)

        db.session.commit()


def test_list_orders_uses_eager_loading(client, app):
    seed_orders(app)

    select_statements = []

    def count_select_statements(
        connection,
        cursor,
        statement,
        parameters,
        context,
        executemany,
    ):
        normalized_statement = statement.lstrip().upper()

        if normalized_statement.startswith("SELECT"):
            select_statements.append(statement)

    with app.app_context():
        engine = db.engine

    event.listen(
        engine,
        "before_cursor_execute",
        count_select_statements,
    )

    try:
        response = client.get("/api/v1/orders")
    finally:
        event.remove(
            engine,
            "before_cursor_execute",
            count_select_statements,
        )

    assert response.status_code == 200

    body = response.get_json()

    assert body["total"] == 3
    assert len(body["items"]) == 3

    for order in body["items"]:
        assert len(order["items"]) == 2
        assert order["total_cents"] == 15600000

        product_names = {
            item["product"]["name"]
            for item in order["items"]
        }

        assert product_names == {
            "Test Laptop",
            "Test Mouse",
        }

    # 1 SELECT lấy orders.
    # 1 SELECT lấy toàn bộ order_items + products.
    assert len(select_statements) == 2, (
        "Expected exactly 2 SELECT statements, "
        f"but got {len(select_statements)}:\n"
        + "\n\n".join(select_statements)
    )