from flask import Flask
from flask.views import MethodView
from flask_smorest import Api, Blueprint, abort
from marshmallow import Schema, fields


# Dữ liệu tạm trong RAM
PRODUCTS = [
    {"id": 1, "name": "Laptop", "price": 1500},
    {"id": 2, "name": "Mouse", "price": 25},
]

# Schema dùng cho response
class ProductSchema(Schema):
    id = fields.Int(required=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)

# Schema dùng để validate POST body
class ProductCreateSchema(Schema):
    name = fields.Str(required=True)
    price = fields.Float(required=True)


products_blp = Blueprint(
    "products",
    __name__,
    description="Quản lý sản phẩm",
)


@products_blp.route("/products")
class ProductList(MethodView):

    @products_blp.response(200, ProductSchema(many=True))
    def get(self):
        """Lấy danh sách sản phẩm."""
        return PRODUCTS

    @products_blp.arguments(ProductCreateSchema)
    @products_blp.response(201, ProductSchema)
    def post(self, product_data):
        """Tạo sản phẩm mới."""
        product = {
            "id": max((item["id"] for item in PRODUCTS), default=0) + 1,
            **product_data,
        }

        PRODUCTS.append(product)
        return product


@products_blp.route("/products/<int:product_id>")
class ProductById(MethodView):

    @products_blp.response(200, ProductSchema)
    def get(self, product_id):
        """Lấy sản phẩm theo ID."""
        product = next(
            (item for item in PRODUCTS if item["id"] == product_id),
            None,
        )

        if product is None:
            abort(404, message="Không tìm thấy sản phẩm")

        return product


app = Flask(__name__)

app.config.update(
    API_TITLE="Product API - Flask-Smorest",
    API_VERSION="1.0.0",
    OPENAPI_VERSION="3.0.3",
    OPENAPI_URL_PREFIX="/",
    OPENAPI_SWAGGER_UI_PATH="/docs",
    OPENAPI_SWAGGER_UI_URL="https://cdn.jsdelivr.net/npm/swagger-ui-dist/",
)

api = Api(app)
api.register_blueprint(products_blp)


if __name__ == "__main__":
    app.run(port=8001, debug=True)