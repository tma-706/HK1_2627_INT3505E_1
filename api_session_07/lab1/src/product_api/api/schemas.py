from marshmallow import (
    Schema,
    ValidationError,
    fields,
    validate,
)

def validate_non_blank(value: str) -> None:
    if not value.strip():
        raise ValidationError("must not be blank")

class ProductOut(Schema):
    id = fields.Int(dump_only=True)
    sku = fields.Str()
    name = fields.Str()
    description = fields.Str(allow_none=True)
    price_cents = fields.Int()
    qty_in_stock = fields.Int()
    archived = fields.Bool()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()

class ProductIn(Schema):
    sku = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=32),
    )
    name = fields.Str(
        required=True,
        validate=[
            validate.Length(min=1, max=255),
            validate_non_blank,
        ],
    )
    description = fields.Str(
        allow_none=True,
        load_default=None,
        validate=validate.Length(max=2000),
    )
    price_cents = fields.Int(
        required=True,
        validate=validate.Range(min=0),
    )
    qty_in_stock = fields.Int(
        load_default=0,
        validate=validate.Range(min=0),
    )

class ProductPatch(Schema):
    name = fields.Str(
        validate=[
            validate.Length(min=1, max=255),
            validate_non_blank,
        ],
    )
    price_cents = fields.Int(
        validate=validate.Range(min=0),
    )

class ReserveIn(Schema):
    qty = fields.Int(
        required=True,
        validate=validate.Range(min=1),
    )