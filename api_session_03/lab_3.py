from flask import Flask, jsonify, request
from data import ORDERS
import base64
import binascii
import json

app = Flask(__name__)

ALL_FIELDS = (
    "id",
    "customer_id",
    "status",
    "total",
    "created_at",
)
SORTABLE_FIELDS = {
    "id",
    "total",
    "created_at",
}

def error_response(detail):
    return jsonify({
        "type": "about:blank",
        "title": "Invalid Request",
        "status": 400,
        "detail": detail,
        "instance": request.path,
    }), 400

def encode_cursor(order, sort_parameter):
    descending = sort_parameter.startswith("-")
    if descending:
        sort_field = sort_parameter[1:]
    else:
        sort_field = sort_parameter

    cursor_data = {
        "sort": sort_parameter,
        "value": order[sort_field],
        "id": order["id"],
    }
    cursor_json = json.dumps(cursor_data)
    cursor_bytes = base64.urlsafe_b64encode(
        cursor_json.encode("utf-8")
    )
    return cursor_bytes.decode("ascii")

def decode_cursor(cursor_text):
    try:
        cursor_bytes = base64.b64decode(
            cursor_text.encode("ascii"),
            altchars=b"-_",
            validate=True,
        )
        cursor_json = cursor_bytes.decode("utf-8")
        cursor_data = json.loads(cursor_json)
        if not isinstance(cursor_data, dict):
            raise ValueError()
        if "sort" not in cursor_data:
            raise ValueError()
        if "value" not in cursor_data:
            raise ValueError()
        if "id" not in cursor_data:
            raise ValueError()
        return cursor_data
    except (
        ValueError,
        TypeError,
        UnicodeError,
        binascii.Error,
    ):
        return None

@app.get("/orders")
def get_orders():
# Kiểm tra và xử lý tham số limit
    limit = request.args.get("limit", 3)
    try:
        limit = int(limit)
    except ValueError:
        return error_response(
            "Limit must be an integer."
        )
    if limit < 1 or limit > 100:
        return error_response(
            "Limit must be between 1 and 100."
        )
# Kiểm tra và xử lý tham số sort
    sort = request.args.get("sort", "id")
    descending = sort.startswith("-")
    if descending:
        sort_field = sort[1:]
    else:
        sort_field = sort
    if sort_field not in SORTABLE_FIELDS:
        return error_response(
            f"Sort field must be one of: {', '.join(SORTABLE_FIELDS)}"
        )
# Kiểm tra và xử lý tham số selected fields
    fields = request.args.get("fields", None)
    if fields is None:
        selected_fields = ALL_FIELDS
    else:
        selected_fields = [
            field.strip() for field in fields.split(",") if field.strip()
        ]
        if not selected_fields:
            return error_response(
                "Fields parameter must not be empty."
            )
        invalid_fields = [
            field for field in selected_fields if field not in ALL_FIELDS
        ]
        if invalid_fields:
            return error_response(
                f"Invalid fields: {', '.join(invalid_fields)}"
            )
    orders = list(ORDERS)
# Lọc theo trạng thái và customer_id nếu có
    status = request.args.get("status", None)
    if status is not None:
        orders = [order for order in orders if order["status"] == status]

    customer_id = request.args.get("customer_id", None)
    if customer_id is not None:
        try:
            customer_id = int(customer_id)
        except ValueError:
            return error_response(
                "Customer ID must be an integer."
            )
        orders = [order for order in orders if order["customer_id"] == customer_id]
# Sắp xếp danh sách đơn hàng
    orders.sort(key=lambda order: (order[sort_field], order["id"]), reverse=descending)
# Xử lý tham số cursor nếu có
    cursor = request.args.get("cursor", None)
    if cursor is not None:
        cursor_data = decode_cursor(cursor)
        if cursor_data is None:
            return error_response(
                "The cursor is malformed or invalid."
            )
        if cursor_data["sort"] != sort:
            return error_response(
                "Cursor sort does not match request sort."
            )
        cursor_position = (
            cursor_data["value"],
            cursor_data["id"],
        )
        try:
            if descending:
                orders = [
                    order for order in orders 
                    if (
                        order[sort_field],
                        order["id"],
                    ) < cursor_position
                ]
            else:
                orders = [
                    order for order in orders
                    if (
                        order[sort_field],
                        order["id"],
                    ) > cursor_position
                ]
        except TypeError:
            return error_response(
                "The cursor contains an invalid value."
            )
# Xác định xem có nhiều đơn hàng hơn giới hạn hay không và tạo trang kết quả
    has_more = len(orders) > limit
    page = orders[:limit]
    if has_more:
        next_cursor = encode_cursor(page[-1], sort)
    else:
        next_cursor = None

    response_data = [
        {
            field: order[field]
            for field in selected_fields
        }
        for order in page
    ]
    return jsonify({
        "data": response_data,
        "pagination": {
            "limit": limit,
            "has_more": has_more,
            "next_cursor": next_cursor,
        },
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)