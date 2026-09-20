from flask import Flask, request, jsonify, make_response
from data import BOOKS

app = Flask(__name__)

def find_by_id(book_id):
    return next((book for book in BOOKS if book['id'] == book_id), None)

@app.get("/books/<int:book_id>")
def fetch_book(book_id):
    book = find_by_id(book_id)
    if book is None:
        return jsonify({"error": "Book not found"}), 404
    resp = make_response(jsonify(book), 200)
    resp.headers["Content-Type"] = "application/json"
    resp.headers["cache-control"] = "max-age=60"
    return resp

@app.put("/books/<int:book_id>")
def update_book(book_id):
    book = find_by_id(book_id)
    if book is None:
        return jsonify({"error": "Book not found"}), 404
    data = request.get_json(silent=True) or {}
    title = data.get("title", "").strip()
    author = data.get("author", "").strip()
    genre = data.get("genre", "").strip()
    price = data.get("price")
    if not title or not author or not genre:
        return jsonify({"error": "Empty title, author, or genre field"}), 422
    if type(price) not in (int, float) or price <= 0:
        return jsonify({"error": "Price must be a positive number"}), 422
    book.clear()
    book.update({
        "id": book_id, 
        "title": title,
        "author": author,
        "genre": genre,
        "price": price
    })
    return jsonify(book), 200

@app.patch("/books/<int:book_id>")
def partial_update_book(book_id):
    book = find_by_id(book_id)
    if book is None:
        return jsonify({"error": "Book not found"}), 404
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"error": "No fields to update"}), 422
    for field in data:
        if field not in ("title", "author", "genre", "price"):
            return jsonify({"error": f"Unsupported field: {field}"}), 422
    if "price" in data:
        price = data["price"]
        if type(price) not in (int, float) or price <= 0:
            return jsonify({"error": "Price must be a positive number"}), 422
    for val in ["title", "author", "genre"]:
        if val in data:
            if not isinstance(data[val], str) or not data[val].strip():
                return jsonify({"error": f"Invalid {val}"}), 422
            data[val] = data[val].strip()
    book.update(data)
    return jsonify(book), 200

@app.delete("/books/<int:book_id>")
def delete_book(book_id):
    book = find_by_id(book_id)
    if book is None:
        return jsonify({"error": "Book not found"}), 404
    BOOKS.remove(book)
    return "", 204

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)