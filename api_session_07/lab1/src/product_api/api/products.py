from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from sqlalchemy import func, update
from sqlalchemy.exc import IntegrityError
from ..errors import (
    ConflictError,
    NotFoundError,
    OutOfStockError,
)
from ..extensions import db
from ..models import Product
from .schemas import (
    ProductIn,
    ProductOut,
    ProductPatch,
    ReserveIn,
)

products_bp = Blueprint(
    "products",
    __name__,
    url_prefix="/api/v1/products",
)

product_in_schema = ProductIn()
product_out_schema = ProductOut()
product_patch_schema = ProductPatch()
reserve_in_schema = ReserveIn()

def get_active_product(product_id: int) -> Product:
    statement = db.select(Product).where(
        Product.id == product_id,
        Product.archived.is_(False),
    )
    product = db.session.scalar(statement)
    if product is None:
        raise NotFoundError("product not found")
    return product

def read_positive_query_parameter(
    name: str,
    default: int,
    maximum: int | None = None,
) -> int:
    raw_value = request.args.get(name)
    if raw_value is None:
        value = default
    else:
        try:
            value = int(raw_value)
        except ValueError as exc:
            raise ValidationError(
                {
                    name: [f"{name} must be an integer"],
                }
            ) from exc
    if value < 1:
        raise ValidationError(
            {
                name: [
                    f"{name} must be greater than or equal to 1"
                ],
            }
        )
    if maximum is not None:
        value = min(value, maximum)
    return value


@products_bp.get("")
def list_products():
    page = read_positive_query_parameter(
        name="page",
        default=1,
    )
    size = read_positive_query_parameter(
        name="size",
        default=20,
        maximum=100,
    )
    active_condition = Product.archived.is_(False)
    statement = (
        db.select(Product)
        .where(active_condition)
        .order_by(Product.id)
        .offset((page - 1) * size)
        .limit(size)
    )
    products = db.session.execute(
        statement
    ).scalars().all()
    # products = db.session.scalars(statement).all() tương đương
    total_statement = (
        db.select(func.count(Product.id))
        .where(active_condition)
    )
    total = db.session.scalar(total_statement) or 0
    return jsonify(
        {
            "items": product_out_schema.dump(
                products,
                many=True,
            ),
            "page": page,
            "size": size,
            "total": total,
        }
    ), 200


@products_bp.get("/<int:product_id>")
def get_product(product_id: int):
    product = get_active_product(product_id)
    return jsonify(
        product_out_schema.dump(product)
    ), 200


@products_bp.post("")
def create_product():
    request_data = request.get_json(silent=True)
    data = product_in_schema.load(request_data)
    product = Product(**data)
    db.session.add(product)
    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        raise ConflictError(
            "sku already exists"
        ) from exc
    return jsonify(
        product_out_schema.dump(product)
    ), 201


@products_bp.post("/<int:product_id>/reserve")
def reserve_product(product_id: int):
    request_data = request.get_json(silent=True)
    data = reserve_in_schema.load(request_data)
    quantity = data["qty"]
    statement = (
        update(Product)
        .where(
            Product.id == product_id,
            Product.archived.is_(False),
            Product.qty_in_stock >= quantity,
        )
        .values(
            qty_in_stock=Product.qty_in_stock - quantity
        )
    )
    result = db.session.execute(statement)
    if result.rowcount == 0:
        db.session.rollback()
        # Nếu tồn tại thì lỗi là thiếu hàng.
        # Nếu không tồn tại, hàm này tự trả 404.
        product = get_active_product(product_id)
        raise OutOfStockError(
            f"only {product.qty_in_stock} item(s) left"
        )
    db.session.commit()
    product = get_active_product(product_id)
    return jsonify(
        product_out_schema.dump(product)
    ), 200


@products_bp.patch("/<int:product_id>")
def patch_product(product_id: int):
    request_data = request.get_json(silent=True)
    data = product_patch_schema.load(
        request_data,
        partial=True,
    )
    if not data:
        raise ValidationError(
            {
                "body": [
                    "at least one field must be provided"
                ],
            }
        )
    product = get_active_product(product_id)
    for field_name, value in data.items():
        setattr(product, field_name, value)
    db.session.commit()
    return jsonify(
        product_out_schema.dump(product)
    ), 200


@products_bp.delete("/<int:product_id>")
def delete_product(product_id: int):
    product = get_active_product(product_id)
    product.archived = True
    db.session.commit()
    return "", 204



# Product(**data) nghĩa là gì?
# Dấu ** gọi là dictionary unpacking. Nó biến các cặp key–value trong dictionary thành keyword arguments.
# product = Product(**data)
# tương đương:
# product = Product(
#     sku=data["sku"],
#     name=data["name"],
#     description=data["description"],
#     price_cents=data["price_cents"],
#     qty_in_stock=data["qty_in_stock"],
# )