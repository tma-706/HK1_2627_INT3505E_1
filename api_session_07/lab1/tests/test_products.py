from product_api.extensions import db
from product_api.models import Product


def test_create_product(client, app):
    response = client.post(
        "/api/v1/products",
        json={
            "sku": "TEST-001",
            "name": "Test Product",
            "description": "Created by pytest",
            "price_cents": 150000,
            "qty_in_stock": 10,
        },
    )

    assert response.status_code == 201

    body = response.get_json()

    assert body["id"] > 0
    assert body["sku"] == "TEST-001"
    assert body["name"] == "Test Product"
    assert body["description"] == "Created by pytest"
    assert body["price_cents"] == 150000
    assert body["qty_in_stock"] == 10
    assert body["archived"] is False

    with app.app_context():
        product = db.session.scalar(
            db.select(Product).where(
                Product.sku == "TEST-001"
            )
        )

        assert product is not None
        assert product.name == "Test Product"
        assert product.qty_in_stock == 10