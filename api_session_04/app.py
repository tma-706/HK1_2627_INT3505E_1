# temp server for testing OpenAPI spec with Swagger Editor
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)

# Cho phép editor.swagger.io gọi API localhost
CORS(app, origins=["https://editor.swagger.io"])

books = [
    {
        "id": 1,
        "title": "Lập trình Python cơ bản",
        "author": "Nguyễn Văn An",
        "isbn": "9786040000000",
        "price": 120000
    },
    {
        "id": 2,
        "title": "Nhập môn Java",
        "author": "Trần Văn Bình",
        "isbn": "9786040000001",
        "price": 100000
    }
]


def problem(status, title, detail, instance):
    response = jsonify({
        "type": "about:blank",
        "title": title,
        "status": status,
        "detail": detail,
        "instance": instance
    })
    response.status_code = status
    response.content_type = "application/problem+json"
    return response


@app.get("/v1/books")
def list_books():
    query = request.args.get("q", "").strip().lower()
    limit_value = request.args.get("limit", "20")

    try:
        limit = int(limit_value)
    except ValueError:
        return problem(
            400,
            "Bad Request",
            "Tham số limit phải là số nguyên.",
            request.full_path.rstrip("?")
        )

    if limit < 1 or limit > 100:
        return problem(
            400,
            "Bad Request",
            "Tham số limit phải nằm trong khoảng từ 1 đến 100.",
            request.full_path.rstrip("?")
        )

    result = books

    if query:
        result = [
            book for book in books
            if query in book["title"].lower()
        ]

    return jsonify(result[:limit]), 200


@app.get("/v1/books/<book_id>")
def get_book_by_id(book_id):
    try:
        parsed_id = int(book_id)
    except ValueError:
        return problem(
            400,
            "Bad Request",
            "BookId phải là số nguyên lớn hơn hoặc bằng 1.",
            request.path
        )

    if parsed_id < 1:
        return problem(
            400,
            "Bad Request",
            "BookId phải là số nguyên lớn hơn hoặc bằng 1.",
            request.path
        )

    book = next(
        (book for book in books if book["id"] == parsed_id),
        None
    )

    if book is None:
        return problem(
            404,
            "Not Found",
            f"Không tìm thấy sách có bookId bằng {parsed_id}.",
            request.path
        )

    return jsonify(book), 200


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)