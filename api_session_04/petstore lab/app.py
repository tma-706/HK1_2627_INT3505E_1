from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import yaml
from flask import Flask, Response, jsonify, redirect, request
from flask_cors import CORS


BASE_DIR = Path(__file__).resolve().parent
SPEC_PATH = BASE_DIR / "pet_store.yaml"
ALLOWED_STATUSES = {"available", "pending", "sold"}
WRITABLE_FIELDS = {"name", "species", "breed", "age", "status", "price"}

app = Flask(__name__)
app.json.ensure_ascii = False

# Cho phép Swagger Editor online gọi API localhost. Swagger UI tại /docs
# chạy cùng origin nên không phụ thuộc CORS.
CORS(app, resources={r"/v1/*": {"origins": "https://editor.swagger.io"}})


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def base64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def create_demo_token() -> str:
    """Tạo JWT HS256 cố định để dùng thử Swagger UI trên máy local."""
    secret = os.getenv("PETSTORE_JWT_SECRET", "petstore-local-secret").encode("utf-8")
    header = base64url(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    payload = base64url(
        json.dumps(
            {"sub": "swagger-demo", "role": "petstore-user"},
            separators=(",", ":"),
        ).encode()
    )
    unsigned_token = f"{header}.{payload}"
    signature = base64url(hmac.new(secret, unsigned_token.encode(), hashlib.sha256).digest())
    return f"{unsigned_token}.{signature}"


DEMO_TOKEN = create_demo_token()


pets: list[dict] = [
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Milo",
        "species": "dog",
        "breed": "Golden Retriever",
        "age": 2,
        "status": "available",
        "price": 2500000,
        "createdAt": "2026-10-07T08:00:00Z",
        "updatedAt": "2026-10-07T08:00:00Z",
    }
]


def unauthorized():
    return jsonify({"message": "Token bị thiếu hoặc không hợp lệ"}), 401


def not_found():
    return jsonify({"message": "Không tìm thấy thú cưng"}), 404


def validation_error(errors: list[str]):
    return jsonify({"message": "Dữ liệu đầu vào không hợp lệ", "errors": errors}), 422


@app.before_request
def require_bearer_token():
    # Global security trong pet_store.yaml chỉ áp dụng cho các API /v1.
    if not request.path.startswith("/v1/"):
        return None

    authorization = request.headers.get("Authorization", "")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not hmac.compare_digest(token, DEMO_TOKEN):
        return unauthorized()
    return None


@app.get("/")
def index():
    return redirect("/docs")


@app.get("/openapi.json")
def openapi_json():
    with SPEC_PATH.open("r", encoding="utf-8") as stream:
        specification = yaml.safe_load(stream)
    return jsonify(specification)


SWAGGER_UI_HTML = """<!doctype html>
<html lang="vi">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Petstore API - Swagger UI</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-standalone-preset.js"></script>
    <script>
      SwaggerUIBundle({
        url: "/openapi.json",
        dom_id: "#swagger-ui",
        deepLinking: true,
        persistAuthorization: true,
        presets: [SwaggerUIBundle.presets.apis, SwaggerUIStandalonePreset],
        layout: "StandaloneLayout"
      });
    </script>
  </body>
</html>
"""


@app.get("/docs")
@app.get("/docs/")
def docs():
    return Response(SWAGGER_UI_HTML, mimetype="text/html")


def positive_integer(raw_value: str | None, default: int, field_name: str):
    if raw_value is None:
        return default, None
    try:
        value = int(raw_value)
    except ValueError:
        return None, f"{field_name} phải là số nguyên"
    if value < 1:
        return None, f"{field_name} phải lớn hơn hoặc bằng 1"
    return value, None


