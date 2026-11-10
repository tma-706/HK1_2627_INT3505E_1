PRODUCTS = [
    {"id": 1, "name": "Laptop", "price": 1500},
    {"id": 2, "name": "Mouse", "price": 25},
]
def list_products():
    return PRODUCTS, 200

def create_product(body):
    product = {
        "id": max(item["id"] for item in PRODUCTS) + 1,
        "name": body["name"],
        "price": body["price"],
    }
    PRODUCTS.append(product)
    return product, 201

def get_product(id):
    product = next(
        (item for item in PRODUCTS if item["id"] == id),
        None,
    )
    if product is None:
        return {"message": "Không tìm thấy sản phẩm"}, 404
    return product, 200
