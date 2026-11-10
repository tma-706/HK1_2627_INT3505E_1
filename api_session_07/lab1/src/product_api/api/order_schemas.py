from marshmallow import Schema, fields, validate

class OrderItemIn(Schema):
    product_id = fields.Int(
        required=True,
        validate=validate.Range(min=1),
    )
    quantity = fields.Int(
        required=True,
        validate=validate.Range(min=1),
    )

class OrderIn(Schema):
    items = fields.List(
        fields.Nested(OrderItemIn),
        required=True,
        validate=validate.Length(min=1),
    )

class ProductSummary(Schema):
    id = fields.Int()
    sku = fields.Str()
    name = fields.Str()

class OrderItemOut(Schema):
    id = fields.Int()
    product_id = fields.Int()
    quantity = fields.Int()
    unit_price_cents = fields.Int()
    line_total_cents = fields.Int()
    product = fields.Nested(ProductSummary)

class OrderOut(Schema):
    id = fields.Int()
    status = fields.Str()
    created_at = fields.DateTime()
    total_cents = fields.Int()
    items = fields.List(
        fields.Nested(OrderItemOut),
    )