def validate_pet_input(data, *, partial: bool) -> list[str]:
    if not isinstance(data, dict):
        return ["Request body phải là một JSON object"]

    errors: list[str] = []
    unknown_fields = sorted(set(data) - WRITABLE_FIELDS)
    if unknown_fields:
        errors.append(f"Trường không được hỗ trợ: {', '.join(unknown_fields)}")

    if partial:
        if not data:
            errors.append("Phải gửi ít nhất một trường để cập nhật")
    else:
        for field in ("name", "species"):
            if field not in data:
                errors.append(f"Thiếu trường bắt buộc: {field}")

    for field in ("name", "species"):
        if field in data and (not isinstance(data[field], str) or not data[field].strip()):
            errors.append(f"{field} phải là chuỗi không rỗng")

    if "breed" in data and data["breed"] is not None and not isinstance(data["breed"], str):
        errors.append("breed phải là chuỗi hoặc null")

    if "age" in data:
        age = data["age"]
        if isinstance(age, bool) or not isinstance(age, int) or age < 0:
            errors.append("age phải là số nguyên lớn hơn hoặc bằng 0")

    if "status" in data and data["status"] not in ALLOWED_STATUSES:
        errors.append("status phải là available, pending hoặc sold")

    if "price" in data:
        price = data["price"]
        if isinstance(price, bool) or not isinstance(price, (int, float)) or price < 0:
            errors.append("price phải là số lớn hơn hoặc bằng 0")

    return errors


@app.get("/v1/pets")
def list_pets():
    page, page_error = positive_integer(request.args.get("page"), 1, "page")
    page_size, page_size_error = positive_integer(
        request.args.get("pageSize"), 10, "pageSize"
    )
    errors = [error for error in (page_error, page_size_error) if error]

    status = request.args.get("status")
    if status is not None and status not in ALLOWED_STATUSES:
        errors.append("status phải là available, pending hoặc sold")
    if errors:
        return validation_error(errors)

    filtered = [pet for pet in pets if status is None or pet["status"] == status]
    start = (page - 1) * page_size
    end = start + page_size
    return jsonify(
        {
            "items": filtered[start:end],
            "page": page,
            "pageSize": page_size,
            "total": len(filtered),
        }
    )


@app.post("/v1/pets")
def create_pet():
    data = request.get_json(silent=True)
    errors = validate_pet_input(data, partial=False)
    if errors:
        return validation_error(errors)

    timestamp = utc_now()
    pet = {
        "id": str(uuid4()),
        "name": data["name"].strip(),
        "species": data["species"].strip(),
        "status": data.get("status", "available"),
        "createdAt": timestamp,
        "updatedAt": timestamp,
    }
    for field in ("breed", "age", "price"):
        if field in data:
            pet[field] = data[field]

    pets.append(pet)
    return jsonify(pet), 201


def find_pet(pet_id: str):
    return next((pet for pet in pets if pet["id"] == pet_id), None)


@app.get("/v1/pets/<pet_id>")
def get_pet_by_id(pet_id: str):
    pet = find_pet(pet_id)
    if pet is None:
        return not_found()
    return jsonify(pet)


@app.patch("/v1/pets/<pet_id>")
def update_pet(pet_id: str):
    pet = find_pet(pet_id)
    if pet is None:
        return not_found()

    data = request.get_json(silent=True)
    errors = validate_pet_input(data, partial=True)
    if errors:
        return validation_error(errors)

    for field in WRITABLE_FIELDS:
        if field in data:
            value = data[field]
            if field in {"name", "species"}:
                value = value.strip()
            pet[field] = value
    pet["updatedAt"] = utc_now()
    return jsonify(pet)


@app.delete("/v1/pets/<pet_id>")
def delete_pet(pet_id: str):
    pet = find_pet(pet_id)
    if pet is None:
        return not_found()

    pets.remove(pet)
    return "", 204


if __name__ == "__main__":
    print("Petstore API: http://localhost:5000")
    print("Swagger UI:  http://localhost:5000/docs")
    print("OpenAPI JSON: http://localhost:5000/openapi.json")
    print(f"Demo JWT (nhập token này vào Authorize):\n{DEMO_TOKEN}")
    app.run(host="localhost", port=5000, debug=True, use_reloader=False)
