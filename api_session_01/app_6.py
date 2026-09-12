from flask import Flask, jsonify, request
from data import BOOKS

_next = len(BOOKS)

app = Flask(__name__)

def find_by_id(book_id):
    return next((book for book in BOOKS if book['id'] == book_id), None)

@app.route("/books", methods=["GET"])
def list_books():
    limit = request.args.get('limit', 100)
    return jsonify(BOOKS[:int(limit)]), 200

@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = find_by_id(book_id)
    if book is None:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book), 200

@app.route("/books", methods=["POST"])
def create_book():
    global _next
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    author = data.get("author")
    genre = data.get("genre")
    price = data.get("price")
    if not title or not author or not genre or not price:
        return jsonify({"error": "Missing required fields"}), 400
    _next += 1
    book = {
        "id": _next,
        "title": title,
        "author": author,
        "genre": genre,
        "price": price
    }
    BOOKS.append(book)
    return jsonify(book), 201, {"Location": f"/books/{_next}"}

@app.route("/books/<int:book_id>", methods=["PUT", "DELETE"])
def modify_book(book_id):
    book = find_by_id(book_id)
    if book is None:
        return jsonify({"error": "Book not found"}), 404
    if request.method == "PUT":
        data = request.get_json(silent=True) or {}
        id = data.get("id")
        title = data.get("title")
        author = data.get("author")
        genre = data.get("genre")
        price = data.get("price")
        for val in [title, author, genre]:
            if not isinstance(val, str) or not val.strip():
                return jsonify({"error": "Invalid data type"}), 400
        if isinstance(price, bool) or not isinstance(price, (int, float)) or price <= 0:
            return jsonify({"error": "Invalid data type"}), 400
        book.clear()
        book.update({
            "id": id,
            "title": title,
            "author": author,
            "genre": genre,
            "price": price
        })
        return jsonify(book), 200
    BOOKS.remove(book)
    return "", 204

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
