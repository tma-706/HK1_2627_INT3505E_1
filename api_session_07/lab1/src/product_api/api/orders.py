from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from sqlalchemy.orm import joinedload, selectinload

from ..errors import NotFoundError
from ..extensions import db
from ..models import Order, OrderItem, Product
from .order_schemas import OrderIn, OrderOut


orders_bp = Blueprint(
    "orders",
    __name__,
    url_prefix="/api/v1/orders",
)

order_in_schema = OrderIn()
order_out_schema = OrderOut()

def get_order_with_items(order_id: int) -> Order:
    statement = (
        db.select(Order)
        .options(
            selectinload(Order.items).joinedload(
                OrderItem.product
            )
        )
        .where(Order.id == order_id)
    )
    order = db.session.scalar(statement)
    if order is None:
        raise NotFoundError("order not found")
    return order

@orders_bp.post("")
def create_order():
    request_data = request.get_json(silent=True)
    data = order_in_schema.load(request_data)
    requested_items = data["items"]
    product_ids = [
        item["product_id"]
        for item in requested_items
    ]
    # Một Product chỉ xuất hiện một lần trong cùng Order.
    if len(product_ids) != len(set(product_ids)):
        raise ValidationError(
            {
                "items": [
                    "duplicate product_id in order"
                ],
            }
        )
    product_statement = db.select(Product).where(
        Product.id.in_(product_ids),
        Product.archived.is_(False),
    )
    products = db.session.execute(
        product_statement
    ).scalars().all()
    products_by_id = {
        product.id: product
        for product in products
    }
    missing_ids = sorted(
        set(product_ids) - set(products_by_id)
    )
    if missing_ids:
        raise NotFoundError(
            f"active product(s) not found: {missing_ids}"
        )
    order = Order(status="pending")
    for item_data in requested_items:
        product = products_by_id[
            item_data["product_id"]
        ]
        order.items.append(
            OrderItem(
                product=product,
                quantity=item_data["quantity"],
                unit_price_cents=product.price_cents,
            )
        )
    db.session.add(order)
    db.session.commit()
    order = get_order_with_items(order.id)
    return jsonify(
        order_out_schema.dump(order)
    ), 201


@orders_bp.get("")
def list_orders():
    statement = (
        db.select(Order)
        .options(
            selectinload(Order.items).joinedload(
                OrderItem.product
            )
        )
        .order_by(Order.id)
    )
    orders = db.session.execute(
        statement
    ).scalars().all()
    return jsonify(
        {
            "items": order_out_schema.dump(
                orders,
                many=True,
            ),
            "total": len(orders),
        }
    ), 200


@orders_bp.get("/<int:order_id>")
def get_order(order_id: int):
    order = get_order_with_items(order_id)
    return jsonify(
        order_out_schema.dump(order)
    ), 200